"""
Gemini API client for text generation tasks.
"""
import time
from typing import Optional

import requests
import structlog

from .config import Config
from .utils.error_handler import VideoGenerationError
from .utils.logger import log_api_call, log_api_response, log_error


class GeminiClient:
    """Client for Google Gemini API."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Gemini Client.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()
        self.api_key = config.google_api_key
        self.model = "gemini-2.5-flash"  # Free/cheap model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def generate_text(self, prompt: str, operation: str = "generate_text") -> str:
        """
        Generate text using Gemini API.

        Args:
            prompt: Text prompt
            operation: Operation name for logging

        Returns:
            Generated text

        Raises:
            VideoGenerationError: If generation fails
        """
        start_time = time.time()

        log_api_call(
            self.logger,
            "Gemini API",
            operation,
            prompt_length=len(prompt)
        )

        try:
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

            headers = {
                "Content-Type": "application/json"
            }

            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2048
                }
            }

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=60
            )

            if response.status_code != 200:
                raise VideoGenerationError(
                    f"Gemini API error: {response.status_code} - {response.text}"
                )

            data = response.json()

            # Extract text from response
            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as e:
                raise VideoGenerationError(f"Failed to extract text from response: {str(e)}")

            duration_ms = (time.time() - start_time) * 1000

            log_api_response(
                self.logger,
                "Gemini API",
                operation,
                success=True,
                duration_ms=duration_ms,
                output_length=len(text)
            )

            return text.strip()

        except requests.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "Gemini API",
                operation,
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            log_error(self.logger, e, f"gemini_client.{operation}")
            raise VideoGenerationError(f"Gemini API request failed: {str(e)}")

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "Gemini API",
                operation,
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            log_error(self.logger, e, f"gemini_client.{operation}")
            raise VideoGenerationError(f"Text generation failed: {str(e)}")
