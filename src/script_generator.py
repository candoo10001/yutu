"""
Script generation module using Claude API to create Korean narration scripts.
"""
import time
from typing import List, Optional, Dict, Any

import anthropic
import structlog

from .config import Config
from .news_fetcher import NewsArticle
from .utils.error_handler import ClaudeAPIError, ScriptGenerationError
from .utils.logger import log_api_call, log_api_response, log_error


class ScriptGenerator:
    """Generates Korean narration scripts from translated articles using Claude API."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Script Generator.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()
        self.client = anthropic.Anthropic(api_key=config.claude_api_key)

    def generate_korean_script(
        self,
        news_articles: List[NewsArticle],
        target_duration: Optional[int] = None,
        enriched_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a Korean narration script directly from English news articles with enriched context.

        Args:
            news_articles: List of NewsArticle instances (English)
            target_duration: Target duration in seconds (defaults to config.video_duration)
            enriched_context: Optional enriched context with background, insights, competitors, market_impact

        Returns:
            Korean narration script (string)

        Raises:
            ScriptGenerationError: If script generation fails
        """
        if not news_articles:
            raise ScriptGenerationError("No articles provided for script generation")

        # Use provided target_duration or default to config value
        duration = target_duration if target_duration is not None else self.config.video_duration

        start_time = time.time()

        log_api_call(
            self.logger,
            "Claude API",
            "generate_korean_script",
            article_count=len(news_articles),
            target_duration=duration
        )

        try:
            # Format articles for script generation
            articles_text = self._format_articles_for_script(news_articles)

            # Create script generation prompt with target duration and enriched context
            prompt = self._create_script_prompt(articles_text, duration, enriched_context)

            # Call Claude API with Haiku (cheaper model)
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Cheaper Haiku model
                max_tokens=1024,  # Scripts should be concise
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            duration_ms = (time.time() - start_time) * 1000

            # Extract script
            script = response.content[0].text.strip()

            log_api_response(
                self.logger,
                "Claude API",
                "generate_korean_script",
                success=True,
                duration_ms=duration_ms,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                script_length=len(script)
            )

            self.logger.info(
                "script_generated",
                script_length=len(script),
                word_count=len(script.split()),
                total_tokens=response.usage.input_tokens + response.usage.output_tokens
            )

            return script

        except anthropic.APIError as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "Claude API",
                "generate_korean_script",
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            raise ClaudeAPIError(f"Claude API error during script generation: {str(e)}")

        except Exception as e:
            log_error(self.logger, e, "script_generator.generate_korean_script")
            raise ScriptGenerationError(f"Script generation failed: {str(e)}")

    def _format_articles_for_script(self, articles: List[NewsArticle]) -> str:
        """
        Format English news articles into a structured text for Korean script generation.

        Args:
            articles: List of NewsArticle instances (English)

        Returns:
            Formatted articles text
        """
        formatted = []

        for i, article in enumerate(articles, 1):
            formatted.append(f"{i}. {article.title}")
            formatted.append(f"   {article.description}")
            formatted.append("")

        return "\n".join(formatted)

    def _create_script_prompt(
        self,
        articles_text: str,
        target_duration: int,
        enriched_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a script generation prompt for Claude with enriched context.

        Args:
            articles_text: Formatted Korean articles text
            target_duration: Target duration in seconds
            enriched_context: Optional enriched context with additional insights

        Returns:
            Script generation prompt
        """
        # Build additional context section if enriched_context is provided
        additional_context = ""
        if enriched_context:
            context_parts = []
            if enriched_context.get("background"):
                context_parts.append(f"**배경:** {enriched_context['background']}")
            if enriched_context.get("insights"):
                context_parts.append(f"**핵심 인사이트:** {enriched_context['insights']}")
            if enriched_context.get("competitors"):
                context_parts.append(f"**경쟁 상황:** {enriched_context['competitors']}")
            if enriched_context.get("market_impact"):
                context_parts.append(f"**시장 영향:** {enriched_context['market_impact']}")

            if context_parts:
                additional_context = "\n\n**추가 컨텍스트 (스크립트에 포함할 것):**\n" + "\n".join(context_parts)

        return f"""You are a professional news anchor. Create a natural Korean narration script for the following business/finance news article.

**CRITICAL RULES:**
1. Input is in English, output MUST be in natural, native Korean (not translated Korean)
2. NO opening greetings or introductions (NO "안녕하십니까", NO "오늘은", NO "말씀드리겠습니다")
3. Start IMMEDIATELY with the news content
4. Write as a native Korean speaker would speak, not as a translation

**News Article (English):**
{articles_text}
{additional_context}

**Script Requirements:**
- **Duration**: EXACTLY {target_duration} seconds
- **Word count**: {int(target_duration * 4.5)}-{int(target_duration * 5)} Korean words (based on Korean TTS speed)
- **Length is CRITICAL** - must match exactly

**Content Structure:**
1. **NO opening** - Start directly with the main news
2. **Natural Korean**: Write as a native Korean speaker, not a translator
   - Use natural Korean sentence structures
   - Use appropriate Korean business/financial terms
   - Numbers should be written naturally (e.g., "2026년" not "이천이십육년")
   - Dates: Use "이천이십육년" → "2026년"
3. **Content flow**:
   - Lead with the main news headline
   - Include enriched context naturally (background, insights, competition, market impact)
   - Focus ONLY on this single news topic - no other news or topics
4. **Tone**: Professional yet accessible, conversational
5. **MANDATORY closing**: End with exactly "지금까지 주식하는 두남자였습니다. 감사합니다"

**TTS 음성 합성을 위한 필수 규칙**:
7. 모든 숫자를 한글로 음성 그대로 작성하세요:
   - "1.5" → "일점오"
   - "2.5%" → "이점오 퍼센트"
   - "$100" → "백 달러"
   - "3분기" → "삼 분기"
   - "10억" → "십억"

8. 영어 약어와 회사명을 한글 발음으로 작성하세요:
   - "Tesla" → "테슬라"
   - "Nvidia" → "엔비디아"
   - "Apple" → "애플"
   - "QE" → "양적완화" (풀네임으로)
   - "Fed" → "연준" (한국어로)
   - "AI" → "에이아이" (발음대로)
   - "CEO" → "최고경영자" (풀네임으로)

9. 모든 단위를 한글로 작성하세요:
   - "%" → "퍼센트"
   - "$" → "달러"
   - "₩" → "원"

스크립트만 출력하세요. 다른 설명이나 주석은 포함하지 마세요."""
