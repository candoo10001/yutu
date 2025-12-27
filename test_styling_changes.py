"""
Quick test to verify the new grayish-black styling with gradient sky blue padding.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.gemini_news_fetcher import GeminiNewsFetcher
from src.gemini_script_generator import GeminiScriptGenerator
from src.pipeline import VideoPipeline


def main():
    print("=" * 70)
    print("Testing New Styling: Grayish-Black + Sky Blue Gradient")
    print("=" * 70)
    print()

    try:
        # Load config
        config = Config.from_env()
        print("✓ Config loaded")
        print()

        # Run pipeline with a quick test
        print("Generating test video with new styling...")
        print("Keyword: Tesla")
        print()

        pipeline = VideoPipeline(config)
        results = pipeline.run(keyword="Tesla")

        if results.get("successful_videos", 0) > 0:
            print()
            print("=" * 70)
            print("✓ SUCCESS - Test video generated!")
            print("=" * 70)
            print()
            print("Check the video to verify:")
            print("  1. Title has grayish-black background (not pure black)")
            print("  2. Title has gradient sky blue padding (top & bottom)")
            print("  3. Title box is taller (more vertical padding)")
            print("  4. Subtitles have grayish-black background")
            print("  5. Subtitles have better outline/shadow visibility")
            print()
            return 0
        else:
            print("✗ No videos generated")
            return 1

    except Exception as e:
        print()
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
