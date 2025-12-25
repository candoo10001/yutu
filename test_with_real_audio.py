#!/usr/bin/env python3
"""
Test script using real audio and images from a previous generation.
Tests subtitle sync with actual Korean TTS audio (not silent).
"""
import json
from pathlib import Path
import structlog

from src.config import Config
from src.video_composer import VideoComposer


def main():
    """Run the test video composition with real audio."""
    print("\n" + "="*60)
    print("TEST SCRIPT: Real Audio & Subtitle Sync")
    print("="*60)
    print("\nTesting with real Korean TTS audio:")
    print("  1. Subtitle sync with 1.2x audio speed")
    print("  2. Enhanced title visibility")
    print("\n" + "="*60 + "\n")

    # Load metadata from most recent generation
    metadata_file = Path("output/metadata_1766636849.json")

    if not metadata_file.exists():
        print(f"❌ Metadata file not found: {metadata_file}")
        return 1

    with open(metadata_file) as f:
        metadata = json.load(f)

    print(f"✓ Loaded metadata from: {metadata_file}")
    print(f"  Article: {metadata['korean_article']['title']}")
    print(f"  Segments: {len(metadata['segments'])}")
    print()

    # Map audio files to segments
    audio_files = [
        "output/audio_segment_1_1766636681.mp3",
        "output/audio_segment_2_1766636708.mp3",
        "output/audio_segment_3_1766636734.mp3",
        "output/audio_segment_4_1766636762.mp3",
        "output/audio_segment_5_1766636787.mp3"
    ]

    # Map image files to segments
    image_files = [
        "output/image_1766636681.png",
        "output/image_1766636708.png",
        "output/image_1766636734.png",
        "output/image_1766636762.png",
        "output/image_1766636787.png"
    ]

    # Generate test titles for each segment
    segment_titles = [
        "버지니아 공대: 선수 복귀 소식",
        "2026년 팀 복귀 계획 발표",
        "팬들의 기대감 상승",
        "새로운 전기 마련 기대",
        "오늘의 진스 뉴스"
    ]

    # Build segments data
    segments_data = []

    print("Verifying files...")
    print("-" * 60)

    for i, segment in enumerate(metadata['segments']):
        audio_path = audio_files[i]
        image_path = image_files[i]

        if not Path(audio_path).exists():
            print(f"❌ Audio file missing: {audio_path}")
            return 1

        if not Path(image_path).exists():
            print(f"❌ Image file missing: {image_path}")
            return 1

        print(f"✓ Segment {i+1}: {segment_titles[i]}")
        print(f"  Audio: {Path(audio_path).name} ({segment['audio_duration']:.2f}s)")
        print(f"  Image: {Path(image_path).name}")

        segments_data.append({
            "image_path": image_path,
            "audio_path": audio_path,
            "audio_duration": segment['audio_duration'],
            "text": segment['text'],
            "title": segment_titles[i],
            "segment_number": segment['segment_number']
        })

    print("\n" + "="*60)
    print(f"Composing test video with {len(segments_data)} segments...")
    print("-" * 60)

    # Initialize config and video composer
    config = Config(
        news_api_key="dummy_key",
        claude_api_key="dummy_key",
        google_api_key="dummy_key",
        elevenlabs_api_key="dummy_key"
    )
    logger = structlog.get_logger()

    # Override subtitle settings
    config.enable_subtitles = True
    config.subtitle_position = "middle"

    video_composer = VideoComposer(config, logger)
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)

    # Create the video
    try:
        final_video_path = video_composer.create_slideshow_with_subtitles(
            segments_data=segments_data,
            output_dir=str(test_dir)
        )

        print("\n" + "="*60)
        print("✓ TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\nFinal test video: {final_video_path}")
        print("\nThis video uses REAL Korean TTS audio!")
        print("\nWhat to check:")
        print("  1. ✅ Subtitle timing: Matches the actual Korean speech")
        print("  2. ✅ 1.2x speed: Audio is sped up, subtitles should match")
        print("  3. ✅ Title visibility: Large font (80px), more padding (~100px)")
        print("  4. ✅ Korean text: Both titles and subtitles render correctly")
        print("\nOriginal video for comparison:")
        print(f"  {metadata['final_video_path']}")
        print("\nExpected duration:")
        total_duration = sum(s['audio_duration'] for s in metadata['segments'])
        print(f"  - Original audio total: {total_duration:.1f}s")
        print(f"  - With 1.2x speed: {total_duration / 1.2:.1f}s")
        print("\nTo view the test video:")
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
