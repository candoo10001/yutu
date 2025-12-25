"""
Script generation module using Claude API to create Korean narration scripts.
"""
import time
from typing import List, Optional

import anthropic
import structlog

from .config import Config
from .translator import KoreanArticle
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

    def generate_korean_script(self, korean_articles: List[KoreanArticle], target_duration: Optional[int] = None) -> str:
        """
        Generate a Korean narration script from translated articles.

        Args:
            korean_articles: List of KoreanArticle instances
            target_duration: Target duration in seconds (defaults to config.video_duration)

        Returns:
            Korean narration script (string)

        Raises:
            ScriptGenerationError: If script generation fails
        """
        if not korean_articles:
            raise ScriptGenerationError("No articles provided for script generation")

        # Use provided target_duration or default to config value
        duration = target_duration if target_duration is not None else self.config.video_duration

        start_time = time.time()

        log_api_call(
            self.logger,
            "Claude API",
            "generate_korean_script",
            article_count=len(korean_articles),
            target_duration=duration
        )

        try:
            # Format articles for script generation
            articles_text = self._format_articles_for_script(korean_articles)

            # Create script generation prompt with target duration
            prompt = self._create_script_prompt(articles_text, duration)

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

    def _format_articles_for_script(self, articles: List[KoreanArticle]) -> str:
        """
        Format Korean articles into a structured text for script generation.

        Args:
            articles: List of KoreanArticle instances

        Returns:
            Formatted articles text
        """
        formatted = []

        for i, article in enumerate(articles, 1):
            formatted.append(f"{i}. {article.title}")
            formatted.append(f"   {article.description}")
            formatted.append("")

        return "\n".join(formatted)

    def _create_script_prompt(self, articles_text: str, target_duration: int) -> str:
        """
        Create a script generation prompt for Claude.

        Args:
            articles_text: Formatted Korean articles text
            target_duration: Target duration in seconds

        Returns:
            Script generation prompt
        """
        return f"""당신은 전문 뉴스 앵커입니다. 다음 비즈니스/금융 뉴스 기사에 대해서만 정확히 {target_duration}초 분량의 자연스러운 한국어 나레이션 스크립트를 작성해주세요.

**중요: 이 뉴스 기사 하나에만 집중하세요. 다른 뉴스나 다른 주제를 언급하지 마세요.**

뉴스 기사:
{articles_text}

중요: 스크립트는 반드시 {target_duration}초 분량이어야 합니다.
- 목표 단어 수: {int(target_duration * 4.5)}-{int(target_duration * 5)} 단어 (한국어 TTS 기준)
- 이 길이를 정확히 맞추는 것이 매우 중요합니다

스크립트 작성 지침:
1. **필수**: 정확히 {target_duration}초 분량 ({int(target_duration * 4.5)}-{int(target_duration * 5)} 단어)
2. **오프닝**: "안녕하세요, 오늘의 진스 뉴스 소식입니다" 같은 짧은 인사로 시작하세요
3. 뉴스 앵커가 읽기에 자연스러운 구어체로 작성하세요
4. **가장 중요**: 제공된 뉴스 기사 하나에만 집중하세요
   - 기사 제목에 나온 주제/기업 하나에만 집중
   - 다른 뉴스, 다른 기업, 다른 주제를 절대 언급하지 마세요
   - 기사 제목에 없는 주제나 내용을 추가하지 마세요
   - 예시: 제목이 "Tesla 주가 상승"이면 Tesla에만 집중. Apple, Nvidia 등 다른 기업은 언급 금지
5. 기사 제목과 설명에 나온 내용만 포함하세요
6. 전문적이면서도 접근하기 쉬운 톤을 유지하세요
7. **클로징**: "지금까지 오늘의 진스 뉴스였습니다. 감사합니다" 같은 짧은 마무리 멘트로 끝내세요

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
