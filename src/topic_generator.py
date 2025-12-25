"""
Topic generation using Gemini AI to discover hottest finance/business topics.
"""
import time
from datetime import datetime
from typing import List, Optional

import google.generativeai as genai
import structlog

from .config import Config
from .news_fetcher import NewsArticle
from .utils.error_handler import VideoGenerationError
from .utils.logger import log_api_call, log_api_response, log_error


class TopicGenerator:
    """Generates content about hottest finance/business topics using Gemini AI."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Topic Generator.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()

        # Configure Gemini
        genai.configure(api_key=config.google_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def generate_hottest_topic(self, keyword: Optional[str] = None) -> List[NewsArticle]:
        """
        Generate content about the hottest finance/business topics using Gemini.

        Args:
            keyword: Optional custom keyword for topic search (e.g., "Tesla", "금리인상", "암호화폐")

        Returns:
            List containing a single NewsArticle with the hottest topic

        Raises:
            VideoGenerationError: If the API request fails
        """
        start_time = time.time()

        log_api_call(
            self.logger,
            "Gemini API",
            "generate_hottest_topic",
            prompt_type="custom_keyword_search" if keyword else "topic_discovery",
            keyword=keyword if keyword else None
        )

        try:
            # Create prompt for Gemini based on whether keyword is provided
            if keyword:
                prompt = f"""You are a financial news analyst creating content for Korean investors and business enthusiasts.

**CRITICAL**: You MUST provide information about "{keyword}" from December 2024 or the most recent available news. Do NOT use outdated information from months ago.

Search for the LATEST and MOST CURRENT business and finance news about "{keyword}" happening RIGHT NOW (December 2024).

Your task:
1. Find the MOST RECENT developments, market movements, or newsworthy events related to "{keyword}" from the past few days or weeks
2. If you don't have real-time data, provide analysis based on general market trends and known information about "{keyword}" as of late 2024
3. Include specific numbers, percentages, dates from RECENT timeframe (December 2024 or latest available)
4. Focus on aspects that matter to Korean investors and business professionals TODAY
5. Explain why this matters to Korean investors and the Korean market RIGHT NOW

Your response must be in this EXACT JSON format:
{{
    "title": "One concise headline (60 chars max) about {keyword} - make it engaging and newsworthy based on RECENT events",
    "description": "A compelling 2-3 sentence description (150-200 chars) that captures the LATEST development or key aspect of {keyword} in December 2024. Include specific numbers and recent details.",
    "insights": "3-4 sentences (250-300 chars) providing quick insights about why this {keyword} news matters to Korean investors RIGHT NOW, current market implications, and impact on Korean companies or economy."
}}

IMPORTANT:
- **CRITICAL**: Focus on December 2024 or the most recent available information - NO OLD NEWS from June or earlier months
- Use phrases like "recently", "this week", "this month", "as of December 2024", "latest developments"
- Include specific recent numbers, percentages, stock prices from the current timeframe
- Explain relevance to Korean market TODAY (Samsung, SK Hynix, Korean economy, etc.)
- Make it engaging for YouTube Shorts video audience interested in CURRENT events
- If {keyword} relates to a company, discuss RECENT stock performance, new products, or current market position
- If {keyword} relates to economic policy, discuss CURRENT impact on Korean investors
- Avoid using specific dates from the past unless truly relevant to current situation
"""
            else:
                prompt = """You are a financial news analyst creating content for Korean investors and business enthusiasts.

**CRITICAL**: You MUST provide information from December 2024 or the most recent available news. Do NOT use outdated information from months ago.

Generate content about one of these HIGH-INTEREST topics for Koreans based on RECENT developments (December 2024):
- Tesla (테슬라) - latest stock movements, new products, recent announcements
- Nvidia (엔비디아) - current chip business, AI developments, recent stock performance
- Apple (애플) - latest product launches, current stock movements
- US Federal Reserve - recent monetary policy decisions, current interest rates
- Samsung (삼성) - latest developments vs global competitors
- Major US tech stocks (FAANG) - current trends
- Cryptocurrency markets - recent movements
- US-China trade relations - latest impact
- Global inflation and recession - current concerns

Choose the MOST interesting and timely topic happening RIGHT NOW (December 2024).

Your response must be in this EXACT JSON format:
{
    "title": "One concise headline (60 chars max) about the hottest CURRENT topic",
    "description": "A compelling 2-3 sentence description (150-200 chars) that captures the LATEST essence and impact of this topic as of December 2024. Make it engaging and informative for Korean investors.",
    "insights": "3-4 sentences (250-300 chars) providing quick insights about why this topic matters to Korean investors RIGHT NOW, what's currently driving it, and recent implications."
}

IMPORTANT:
- Include specific numbers, percentages, and company names from RECENT timeframe (December 2024)
- Use phrases like "recently", "this month", "as of December 2024", "latest developments"
- Make it engaging for a YouTube Shorts video audience interested in CURRENT global business and investing
- NO OLD NEWS from June or earlier months
"""

            # Call Gemini API
            response = self.model.generate_content(prompt)

            if not response or not response.text:
                raise VideoGenerationError("Gemini returned empty response")

            duration_ms = (time.time() - start_time) * 1000

            # Parse the JSON response
            import json
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            topic_data = json.loads(response_text)

            # Create NewsArticle from generated topic
            article = NewsArticle(
                title=topic_data["title"],
                description=topic_data["description"] + " " + topic_data["insights"],
                url="https://generated-content.ai",
                published_at=datetime.now(),
                source="Gemini AI Market Analysis",
                author="AI Financial Analyst",
                content=topic_data["insights"]
            )

            log_api_response(
                self.logger,
                "Gemini API",
                "generate_hottest_topic",
                success=True,
                duration_ms=duration_ms,
                topic_title=article.title,
                keyword=keyword if keyword else None
            )

            if keyword:
                self.logger.info(
                    "topic_generated_from_keyword",
                    keyword=keyword,
                    title=article.title,
                    description_length=len(article.description)
                )
            else:
                self.logger.info(
                    "topic_generated",
                    title=article.title,
                    description_length=len(article.description)
                )

            return [article]

        except json.JSONDecodeError as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "Gemini API",
                "generate_hottest_topic",
                success=False,
                duration_ms=duration_ms,
                error=f"JSON parsing error: {str(e)}"
            )
            self.logger.error(
                "gemini_response_parse_error",
                error=str(e),
                response_text=response_text if 'response_text' in locals() else "No response"
            )
            raise VideoGenerationError(f"Failed to parse Gemini response: {str(e)}")

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "Gemini API",
                "generate_hottest_topic",
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            log_error(self.logger, e, "topic_generator.generate_hottest_topic")
            raise VideoGenerationError(f"Failed to generate topic: {str(e)}")
