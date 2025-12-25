"""
Context enrichment module using Gemini with Google Search to add deeper insights.
"""
import time
import json
from typing import Optional, Dict, Any

import requests
import structlog

from .config import Config
from .news_fetcher import NewsArticle
from .utils.error_handler import VideoGenerationError
from .utils.logger import log_api_call, log_api_response, log_error


class ContextEnricher:
    """Enriches news articles with deeper insights using Gemini with Google Search."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Context Enricher.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()
        self.api_key = config.google_api_key
        self.model = "gemini-2.0-flash-exp"  # Supports Google Search grounding
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def enrich_article_context(self, article: NewsArticle) -> Dict[str, Any]:
        """
        Enrich a news article with additional context, insights, and competitor information.

        Args:
            article: NewsArticle instance to enrich

        Returns:
            Dictionary containing enriched context with:
            - background: Background information on the topic
            - insights: Key insights and analysis
            - competitors: Competitor information (if applicable)
            - market_impact: Market implications

        Raises:
            VideoGenerationError: If enrichment fails
        """
        start_time = time.time()

        log_api_call(
            self.logger,
            "Gemini Context Enrichment",
            "enrich_article",
            article_title=article.title[:60]
        )

        try:
            # Create enrichment prompt
            prompt = self._create_enrichment_prompt(article)

            # Call Gemini with Google Search
            response_text = self._call_gemini_with_search(prompt)

            # Parse response
            enriched_context = self._parse_enrichment_response(response_text)

            duration_ms = (time.time() - start_time) * 1000

            log_api_response(
                self.logger,
                "Gemini Context Enrichment",
                "enrich_article",
                success=True,
                duration_ms=duration_ms,
                has_background=bool(enriched_context.get("background")),
                has_insights=bool(enriched_context.get("insights")),
                has_competitors=bool(enriched_context.get("competitors"))
            )

            self.logger.info(
                "context_enriched",
                article_title=article.title[:60],
                sections_added=len([k for k, v in enriched_context.items() if v])
            )

            return enriched_context

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "Gemini Context Enrichment",
                "enrich_article",
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            log_error(self.logger, e, "context_enricher.enrich_article_context")

            # Return minimal context on error
            self.logger.warning(
                "context_enrichment_failed_using_minimal",
                error=str(e),
                article_title=article.title[:60]
            )
            return {
                "background": "",
                "insights": "",
                "competitors": "",
                "market_impact": ""
            }

    def _create_enrichment_prompt(self, article: NewsArticle) -> str:
        """
        Create a prompt for Gemini to enrich article context.

        Args:
            article: NewsArticle instance

        Returns:
            Formatted prompt string
        """
        return f"""You are a business analyst researching this news topic:

**Title:** {article.title}
**Description:** {article.description}
**Source:** {article.source}

Please research and provide the following information in JSON format:

1. **background**: Brief background context (2-3 sentences) - What led to this news? Historical context?
2. **insights**: Key insights and analysis (2-3 sentences) - What does this mean? Why is it significant?
3. **competitors**: Competitor information if applicable (1-2 sentences) - How are competitors positioned? Any competitive dynamics?
4. **market_impact**: Market implications (1-2 sentences) - What's the potential impact on the market/industry?

IMPORTANT REQUIREMENTS:
- Use current, up-to-date information from today
- Be specific and factual
- Keep each section concise (1-3 sentences max)
- If a section is not applicable (e.g., no competitors for macro news), leave it as empty string ""
- Focus on business, finance, and technology aspects

Return ONLY a JSON object with this exact format:
{{
  "background": "Background context here...",
  "insights": "Key insights here...",
  "competitors": "Competitor info here or empty string if not applicable",
  "market_impact": "Market implications here..."
}}

CRITICAL: Return ONLY the JSON object, no markdown formatting, no extra text, no code blocks.
Start your response with {{ and end with }}"""

    def _call_gemini_with_search(self, prompt: str) -> str:
        """
        Call Gemini API with Google Search grounding enabled.

        Args:
            prompt: The prompt to send to Gemini

        Returns:
            Raw response text from Gemini

        Raises:
            VideoGenerationError: If API call fails
        """
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

        headers = {
            "Content-Type": "application/json"
        }

        # Enable Google Search grounding
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "tools": [{
                "googleSearch": {}  # Enable Google Search grounding
            }],
            "generationConfig": {
                "temperature": 0.4,  # Lower temperature for factual accuracy
                "maxOutputTokens": 2048,
                "responseModalities": ["TEXT"]
            }
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=90
            )

            if response.status_code != 200:
                error_msg = f"Gemini API error: {response.status_code} - {response.text}"
                self.logger.error("gemini_enrichment_error", status=response.status_code, error=response.text)
                raise VideoGenerationError(error_msg)

            data = response.json()

            # Extract text from response
            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text.strip()
            except (KeyError, IndexError) as e:
                self.logger.error("failed_to_parse_enrichment_response", error=str(e), response=data)
                raise VideoGenerationError(f"Failed to extract text from Gemini response: {str(e)}")

        except requests.RequestException as e:
            raise VideoGenerationError(f"Gemini API request failed: {str(e)}")

    def _parse_enrichment_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Gemini's enrichment response into structured data.

        Args:
            response_text: Raw response text from Gemini

        Returns:
            Dictionary with enriched context
        """
        try:
            # Clean up response - remove markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            # Parse JSON
            enriched_data = json.loads(response_text)

            # Validate and extract fields
            return {
                "background": enriched_data.get("background", "").strip(),
                "insights": enriched_data.get("insights", "").strip(),
                "competitors": enriched_data.get("competitors", "").strip(),
                "market_impact": enriched_data.get("market_impact", "").strip()
            }

        except json.JSONDecodeError as e:
            self.logger.error(
                "failed_to_parse_enrichment_json",
                error=str(e),
                response_preview=response_text[:500]
            )
            # Return empty context on parse error
            return {
                "background": "",
                "insights": "",
                "competitors": "",
                "market_impact": ""
            }
