"""
Image generation module using Google Gemini Image API.
"""
import base64
import time
from pathlib import Path
from typing import Optional

import requests
import structlog

from .config import Config
from .utils.error_handler import VideoGenerationError
from .utils.logger import log_api_call, log_api_response, log_error


class ImageGenerator:
    """Generates images using Gemini Image API (gemini-2.5-flash-image)."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Image Generator.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()
        self.api_key = config.google_api_key
        self.model = "gemini-2.5-flash-image"  # Model with image generation
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def generate_image(
        self,
        prompt: str,
        output_dir: str = "output",
        aspect_ratio: str = "9:16"
    ) -> str:
        """
        Generate an image from a text prompt using Gemini Image API.

        Args:
            prompt: Image generation prompt (without text instructions)
            output_dir: Directory to save the generated image
            aspect_ratio: Aspect ratio for the image (9:16 for vertical, 16:9 for horizontal, 1:1 for square)

        Returns:
            Path to the generated image file

        Raises:
            VideoGenerationError: If image generation fails
        """
        start_time = time.time()

        # Enhance prompt to explicitly exclude text
        enhanced_prompt = f"{prompt}. NO TEXT, NO WORDS, NO CAPTIONS in the image. Pure visual content only."

        log_api_call(
            self.logger,
            "Gemini Image",
            "generate_image",
            prompt_length=len(enhanced_prompt),
            aspect_ratio=aspect_ratio
        )

        try:
            # Call Gemini Image API
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

            headers = {
                "Content-Type": "application/json"
            }

            payload = {
                "contents": [{
                    "parts": [{
                        "text": enhanced_prompt
                    }]
                }],
                "generationConfig": {
                    "responseModalities": ["IMAGE"]  # Request only IMAGE, not TEXT
                }
            }

            self.logger.info("calling_gemini_image_api", model=self.model)

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=60
            )

            # Log response
            self.logger.info(
                "gemini_image_response",
                status_code=response.status_code,
                response_preview=response.text[:200] if response.text else ""
            )

            if response.status_code != 200:
                raise VideoGenerationError(
                    f"Gemini Image API error: {response.status_code} - {response.text}"
                )

            data = response.json()

            # Extract image from response
            # Response format: candidates[0].content.parts[] - find the part with inlineData
            try:
                # Check if candidates exist
                if "candidates" not in data or len(data["candidates"]) == 0:
                    self.logger.error("no_candidates_in_response", response_data=str(data)[:500])
                    raise VideoGenerationError("No candidates in API response")

                candidate = data["candidates"][0]
                
                # Check for finishReason - STOP means successful completion, others indicate issues
                if "finishReason" in candidate:
                    finish_reason = candidate.get("finishReason")
                    
                    # STOP means the generation completed successfully - this is normal
                    if finish_reason == "STOP":
                        # This is expected - generation completed successfully
                        self.logger.debug(
                            "candidate_finish_reason_stop",
                            finish_reason=finish_reason,
                            has_content="content" in candidate
                        )
                        # Continue processing - don't treat STOP as an error
                    elif finish_reason in ["SAFETY", "RECITATION"]:
                        # Content was blocked by safety filters
                        self.logger.warning(
                            "candidate_finish_reason_blocked",
                            finish_reason=finish_reason,
                            candidate_keys=list(candidate.keys())
                        )
                        safety_ratings = candidate.get("safetyRatings", [])
                        blocking_ratings = [r for r in safety_ratings 
                                           if r.get("probability") in ["HIGH", "MEDIUM"]]
                        error_msg = f"Content blocked by safety filters (finishReason: {finish_reason})"
                        if blocking_ratings:
                            error_msg += f": {blocking_ratings}"
                        raise VideoGenerationError(error_msg)
                    elif finish_reason == "OTHER":
                        self.logger.warning(
                            "candidate_finish_reason_other",
                            finish_reason=finish_reason,
                            candidate_keys=list(candidate.keys())
                        )
                        raise VideoGenerationError(f"Content generation failed (finishReason: {finish_reason}). The prompt may be inappropriate or the API may be experiencing issues.")
                    else:
                        # Unknown finish reason - log but don't fail if content exists
                        self.logger.warning(
                            "candidate_finish_reason_unknown",
                            finish_reason=finish_reason,
                            candidate_keys=list(candidate.keys())
                        )
                        # Only fail if there's no content
                        if "content" not in candidate:
                            raise VideoGenerationError(f"Content generation failed (finishReason: {finish_reason})")
                
                # Check for safety rating blocking
                if "safetyRatings" in candidate:
                    blocking_ratings = [r for r in candidate["safetyRatings"] 
                                       if r.get("probability") in ["HIGH", "MEDIUM"]]
                    if blocking_ratings:
                        self.logger.warning("content_blocked_by_safety", ratings=blocking_ratings)
                        raise VideoGenerationError(f"Content blocked by safety filters: {blocking_ratings}")

                if "content" not in candidate:
                    self.logger.error(
                        "no_content_in_candidate",
                        candidate_keys=list(candidate.keys()),
                        finish_reason=candidate.get("finishReason", "not provided")
                    )
                    raise VideoGenerationError(
                        f"No content in candidate response. Finish reason: {candidate.get('finishReason', 'unknown')}"
                    )

                parts = candidate["content"]["parts"]
                
                # Log parts structure for debugging
                part_types = [list(part.keys()) for part in parts]
                self.logger.debug("response_parts_structure", part_types=part_types)
                
                image_part = None
                for i, part in enumerate(parts):
                    if "inlineData" in part:
                        image_part = part
                        self.logger.debug("found_image_part", part_index=i)
                        break

                if not image_part:
                    # Log what we actually received
                    self.logger.error(
                        "no_image_in_response",
                        response_structure={
                            "has_candidates": "candidates" in data,
                            "num_candidates": len(data.get("candidates", [])),
                            "num_parts": len(parts),
                            "part_keys": part_types
                        },
                        response_preview=str(data)[:1000]
                    )
                    raise VideoGenerationError("No image found in response - check logs for response structure")

                image_data = image_part["inlineData"]["data"]
                mime_type = image_part["inlineData"]["mimeType"]
                
                if not image_data:
                    raise VideoGenerationError("Image data is empty in response")
                    
            except (KeyError, IndexError) as e:
                self.logger.error("response_parsing_error", error=str(e), response_preview=str(data)[:500])
                raise VideoGenerationError(f"Failed to extract image from response: {str(e)}. Check logs for response structure.")

            # Determine file extension from mime type
            extension = "jpg"
            if "png" in mime_type:
                extension = "png"
            elif "webp" in mime_type:
                extension = "webp"

            # Save image
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            image_file = output_path / f"image_{int(time.time())}.{extension}"

            # Decode and save image
            image_bytes = base64.b64decode(image_data)
            with open(image_file, "wb") as f:
                f.write(image_bytes)

            # Verify file was saved
            file_size = image_file.stat().st_size
            if file_size == 0:
                raise VideoGenerationError("Generated image file is empty")

            duration_ms = (time.time() - start_time) * 1000

            log_api_response(
                self.logger,
                "Gemini Image",
                "generate_image",
                success=True,
                duration_ms=duration_ms,
                image_path=str(image_file)
            )

            self.logger.info(
                "image_generated",
                image_path=str(image_file),
                file_size_kb=round(file_size / 1024, 2),
                generation_time_seconds=round(duration_ms / 1000, 2)
            )

            return str(image_file)

        except requests.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "Gemini Image",
                "generate_image",
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            log_error(self.logger, e, "image_generator.generate_image")
            raise VideoGenerationError(f"Gemini Image API request failed: {str(e)}")

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "Gemini Image",
                "generate_image",
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            log_error(self.logger, e, "image_generator.generate_image")
            raise VideoGenerationError(f"Image generation failed: {str(e)}")
