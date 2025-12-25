"""
Background music generation for YouTube Shorts.
"""
import random
import subprocess
from pathlib import Path
from typing import Optional, List

import structlog

from .config import Config
from .utils.error_handler import VideoGenerationError


class BackgroundMusicGenerator:
    """Generates simple background music for videos."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Background Music Generator.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()
        self.music_folder = Path("background_music")

    def _get_available_music_files(self) -> List[Path]:
        """
        Get list of available background music files.

        Returns:
            List of Path objects for music files
        """
        if not self.music_folder.exists():
            return []

        # Support common audio formats
        music_files = []
        for ext in ['*.mp3', '*.wav', '*.m4a', '*.aac', '*.ogg']:
            music_files.extend(self.music_folder.glob(ext))

        return list(music_files)

    def _prepare_music_file(self, source_file: Path, duration: float, output_file: Path) -> str:
        """
        Prepare an existing music file to match the required duration.
        Loops the music if it's shorter than needed, or trims if longer.

        Args:
            source_file: Path to source music file
            duration: Required duration in seconds
            output_file: Path to output file

        Returns:
            Path to the prepared music file

        Raises:
            VideoGenerationError: If preparation fails
        """
        try:
            # Use ffmpeg to loop/trim the music to exact duration
            # The -stream_loop option loops the input, and -t sets duration
            subprocess.run([
                'ffmpeg',
                '-stream_loop', '-1',  # Loop indefinitely
                '-i', str(source_file),
                '-t', str(duration),  # Trim to exact duration
                '-af', 'afade=t=out:st=' + str(duration - 2) + ':d=2',  # Fade out at end
                '-c:a', 'libmp3lame',
                '-b:a', '192k',
                str(output_file)
            ], check=True, capture_output=True)

            file_size = output_file.stat().st_size
            if file_size == 0:
                raise VideoGenerationError("Prepared background music file is empty")

            self.logger.info(
                "background_music_prepared",
                source=str(source_file),
                output=str(output_file),
                file_size_kb=round(file_size / 1024, 2),
                duration=duration
            )

            return str(output_file)

        except subprocess.CalledProcessError as e:
            stderr_output = e.stderr.decode('utf-8') if e.stderr else "No error output"
            self.logger.error("ffmpeg_music_prep_error", error=stderr_output)
            raise VideoGenerationError(f"Music preparation failed: {stderr_output}")

    def _generate_synthetic_music(self, duration: float, output_file: Path) -> str:
        """
        Generate synthetic background music using ffmpeg sine waves.

        Args:
            duration: Duration in seconds
            output_file: Output file path

        Returns:
            Path to the generated music file

        Raises:
            VideoGenerationError: If generation fails
        """
        try:
            # Generate synthetic background music with rhythm and harmonics
            subprocess.run([
                'ffmpeg',
                # Bass line (low frequency for foundation)
                '-f', 'lavfi', '-i', f'sine=frequency=110:duration={duration}',  # A2
                # Mid tones (melody)
                '-f', 'lavfi', '-i', f'sine=frequency=220:duration={duration}',  # A3
                '-f', 'lavfi', '-i', f'sine=frequency=330:duration={duration}',  # E4
                '-f', 'lavfi', '-i', f'sine=frequency=440:duration={duration}',  # A4
                # High harmonics (shimmer)
                '-f', 'lavfi', '-i', f'sine=frequency=660:duration={duration}',  # E5
                '-f', 'lavfi', '-i', f'sine=frequency=880:duration={duration}',  # A5
                # Rhythm pulse (adds energy)
                '-f', 'lavfi', '-i', f'sine=frequency=165:duration={duration}',  # E3 (pulse)
                '-filter_complex',
                # Mix all layers with different volumes for depth
                '[0:a]volume=0.20[bass];'
                '[1:a]volume=0.25[mid1];'
                '[2:a]volume=0.25[mid2];'
                '[3:a]volume=0.25[mid3];'
                '[4:a]volume=0.15[high1];'
                '[5:a]volume=0.15[high2];'
                '[6:a]atempo=1.5,volume=0.10[pulse];'
                '[bass][mid1][mid2][mid3][high1][high2][pulse]amix=inputs=7:duration=longest:dropout_transition=3,'
                'volume=1.0,'
                'highpass=f=80,'
                'lowpass=f=8000',
                '-c:a', 'libmp3lame',
                '-b:a', '192k',
                str(output_file)
            ], check=True, capture_output=True)

            file_size = output_file.stat().st_size
            if file_size == 0:
                raise VideoGenerationError("Generated background music file is empty")

            self.logger.info(
                "synthetic_background_music_generated",
                music_path=str(output_file),
                file_size_kb=round(file_size / 1024, 2),
                duration=duration
            )

            return str(output_file)

        except subprocess.CalledProcessError as e:
            stderr_output = e.stderr.decode('utf-8') if e.stderr else "No error output"
            self.logger.error("ffmpeg_synthetic_music_error", error=stderr_output)
            raise VideoGenerationError(f"Synthetic music generation failed: {stderr_output}")

    def generate_background_music(self, duration: float, output_dir: str = "output") -> str:
        """
        Generate or select background music.
        First tries to use existing music files from background_music/ folder,
        falls back to synthetic generation if none available.

        Args:
            duration: Duration of the music in seconds
            output_dir: Directory to save the generated music

        Returns:
            Path to the generated music file

        Raises:
            VideoGenerationError: If music generation fails
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            import time
            music_file = output_path / f"bgm_{int(time.time())}.mp3"

            # Check for existing music files
            available_music = self._get_available_music_files()

            if available_music:
                # Use existing music file
                selected_music = random.choice(available_music)
                self.logger.info(
                    "using_existing_background_music",
                    source_file=str(selected_music),
                    duration=duration,
                    output_path=str(music_file)
                )
                return self._prepare_music_file(selected_music, duration, music_file)
            else:
                # Fall back to synthetic generation
                self.logger.info(
                    "generating_synthetic_background_music",
                    duration=duration,
                    output_path=str(music_file)
                )
                return self._generate_synthetic_music(duration, music_file)

        except Exception as e:
            self.logger.error("bgm_generation_error", error=str(e))
            raise VideoGenerationError(f"Background music generation failed: {str(e)}")
