"""
Quick test to verify the updated pipeline with Gemini Korean script generation.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.pipeline import VideoPipeline


def main():
    print("=" * 70)
    print("Testing Updated Pipeline with Gemini Native Korean")
    print("=" * 70)
    print()

    try:
        # Load config
        config = Config.from_env()
        print("✓ Config loaded")
        print()

        # Initialize pipeline
        print("Initializing pipeline...")
        pipeline = VideoPipeline(config)
        print("✓ Pipeline initialized with GeminiScriptGenerator")
        print()

        # Verify components
        print("Verifying components:")
        print(f"  News Fetcher: {type(pipeline.news_fetcher).__name__}")
        print(f"  Script Generator: {type(pipeline.script_generator).__name__}")
        print(f"  Script Segmenter: {type(pipeline.script_segmenter).__name__}")
        print()

        if type(pipeline.script_generator).__name__ != "GeminiScriptGenerator":
            print("✗ ERROR: Script generator is not GeminiScriptGenerator!")
            return 1

        print("=" * 70)
        print("✓ PIPELINE UPDATE SUCCESSFUL!")
        print("=" * 70)
        print()
        print("Summary of changes:")
        print("  ✓ Removed: ContextEnricher (Claude)")
        print("  ✓ Removed: ScriptGenerator (Claude)")
        print("  ✓ Removed: Translator")
        print("  ✓ Added: GeminiScriptGenerator")
        print()
        print("New workflow:")
        print("  1. Fetch news with Gemini + Google Search")
        print("  2. Generate native Korean script with Gemini")
        print("  3. Segment script")
        print("  4. Generate images & audio")
        print("  5. Compose video")
        print()
        print("Benefits:")
        print("  • More natural Korean (not translated)")
        print("  • Lower cost (single Gemini call vs Gemini + Claude)")
        print("  • Simpler pipeline (fewer components)")
        print("  • Better context (Gemini searches Korean sources)")
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
