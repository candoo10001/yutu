"""
Image prompt generation module for script segments using Gemini API.
"""
import time
from typing import Optional

import structlog

from .config import Config
from .gemini_client import GeminiClient
from .script_segmenter import ScriptSegment
from .utils.error_handler import VideoGenerationError
from .utils.logger import log_api_call, log_api_response, log_error


class SegmentImagePromptGenerator:
    """Generates image prompts for script segments using Gemini API."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Segment Image Prompt Generator.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()
        self.gemini_client = GeminiClient(config, logger)

    def generate_image_prompt(self, segment: ScriptSegment, context: str = "") -> str:
        """
        Generate an image prompt for a script segment.

        Args:
            segment: ScriptSegment instance
            context: Additional context about the overall topic (optional)

        Returns:
            Image generation prompt (string)

        Raises:
            VideoGenerationError: If prompt generation fails
        """
        start_time = time.time()

        log_api_call(
            self.logger,
            "Gemini API",
            "generate_image_prompt",
            segment_number=segment.segment_number,
            segment_length=len(segment.text)
        )

        try:
            # Create prompt for Gemini
            prompt = self._create_image_prompt_generation_prompt(segment, context)

            # Call Gemini API (much cheaper than Claude)
            image_prompt = self.gemini_client.generate_text(
                prompt=prompt,
                operation="generate_image_prompt"
            )

            duration_ms = (time.time() - start_time) * 1000

            log_api_response(
                self.logger,
                "Gemini API",
                "generate_image_prompt",
                success=True,
                duration_ms=duration_ms,
                prompt_length=len(image_prompt)
            )

            self.logger.info(
                "image_prompt_generated",
                segment_number=segment.segment_number,
                prompt_length=len(image_prompt),
                prompt_preview=image_prompt[:100] + "..." if len(image_prompt) > 100 else image_prompt
            )

            return image_prompt

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "Gemini API",
                "generate_image_prompt",
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            log_error(self.logger, e, "segment_image_prompt_generator.generate_image_prompt")
            raise VideoGenerationError(f"Image prompt generation failed: {str(e)}")

    def _create_image_prompt_generation_prompt(self, segment: ScriptSegment, context: str) -> str:
        """
        Create a prompt for Gemini to generate an image prompt.

        Args:
            segment: ScriptSegment instance
            context: Additional context

        Returns:
            Gemini prompt for image generation
        """
        context_section = f"\n\nOverall Context: {context}" if context else ""

        return f"""You are an expert at creating PHOTOREALISTIC image generation prompts for YouTube Shorts news content.

Create a detailed PHOTOREALISTIC image generation prompt in English for the following Korean script segment:

Script Segment #{segment.segment_number}:
"{segment.text}"{context_section}

Requirements:
1. **CRITICAL**: The image must NOT contain any text, words, or captions
2. **PHOTOREALISM**: Use real-world photography style, NOT illustration or 3D render
3. **SUBJECT-FOCUSED**: Focus on the main subject/object mentioned in the script, NOT human figures
   - If the script mentions Ethereum/cryptocurrency → Show Ethereum logo, coin, blockchain symbol
   - If the script mentions Tesla → Show Tesla cars, Tesla logo, Tesla vehicles
   - If the script mentions Apple → Show Apple products, iPhone, MacBook, Apple logo
   - If the script mentions stock market → Show stock ticker displays, charts, trading screens (NOT people)
   - If the script mentions a company → Show company logo, products, headquarters building
4. Use photography terminology: "shot on Sony A7IV", "85mm lens", "f/1.4", "natural lighting", "shallow depth of field"
5. Suitable for vertical format (9:16 aspect ratio) for YouTube Shorts
6. Professional news photography quality - like Reuters, AP, Bloomberg
7. Include specific details: exact scene, camera angle, lighting, mood
8. Focus on objects, products, logos, symbols, and company-related visuals
9. Write the prompt in English only

AVOID: 
- Human figures, people, traders, workers (unless the script specifically requires showing people)
- 3D renders, illustrations, cartoon style, abstract art, futuristic/sci-fi elements, glowing effects, digital art style
- Generic office scenes or corporate environments - focus on the SPECIFIC subject mentioned

Output ONLY the image generation prompt, nothing else.

Example format:
"Professional business photograph of [specific real scene], shot on Sony A7IV with 85mm lens, f/2.8, natural office lighting, shallow depth of field, photojournalism style, Reuters quality, vertical 9:16 composition, ultra-realistic, NO TEXT"
"""
