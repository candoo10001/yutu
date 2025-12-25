"""
Audio generation module using ElevenLabs API for Korean TTS.
"""
import time
from pathlib import Path
from typing import Optional, Tuple

import structlog
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

from .config import Config
from .utils.error_handler import ElevenLabsAPIError
from .utils.logger import log_api_call, log_api_response, log_error


class AudioGenerator:
    """Generates Korean audio narration using ElevenLabs TTS."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Audio Generator.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()
        self.client = ElevenLabs(api_key=config.elevenlabs_api_key)

    def generate_korean_audio(
        self,
        korean_script: str,
        output_dir: str = "output"
    ) -> Tuple[str, float]:
        """
        Generate Korean audio narration from a script.

        Args:
            korean_script: Korean narration script
            output_dir: Directory to save the generated audio

        Returns:
            Tuple of (audio file path, duration in seconds)

        Raises:
            ElevenLabsAPIError: If audio generation fails
        """
        start_time = time.time()

        log_api_call(
            self.logger,
            "ElevenLabs API",
            "generate_audio",
            script_length=len(korean_script),
            language="Korean"
        )

        try:
            # Get or select Korean voice
            voice_id = self._get_korean_voice_id()

            # Configure voice settings
            voice_settings = VoiceSettings(
                stability=self.config.audio_stability,
                similarity_boost=self.config.audio_similarity,
                style=self.config.audio_style,
                use_speaker_boost=True
            )

            # Generate audio
            self.logger.info(
                "generating_audio",
                voice_id=voice_id,
                model=self.config.elevenlabs_model
            )

            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                model_id=self.config.elevenlabs_model,
                text=korean_script,
                voice_settings=voice_settings
            )

            # Save audio to file
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            audio_file = output_path / f"audio_{int(time.time())}.mp3"

            # Write audio stream to file
            with open(audio_file, "wb") as f:
                for chunk in audio_generator:
                    f.write(chunk)

            # Get file size and estimate duration
            file_size = Path(audio_file).stat().st_size

            if file_size == 0:
                raise ElevenLabsAPIError("Generated audio file is empty")

            # Rough estimation: MP3 at 128kbps = ~16KB per second
            estimated_duration = file_size / (16 * 1024)

            duration_ms = (time.time() - start_time) * 1000

            log_api_response(
                self.logger,
                "ElevenLabs API",
                "generate_audio",
                success=True,
                duration_ms=duration_ms,
                audio_path=str(audio_file),
                file_size_bytes=file_size
            )

            self.logger.info(
                "audio_generated",
                audio_path=str(audio_file),
                file_size_mb=round(file_size / (1024 * 1024), 2),
                estimated_duration_seconds=round(estimated_duration, 1)
            )

            return str(audio_file), estimated_duration

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "ElevenLabs API",
                "generate_audio",
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )

            if "quota" in str(e).lower():
                raise ElevenLabsAPIError("ElevenLabs API quota exceeded")
            elif "unauthorized" in str(e).lower() or "401" in str(e):
                raise ElevenLabsAPIError("Invalid ElevenLabs API key", status_code=401)
            else:
                log_error(self.logger, e, "audio_generator.generate_korean_audio")
                raise ElevenLabsAPIError(f"Audio generation failed: {str(e)}")

    def generate_segment_audio(
        self,
        script_text: str,
        segment_number: int,
        output_dir: str = "output"
    ) -> Tuple[str, float]:
        """
        Generate Korean audio for a single script segment.

        Args:
            script_text: Script text for this segment
            segment_number: Segment number for file naming
            output_dir: Directory to save the generated audio

        Returns:
            Tuple of (audio file path, duration in seconds)

        Raises:
            ElevenLabsAPIError: If audio generation fails
        """
        start_time = time.time()

        log_api_call(
            self.logger,
            "ElevenLabs API",
            "generate_segment_audio",
            script_length=len(script_text),
            segment_number=segment_number,
            language="Korean"
        )

        try:
            # Get or select Korean voice
            voice_id = self._get_korean_voice_id()

            # Configure voice settings
            voice_settings = VoiceSettings(
                stability=self.config.audio_stability,
                similarity_boost=self.config.audio_similarity,
                style=self.config.audio_style,
                use_speaker_boost=True
            )

            # Generate audio
            self.logger.info(
                "generating_segment_audio",
                segment_number=segment_number,
                voice_id=voice_id,
                model=self.config.elevenlabs_model
            )

            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                model_id=self.config.elevenlabs_model,
                text=script_text,
                voice_settings=voice_settings
            )

            # Save audio to file
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            audio_file = output_path / f"audio_segment_{segment_number}_{int(time.time())}.mp3"

            # Write audio stream to file
            with open(audio_file, "wb") as f:
                for chunk in audio_generator:
                    f.write(chunk)

            # Get file size and estimate duration
            file_size = Path(audio_file).stat().st_size

            if file_size == 0:
                raise ElevenLabsAPIError("Generated audio file is empty")

            # Rough estimation: MP3 at 128kbps = ~16KB per second
            estimated_duration = file_size / (16 * 1024)

            duration_ms = (time.time() - start_time) * 1000

            log_api_response(
                self.logger,
                "ElevenLabs API",
                "generate_segment_audio",
                success=True,
                duration_ms=duration_ms,
                audio_path=str(audio_file),
                file_size_bytes=file_size,
                segment_number=segment_number
            )

            self.logger.info(
                "segment_audio_generated",
                segment_number=segment_number,
                audio_path=str(audio_file),
                file_size_mb=round(file_size / (1024 * 1024), 2),
                estimated_duration_seconds=round(estimated_duration, 1)
            )

            return str(audio_file), estimated_duration

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_response(
                self.logger,
                "ElevenLabs API",
                "generate_segment_audio",
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )

            if "quota" in str(e).lower():
                raise ElevenLabsAPIError("ElevenLabs API quota exceeded")
            elif "unauthorized" in str(e).lower() or "401" in str(e):
                raise ElevenLabsAPIError("Invalid ElevenLabs API key", status_code=401)
            else:
                log_error(self.logger, e, "audio_generator.generate_segment_audio")
                raise ElevenLabsAPIError(f"Segment audio generation failed: {str(e)}")

    def _get_korean_voice_id(self) -> str:
        """
        Get the Korean voice ID from config or find a suitable Korean voice.

        Returns:
            Voice ID for Korean TTS

        Raises:
            ElevenLabsAPIError: If no Korean voice is available
        """
        # If voice ID is specified in config, use it
        if self.config.elevenlabs_voice_id:
            self.logger.info(
                "using_configured_voice",
                voice_id=self.config.elevenlabs_voice_id
            )
            return self.config.elevenlabs_voice_id

        # Otherwise, try to find a Korean voice
        try:
            self.logger.info("searching_for_korean_voice")

            voices_response = self.client.voices.get_all()
            voices = voices_response.voices

            # Look for voices that support Korean
            korean_voices = []
            for voice in voices:
                # Check if voice supports Korean (multilingual voices)
                if hasattr(voice, 'labels') and voice.labels:
                    if 'language' in voice.labels and 'korean' in voice.labels.get('language', '').lower():
                        korean_voices.append(voice)

            if korean_voices:
                selected_voice = korean_voices[0]
                self.logger.info(
                    "korean_voice_found",
                    voice_id=selected_voice.voice_id,
                    voice_name=selected_voice.name
                )
                return selected_voice.voice_id

            # Fallback: use first available multilingual voice
            for voice in voices:
                if 'multilingual' in voice.name.lower():
                    self.logger.warning(
                        "using_multilingual_voice_fallback",
                        voice_id=voice.voice_id,
                        voice_name=voice.name
                    )
                    return voice.voice_id

            # Last resort: use first available voice
            if voices:
                default_voice = voices[0]
                self.logger.warning(
                    "using_default_voice_fallback",
                    voice_id=default_voice.voice_id,
                    voice_name=default_voice.name,
                    message="No Korean-specific voice found, results may not be optimal"
                )
                return default_voice.voice_id

            raise ElevenLabsAPIError("No voices available in ElevenLabs account")

        except Exception as e:
            log_error(self.logger, e, "audio_generator._get_korean_voice_id")
            raise ElevenLabsAPIError(f"Failed to get Korean voice: {str(e)}")
