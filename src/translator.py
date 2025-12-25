"""
Translation module using Gemini API to translate news to Korean.
"""
import time
from dataclasses import dataclass
from typing import List, Optional

import structlog

from .config import Config
from .gemini_client import GeminiClient
from .news_fetcher import NewsArticle
from .utils.error_handler import TranslationError
from .utils.logger import log_error


@dataclass
class KoreanArticle:
    """Represents a Korean-translated news article."""
    title: str
    description: str
    original_title: str
    original_description: str
    source: str

    def __str__(self) -> str:
        return f"{self.title} - {self.source}"


class Translator:
    """Translates English news articles to Korean using Gemini API."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Translator.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()
        self.client = GeminiClient(config, logger)

    def translate_to_korean(self, articles: List[NewsArticle]) -> List[KoreanArticle]:
        """
        Translate English news articles to Korean.

        Args:
            articles: List of NewsArticle instances to translate

        Returns:
            List of KoreanArticle instances

        Raises:
            TranslationError: If translation fails
        """
        if not articles:
            self.logger.warning("no_articles_to_translate")
            return []

        try:
            # Prepare articles for translation
            articles_text = self._format_articles_for_translation(articles)

            # Create translation prompt
            prompt = self._create_translation_prompt(articles_text)

            # Call Gemini API
            translated_text = self.client.generate_text(prompt, "translate_to_korean")

            # Parse translated articles
            korean_articles = self._parse_translated_articles(
                translated_text,
                articles
            )

            self.logger.info(
                "translation_completed",
                article_count=len(korean_articles)
            )

            return korean_articles

        except Exception as e:
            log_error(self.logger, e, "translator.translate_to_korean")
            raise TranslationError(f"Translation failed: {str(e)}")

    def _format_articles_for_translation(self, articles: List[NewsArticle]) -> str:
        """
        Format articles into a structured text for translation.

        Args:
            articles: List of NewsArticle instances

        Returns:
            Formatted articles text
        """
        formatted = []

        for i, article in enumerate(articles, 1):
            formatted.append(f"Article {i}:")
            formatted.append(f"Title: {article.title}")
            formatted.append(f"Description: {article.description}")
            formatted.append("")

        return "\n".join(formatted)

    def _create_translation_prompt(self, articles_text: str) -> str:
        """
        Create a translation prompt for Claude.

        Args:
            articles_text: Formatted articles text

        Returns:
            Translation prompt
        """
        return f"""You are a professional translator specializing in business and finance news.
Translate the following English news articles into natural, fluent Korean.

Instructions:
1. Translate to natural Korean suitable for news narration
2. Preserve business/finance terminology appropriately (use Korean equivalents when common, otherwise use English terms in Korean pronunciation)
3. Maintain the professional tone suitable for business news
4. Keep the structure: For each article, provide "Title:" and "Description:"
5. Number each article (Article 1, Article 2, etc.)

Here are the articles to translate:

{articles_text}

Please provide the Korean translations maintaining the same structure."""

    def _parse_translated_articles(
        self,
        translated_text: str,
        original_articles: List[NewsArticle]
    ) -> List[KoreanArticle]:
        """
        Parse Claude's translated response into KoreanArticle instances.

        Args:
            translated_text: Claude's translation response
            original_articles: Original English articles

        Returns:
            List of KoreanArticle instances

        Raises:
            TranslationError: If parsing fails
        """
        korean_articles = []

        try:
            # Split by article markers (handle both English and Korean)
            if "Article " in translated_text:
                article_sections = translated_text.split("Article ")[1:]
            elif "기사 " in translated_text:
                article_sections = translated_text.split("기사 ")[1:]
            else:
                # Fallback: try to parse anyway
                article_sections = [translated_text]

            for i, section in enumerate(article_sections):
                if i >= len(original_articles):
                    break

                # Extract title and description
                lines = section.strip().split("\n")

                title = ""
                description = ""

                for line in lines:
                    line = line.strip()
                    # Check for title markers (English and Korean)
                    if any(line.startswith(marker) for marker in ["Title:", "제목:", "title:"]):
                        title = line.split(":", 1)[1].strip()
                    # Check for description markers (English and Korean)
                    elif any(line.startswith(marker) for marker in ["Description:", "설명:", "내용:", "description:"]):
                        description = line.split(":", 1)[1].strip()
                    elif title and not description and line:
                        # Sometimes description continues on next line
                        description += " " + line

                # Fallback if parsing failed
                if not title or not description:
                    self.logger.warning(
                        "translation_parsing_incomplete",
                        article_index=i,
                        section_preview=section[:100]
                    )
                    # Use original as fallback
                    title = original_articles[i].title
                    description = original_articles[i].description

                korean_article = KoreanArticle(
                    title=title,
                    description=description,
                    original_title=original_articles[i].title,
                    original_description=original_articles[i].description,
                    source=original_articles[i].source
                )

                korean_articles.append(korean_article)

            return korean_articles

        except Exception as e:
            log_error(self.logger, e, "translator._parse_translated_articles")
            raise TranslationError(f"Failed to parse translated articles: {str(e)}")
