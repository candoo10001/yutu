#!/usr/bin/env python3
"""
Test script to verify subtitle font size is displaying correctly.
Creates a simple test video with subtitles to visually check font size.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import Config
from src.video_composer import VideoComposer
import structlog

def create_test_subtitle_file(output_dir: Path) -> Path:
    """Create a test SRT subtitle file with Korean text."""
    subtitle_file = output_dir / "test_subtitles.srt"
    
    # Test Korean text with various word lengths
    test_subtitles = """1
00:00:00,000 --> 00:00:03,000
안녕하세요, 오늘의 비즈니스
소식입니다.

2
00:00:03,000 --> 00:00:06,000
구글 TPU 사업이
눈에 띄게 성장하고 있습니다.

3
00:00:06,000 --> 00:00:09,000
테슬라 주가가 오르고
애플도 함께 상승했습니다.

4
00:00:09,000 --> 00:00:12,000
이번 주 주요 뉴스를
요약해드리겠습니다.
"""
    
    with open(subtitle_file, 'w', encoding='utf-8') as f:
        f.write(test_subtitles)
    
    return subtitle_file

def main():
    """Create a test video with subtitles to check font size."""
    print("Creating test video with subtitles to check font size...")
    
    # Load config
    try:
        config = Config.from_env()
        print(f"✓ Config loaded successfully")
        print(f"  Subtitle font size from config: {config.subtitle_font_size}px")
        
        # Check if env var overrides the default
        import os
        env_font_size = os.getenv("SUBTITLE_FONT_SIZE")
        if env_font_size:
            print(f"  NOTE: SUBTITLE_FONT_SIZE env var is set to: {env_font_size}px")
            print(f"  This will override the default in config.py")
    except Exception as e:
        print(f"Error loading config: {e}")
        print("Make sure you have a .env file with required API keys")
        return
    
    # Setup logger
    logger = structlog.get_logger()
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Create video composer
    composer = VideoComposer(config, logger)
    
    # Create a simple test video (solid color background)
    import subprocess
    import time
    
    timestamp = int(time.time())
    test_video = output_dir / f"test_video_{timestamp}.mp4"
    
    print(f"Creating test video: {test_video}")
    
    # Create a 5-second solid color video (1080x1920 for 9:16 aspect ratio)
    subprocess.run([
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'color=c=blue:size=1080x1920:duration=12',  # Blue background, 12 seconds
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        str(test_video)
    ], check=True, capture_output=True)
    
    print("Test video created")
    
    # Create test subtitle file
    subtitle_file = create_test_subtitle_file(output_dir)
    print(f"Test subtitle file created: {subtitle_file}")
    
    # Apply subtitles with current config settings
    print(f"Applying subtitles with font size: {config.subtitle_font_size}")
    print(f"Video resolution: {config.video_resolution}")
    print(f"Aspect ratio: {config.video_aspect_ratio}")
    
    final_video = output_dir / f"test_with_subtitles_{timestamp}.mp4"
    
    # Apply subtitles using the SAME method as actual video production
    # Use subtitles filter with ASS format (same as video_composer.py) for accurate testing
    print("Applying subtitles using 'subtitles' filter (same method as actual video production)...")
    
    font_size = config.subtitle_font_size
    
    print(f"\n{'='*60}")
    print(f"Font size to use: {font_size} pixels")
    print(f"  (Read from: config.subtitle_font_size = {config.subtitle_font_size})")
    print(f"  This matches the FontSize used in actual video production")
    print(f"{'='*60}\n")
    
    # Use the EXACT same subtitle style as video_composer.py
    subtitle_style = (
        f"FontSize={font_size},"
        f"PrimaryColour=&HFFFFFF,"
        f"BackColour=&H80000000,"
        f"BorderStyle=3,"
        f"Outline=2,"
        f"Shadow=1,"
        f"Alignment=2,"  # Center alignment
        f"MarginV=50,"
        f"MarginL=60,"
        f"MarginR=60,"
        f"PlayResX=1080,"
        f"PlayResY=1920,"
        f"WordWrap=1"
    )
    
    # Escape subtitle file path for ffmpeg
    subtitle_path_escaped = str(subtitle_file).replace(':', '\\:').replace('[', '\\[').replace(']', '\\]')
    subtitle_style_escaped = subtitle_style.replace(',', '\\,')
    
    # Create video with current font size using subtitles filter (same as production)
    print(f"Creating test video with FontSize={font_size} (PlayResY=1920)...")
    subprocess.run([
        'ffmpeg',
        '-i', str(test_video),
        '-vf', f"subtitles={subtitle_path_escaped}:force_style='{subtitle_style_escaped}'",
        '-t', '12',  # Duration of test video
        '-c:a', 'copy',
        '-y',  # Overwrite output file
        str(final_video)
    ], check=True, capture_output=True)
    
    # Also create comparison with larger font size
    large_font_test = output_dir / f"test_large_font_{timestamp}.mp4"
    large_font_size = 140  # Test with 140 for comparison
    
    large_subtitle_style = (
        f"FontSize={large_font_size},"
        f"PrimaryColour=&HFFFFFF,"
        f"BackColour=&H80000000,"
        f"BorderStyle=3,"
        f"Outline=2,"
        f"Shadow=1,"
        f"Alignment=2,"
        f"MarginV=50,"
        f"MarginL=60,"
        f"MarginR=60,"
        f"PlayResX=1080,"
        f"PlayResY=1920,"
        f"WordWrap=1"
    )
    large_style_escaped = large_subtitle_style.replace(',', '\\,')
    
    print(f"Creating comparison video with FontSize={large_font_size} (PlayResY=1920)...")
    subprocess.run([
        'ffmpeg',
        '-i', str(test_video),
        '-vf', f"subtitles={subtitle_path_escaped}:force_style='{large_style_escaped}'",
        '-t', '12',
        '-c:a', 'copy',
        '-y',
        str(large_font_test)
    ], check=True, capture_output=True)
    
    print(f"\n✅ Test videos created:")
    print(f"  1. Current font size ({font_size}px): {final_video}")
    print(f"  2. Large font size ({large_font_size}px) for comparison: {large_font_test}")
    print(f"\nFont size settings:")
    print(f"  - FontSize: {config.subtitle_font_size}")
    print(f"  - PlayResX: 1080")
    print(f"  - PlayResY: 1920")
    print(f"\nOpen the video file to visually check if the font size is appropriate.")
    print(f"If the font is too small, increase SUBTITLE_FONT_SIZE in .env or config.py")
    print(f"If the font is too large, decrease SUBTITLE_FONT_SIZE")

if __name__ == "__main__":
    main()

