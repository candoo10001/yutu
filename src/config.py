"""
Configuration management for the video generation pipeline.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .utils.error_handler import ConfigurationError


# Load environment variables from .env file
# In GitHub Actions, .env.example is copied to .env before running
load_dotenv()


@dataclass
class Config:
    """Configuration settings for the video generation pipeline."""

    # API Keys (required)
    claude_api_key: str
    google_api_key: str
    elevenlabs_api_key: str

    # API Keys (optional - not used with Gemini news fetcher)
    news_api_key: Optional[str] = None
    
    # API Keys (optional)
    kling_access_key: Optional[str] = None
    kling_secret_key: Optional[str] = None

    # News API Settings
    news_category: str = "business"
    news_country: str = "us"
    max_news_articles: int = 5

    # Claude API Settings
    claude_model: str = "claude-3-5-sonnet-20241022"
    claude_max_tokens: int = 2048
    claude_temperature: float = 0.7

    # Video Settings
    video_duration: int = 60  # Target duration for final video (1 minute with enriched insights)
    segment_duration: int = 4  # Duration for each image segment (3-5 seconds)
    video_aspect_ratio: str = "9:16"  # Portrait for YouTube Shorts
    video_resolution: str = "1080p"

    # Subtitle Settings
    enable_subtitles: bool = True
    subtitle_font_size: int = 130  # Optimal font size for mobile readability (between 120-140px)
    subtitle_font_color: str = "white"
    subtitle_background_color: str = "black@0.6"  # Semi-transparent black
    subtitle_position: str = "bottom"  # Options: top, center, bottom

    # Background Music
    enable_background_music: bool = True
    background_music_volume: float = 0.06  # Volume level (0.0-1.0) - 6% to not overpower voice

    # Audio Settings (ElevenLabs)
    elevenlabs_voice_id: Optional[str] = None
    elevenlabs_model: str = "eleven_multilingual_v2"
    audio_stability: float = 0.5
    audio_similarity: float = 0.75
    audio_style: float = 0.5

    # Application Settings
    log_level: str = "INFO"
    output_dir: str = "output"
    log_dir: str = "logs"
    retry_attempts: int = 3
    retry_delay: float = 2.0

    @classmethod
    def from_env(cls) -> "Config":
        """
        Create a Config instance from environment variables.

        Returns:
            Config instance

        Raises:
            ConfigurationError: If required environment variables are missing
        """
        # Required API keys (using Gemini for news, no News API needed)
        required_keys = {
            "CLAUDE_API_KEY": "claude_api_key",
            "GOOGLE_API_KEY": "google_api_key",
            "ELEVENLABS_API_KEY": "elevenlabs_api_key",
        }

        config_dict = {}

        # Check and load required keys
        for env_key, config_key in required_keys.items():
            value = os.getenv(env_key)
            if not value:
                raise ConfigurationError(
                    f"Missing required environment variable: {env_key}",
                    missing_key=env_key
                )
            config_dict[config_key] = value

        # Optional keys (legacy News API support)
        config_dict["news_api_key"] = os.getenv("NEWS_API_KEY")

        # Optional Kling keys (for legacy support, but no longer required)
        config_dict["kling_access_key"] = os.getenv("KLING_ACCESS_KEY")
        config_dict["kling_secret_key"] = os.getenv("KLING_SECRET_KEY")

        # Optional settings with defaults
        config_dict.update({
            "news_category": os.getenv("NEWS_CATEGORY", "business"),
            "news_country": os.getenv("NEWS_COUNTRY", "us"),
            "max_news_articles": int(os.getenv("MAX_NEWS_ARTICLES", "5")),
            "claude_model": os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
            "claude_max_tokens": int(os.getenv("CLAUDE_MAX_TOKENS", "2048")),
            "claude_temperature": float(os.getenv("CLAUDE_TEMPERATURE", "0.7")),
            "video_duration": int(os.getenv("VIDEO_DURATION", "30")),
            "segment_duration": int(os.getenv("SEGMENT_DURATION", "4")),
            "video_aspect_ratio": os.getenv("VIDEO_ASPECT_RATIO", "9:16"),
            "video_resolution": os.getenv("VIDEO_RESOLUTION", "1080p"),
            "enable_subtitles": os.getenv("ENABLE_SUBTITLES", "true").lower() == "true",
            "subtitle_font_size": int(os.getenv("SUBTITLE_FONT_SIZE", "130")),
            "subtitle_font_color": os.getenv("SUBTITLE_FONT_COLOR", "white"),
            "subtitle_background_color": os.getenv("SUBTITLE_BACKGROUND_COLOR", "black@0.6"),
            "subtitle_position": os.getenv("SUBTITLE_POSITION", "bottom"),
            "enable_background_music": os.getenv("ENABLE_BACKGROUND_MUSIC", "true").lower() == "true",
            "background_music_volume": float(os.getenv("BACKGROUND_MUSIC_VOLUME", "0.2")),
            "elevenlabs_voice_id": os.getenv("ELEVENLABS_VOICE_ID"),
            "elevenlabs_model": os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2"),
            "audio_stability": float(os.getenv("AUDIO_STABILITY", "0.5")),
            "audio_similarity": float(os.getenv("AUDIO_SIMILARITY", "0.75")),
            "audio_style": float(os.getenv("AUDIO_STYLE", "0.5")),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "output_dir": os.getenv("OUTPUT_DIR", "output"),
            "log_dir": os.getenv("LOG_DIR", "logs"),
            "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", "3")),
            "retry_delay": float(os.getenv("RETRY_DELAY", "2.0")),
        })

        return cls(**config_dict)

    def validate(self):
        """
        Validate configuration settings.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Validate news category
        valid_categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]
        if self.news_category not in valid_categories:
            raise ConfigurationError(
                f"Invalid news category: {self.news_category}. "
                f"Must be one of: {', '.join(valid_categories)}"
            )

        # Validate max news articles
        if self.max_news_articles < 1 or self.max_news_articles > 100:
            raise ConfigurationError("max_news_articles must be between 1 and 100")

        # Validate temperature
        if not 0 <= self.claude_temperature <= 1:
            raise ConfigurationError("claude_temperature must be between 0 and 1")

        # Validate audio settings
        if not 0 <= self.audio_stability <= 1:
            raise ConfigurationError("audio_stability must be between 0 and 1")
        if not 0 <= self.audio_similarity <= 1:
            raise ConfigurationError("audio_similarity must be between 0 and 1")
        if not 0 <= self.audio_style <= 1:
            raise ConfigurationError("audio_style must be between 0 and 1")

        # Create output directories if they don't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)

    def __repr__(self) -> str:
        """Return a safe string representation (without API keys)."""
        return (
            f"Config("
            f"news_category={self.news_category}, "
            f"news_country={self.news_country}, "
            f"max_news_articles={self.max_news_articles}, "
            f"claude_model={self.claude_model}, "
            f"video_duration={self.video_duration}, "
            f"log_level={self.log_level}"
            f")"
        )
