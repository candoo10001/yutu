"""
News API integration for fetching business/finance news.
"""
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import structlog
from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException

from .config import Config
from .utils.error_handler import NewsAPIError
from .utils.logger import log_api_call, log_api_response, log_error


@dataclass
class NewsArticle:
    """Represents a news article."""
    title: str
    description: str
    url: str
    published_at: datetime
    source: str
    author: Optional[str] = None
    content: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.title} - {self.source}"


class NewsFetcher:
    """Fetches news articles from News API."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the News Fetcher.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()
        self.client = NewsApiClient(api_key=config.news_api_key)

    def fetch_top_business_news(self, keyword: Optional[str] = None) -> List[NewsArticle]:
        """
        Fetch top business/finance news articles.

        Args:
            keyword: Optional keyword to search for specific topics

        Returns:
            List of NewsArticle instances

        Raises:
            NewsAPIError: If the API request fails
        """
        start_time = time.time()

        if keyword:
            log_api_call(
                self.logger,
                "News API",
                "search_everything",
                keyword=keyword,
                max_articles=self.config.max_news_articles
            )
        else:
            log_api_call(
                self.logger,
                "News API",
                "fetch_top_headlines",
                category=self.config.news_category,
                country=self.config.news_country,
                max_articles=self.config.max_news_articles
            )

        try:
            # If keyword is provided, use everything endpoint with business/finance focus
            if keyword:
                # Search for the keyword - we'll filter for business relevance in _filter_articles
                # News API's q parameter does simple keyword matching
                response = self.client.get_everything(
                    q=keyword,
                    language='en',
                    sort_by='relevancy',  # Sort by relevance instead of date for better keyword matches
                    page_size=min(self.config.max_news_articles * 4, 100)  # Fetch more for better filtering
                )
            else:
                # Fetch top headlines
                response = self.client.get_top_headlines(
                    category=self.config.news_category,
                    country=self.config.news_country,
                    page_size=min(self.config.max_news_articles * 2, 100)  # Fetch extra for filtering
                )

            duration_ms = (time.time() - start_time) * 1000

            operation = "search_everything" if keyword else "fetch_top_headlines"

            if response.get("status") != "ok":
                error_message = response.get("message", "Unknown error")
                log_api_response(
                    self.logger,
                    "News API",
                    operation,
                    success=False,
                    duration_ms=duration_ms,
                    error=error_message
                )
                raise NewsAPIError(f"News API error: {error_message}")

            articles = response.get("articles", [])

            # Convert to NewsArticle instances
            news_articles = self._parse_articles(articles)

            # Filter and rank articles
            news_articles = self._filter_articles(news_articles, keyword=keyword)
            news_articles = self._rank_articles(news_articles, keyword=keyword)

            # Limit to max_news_articles
            news_articles = news_articles[:self.config.max_news_articles]

            log_api_response(
                self.logger,
                "News API",
                operation,
                success=True,
                duration_ms=duration_ms,
                articles_fetched=len(news_articles),
                keyword=keyword if keyword else None
            )

            if keyword:
                self.logger.info(
                    "news_fetched_by_keyword",
                    keyword=keyword,
                    count=len(news_articles),
                    sources=[article.source for article in news_articles]
                )
            else:
                self.logger.info(
                    "news_fetched",
                    count=len(news_articles),
                    sources=[article.source for article in news_articles]
                )

            return news_articles

        except NewsAPIException as e:
            duration_ms = (time.time() - start_time) * 1000
            operation = "search_everything" if keyword else "fetch_top_headlines"
            log_api_response(
                self.logger,
                "News API",
                operation,
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            raise NewsAPIError(f"Failed to fetch news: {str(e)}")

        except Exception as e:
            log_error(self.logger, e, "news_fetcher.fetch_top_business_news")
            raise NewsAPIError(f"Unexpected error fetching news: {str(e)}")

    def _parse_articles(self, raw_articles: List[dict]) -> List[NewsArticle]:
        """
        Parse raw API response into NewsArticle instances.

        Args:
            raw_articles: List of article dicts from API

        Returns:
            List of NewsArticle instances
        """
        articles = []

        for article in raw_articles:
            try:
                # Parse published date
                published_at_str = article.get("publishedAt")
                if published_at_str:
                    published_at = datetime.fromisoformat(
                        published_at_str.replace("Z", "+00:00")
                    )
                else:
                    published_at = datetime.now()

                # Create NewsArticle instance
                news_article = NewsArticle(
                    title=article.get("title", ""),
                    description=article.get("description", ""),
                    url=article.get("url", ""),
                    published_at=published_at,
                    source=article.get("source", {}).get("name", "Unknown"),
                    author=article.get("author"),
                    content=article.get("content")
                )

                articles.append(news_article)

            except Exception as e:
                self.logger.warning(
                    "failed_to_parse_article",
                    error=str(e),
                    article_title=article.get("title", "Unknown")
                )
                continue

        return articles

    def _filter_articles(self, articles: List[NewsArticle], keyword: Optional[str] = None) -> List[NewsArticle]:
        """
        Filter out low-quality articles and ensure keyword relevance.

        Args:
            articles: List of NewsArticle instances
            keyword: Optional keyword to filter for relevance

        Returns:
            Filtered list of NewsArticle instances
        """
        filtered = []

        for article in articles:
            # Filter out articles with missing title or description
            if not article.title or not article.description:
                continue

            # Filter out very short descriptions
            if len(article.description) < 50:
                continue

            # Filter out [Removed] content (common in News API)
            if "[Removed]" in article.description or "[Removed]" in article.title:
                continue

            # If keyword is provided, ensure the article is relevant to the keyword
            if keyword:
                keyword_lower = keyword.lower()
                title_lower = article.title.lower()
                desc_lower = article.description.lower()
                
                # Check if keyword appears in title or description
                if keyword_lower not in title_lower and keyword_lower not in desc_lower:
                    # Also check for common variations (e.g., "Samsung" matches "Samsung's", "Samsung.")
                    # Split keyword if it's a phrase and check if key parts appear
                    keyword_parts = keyword_lower.split()
                    if len(keyword_parts) > 1:
                        # For multi-word keywords, at least the main word should appear
                        main_word = keyword_parts[0]  # Usually the company/product name
                        if main_word not in title_lower and main_word not in desc_lower:
                            self.logger.debug(
                                "filtered_irrelevant_article",
                                keyword=keyword,
                                title=article.title[:50]
                            )
                            continue
                    else:
                        # Single word keyword must appear
                        self.logger.debug(
                            "filtered_irrelevant_article",
                            keyword=keyword,
                            title=article.title[:50]
                        )
                        continue

                # Additional business/finance relevance check for keyword searches
                business_terms = [
                    "business", "finance", "financial", "stock", "market", "company", "earnings",
                    "revenue", "profit", "investment", "trading", "share", "shares", "sales",
                    "quarter", "quarterly", "annual", "growth", "decline", "rise", "fall",
                    "CEO", "executive", "corporate", "IPO", "acquisition", "merger"
                ]
                text_to_check = (title_lower + " " + desc_lower).lower()
                has_business_term = any(term in text_to_check for term in business_terms)
                
                if not has_business_term:
                    self.logger.debug(
                        "filtered_non_business_article",
                        keyword=keyword,
                        title=article.title[:50]
                    )
                continue

            filtered.append(article)

        return filtered

    def _rank_articles(self, articles: List[NewsArticle], keyword: Optional[str] = None) -> List[NewsArticle]:
        """
        Rank articles by relevance and recency.
        Prioritizes articles with keyword in title, then by recency.

        Args:
            articles: List of NewsArticle instances
            keyword: Optional keyword to rank by relevance

        Returns:
            Sorted list of NewsArticle instances
        """
        def ranking_key(article: NewsArticle) -> tuple:
            """
            Returns a tuple for sorting: (has_keyword_in_title, published_at)
            Articles with keyword in title come first, then sorted by date.
            """
            score = 0
            if keyword:
                keyword_lower = keyword.lower()
                title_lower = article.title.lower()
                
                # Prioritize articles with keyword in title
                if keyword_lower in title_lower:
                    score = 1  # Higher score = appears first (we reverse later)
            
            # Use negative timestamp so newer articles (larger timestamp) come first
            return (score, article.published_at.timestamp())
        
        # Sort: keyword in title first, then by most recent
        return sorted(articles, key=ranking_key, reverse=True)
