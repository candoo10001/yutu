"""
Gemini-based script generator that produces Korean scripts directly.
"""
import time
import json
from typing import List, Optional, Dict, Any

import requests
import structlog

from .config import Config
from .news_fetcher import NewsArticle
from .utils.error_handler import VideoGenerationError
from .utils.logger import log_api_call, log_api_response, log_error


class GeminiScriptGenerator:
    """Generates Korean narration scripts directly using Gemini with Google Search."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Gemini Script Generator.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()
        self.api_key = config.google_api_key
        self.model = "gemini-2.0-flash-exp"  # Supports Google Search grounding
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def generate_korean_script(
        self,
        news_articles: List[NewsArticle],
        target_duration: Optional[int] = None
    ) -> str:
        """
        Generate a Korean narration script directly using Gemini with Google Search.

        This method researches the topic in Korean sources and generates a natural Korean script,
        rather than translating from English.

        Args:
            news_articles: List of NewsArticle instances (English)
            target_duration: Target duration in seconds (defaults to config.video_duration)

        Returns:
            Korean narration script (string)

        Raises:
            VideoGenerationError: If script generation fails
        """
        if not news_articles:
            raise VideoGenerationError("No articles provided for script generation")

        # Use provided target_duration or default to config value
        duration = target_duration if target_duration is not None else self.config.video_duration

        start_time = time.time()

        log_api_call(
            self.logger,
            "Gemini Script Generator",
            "generate_korean_script",
            article_count=len(news_articles),
            target_duration=duration
        )

        try:
            # Get the main article
            article = news_articles[0]

            # Create Korean script generation prompt
            prompt = self._create_korean_script_prompt(article, duration)

            # Call Gemini with Google Search
            response_text = self._call_gemini_with_search(prompt)

            # Clean up the script
            korean_script = self._clean_script(response_text)

            duration_ms = (time.time() - start_time) * 1000

            log_api_response(
                self.logger,
                "Gemini Script Generator",
                "generate_korean_script",
                success=True,
                duration_ms=duration_ms,
                script_length=len(korean_script)
            )

            self.logger.info(
                "korean_script_generated",
                script_length=len(korean_script),
                word_count=len(korean_script.split())
            )

            return korean_script

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "Gemini Script Generator",
                "generate_korean_script",
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            log_error(self.logger, e, "gemini_script_generator.generate_korean_script")
            raise VideoGenerationError(f"Failed to generate Korean script: {str(e)}")

    def _create_korean_script_prompt(self, article: NewsArticle, target_duration: int) -> str:
        """
        Create a prompt for Gemini to generate a Korean script directly.

        Args:
            article: NewsArticle instance
            target_duration: Target duration in seconds

        Returns:
            Formatted prompt string
        """
        # Calculate target word count for Korean (Korean TTS: ~4.5-5 words/second)
        target_words_min = int(target_duration * 4.5)
        target_words_max = int(target_duration * 5)

        return f"""당신은 한국의 전문 비즈니스 뉴스 앵커입니다. 다음 뉴스 주제에 대해 한국어로 자연스러운 뉴스 나레이션 스크립트를 작성하세요.

**뉴스 주제:**
제목: {article.title}
설명: {article.description}
출처: {article.source}

**중요: Google Search를 사용하여 이 주제에 대한 최신 한국어 정보를 검색하고, 다음 내용을 포함하세요:**
1. **배경 정보**: 이 뉴스가 나오게 된 배경과 맥락 (2-3문장)
2. **핵심 인사이트**: 이 뉴스의 중요성과 의미 (2-3문장)
3. **경쟁 상황**: 관련된 경쟁사나 업계 동향 (해당되는 경우, 1-2문장)
4. **시장 영향**: 시장이나 산업에 미치는 영향 (1-2문장)

**스크립트 작성 규칙:**

1. **길이**: 정확히 {target_duration}초 분량
   - 단어 수: {target_words_min}-{target_words_max} 단어
   - 이 길이는 매우 중요합니다!

2. **시작 방식** (매우 중요!):
   - ❌ 절대 금지: "알겠습니다", "다음은", "요청하신", "스크립트입니다" 같은 AI 응답
   - ❌ 인사말 금지: "안녕하십니까", "오늘은", "말씀드리겠습니다"
   - ✅ 뉴스 내용으로 바로 시작
   - 예: "테슬라 주가가 오늘 500달러를 돌파했습니다."

3. **내용 구성**:
   - 첫 문장: 메인 뉴스 헤드라인
   - 중간 부분: 배경, 인사이트, 경쟁 상황, 시장 영향을 자연스럽게 포함
   - 이 뉴스 주제 하나에만 집중 (다른 뉴스 언급 금지)

4. **언어 스타일**:
   - 자연스러운 한국어 (번역체 아님)
   - 한국 비즈니스 뉴스 용어 사용
   - 전문적이지만 이해하기 쉽게
   - 대화하듯 자연스럽게

5. **필수 종료 멘트**:
   - 마지막에 반드시 이렇게 끝내세요: "지금까지 주식하는 두남자였습니다. 감사합니다."

6. **TTS 음성 합성을 위한 필수 규칙**:
   - 모든 숫자를 한글로 음성 그대로 작성:
     * "1.5" → "일점오"
     * "2.5%" → "이점오 퍼센트"
     * "$100" → "백 달러"
     * "3분기" → "삼 분기"
     * "10억" → "십억"

   - 큰 숫자 처리 (매우 중요!):
     * ❌ 절대 사용 금지: 콤마 (,), 소수점 3자리 이상
     * "87,824.007813" → "약 팔만 팔천" (반올림, 간단하게)
     * "88,000 USDT" → "팔만 팔천 유에스디티"
     * "$1,234.56" → "천이백삼십사 달러"
     * 소수점은 최대 2자리까지만: "1.234" → "일점이삼"

   - 영어 약어와 회사명을 한글 발음으로:
     * "Tesla" → "테슬라"
     * "Nvidia" → "엔비디아"
     * "Apple" → "애플"
     * "QE" → "양적완화" (풀네임)
     * "Fed" → "연준" (한국어)
     * "AI" → "에이아이" (발음)
     * "CEO" → "최고경영자" (풀네임)

   - 모든 단위를 한글로:
     * "%" → "퍼센트"
     * "$" → "달러"
     * "₩" → "원"

**출력 형식:**
- ❌ 절대 금지: "알겠습니다", "다음은 스크립트입니다" 같은 AI 응답 문구
- ❌ 금지: 설명, 주석, 마크다운 포맷
- ✅ 뉴스 내용으로 바로 시작하는 순수 한국어 텍스트만 출력
- 예: "테슬라 주가가..." (O) / "알겠습니다. 다음은..." (X)

지금 Google Search로 이 주제를 한국어로 검색하여 최신 정보를 찾고, 뉴스 내용으로 바로 시작하는 자연스러운 한국어 뉴스 스크립트를 작성하세요."""

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
                "temperature": 0.7,  # Balanced for natural Korean
                "maxOutputTokens": 2048,
                "responseModalities": ["TEXT"]
            }
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=120
            )

            if response.status_code != 200:
                error_msg = f"Gemini API error: {response.status_code} - {response.text}"
                self.logger.error("gemini_script_error", status=response.status_code, error=response.text)
                raise VideoGenerationError(error_msg)

            data = response.json()

            # Extract text from response
            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text.strip()
            except (KeyError, IndexError) as e:
                self.logger.error("failed_to_parse_gemini_script", error=str(e), response=data)
                raise VideoGenerationError(f"Failed to extract text from Gemini response: {str(e)}")

        except requests.RequestException as e:
            raise VideoGenerationError(f"Gemini API request failed: {str(e)}")

    def _clean_script(self, script_text: str) -> str:
        """
        Clean up the script by removing any markdown formatting, AI preambles, or extra text.

        Args:
            script_text: Raw script text from Gemini

        Returns:
            Cleaned script text
        """
        # Remove markdown code blocks if present
        script_text = script_text.strip()
        if script_text.startswith("```"):
            # Remove first code block marker
            lines = script_text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            script_text = "\n".join(lines).strip()

        # Remove AI assistant preambles (common patterns)
        ai_preambles = [
            "알겠습니다.",
            "다음은",
            "요청하신",
            "스크립트입니다",
            "네,",
            "좋습니다.",
            "Here is",
            "Here's",
        ]

        lines = script_text.split("\n")
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            # Skip lines that are just AI preambles
            if any(line.startswith(preamble) for preamble in ai_preambles):
                continue
            # Skip empty lines at the beginning
            if not cleaned_lines and not line:
                continue
            cleaned_lines.append(line)

        script_text = "\n".join(cleaned_lines).strip()

        return script_text
