"""
Test video composition using existing metadata and media files.
This skips all API calls and just tests the video composition with styling.
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.video_composer import VideoComposer


def main():
    print("=" * 70)
    print("Testing Video Composition with Existing Metadata")
    print("=" * 70)
    print()

    try:
        # Load config
        config = Config.from_env()
        print("✓ Config loaded")

        # Find the most recent metadata file
        output_dir = Path("output")
        metadata_files = sorted(output_dir.glob("metadata_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

        if not metadata_files:
            print("✗ No metadata files found")
            return 1

        metadata_file = metadata_files[0]
        print(f"✓ Using metadata file: {metadata_file.name}")
        print()

        # Load metadata
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        segments = metadata.get('segments', [])
        if not segments:
            print("✗ No segments found in metadata")
            return 1

        print(f"✓ Found {len(segments)} segments")

        # Find corresponding audio and media files
        # The metadata was created with a timestamp, let's extract it
        timestamp = metadata_file.stem.split('_')[1]

        # Build segments_data for VideoComposer
        segments_data = []
        missing_files = []

        for seg in segments:
            seg_num = seg['segment_number']

            # Look for audio file
            audio_pattern = f"audio_segment_{seg_num}_*.mp3"
            audio_files = list(output_dir.glob(audio_pattern))

            if not audio_files:
                missing_files.append(f"Audio file: {audio_pattern}")
                continue

            # Use the most recent audio file for this segment
            audio_file = sorted(audio_files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

            # Look for image or use predefined media
            image_pattern = f"image_*.png"
            image_files = list(output_dir.glob(image_pattern))

            # If we have images, use the most recent one, otherwise we'll use predefined media
            if image_files:
                media_path = str(sorted(image_files, key=lambda p: p.stat().st_mtime, reverse=True)[0])
            else:
                # Use a predefined media file (stock market video as fallback)
                media_path = "predefined_media/stock-market/kling_20251225_Text_to_Video_economic_g_1728_0.mp4"

            segments_data.append({
                'segment_number': seg_num,
                'text': seg['text'],
                'title': f"테슬라 뉴스 {seg_num}",  # Generic title
                'audio_path': str(audio_file),
                'audio_duration': seg['audio_duration'],
                'image_path': media_path
            })

        if missing_files:
            print("⚠ Missing files:")
            for mf in missing_files:
                print(f"  - {mf}")
            print()

        if not segments_data:
            print("✗ No valid segments with audio files found")
            return 1

        print(f"✓ Prepared {len(segments_data)} segments for video composition")
        print()

        # Create VideoComposer and generate video
        print("Creating video with new styling...")
        print("  - Grayish-black backgrounds")
        print("  - Gradient sky blue padding")
        print("  - Fixed audio/video sync")
        print()

        video_composer = VideoComposer(config)
        final_video_path = video_composer.create_slideshow_with_subtitles(
            segments_data=segments_data,
            output_dir=output_dir
        )

        print()
        print("=" * 70)
        print("✓ SUCCESS - Video created!")
        print("=" * 70)
        print()
        print(f"Video path: {final_video_path}")

        # Get video duration
        import subprocess
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', str(final_video_path)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            duration = float(result.stdout.strip())
            print(f"Video duration: {duration:.2f} seconds")

            # Calculate expected duration based on audio
            total_audio = sum(seg['audio_duration'] for seg in segments_data)
            speed_factor = 1.2
            expected_duration = total_audio / speed_factor

            print(f"Expected duration (audio/1.2): {expected_duration:.2f} seconds")
            print(f"Difference: {abs(duration - expected_duration):.2f} seconds")

            if abs(duration - expected_duration) < 2.0:
                print("✓ Audio/video sync looks good!")
            else:
                print("⚠ Audio/video sync may need adjustment")

        print()
        return 0

    except Exception as e:
        print()
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
