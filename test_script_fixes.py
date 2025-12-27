"""
Test script generation fixes for AI preamble and number formatting.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.gemini_news_fetcher import GeminiNewsFetcher
from src.gemini_script_generator import GeminiScriptGenerator


def main():
    print("=" * 70)
    print("Testing Script Generation Fixes")
    print("=" * 70)
    print()

    try:
        # Load config
        config = Config.from_env()
        print("✓ Config loaded")
        print()

        # Fetch news
        print("Fetching Bitcoin news (likely to have large numbers)...")
        news_fetcher = GeminiNewsFetcher(config)
        articles = news_fetcher.fetch_top_business_news(keyword="Bitcoin")

        if not articles:
            print("✗ No articles found")
            return 1

        article = articles[0]
        print(f"✓ Article: {article.title[:60]}...")
        print()

        # Generate Korean script
        print("Generating Korean script...")
        script_generator = GeminiScriptGenerator(config)
        korean_script = script_generator.generate_korean_script([article], target_duration=60)

        print("=" * 70)
        print("GENERATED SCRIPT:")
        print("=" * 70)
        print()
        print(korean_script)
        print()
        print("=" * 70)
        print()

        # Check for issues
        print("Checking for issues:")
        print("-" * 70)

        issues_found = False

        # Check 1: AI preambles
        ai_preambles = ["알겠습니다", "다음은", "요청하신", "스크립트입니다", "네,", "좋습니다"]
        for preamble in ai_preambles:
            if preamble in korean_script[:50]:  # Check first 50 chars
                print(f"❌ Found AI preamble: '{preamble}' at start of script")
                issues_found = True

        if not issues_found:
            print("✓ No AI preambles found at start")

        # Check 2: Comma in numbers
        if "," in korean_script and any(char.isdigit() for char in korean_script):
            # Check if comma appears near digits
            for i, char in enumerate(korean_script):
                if char == "," and i > 0 and i < len(korean_script) - 1:
                    if korean_script[i-1].isdigit() or korean_script[i+1].isdigit():
                        print(f"⚠ Warning: Found comma near digits around position {i}")
                        context = korean_script[max(0,i-10):min(len(korean_script),i+10)]
                        print(f"  Context: ...{context}...")
                        issues_found = True

        # Check 3: Long decimal numbers (more than 2 decimal places)
        import re
        long_decimals = re.findall(r'\d+\.\d{3,}', korean_script)
        if long_decimals:
            print(f"⚠ Warning: Found long decimal numbers: {long_decimals}")
            print("  (These should be simplified for TTS)")
            issues_found = True

        if not issues_found:
            print("✓ No number formatting issues detected")

        print()
        print("=" * 70)
        if not issues_found:
            print("✓ ALL CHECKS PASSED!")
        else:
            print("⚠ Some issues found (see above)")
        print("=" * 70)
        print()

        return 0 if not issues_found else 1

    except Exception as e:
        print()
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
