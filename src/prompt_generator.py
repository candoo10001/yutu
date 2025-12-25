"""
Video prompt generation module using Gemini API to create visual prompts for Kling.
"""
import time
from typing import List, Optional

import structlog

from .config import Config
from .gemini_client import GeminiClient
from .news_fetcher import NewsArticle
from .utils.error_handler import PromptGenerationError
from .utils.logger import log_error


class PromptGenerator:
    """Generates visual video prompts for Kling API using Gemini."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Prompt Generator.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()
        self.client = GeminiClient(config, logger)

    def generate_video_prompt(self, articles: List[NewsArticle]) -> str:
        """
        Generate a visual video prompt from news articles.

        Args:
            articles: List of NewsArticle instances

        Returns:
            Video prompt string optimized for Kling API

        Raises:
            PromptGenerationError: If prompt generation fails
        """
        if not articles:
            raise PromptGenerationError("No articles provided for prompt generation")

        start_time = time.time()

        log_api_call(
            self.logger,
            "Claude API",
            "generate_video_prompt",
            article_count=len(articles),
            target_duration=self.config.video_duration
        )

        try:
            # Format articles for prompt generation
            articles_text = self._format_articles(articles)

            # Create prompt generation request
            prompt = self._create_prompt_request(articles_text)

            # Call Claude API
            response = self.client.messages.create(
                model=self.config.claude_model,
                max_tokens=512,  # Video prompts should be concise
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            duration_ms = (time.time() - start_time) * 1000

            # Extract video prompt
            video_prompt = response.content[0].text.strip()

            log_api_response(
                self.logger,
                "Claude API",
                "generate_video_prompt",
                success=True,
                duration_ms=duration_ms,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                prompt_length=len(video_prompt)
            )

            self.logger.info(
                "video_prompt_generated",
                prompt_length=len(video_prompt),
                total_tokens=response.usage.input_tokens + response.usage.output_tokens
            )

            return video_prompt

        except anthropic.APIError as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "Claude API",
                "generate_video_prompt",
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            raise ClaudeAPIError(f"Claude API error during prompt generation: {str(e)}")

        except Exception as e:
            log_error(self.logger, e, "prompt_generator.generate_video_prompt")
            raise PromptGenerationError(f"Prompt generation failed: {str(e)}")

    def _format_articles(self, articles: List[NewsArticle]) -> str:
        """
        Format articles for prompt generation.

        Args:
            articles: List of NewsArticle instances

        Returns:
            Formatted articles text
        """
        formatted = []

        for i, article in enumerate(articles, 1):
            formatted.append(f"{i}. {article.title}")
            formatted.append(f"   {article.description}")
            formatted.append("")

        return "\n".join(formatted)

    def _create_prompt_request(self, articles_text: str) -> str:
        """
        Create the prompt for Claude to generate a video prompt.

        Args:
            articles_text: Formatted articles text

        Returns:
            Claude prompt for video prompt generation
        """
        return f"""You are an expert video content creator specializing in business and finance news.
Create a compelling visual video prompt for AI video generation based on these news articles.

News Articles:
{articles_text}

Create a {self.config.video_duration}-second video prompt that:
1. Tells a cohesive visual story about the top business news
2. Includes specific visual descriptions (settings, objects, people, actions)
3. Specifies professional, corporate visual style
4. Suggests appropriate camera angles and movements
5. Sets a professional, modern mood suitable for business news
6. Works well for AI video generation (be concrete and detailed)
7. Focuses on abstract business concepts visualized (charts, cityscapes, office scenes, technology, etc.)

Format: Provide a single, detailed paragraph describing the video. Be specific about visuals, style, and atmosphere.
Do not include any explanations or notes - just the video prompt itself."""

    def generate_video_prompt_for_segment(
        self,
        articles: List[NewsArticle],
        script_segment: str,
        segment_number: int,
        total_segments: int
    ) -> str:
        """
        Generate a visual video prompt for a specific script segment.

        Args:
            articles: List of NewsArticle instances
            script_segment: The script text for this segment
            segment_number: Which segment this is (1-indexed)
            total_segments: Total number of segments

        Returns:
            Video prompt string optimized for Kling API

        Raises:
            PromptGenerationError: If prompt generation fails
        """
        if not articles:
            raise PromptGenerationError("No articles provided for prompt generation")

        try:
            # Format articles for prompt generation
            articles_text = self._format_articles(articles)

            # Create segment-specific prompt
            prompt = self._create_segment_prompt_request(
                articles_text,
                script_segment,
                segment_number,
                total_segments
            )

            # Call Gemini API
            video_prompt = self.client.generate_text(
                prompt,
                f"generate_video_prompt_segment_{segment_number}"
            )

            return video_prompt

        except Exception as e:
            log_error(self.logger, e, "prompt_generator.generate_video_prompt_for_segment")
            raise PromptGenerationError(f"Segment prompt generation failed: {str(e)}")

    def _create_segment_prompt_request(
        self,
        articles_text: str,
        script_segment: str,
        segment_number: int,
        total_segments: int
    ) -> str:
        """
        Create the prompt for Claude to generate a segment-specific video prompt.

        Args:
            articles_text: Formatted articles text
            script_segment: The narration script for this segment
            segment_number: Which segment this is (1-indexed)
            total_segments: Total number of segments

        Returns:
            Claude prompt for video prompt generation
        """
        segment_context = ""
        if segment_number == 1:
            segment_context = "This is the OPENING segment - establish the professional business news setting."
        elif segment_number == total_segments:
            segment_context = "This is the CLOSING segment - wrap up the narrative with a strong conclusion."
        else:
            segment_context = f"This is segment {segment_number} of {total_segments} - continue the visual narrative."

        return f"""You are an expert video content creator for business news.
Create an 8-second visual video prompt that matches this narration segment.

News Articles Context:
{articles_text}

Narration Script for This Segment:
"{script_segment}"

{segment_context}

Create a video prompt that:
1. Visually represents the content being narrated in this specific segment
2. Uses professional business visuals (office environments, city skylines, charts, technology, professional meetings, etc.)
3. Matches the tone and content of the narration
4. Flows naturally as part {segment_number} of a {total_segments}-part story
5. Includes specific camera movements and visual details
6. Maintains a consistent professional, modern style
7. Is concrete and specific for AI video generation
8. **IMPORTANT**: Do NOT include any people speaking, narrators, announcers, or text-on-screen. Focus ONLY on visual scenes, objects, and environments related to the news content.

Format: Provide only a single detailed paragraph describing the video visuals. Be very specific.
Do not include explanations - just the video prompt itself."""
