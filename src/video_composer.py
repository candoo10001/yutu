"""
Video composition module using ffmpeg to combine video and audio.
"""
import subprocess
from pathlib import Path
from typing import Optional

import ffmpeg
import structlog

from .config import Config
from .utils.error_handler import VideoCompositionError, VideoGenerationError
from .utils.logger import log_error


class VideoComposer:
    """Combines video and Korean audio using ffmpeg."""

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Video Composer.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()

    def _convert_tts_to_subtitle_format(self, text: str) -> str:
        """
        Convert TTS-optimized Korean text to subtitle-friendly format.
        Converts Korean number words back to numeric symbols for better readability.

        Args:
            text: TTS-optimized Korean text with spelled-out numbers

        Returns:
            Subtitle-friendly text with numeric symbols
        """
        import re

        # Common number word to numeric conversions
        replacements = [
            # Percentages
            (r'퍼센트', '%'),

            # Currency
            (r'달러', '$'),
            (r'원', '₩'),

            # Common fractions and decimals (context-aware)
            (r'일점오', '1.5'),
            (r'이점오', '2.5'),
            (r'삼점오', '3.5'),
            (r'사점오', '4.5'),
            (r'오점오', '5.5'),
            (r'육점오', '6.5'),
            (r'칠점오', '7.5'),
            (r'팔점오', '8.5'),
            (r'구점오', '9.5'),

            # Large numbers
            (r'(\d+)\s*억', r'\1억'),  # Keep spacing correct for billions
            (r'(\d+)\s*만', r'\1만'),  # Keep spacing correct for ten-thousands

            # Quarter references (분기)
            (r'일\s*분기', '1분기'),
            (r'이\s*분기', '2분기'),
            (r'삼\s*분기', '3분기'),
            (r'사\s*분기', '4분기'),

            # Common number + 억 patterns
            (r'십억', '10억'),
            (r'백억', '100억'),
            (r'천억', '1000억'),
            (r'일조', '1조'),
        ]

        result = text
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result)

        return result

    def combine_video_audio(
        self,
        video_path: str,
        audio_path: str,
        output_dir: str = "output"
    ) -> str:
        """
        Combine video and audio into a single video file.

        Args:
            video_path: Path to the video file (without audio)
            audio_path: Path to the Korean audio file
            output_dir: Directory to save the final video

        Returns:
            Path to the final video file with audio

        Raises:
            VideoCompositionError: If composition fails
        """
        # Validate input files exist
        if not Path(video_path).exists():
            raise VideoCompositionError(f"Video file not found: {video_path}")

        if not Path(audio_path).exists():
            raise VideoCompositionError(f"Audio file not found: {audio_path}")

        # Create output path
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        import time
        final_video = output_path / f"final_video_{int(time.time())}.mp4"

        # Get durations of video and audio
        video_duration = self.get_video_duration(video_path)
        audio_duration = self.get_audio_duration(audio_path)

        self.logger.info(
            "combining_video_audio",
            video_path=video_path,
            audio_path=audio_path,
            output_path=str(final_video),
            video_duration=video_duration,
            audio_duration=audio_duration
        )

        try:
            video_input = ffmpeg.input(video_path)
            audio_input = ffmpeg.input(audio_path)

            # If audio is longer than video, slow down video to match audio duration
            if audio_duration > video_duration:
                speed_factor = video_duration / audio_duration
                self.logger.info(
                    "slowing_down_video",
                    speed_factor=speed_factor,
                    original_duration=video_duration,
                    target_duration=audio_duration
                )

                # Use setpts filter to slow down video
                # setpts=PTS/speed means slow down (speed < 1)
                # setpts=PTS*speed means speed up (speed > 1)
                # We want to stretch video, so use PTS/speed_factor
                video_input = video_input.filter('setpts', f'PTS/{speed_factor}')

                output = ffmpeg.output(
                    video_input,
                    audio_input,
                    str(final_video),
                    vcodec='libx264',  # Need to re-encode when using filters
                    acodec='aac',
                    audio_bitrate='192k',
                    shortest=None,
                    strict='experimental'
                )
            else:
                # Video is longer or equal, just combine normally
                output = ffmpeg.output(
                    video_input,
                    audio_input,
                    str(final_video),
                    vcodec='copy',
                    acodec='aac',
                    audio_bitrate='192k',
                    shortest=None,
                    strict='experimental'
                )

            # Run ffmpeg
            ffmpeg.run(
                output,
                capture_stdout=True,
                capture_stderr=True,
                overwrite_output=True
            )

            # Verify output file was created
            if not final_video.exists():
                raise VideoCompositionError("Output video file was not created")

            file_size = final_video.stat().st_size
            if file_size == 0:
                raise VideoCompositionError("Output video file is empty")

            self.logger.info(
                "video_audio_combined",
                final_video=str(final_video),
                file_size_mb=round(file_size / (1024 * 1024), 2)
            )

            return str(final_video)

        except ffmpeg.Error as e:
            # Extract ffmpeg error output
            stderr_output = e.stderr.decode('utf-8') if e.stderr else "No error output"

            log_error(self.logger, e, "video_composer.combine_video_audio")

            self.logger.error(
                "ffmpeg_error",
                error=stderr_output
            )

            raise VideoCompositionError(
                f"ffmpeg failed to combine video and audio: {stderr_output}",
                ffmpeg_output=stderr_output
            )

        except Exception as e:
            log_error(self.logger, e, "video_composer.combine_video_audio")
            raise VideoCompositionError(f"Video composition failed: {str(e)}")

    def get_video_duration(self, video_path: str) -> float:
        """
        Get the duration of a video file in seconds.

        Args:
            video_path: Path to the video file

        Returns:
            Duration in seconds

        Raises:
            VideoCompositionError: If unable to get duration
        """
        try:
            probe = ffmpeg.probe(video_path)
            duration = float(probe['format']['duration'])
            return duration

        except Exception as e:
            log_error(self.logger, e, "video_composer.get_video_duration")
            raise VideoCompositionError(f"Failed to get video duration: {str(e)}")

    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get the duration of an audio file in seconds.

        Args:
            audio_path: Path to the audio file

        Returns:
            Duration in seconds

        Raises:
            VideoCompositionError: If unable to get duration
        """
        try:
            probe = ffmpeg.probe(audio_path)
            duration = float(probe['format']['duration'])
            return duration

        except Exception as e:
            log_error(self.logger, e, "video_composer.get_audio_duration")
            raise VideoCompositionError(f"Failed to get audio duration: {str(e)}")

    def concatenate_videos(self, video_paths: list, output_dir: str = "output") -> str:
        """
        Concatenate multiple video clips into a single video.

        Args:
            video_paths: List of paths to video files to concatenate
            output_dir: Directory to save the concatenated video

        Returns:
            Path to the concatenated video file

        Raises:
            VideoCompositionError: If concatenation fails
        """
        if not video_paths:
            raise VideoCompositionError("No video paths provided for concatenation")

        if len(video_paths) == 1:
            return video_paths[0]  # No need to concatenate

        # Validate all input files exist
        for video_path in video_paths:
            if not Path(video_path).exists():
                raise VideoCompositionError(f"Video file not found: {video_path}")

        # Create output path
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        import time
        concatenated_video = output_path / f"concatenated_{int(time.time())}.mp4"

        # Create a temporary file list for ffmpeg concat
        concat_list_file = output_path / f"concat_list_{int(time.time())}.txt"

        try:
            self.logger.info(
                "concatenating_videos",
                video_count=len(video_paths),
                output_path=str(concatenated_video)
            )

            # Write the concat list file
            with open(concat_list_file, 'w') as f:
                for video_path in video_paths:
                    # ffmpeg concat format requires absolute paths
                    abs_path = Path(video_path).resolve()
                    f.write(f"file '{abs_path}'\n")

            # Use ffmpeg concat demuxer to concatenate videos
            # Re-encode to ensure smooth transitions and consistent timing
            # This prevents freezes/delays between clips
            subprocess.run([
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_list_file),
                '-c:v', 'libx264',  # Re-encode video for smooth transitions
                '-c:a', 'aac',  # Re-encode audio
                '-pix_fmt', 'yuv420p',
                '-vsync', 'cfr',  # Constant frame rate for smooth playback
                '-r', '30',  # Standardize frame rate to 30fps
                '-preset', 'medium',
                '-crf', '23',  # Quality setting
                '-movflags', '+faststart',  # Enable fast start for web playback
                str(concatenated_video)
            ], check=True, capture_output=True)

            # Clean up the concat list file
            concat_list_file.unlink()

            # Verify output file was created
            if not concatenated_video.exists():
                raise VideoCompositionError("Concatenated video file was not created")

            file_size = concatenated_video.stat().st_size
            if file_size == 0:
                raise VideoCompositionError("Concatenated video file is empty")

            self.logger.info(
                "videos_concatenated",
                concatenated_video=str(concatenated_video),
                file_size_mb=round(file_size / (1024 * 1024), 2)
            )

            return str(concatenated_video)

        except subprocess.CalledProcessError as e:
            # Clean up the concat list file if it exists
            if concat_list_file.exists():
                concat_list_file.unlink()

            stderr_output = e.stderr.decode('utf-8') if e.stderr else "No error output"

            log_error(self.logger, e, "video_composer.concatenate_videos")

            self.logger.error(
                "ffmpeg_concatenation_error",
                error=stderr_output
            )

            raise VideoCompositionError(
                f"ffmpeg failed to concatenate videos: {stderr_output}",
                ffmpeg_output=stderr_output
            )

        except Exception as e:
            # Clean up the concat list file if it exists
            if concat_list_file.exists():
                concat_list_file.unlink()

            log_error(self.logger, e, "video_composer.concatenate_videos")
            raise VideoCompositionError(f"Video concatenation failed: {str(e)}")

    def _is_video_file(self, file_path: str) -> bool:
        """
        Check if a file is a video (vs an image).

        Args:
            file_path: Path to the file

        Returns:
            True if video, False if image
        """
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'}
        return Path(file_path).suffix.lower() in video_extensions

    def _prepare_video_clip(
        self,
        media_path: str,
        target_duration: float,
        output_path: Path,
        width: int,
        height: int,
        segment_title: str
    ) -> None:
        """
        Prepare a video clip from pre-defined video, matching target duration.

        Args:
            media_path: Path to the video file
            target_duration: Target duration in seconds
            output_path: Path for the output clip
            width: Output width
            height: Output height
            segment_title: Title to overlay

        Raises:
            VideoCompositionError: If preparation fails
        """
        try:
            # Get video duration
            video_duration = self.get_video_duration(media_path)

            self.logger.info(
                "preparing_video_clip",
                video_duration=video_duration,
                target_duration=target_duration,
                will_loop=video_duration < target_duration
            )

            # Prepare title overlay with Korean font support (cross-platform)
            import platform
            if platform.system() == "Darwin":  # macOS
                font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
                font_name = "AppleSDGothicNeo-Regular"
            else:  # Linux (Ubuntu) - use Noto Sans CJK
                font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
                font_name = "Noto Sans CJK KR"
            
            # Escape special characters in title text for ffmpeg
            # Colons need to be escaped as they're used as parameter separators in filters
            escaped_title = segment_title.replace("'", "'\\''").replace(":", "\\:")

            # Enhanced title for mobile visibility: larger font (80), extra tall box (260), extreme top padding
            # Extreme top padding: text starts at ~160px from top for absolute maximum mobile visibility
            title_filter = (
                f"drawbox=y=0:color=black@0.8:width={width}:height=260:t=fill,"
                # Outer glow effects (yellow glow for visibility)
                f"drawtext=text='{escaped_title}':fontfile={font_path}:"
                f"fontsize=80:fontcolor=yellow@0.3:x=(w-text_w)/2:y=158:borderw=0,"
                f"drawtext=text='{escaped_title}':fontfile={font_path}:"
                f"fontsize=80:fontcolor=yellow@0.2:x=(w-text_w)/2:y=156:borderw=0,"
                # Main text with bold outline for readability
                f"drawtext=text='{escaped_title}':fontfile={font_path}:"
                f"fontsize=80:fontcolor=white:x=(w-text_w)/2:y=162:borderw=5:bordercolor=black@0.9,"
                # Inner highlight layer
                f"drawtext=text='{escaped_title}':fontfile={font_path}:"
                f"fontsize=80:fontcolor=white:x=(w-text_w)/2:y=160"
            )

            # Build ffmpeg command
            # Force keyframe at the start for smooth concatenation
            fps = 30
            if video_duration < target_duration:
                # Video is shorter → loop it
                num_loops = int(target_duration / video_duration) + 1
                subprocess.run([
                    'ffmpeg',
                    '-stream_loop', str(num_loops),
                    '-i', media_path,
                    '-t', str(target_duration),
                    '-vf', f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},{title_filter}",
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-r', str(fps),  # Set frame rate
                    '-vsync', 'cfr',  # Constant frame rate
                    '-g', str(fps),  # Keyframe interval = 1 second (force keyframe at start)
                    '-keyint_min', str(fps),  # Minimum keyframe interval
                    '-force_key_frames', 'expr:gte(t,0)',  # Force keyframe at t=0
                    '-an',  # No audio
                    str(output_path)
                ], check=True, capture_output=True)
            else:
                # Video is longer or equal → trim it
                subprocess.run([
                    'ffmpeg',
                    '-i', media_path,
                    '-t', str(target_duration),
                    '-vf', f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},{title_filter}",
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-r', str(fps),  # Set frame rate
                    '-vsync', 'cfr',  # Constant frame rate
                    '-g', str(fps),  # Keyframe interval = 1 second (force keyframe at start)
                    '-keyint_min', str(fps),  # Minimum keyframe interval
                    '-force_key_frames', 'expr:gte(t,0)',  # Force keyframe at t=0
                    '-an',  # No audio
                    str(output_path)
                ], check=True, capture_output=True)

            self.logger.info("video_clip_prepared", output_path=str(output_path))

        except subprocess.CalledProcessError as e:
            stderr_output = e.stderr.decode('utf-8') if e.stderr else "No error output"
            self.logger.error("video_clip_prep_error", error=stderr_output)
            raise VideoCompositionError(f"Failed to prepare video clip: {stderr_output}")

    def create_slideshow_with_subtitles(
        self,
        segments_data: list,
        output_dir: str = "output"
    ) -> str:
        """
        Create a slideshow video from images/videos with synchronized audio and subtitles.

        Args:
            segments_data: List of dictionaries containing:
                - image_path: Path to the image/video file
                - audio_path: Path to the audio file
                - audio_duration: Duration of the audio
                - text: Subtitle text for this segment
                - segment_number: Segment number
            output_dir: Directory to save the final video

        Returns:
            Path to the final slideshow video

        Raises:
            VideoCompositionError: If creation fails
        """
        if not segments_data:
            raise VideoCompositionError("No segments provided for slideshow")

        self.logger.info(
            "creating_slideshow_with_subtitles",
            num_segments=len(segments_data)
        )

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        import time
        timestamp = int(time.time())

        try:
            # Step 1: Create video clips for each image with its duration
            video_clips = []

            # Define audio speed factor (used throughout video composition)
            speed_factor = 1.2  # 1.2x speed for Korean TTS

            for i, segment in enumerate(segments_data):
                # Adjust clip duration to match sped-up audio
                # When audio is sped up by 1.2x, actual duration is original_duration / 1.2
                clip_duration = segment['audio_duration'] / speed_factor

                media_path = segment['image_path']  # Could be image or video
                clip_output = output_path / f"clip_{i}_{timestamp}.mp4"

                # Calculate resolution based on aspect ratio
                aspect_ratio = self.config.video_aspect_ratio
                if aspect_ratio == "9:16":
                    width, height = 1080, 1920  # Portrait
                elif aspect_ratio == "16:9":
                    width, height = 1920, 1080  # Landscape
                else:  # 1:1
                    width, height = 1080, 1080  # Square

                # Get segment title for overlay
                segment_title = segment.get('title', '').replace("'", "\\'")

                # Truncate title if too long to prevent overflow
                # For short-form video, keep titles concise (max 10 chars)
                max_title_length = 10
                if len(segment_title) > max_title_length:
                    segment_title = segment_title[:max_title_length] + "..."

                # Check if media is a video or image
                if self._is_video_file(media_path):
                    # Handle pre-defined video
                    self.logger.info(
                        "creating_video_clip_from_video",
                        segment_number=segment['segment_number'],
                        video_path=media_path,
                        duration=clip_duration
                    )

                    self._prepare_video_clip(
                        media_path=media_path,
                        target_duration=clip_duration,
                        output_path=clip_output,
                        width=width,
                        height=height,
                        segment_title=segment_title
                    )

                    video_clips.append(str(clip_output))
                    continue

                # Handle image with Ken Burns effect
                self.logger.info(
                    "creating_video_clip_from_image",
                    segment_number=segment['segment_number'],
                    image_path=media_path,
                    duration=clip_duration
                )

                # Create video clip from image with dynamic Ken Burns effect (zoom + pan)
                fps = 30

                # Calculate total frames for zoompan filter
                total_frames = int(clip_duration * fps)

                # Dynamic movement patterns: Mix of zoom-in, zoom-out, and varied panning
                # Each pattern creates lively, engaging motion perfect for short clips
                # Using zoompan filter with proper syntax: z='zoom+delta' or z='zoom-delta'
                # 'on' is frame number (0, 1, 2, ...), zoom starts at initial value
                movement_patterns = [
                    # Pattern 0: Zoom IN (starts at zoom=1.2, increases to ~1.5) + pan right
                    # Creates focus effect moving right
                    f"scale=3*iw:3*ih,zoompan=z='1.2+0.001*on':x='iw/2-(iw/zoom/2)+on*1.5':y='ih/2-(ih/zoom/2)':d={total_frames}:s={width}x{height}:fps={fps}",
                    
                    # Pattern 1: Zoom OUT (starts at zoom=1.5, decreases to ~1.2) + pan left
                    # Creates reveal effect moving left
                    f"scale=3*iw:3*ih,zoompan=z='1.5-0.001*on':x='iw/2-(iw/zoom/2)-on*1.2':y='ih/2-(ih/zoom/2)':d={total_frames}:s={width}x{height}:fps={fps}",
                    
                    # Pattern 2: Zoom IN + diagonal pan (zoom in, move diagonally down-right)
                    # Creates dramatic focus from top-left
                    f"scale=3*iw:3*ih,zoompan=z='1.2+0.0012*on':x='iw/2-(iw/zoom/2)+on*1':y='ih/2-(ih/zoom/2)+on*0.7':d={total_frames}:s={width}x{height}:fps={fps}",
                    
                    # Pattern 3: Zoom OUT + upward pan (zoom out, move up)
                    # Creates upward reveal effect
                    f"scale=3*iw:3*ih,zoompan=z='1.5-0.001*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)-on*1.3':d={total_frames}:s={width}x{height}:fps={fps}",
                    
                    # Pattern 4: Strong zoom IN + slow pan right
                    # Creates intense focus with subtle movement
                    f"scale=3.5*iw:3.5*ih,zoompan=z='1.1+0.0015*on':x='iw/2-(iw/zoom/2)+on*0.8':y='ih/2-(ih/zoom/2)':d={total_frames}:s={width}x{height}:fps={fps}",
                    
                    # Pattern 5: Zoom OUT + diagonal pan (zoom out, move diagonally up-left)
                    # Creates sweeping reveal
                    f"scale=3*iw:3*ih,zoompan=z='1.5-0.0012*on':x='iw/2-(iw/zoom/2)-on*0.9':y='ih/2-(ih/zoom/2)-on*0.8':d={total_frames}:s={width}x{height}:fps={fps}",
                    
                    # Pattern 6: Moderate zoom IN + downward pan
                    # Creates focus moving down
                    f"scale=3*iw:3*ih,zoompan=z='1.2+0.0008*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)+on*1.1':d={total_frames}:s={width}x{height}:fps={fps}",
                    
                    # Pattern 7: Zoom OUT + horizontal sweep (zoom out, move right)
                    # Creates wide reveal sweep
                    f"scale=3*iw:3*ih,zoompan=z='1.5-0.001*on':x='iw/2-(iw/zoom/2)-on*1.6':y='ih/2-(ih/zoom/2)':d={total_frames}:s={width}x{height}:fps={fps}",
                ]

                # Select pattern based on segment index to add variety across the video
                ken_burns = movement_patterns[i % len(movement_patterns)]

                # Enhanced title overlay with gradient background and glow effect
                # Prepare title overlay with rounded, cute Korean font
                # Use project-bundled font for cross-platform compatibility
                font_path = str(Path(__file__).parent.parent / "fonts" / "NanumSquareB.ttf")
                font_name = "NanumSquare"
                
                # Escape special characters in title text for ffmpeg
                # Colons need to be escaped as they're used as parameter separators in filters
                escaped_title = segment_title.replace("'", "'\\''").replace(":", "\\:")

                # Enhanced title for mobile visibility: larger font (80), extra tall box (440), extreme top padding
                # Extreme top padding: text starts at ~220px from top for absolute maximum mobile visibility
                title_filter = (
                    # Sky blue padding at top (solid color, no opacity)
                    f"drawbox=y=0:color=0x87CEEB:width={width}:height=40:t=fill,"
                    # Grayish-black background bar (solid, not pure black)
                    f"drawbox=y=40:color=0x3a3a3a:width={width}:height=360:t=fill,"
                    # Sky blue padding at bottom of title area (solid color, no opacity)
                    f"drawbox=y=400:color=0x87CEEB:width={width}:height=40:t=fill,"
                    # Outer glow effect (multiple layers for smooth glow)
                    f"drawtext=text='{escaped_title}':fontfile={font_path}:"
                    f"fontsize=80:fontcolor=yellow@0.3:x=(w-text_w)/2:y=218:borderw=0,"
                    f"drawtext=text='{escaped_title}':fontfile={font_path}:"
                    f"fontsize=80:fontcolor=yellow@0.2:x=(w-text_w)/2:y=216:borderw=0,"
                    # Main text with bold outline for readability
                    f"drawtext=text='{escaped_title}':fontfile={font_path}:"
                    f"fontsize=80:fontcolor=white:x=(w-text_w)/2:y=222:borderw=5:bordercolor=black@0.9,"
                    # Inner highlight layer
                    f"drawtext=text='{escaped_title}':fontfile={font_path}:"
                    f"fontsize=80:fontcolor=white:x=(w-text_w)/2:y=220"
                )

                # Combine Ken Burns effect with title overlay
                full_filter = (
                    f"{ken_burns},"
                    f"trim=duration={clip_duration},"
                    f"setpts=PTS-STARTPTS,"
                    f"{title_filter}"
                )

                # Use ffmpeg to create video from image with Ken Burns effect and title overlay
                # Ensure consistent frame rate and keyframes for smooth concatenation
                subprocess.run([
                    'ffmpeg',
                    '-loop', '1',
                    '-i', segment['image_path'],
                    '-c:v', 'libx264',
                    '-t', str(clip_duration),
                    '-pix_fmt', 'yuv420p',
                    '-vf', full_filter,
                    '-r', str(fps),  # Set frame rate
                    '-vsync', 'cfr',  # Constant frame rate
                    '-g', str(fps),  # Keyframe interval = 1 second (force keyframe at start)
                    '-keyint_min', str(fps),  # Minimum keyframe interval
                    '-force_key_frames', 'expr:gte(t,0)',  # Force keyframe at t=0
                    '-preset', 'medium',
                    '-crf', '23',
                    str(clip_output)
                ], check=True, capture_output=True)

                video_clips.append(str(clip_output))

                self.logger.info(
                    "video_clip_created",
                    segment_number=segment['segment_number'],
                    clip_path=str(clip_output)
                )

            # Step 2: Concatenate all video clips
            self.logger.info("concatenating_video_clips")
            concatenated_video = self.concatenate_videos(video_clips, output_dir)

            # Step 3: Concatenate all audio files
            self.logger.info("concatenating_audio_files")
            audio_list_file = output_path / f"audio_list_{timestamp}.txt"
            concatenated_audio = output_path / f"concatenated_audio_{timestamp}.mp3"

            with open(audio_list_file, 'w') as f:
                for segment in segments_data:
                    abs_path = Path(segment['audio_path']).resolve()
                    f.write(f"file '{abs_path}'\n")

            subprocess.run([
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(audio_list_file),
                '-c', 'copy',
                str(concatenated_audio)
            ], check=True, capture_output=True)

            audio_list_file.unlink()  # Clean up

            # Step 4: Create subtitle file (ASS format) with proper styling
            # Note: speed_factor is already defined earlier when creating video clips
            # Adjust subtitle timing to match sped-up audio (divide by speed_factor)
            if self.config.enable_subtitles:
                self.logger.info("creating_subtitle_file", speed_factor=speed_factor)
                subtitle_file = output_path / f"subtitles_{timestamp}.ass"

                # Get font name for ASS file
                # Use rounded, cute Korean fonts for friendly appearance
                import platform
                if platform.system() == "Darwin":  # macOS
                    font_name = "NanumSquare"  # Rounded, friendly font
                else:  # Linux (Ubuntu) - install with: apt-get install fonts-nanum
                    font_name = "NanumSquare"  # Rounded, friendly font

                with open(subtitle_file, 'w', encoding='utf-8') as f:
                    # Write ASS header with style definition
                    f.write("[Script Info]\n")
                    f.write("ScriptType: v4.00+\n")
                    f.write("PlayResX: 1080\n")
                    f.write("PlayResY: 1920\n")
                    f.write("WrapStyle: 1\n\n")

                    f.write("[V4+ Styles]\n")
                    f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
                    # PrimaryColour=white text, OutlineColour=very dark gray outline, BackColour=very dark gray background box
                    # Spacing=5 adds character spacing for better readability
                    f.write(f"Style: Default,{font_name},{self.config.subtitle_font_size},&H00FFFFFF,&H000000FF,&H00282828,&H00282828,0,0,0,0,100,100,5,0,3,6,2,2,60,60,820,1\n\n")

                    f.write("[Events]\n")
                    f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")

                    current_time = 0.0
                    subtitle_index = 1

                    for segment in segments_data:
                        # Convert TTS-optimized text to subtitle format (numbers as symbols)
                        subtitle_text = self._convert_tts_to_subtitle_format(segment['text'])

                        # Split text into words (Korean uses spaces between phrases/clauses)
                        words = subtitle_text.split()
                        total_words = len(words)

                        if total_words == 0:
                            continue

                        # Calculate duration per word (adjusted for audio speed)
                        # When audio is sped up by 1.2x, the actual duration is original_duration / 1.2
                        segment_duration = segment['audio_duration'] / speed_factor
                        time_per_word = segment_duration / total_words

                        # Group words into chunks for 2-line subtitles
                        # Show 3-4 words total, split into 2 lines (1-2 words per line)
                        # This makes subtitles more compact and prevents long lines
                        words_per_line = 2  # Words per line
                        total_words_per_subtitle = 4  # Total words for 2 lines (2 lines × 2 words)

                        for i in range(0, total_words, total_words_per_subtitle):
                            # Get words for this subtitle (up to total_words_per_subtitle)
                            word_chunk = words[i:i + total_words_per_subtitle]
                            chunk_word_count = len(word_chunk)

                            if chunk_word_count == 0:
                                continue

                            # Split words into two groups to ensure we never break Korean words
                            # Korean doesn't use spaces between characters, so we split at word boundaries (spaces)
                            # Try to balance line lengths while keeping words intact
                            mid_point = (chunk_word_count + 1) // 2  # Start with roughly half by word count
                            line1_words = word_chunk[:mid_point]
                            line2_words = word_chunk[mid_point:]
                            
                            # Join words with spaces - this ensures Korean words stay intact
                            line1_text = ' '.join(line1_words)
                            line2_text = ' '.join(line2_words)
                            
                            # Adjust split point if first line is too long (Korean: ~10-12 chars per line for compact display)
                            # This prevents ffmpeg from breaking long lines and splitting Korean characters
                            # Shorter lines = less space taken up in video
                            max_chars_per_line = 12  # Maximum characters per line for Korean subtitles (compact)
                            
                            if len(line1_text) > max_chars_per_line and mid_point > 1:
                                # First line too long, move words to second line
                                while len(line1_text) > max_chars_per_line and len(line1_words) > 1:
                                    line2_words.insert(0, line1_words.pop())
                                    line1_text = ' '.join(line1_words)
                                    line2_text = ' '.join(line2_words)
                            
                            # Only create 2-line subtitle if we have words for both lines
                            # This prevents splitting single words across lines
                            if line2_text and len(line1_words) > 0 and len(line2_words) > 0:
                                chunk_text = f"{line1_text}\n{line2_text}"
                            else:
                                # If split would result in empty second line or only one word, keep on one line
                                chunk_text = ' '.join(word_chunk)

                            # Calculate timing for this subtitle chunk
                            # Subtitles sync exactly with narrative voice timing
                            start_time = current_time
                            end_time = current_time + (time_per_word * chunk_word_count)

                            # Convert newlines to ASS format (\N instead of \n)
                            ass_text = chunk_text.replace('\n', '\\N')

                            # Add padding around text using hard spaces (\h in ASS format)
                            # This creates visual padding inside the background box
                            ass_text = f"\\h\\h{ass_text}\\h\\h"

                            # ASS format: Dialogue: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
                            f.write(f"Dialogue: 0,{self._format_ass_time(start_time)},{self._format_ass_time(end_time)},Default,,0,0,0,,{ass_text}\n")

                            subtitle_index += 1
                            current_time = end_time

                # Step 5: Combine video, audio, and subtitles
                self.logger.info("combining_video_audio_subtitles")
                final_video = output_path / f"final_shorts_{timestamp}.mp4"

                # Build subtitle filter for ffmpeg with proper word wrapping
                # Position subtitles based on config
                subtitle_y = "h-th-50" if self.config.subtitle_position == "bottom" else \
                            "50" if self.config.subtitle_position == "top" else "(h-th)/2"

                # Create subtitle style with word wrapping enabled
                # WordWrap=1 ensures words break correctly and aren't cut off
                # Note: FontSize is in pixels relative to PlayResY
                # With PlayResY=1920 (full video height), font size needs to be larger for visibility
                # Font size of 100 with PlayResY=1920 provides good readability on mobile devices
                # Using Alignment=2 (bottom-center) with MarginV=960 to position in vertical center
                # Combine video with audio and burn in subtitles (ASS format with embedded styling)
                video_input = ffmpeg.input(concatenated_video)
                audio_input = ffmpeg.input(str(concatenated_audio))

                # Apply speed and volume to audio (before mixing with background music or output)
                # speed_factor already defined earlier (before subtitle generation)
                volume_boost = 1.5  # 50% volume increase
                audio_volume = audio_input.filter('volume', volume_boost)
                audio_speed = audio_volume.filter('atempo', speed_factor)

                # Use subtitles filter to burn in ASS subtitles
                # Styling is embedded in the ASS file itself
                video_with_subs = video_input.filter('subtitles', str(subtitle_file))

                # Add sky blue gradient padding bars at top and bottom of entire video
                # This creates a frame effect around the whole video
                aspect_ratio = self.config.video_aspect_ratio
                if aspect_ratio == "9:16":
                    video_height = 1920
                elif aspect_ratio == "16:9":
                    video_height = 1080
                else:  # 1:1
                    video_height = 1080

                # Add sky blue padding bars on all four edges to create a frame effect
                # Solid color (no opacity) for clearer visibility
                padding_width = 50  # Larger padding for more prominent frame effect

                # Top padding bar
                video_with_subs = video_with_subs.filter('drawbox',
                    x=0, y=0, w='iw', h=padding_width,
                    color='0x87CEEB', t='fill')

                # Bottom padding bar
                video_with_subs = video_with_subs.filter('drawbox',
                    x=0, y=video_height-padding_width, w='iw', h=padding_width,
                    color='0x87CEEB', t='fill')

                # Get video width for left/right padding
                if aspect_ratio == "9:16":
                    video_width = 1080
                elif aspect_ratio == "16:9":
                    video_width = 1920
                else:  # 1:1
                    video_width = 1080

                # Left padding bar
                video_with_subs = video_with_subs.filter('drawbox',
                    x=0, y=0, w=padding_width, h='ih',
                    color='0x87CEEB', t='fill')

                # Right padding bar
                video_with_subs = video_with_subs.filter('drawbox',
                    x=video_width-padding_width, y=0, w=padding_width, h='ih',
                    color='0x87CEEB', t='fill')

                # Calculate total audio duration for icon animation
                total_audio_duration = sum(seg['audio_duration'] for seg in segments_data) / speed_factor

                # Add spinning business icon in bottom left corner for lively effect
                # Position: Bottom left corner, just inside the sky blue padding
                icon_size = 180  # Much larger size for clear visibility
                icon_x = 70  # 70px from left edge (just inside sky blue padding)
                icon_y = video_height - 250  # 250px from bottom (above sky blue padding)

                # Create spinning icon overlay
                # The icon rotates continuously: 1 full rotation every 3 seconds (120 degrees/second)
                # Priority: Use channel logo from assets folder, fallback to generated icon
                channel_logo_path = output_path.parent / 'assets' / 'channel_logo.png'

                if channel_logo_path.exists():
                    # Use custom channel logo and resize it (always regenerate to apply new size)
                    icon_path = output_path / f'resized_channel_logo_{icon_size}.png'
                    from PIL import Image
                    logo = Image.open(channel_logo_path)
                    # Resize to icon_size while maintaining aspect ratio
                    logo.thumbnail((icon_size, icon_size), Image.Resampling.LANCZOS)
                    logo.save(str(icon_path))
                else:
                    # Fallback: Create default business icon
                    icon_path = output_path / 'business_icon.png'
                    if not icon_path.exists():
                        from PIL import Image, ImageDraw, ImageFont
                        img = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
                        draw = ImageDraw.Draw(img)
                        circle_color = (135, 206, 235, 255)  # Sky blue
                        margin = icon_size // 10
                        draw.ellipse([margin, margin, icon_size-margin, icon_size-margin], fill=circle_color)
                        try:
                            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", icon_size//2)
                        except:
                            font = ImageFont.load_default()
                        text = "$"
                        bbox = draw.textbbox((0, 0), text, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        text_x = (icon_size - text_width) // 2
                        text_y = (icon_size - text_height) // 2 - 5
                        draw.text((text_x, text_y), text, fill='white', font=font)
                        img.save(str(icon_path))

                # Add spinning icon overlay for lively effect
                # Using FFmpeg's rotate filter with time-based angle
                icon_input = ffmpeg.input(str(icon_path), loop=1)
                # Rotate icon: 360 degrees every 3 seconds = 2*PI radians every 3 seconds
                rotated_icon = icon_input.filter('rotate', 't*2*PI/3', fillcolor='none')
                video_with_subs = ffmpeg.overlay(
                    video_with_subs,
                    rotated_icon,
                    x=icon_x,
                    y=icon_y,
                    shortest=1
                )

                # Add background music if enabled
                if self.config.enable_background_music:
                    self.logger.info("adding_background_music")

                    # Generate background music
                    from .background_music_generator import BackgroundMusicGenerator
                    bgm_generator = BackgroundMusicGenerator(self.config, self.logger)

                    # total_audio_duration already calculated above for icon overlay
                    
                    try:
                        bgm_path = bgm_generator.generate_background_music(
                            duration=total_audio_duration,
                            output_dir=output_dir
                        )
                        
                        self.logger.info(
                            "background_music_generated",
                            bgm_path=bgm_path,
                            duration=total_audio_duration,
                            file_exists=Path(bgm_path).exists() if bgm_path else False
                        )
                        
                        if not bgm_path or not Path(bgm_path).exists():
                            self.logger.warning(
                                "background_music_file_not_found",
                                bgm_path=bgm_path,
                                action="skipping_background_music"
                            )
                            # Fall through to no background music case
                            raise FileNotFoundError(f"Background music file not found: {bgm_path}")

                        # Mix voiceover with background music
                        bgm_input = ffmpeg.input(bgm_path)
                        
                        # Apply volume to background music before mixing
                        bgm_volume = bgm_input.filter('volume', self.config.background_music_volume)

                        # Mix audio: voiceover (already has volume and speed applied) + background music at reduced volume
                        # Use 'longest' so background music plays for full duration even if voiceover ends early (due to speed up)
                        mixed_audio = ffmpeg.filter(
                            [audio_speed, bgm_volume],
                            'amix',
                            inputs=2,
                            duration='longest'  # Use longest to ensure background music plays full duration
                        )

                        output = ffmpeg.output(
                            video_with_subs,
                            mixed_audio,
                            str(final_video),
                            vcodec='libx264',
                            acodec='aac',
                            audio_bitrate='192k'
                        )
                    except (FileNotFoundError, VideoCompositionError, VideoGenerationError, Exception) as e:
                        # If background music generation fails, log and fall back to voiceover only
                        self.logger.warning(
                            "background_music_failed_fallback",
                            error=str(e),
                            error_type=type(e).__name__,
                            action="using_voiceover_only"
                        )
                        output = ffmpeg.output(
                            video_with_subs,
                            audio_speed,  # Use voiceover with volume and speed
                            str(final_video),
                            vcodec='libx264',
                            acodec='aac',
                            audio_bitrate='192k'
                        )

                    output = ffmpeg.output(
                        video_with_subs,
                        mixed_audio,
                        str(final_video),
                        vcodec='libx264',
                        acodec='aac',
                        audio_bitrate='192k'
                    )
                else:
                    # Use voiceover with volume and speed already applied (when no background music)
                    output = ffmpeg.output(
                        video_with_subs,
                        audio_speed,  # Already has volume boost and speed applied
                        str(final_video),
                        vcodec='libx264',
                        acodec='aac',
                        audio_bitrate='192k'
                    )

                ffmpeg.run(output, capture_stdout=True, capture_stderr=True, overwrite_output=True)
            else:
                # Just combine video and audio without subtitles
                self.logger.info("combining_video_audio_no_subtitles")
                final_video = output_path / f"final_shorts_{timestamp}.mp4"
                final_video_str = self.combine_video_audio(concatenated_video, str(concatenated_audio), output_dir)
                final_video = Path(final_video_str)

            # Verify output
            if not final_video.exists():
                raise VideoCompositionError("Final video was not created")

            file_size = final_video.stat().st_size
            if file_size == 0:
                raise VideoCompositionError("Final video is empty")

            self.logger.info(
                "slideshow_created",
                final_video=str(final_video),
                file_size_mb=round(file_size / (1024 * 1024), 2)
            )

            # Clean up temporary files
            for clip in video_clips:
                Path(clip).unlink(missing_ok=True)
            Path(concatenated_video).unlink(missing_ok=True)
            Path(concatenated_audio).unlink(missing_ok=True)
            if self.config.enable_subtitles:
                Path(subtitle_file).unlink(missing_ok=True)

            return str(final_video)

        except subprocess.CalledProcessError as e:
            stderr_output = e.stderr.decode('utf-8') if e.stderr else "No error output"
            log_error(self.logger, e, "video_composer.create_slideshow_with_subtitles")
            self.logger.error("ffmpeg_slideshow_error", error=stderr_output)
            raise VideoCompositionError(f"Failed to create slideshow: {stderr_output}")

        except Exception as e:
            log_error(self.logger, e, "video_composer.create_slideshow_with_subtitles")
            raise VideoCompositionError(f"Slideshow creation failed: {str(e)}")

    def _format_srt_time(self, seconds: float) -> str:
        """
        Format seconds as SRT timestamp (HH:MM:SS,mmm).

        Args:
            seconds: Time in seconds

        Returns:
            Formatted SRT timestamp
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _format_ass_time(self, seconds: float) -> str:
        """
        Format seconds as ASS timestamp (H:MM:SS.CC).

        Args:
            seconds: Time in seconds

        Returns:
            Formatted ASS timestamp
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds % 1) * 100)

        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"

    def _color_to_hex(self, color: str) -> str:
        """
        Convert color name or format to hex for ffmpeg subtitles.

        Args:
            color: Color string (e.g., "white", "black@0.6")

        Returns:
            Hex color code for ffmpeg
        """
        # Handle transparency (e.g., "black@0.6")
        if "@" in color:
            color_name, alpha = color.split("@")
            alpha_value = int((1 - float(alpha)) * 255)  # Invert alpha for ffmpeg
        else:
            color_name = color
            alpha_value = 0

        # Basic color mapping
        color_map = {
            "white": "FFFFFF",
            "black": "000000",
            "red": "FF0000",
            "green": "00FF00",
            "blue": "0000FF",
            "yellow": "FFFF00"
        }

        color_hex = color_map.get(color_name.lower(), "FFFFFF")

        # Return in ffmpeg format (AABBGGRR)
        return f"{alpha_value:02X}{color_hex[4:6]}{color_hex[2:4]}{color_hex[0:2]}"
