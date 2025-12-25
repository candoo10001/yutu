"""
Video generation module using Google Veo 3 API.
"""
import time
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types
import structlog

from .config import Config
from .utils.error_handler import VideoGenerationError
from .utils.logger import log_api_call, log_api_response, log_error


class VeoGenerator:
    """Generates videos using Google Veo 3 API."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Veo Generator.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()
        # Initialize client with API key
        try:
            self.client = genai.Client(api_key=config.google_api_key)
        except TypeError as e:
            # Fallback: try with environment variable
            import os
            os.environ["GOOGLE_API_KEY"] = config.google_api_key
            self.client = genai.Client()
        # Use veo-3.1-generate-preview for latest features or veo-3.0-generate-001 for stable
        self.model = "veo-3.1-generate-preview"

    def generate_video(
        self,
        prompt: str,
        korean_script: str = None,
        aspect_ratio: str = "16:9",
        resolution: str = "720p",
        output_dir: str = "output"
    ) -> str:
        """
        Generate a video using Veo 3 API.

        Args:
            prompt: Visual description prompt
            korean_script: Optional Korean dialogue/narration to include
            aspect_ratio: Video aspect ratio (16:9 or 9:16)
            resolution: Video resolution (720p or 1080p)
            output_dir: Directory to save the generated video

        Returns:
            Path to the generated video file

        Raises:
            VideoGenerationError: If video generation fails
        """
        start_time = time.time()

        # Combine visual prompt with Korean dialogue if provided
        # Veo 3 generates audio from dialogue cues in the prompt
        # For Korean audio: must specify "speaking in Korean" or "must speak in Korean"
        # Include exact Korean sentences within quotation marks
        # IMPORTANT: Add audio separately without affecting visual content
        if korean_script:
            # Add Korean narration audio separately - this won't affect the visual prompt
            # The visual prompt describes scenes, and audio is added as narration overlay
            full_prompt = f"{prompt}\n\nBackground narration audio in Korean: \"{korean_script}\". The narrator must speak in Korean."
        else:
            full_prompt = prompt

        log_api_call(
            self.logger,
            "Veo 3 API",
            "generate_video",
            prompt_length=len(full_prompt),
            has_korean_audio=bool(korean_script)
        )

        try:
            self.logger.info(
                "generating_video_with_veo3",
                model=self.model,
                aspect_ratio=aspect_ratio,
                resolution=resolution
            )

            # Call Veo 3 API (audio is generated natively by Veo 3.1)
            # Veo 3.1 supports durations of 4, 6, or 8 seconds per clip
            # Use 8 seconds for maximum duration per clip
            operation = self.client.models.generate_videos(
                model=self.model,
                prompt=full_prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio=aspect_ratio,
                    resolution=resolution,
                    duration_seconds="8",  # Maximum duration per clip
                ),
            )

            # Wait for video generation to complete
            self.logger.info("waiting_for_video_generation", operation_name=operation.name)

            # Poll for completion
            max_wait_seconds = 600  # 10 minutes
            poll_interval = 15  # Check every 15 seconds
            elapsed = 0

            while not operation.done and elapsed < max_wait_seconds:
                time.sleep(poll_interval)
                elapsed += poll_interval
                # Refresh operation status
                operation = self.client.operations.get(operation)
                self.logger.info(
                    "video_generation_status",
                    elapsed_seconds=elapsed,
                    max_wait_seconds=max_wait_seconds
                )

            if not operation.done:
                raise VideoGenerationError(
                    f"Video generation timed out after {max_wait_seconds} seconds"
                )

            # Check if there was an error in the operation
            if hasattr(operation, 'error') and operation.error:
                raise VideoGenerationError(f"Veo API error: {operation.error}")

            # Get the generated video - use operation.response (as per documentation)
            generated_video = None
            if hasattr(operation, 'response') and operation.response:
                if hasattr(operation.response, 'generated_videos') and operation.response.generated_videos:
                    generated_video = operation.response.generated_videos[0]

            if not generated_video:
                # Log the operation structure for debugging
                self.logger.error(
                    "no_video_in_response",
                    operation_done=operation.done,
                    has_response=hasattr(operation, 'response'),
                    has_result=hasattr(operation, 'result'),
                    response_str=str(operation.response) if hasattr(operation, 'response') else None
                )
                raise VideoGenerationError("No video generated in response - check logs for details")

            # Download the video
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            video_file = output_path / f"veo_video_{int(time.time())}.mp4"

            # Download video file using the client
            self.client.files.download(file=generated_video.video)
            generated_video.video.save(str(video_file))

            # Verify file was saved
            file_size = video_file.stat().st_size
            if file_size == 0:
                raise VideoGenerationError("Generated video file is empty")

            duration_ms = (time.time() - start_time) * 1000

            log_api_response(
                self.logger,
                "Veo 3 API",
                "generate_video",
                success=True,
                duration_ms=duration_ms,
                video_path=str(video_file)
            )

            self.logger.info(
                "veo_video_generated",
                video_path=str(video_file),
                file_size_mb=round(file_size / (1024 * 1024), 2),
                generation_time_seconds=round(duration_ms / 1000, 2)
            )

            return str(video_file)

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "Veo 3 API",
                "generate_video",
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            log_error(self.logger, e, "veo_generator.generate_video")
            raise VideoGenerationError(f"Veo 3 video generation failed: {str(e)}")
