#!/usr/bin/env python3
"""
Test script for video composition changes (subtitle sync and title visibility).
Creates a test video using pre-defined images and generated test audio.
No API calls required - uses local resources only.
"""
import subprocess
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import structlog

from src.config import Config
from src.video_composer import VideoComposer


def create_test_image(output_path: str, color: tuple, text: str, width: int = 1080, height: int = 1920):
    """Create a simple test image with colored background and text."""
    # Create image with solid color
    img = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img)

    # Add text in the center
    try:
        # Try to use a larger font
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
    except:
        font = ImageFont.load_default()

    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Draw text in center
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), text, fill='white', font=font)

    # Save image
    img.save(output_path)
    print(f"✓ Created test image: {output_path}")


def create_test_audio(output_path: str, duration: float, text: str = ""):
    """Create a silent audio file with specified duration (simulates TTS output)."""
    # Generate silent audio using ffmpeg
    # This simulates what would come from the TTS API
    subprocess.run([
        'ffmpeg',
        '-f', 'lavfi',
        '-i', f'anullsrc=r=44100:cl=stereo',
        '-t', str(duration),
        '-acodec', 'libmp3lame',
        '-ab', '128k',
        '-y',  # Overwrite if exists
        output_path
    ], check=True, capture_output=True)
    print(f"✓ Created test audio: {output_path} ({duration}s)")


def main():
    """Run the test video composition."""
    print("\n" + "="*60)
    print("TEST SCRIPT: Video Composition Changes")
    print("="*60)
    print("\nTesting:")
    print("  1. Subtitle sync with 1.2x audio speed")
    print("  2. Enhanced title visibility (larger font, more padding)")
    print("\n" + "="*60 + "\n")

    # Setup
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)

    timestamp = int(time.time())

    # Create test segments data
    # Each segment has: image, audio, text, title, duration
    test_segments = [
        {
            "text": "첫 번째 테스트 세그먼트입니다 자막 동기화를 확인합니다",
            "title": "테스트 1: 자막 동기화",
            "duration": 5.0,
            "color": (66, 135, 245)  # Blue
        },
        {
            "text": "두 번째 테스트 세그먼트입니다 제목 가시성을 확인합니다",
            "title": "테스트 2: 제목 표시",
            "duration": 5.0,
            "color": (52, 199, 89)  # Green
        },
        {
            "text": "세 번째 테스트 세그먼트입니다 모바일 환경에서 잘 보이는지 확인합니다",
            "title": "테스트 3: 모바일 최적화",
            "duration": 6.0,
            "color": (255, 149, 0)  # Orange
        },
        {
            "text": "마지막 테스트 세그먼트입니다 모든 변경사항이 잘 적용되었습니다",
            "title": "테스트 4: 최종 확인",
            "duration": 6.0,
            "color": (255, 59, 48)  # Red
        }
    ]

    print("Step 1: Creating test images and audio files...")
    print("-" * 60)

    segments_data = []

    for i, segment_info in enumerate(test_segments):
        segment_num = i + 1

        # Create test image
        image_path = test_dir / f"test_image_{segment_num}_{timestamp}.jpg"
        create_test_image(
            str(image_path),
            segment_info["color"],
            f"Segment {segment_num}",
            width=1080,
            height=1920
        )

        # Create test audio (silent, but with correct duration)
        audio_path = test_dir / f"test_audio_{segment_num}_{timestamp}.mp3"
        create_test_audio(
            str(audio_path),
            segment_info["duration"],
            segment_info["text"]
        )

        # Build segment data structure expected by VideoComposer
        segments_data.append({
            "image_path": str(image_path),
            "audio_path": str(audio_path),
            "audio_duration": segment_info["duration"],
            "text": segment_info["text"],
            "title": segment_info["title"],  # Key must be 'title', not 'segment_title'
            "segment_number": segment_num
        })

    print("\n" + "="*60)
    print(f"Step 2: Composing video with {len(segments_data)} segments...")
    print("-" * 60)

    # Initialize config with dummy API keys (not used in this test)
    config = Config(
        news_api_key="dummy_key",
        claude_api_key="dummy_key",
        google_api_key="dummy_key",
        elevenlabs_api_key="dummy_key"
    )
    logger = structlog.get_logger()

    # Override subtitle settings if needed
    config.enable_subtitles = True
    config.subtitle_position = "middle"  # Test middle position

    video_composer = VideoComposer(config, logger)

    # Create the video
    try:
        final_video_path = video_composer.create_slideshow_with_subtitles(
            segments_data=segments_data,
            output_dir=str(test_dir)
        )

        print("\n" + "="*60)
        print("✓ TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\nFinal video created: {final_video_path}")
        print("\nWhat to check in the video:")
        print("  1. Subtitles sync: Should match the 1.2x sped-up audio")
        print("  2. Title visibility: Larger font (80), taller box (220px), more top padding")
        print("  3. Title position: Should be clearly visible on mobile")
        print("\nExpected total duration: ~18 seconds (22s / 1.2 speed)")
        print(f"  - Original total: {sum(s['audio_duration'] for s in segments_data)}s")
        print(f"  - Sped up (1.2x): {sum(s['audio_duration'] for s in segments_data) / 1.2:.1f}s")
        print("\n" + "="*60 + "\n")

        # Get actual video duration
        result = subprocess.run([
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            final_video_path
        ], capture_output=True, text=True, check=True)

        actual_duration = float(result.stdout.strip())
        print(f"Actual video duration: {actual_duration:.1f}s")
        print("\nTo view the test video, run:")
        print(f"  open {final_video_path}")
        print()

    except Exception as e:
        print("\n" + "="*60)
        print("✗ TEST FAILED!")
        print("="*60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        print()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
