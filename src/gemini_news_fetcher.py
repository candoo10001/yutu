"""
Gemini-based news fetcher using Google Search grounding for real-time news.
"""
import time
import json
import re
from datetime import datetime, timezone
from typing import List, Optional

import requests
import structlog

from .config import Config
from .news_fetcher import NewsArticle
from .utils.error_handler import NewsAPIError
from .utils.logger import log_api_call, log_api_response, log_error


class GeminiNewsFetcher:
    """Fetches news articles using Gemini with Google Search grounding."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Gemini News Fetcher.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()
        self.api_key = config.google_api_key
        self.model = "gemini-2.0-flash-exp"  # Supports Google Search grounding
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def fetch_top_business_news(self, keyword: Optional[str] = None) -> List[NewsArticle]:
        """
        Fetch top business/finance/tech news articles using Gemini with Google Search.

        Args:
            keyword: Optional keyword to search for specific topics

        Returns:
            List of NewsArticle instances

        Raises:
            NewsAPIError: If the API request fails
        """
        start_time = time.time()

        # Determine search query based on keyword
        if keyword:
            search_query = f"latest {keyword} news today business technology finance"
        else:
            search_query = "latest business technology finance cryptocurrency news today"

        log_api_call(
            self.logger,
            "Gemini News API",
            "fetch_with_google_search",
            keyword=keyword,
            search_query=search_query,
            max_articles=self.config.max_news_articles
        )

        try:
            # Create prompt for Gemini to fetch and structure news
            prompt = self._create_news_fetch_prompt(keyword, self.config.max_news_articles)

            # Call Gemini with Google Search grounding
            articles_data = self._call_gemini_with_search(prompt)

            # Parse response into NewsArticle objects
            news_articles = self._parse_gemini_response(articles_data)

            duration_ms = (time.time() - start_time) * 1000

            log_api_response(
                self.logger,
                "Gemini News API",
                "fetch_with_google_search",
                success=True,
                duration_ms=duration_ms,
                articles_fetched=len(news_articles),
                keyword=keyword if keyword else None
            )

            if keyword:
                self.logger.info(
                    "news_fetched_by_keyword_gemini",
                    keyword=keyword,
                    count=len(news_articles),
                    sources=[article.source for article in news_articles]
                )
            else:
                self.logger.info(
                    "news_fetched_gemini",
                    count=len(news_articles),
                    sources=[article.source for article in news_articles]
                )

            return news_articles

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "Gemini News API",
                "fetch_with_google_search",
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            log_error(self.logger, e, "gemini_news_fetcher.fetch_top_business_news")
            raise NewsAPIError(f"Failed to fetch news via Gemini: {str(e)}")

    def _create_news_fetch_prompt(self, keyword: Optional[str], max_articles: int) -> str:
        """
        Create a prompt for Gemini to fetch and structure news articles.

        Args:
            keyword: Optional keyword for topic-specific search
            max_articles: Maximum number of articles to fetch

        Returns:
            Formatted prompt string
        """
        today = datetime.now().strftime("%Y-%m-%d")

        if keyword:
            topic_instruction = f"Search for the latest news about '{keyword}' in business, technology, or finance."
        else:
            topic_instruction = "Search for today's top business, technology, finance, or cryptocurrency news."

        return f"""You are a news researcher. {topic_instruction}

Today's date: {today}

IMPORTANT REQUIREMENTS:
1. Find ONLY articles published TODAY ({today}) or within the last 24 hours
2. Focus on business, technology, finance, cryptocurrency, or stock market news
3. Return EXACTLY {max_articles} articles
4. Each article must have: title, description (2-3 sentences), source name, published date, and URL
5. Prioritize major news outlets (Bloomberg, Reuters, CNBC, TechCrunch, CoinDesk, etc.)
6. Exclude: sports, entertainment, politics (unless related to business/finance)

Return the results as a JSON array with this EXACT format:
[
  {{
    "title": "Article title here",
    "description": "2-3 sentence summary of the article",
    "source": "Source name (e.g., Bloomberg, Reuters)",
    "published_at": "2025-12-26T10:30:00Z",
    "url": "https://example.com/article"
  }}
]

CRITICAL: Return ONLY the JSON array, no markdown formatting, no extra text, no code blocks.
Start your response with [ and end with ]"""

    def _call_gemini_with_search(self, prompt: str) -> str:
        """
        Call Gemini API with Google Search grounding enabled.

        Args:
            prompt: The prompt to send to Gemini

        Returns:
            Raw response text from Gemini

        Raises:
            NewsAPIError: If API call fails
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
                "temperature": 0.3,  # Lower temperature for more factual responses
                "maxOutputTokens": 4096,
                "responseModalities": ["TEXT"]
            }
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=90  # Longer timeout for search
            )

            if response.status_code != 200:
                error_msg = f"Gemini API error: {response.status_code} - {response.text}"
                self.logger.error("gemini_api_error", status=response.status_code, error=response.text)
                raise NewsAPIError(error_msg)

            data = response.json()

            # Extract text from response
            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text.strip()
            except (KeyError, IndexError) as e:
                self.logger.error("failed_to_parse_gemini_response", error=str(e), response=data)
                raise NewsAPIError(f"Failed to extract text from Gemini response: {str(e)}")

        except requests.RequestException as e:
            raise NewsAPIError(f"Gemini API request failed: {str(e)}")

    def _parse_gemini_response(self, response_text: str) -> List[NewsArticle]:
        """
        Parse Gemini's response into NewsArticle objects.

        Args:
            response_text: Raw response text from Gemini

        Returns:
            List of NewsArticle instances
        """
        articles = []

        try:
            # Clean up response - remove markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove trailing ```
            response_text = response_text.strip()

            # Parse JSON
            articles_data = json.loads(response_text)

            if not isinstance(articles_data, list):
                self.logger.warning("gemini_response_not_array", type=type(articles_data))
                return []

            for article_dict in articles_data:
                try:
                    # Parse published date
                    published_at_str = article_dict.get("published_at", "")
                    if published_at_str:
                        # Try multiple date formats
                        try:
                            published_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
                        except ValueError:
                            # Fallback to now if parsing fails
                            published_at = datetime.now(timezone.utc)
                    else:
                        published_at = datetime.now(timezone.utc)

                    # Create NewsArticle instance
                    article = NewsArticle(
                        title=article_dict.get("title", ""),
                        description=article_dict.get("description", ""),
                        url=article_dict.get("url", "https://news.google.com"),
                        published_at=published_at,
                        source=article_dict.get("source", "Google News"),
                        author=article_dict.get("author"),
                        content=article_dict.get("description", "")  # Use description as content
                    )

                    # Validate article has minimum required fields
                    if article.title and article.description and len(article.description) > 30:
                        articles.append(article)
                    else:
                        self.logger.warning(
                            "skipped_incomplete_article",
                            title=article.title[:50] if article.title else "N/A",
                            has_description=bool(article.description),
                            desc_length=len(article.description) if article.description else 0
                        )

                except Exception as e:
                    self.logger.warning(
                        "failed_to_parse_article_from_gemini",
                        error=str(e),
                        article_data=article_dict
                    )
                    continue

        except json.JSONDecodeError as e:
            self.logger.error(
                "failed_to_parse_json_response",
                error=str(e),
                response_preview=response_text[:500]
            )
            # Try to extract any JSON array from the text
            articles = self._fallback_json_extraction(response_text)

        return articles

    def _fallback_json_extraction(self, text: str) -> List[NewsArticle]:
        """
        Fallback method to extract JSON from text if direct parsing fails.

        Args:
            text: Raw response text

        Returns:
            List of NewsArticle instances
        """
        articles = []

        try:
            # Try to find JSON array in the text using regex
            json_match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                articles_data = json.loads(json_text)

                for article_dict in articles_data:
                    try:
                        article = NewsArticle(
                            title=article_dict.get("title", ""),
                            description=article_dict.get("description", ""),
                            url=article_dict.get("url", "https://news.google.com"),
                            published_at=datetime.now(timezone.utc),
                            source=article_dict.get("source", "Google News"),
                            author=article_dict.get("author"),
                            content=article_dict.get("description", "")
                        )

                        if article.title and article.description:
                            articles.append(article)

                    except Exception:
                        continue

        except Exception as e:
            self.logger.error("fallback_extraction_failed", error=str(e))

        return articles
