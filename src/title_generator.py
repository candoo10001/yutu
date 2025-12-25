"""
Title generation module for creating catchy segment titles using Gemini API.
"""
import time
from typing import Optional

import structlog

from .config import Config
from .gemini_client import GeminiClient
from .script_segmenter import ScriptSegment
from .utils.error_handler import VideoGenerationError
from .utils.logger import log_api_call, log_api_response, log_error


class TitleGenerator:
    """Generates catchy titles for script segments using Gemini API."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Title Generator.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()
        self.gemini_client = GeminiClient(config, logger)

    def generate_title(self, segment: ScriptSegment, context: str = "") -> str:
        """
        Generate a catchy title for a script segment.

        Args:
            segment: ScriptSegment instance
            context: Additional context about the overall topic (optional)

        Returns:
            Meaningful title sentence in Korean

        Raises:
            VideoGenerationError: If title generation fails
        """
        start_time = time.time()

        log_api_call(
            self.logger,
            "Gemini API",
            "generate_title",
            segment_number=segment.segment_number,
            segment_length=len(segment.text)
        )

        try:
            # Create prompt for Gemini
            prompt = self._create_title_generation_prompt(segment, context)

            # Call Gemini API (much cheaper than Claude)
            title = self.gemini_client.generate_text(
                prompt=prompt,
                operation="generate_title"
            )

            # Clean up the title (remove quotes, extra spaces)
            title = title.strip().strip('"').strip("'").strip()

            duration_ms = (time.time() - start_time) * 1000

            log_api_response(
                self.logger,
                "Gemini API",
                "generate_title",
                success=True,
                duration_ms=duration_ms,
                title=title
            )

            self.logger.info(
                "title_generated",
                segment_number=segment.segment_number,
                title=title
            )

            return title

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "Gemini API",
                "generate_title",
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            log_error(self.logger, e, "title_generator.generate_title")
            raise VideoGenerationError(f"Title generation failed: {str(e)}")

    def _create_title_generation_prompt(self, segment: ScriptSegment, context: str) -> str:
        """
        Create a prompt for Gemini to generate a catchy title.

        Args:
            segment: ScriptSegment instance
            context: Additional context

        Returns:
            Gemini prompt for title generation
        """
        context_section = f"\n\nOverall Context: {context}" if context else ""

        return f"""You are an expert at creating meaningful Korean titles for YouTube Shorts segments.

Create a SHORT Korean title that makes sense as a complete sentence for the following script segment:

Script Segment #{segment.segment_number}:
"{segment.text}"{context_section}

Requirements:
1. **CRITICAL**: The title must form a complete, meaningful sentence (max 5 words)
2. The sentence should make grammatical sense and convey the key message
3. Keep it concise but complete - aim for 3-5 words that form a natural sentence
4. Catchy and attention-grabbing while being grammatically correct
5. Summarizes the key point of this segment in a natural Korean sentence structure
6. Perfect for a title bar overlay on video

Examples of good titles (meaningful sentences):
- "엔비디아 주가 급등하며 신기록" (Nvidia stock surged to set a new record)
- "테슬라 전기차 판매에서 새로운 기록" (Tesla achieved a new record in electric vehicle sales)
- "연준 금리 동결을 결정" (The Fed decided to freeze interest rates)
- "삼성 경쟁사들을 제치고 시장을 역전" (Samsung overtook competitors to reverse the market)

Output ONLY the title in Korean, nothing else. No quotes, no explanations.
"""
