"""
Custom exceptions and error handling for the video generation pipeline.
"""
from typing import Optional


class VideoGenerationError(Exception):
    """Base exception for video generation pipeline errors."""
    pass


class ConfigurationError(VideoGenerationError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, missing_key: Optional[str] = None):
        self.missing_key = missing_key
        super().__init__(message)


class NewsAPIError(VideoGenerationError):
    """Raised when News API operations fail."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


class ClaudeAPIError(VideoGenerationError):
    """Raised when Claude API operations fail."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


class KlingAPIError(VideoGenerationError):
    """Raised when Kling API operations fail."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        task_id: Optional[str] = None
    ):
        self.status_code = status_code
        self.task_id = task_id
        super().__init__(message)


class ElevenLabsAPIError(VideoGenerationError):
    """Raised when ElevenLabs API operations fail."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


class VideoCompositionError(VideoGenerationError):
    """Raised when video/audio composition fails."""

    def __init__(self, message: str, ffmpeg_output: Optional[str] = None):
        self.ffmpeg_output = ffmpeg_output
        super().__init__(message)


class TranslationError(VideoGenerationError):
    """Raised when translation operations fail."""
    pass


class ScriptGenerationError(VideoGenerationError):
    """Raised when script generation fails."""
    pass


class PromptGenerationError(VideoGenerationError):
    """Raised when prompt generation fails."""
    pass


def is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error is retryable.

    Args:
        error: The exception to check

    Returns:
        True if the error should be retried, False otherwise
    """
    # Rate limit errors (429) are retryable
    if hasattr(error, 'status_code'):
        if error.status_code in [429, 500, 502, 503, 504]:
            return True

    # Network errors are retryable
    if isinstance(error, (ConnectionError, TimeoutError)):
        return True

    # Configuration errors are NOT retryable
    if isinstance(error, ConfigurationError):
        return False

    # Most API errors are retryable
    if isinstance(error, (NewsAPIError, ClaudeAPIError, KlingAPIError, ElevenLabsAPIError)):
        return True

    # Default to non-retryable
    return False


def get_error_category(error: Exception) -> str:
    """
    Categorize an error for logging and reporting.

    Args:
        error: The exception to categorize

    Returns:
        Error category string
    """
    if isinstance(error, ConfigurationError):
        return "configuration"
    elif isinstance(error, NewsAPIError):
        return "news_api"
    elif isinstance(error, ClaudeAPIError):
        return "claude_api"
    elif isinstance(error, KlingAPIError):
        return "kling_api"
    elif isinstance(error, ElevenLabsAPIError):
        return "elevenlabs_api"
    elif isinstance(error, VideoCompositionError):
        return "video_composition"
    elif isinstance(error, TranslationError):
        return "translation"
    elif isinstance(error, ScriptGenerationError):
        return "script_generation"
    elif isinstance(error, PromptGenerationError):
        return "prompt_generation"
    else:
        return "unknown"
