"""
Test Gemini's native Korean script generation vs Claude's translation approach.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.gemini_news_fetcher import GeminiNewsFetcher
from src.gemini_script_generator import GeminiScriptGenerator
from src.script_generator import ScriptGenerator
from src.context_enricher import ContextEnricher


def main():
    print("Comparing Korean Script Generation Methods")
    print("=" * 70)
    print()

    try:
        # Load config
        config = Config.from_env()
        print("✓ Config loaded")
        print()

        # Fetch news
        print("Step 1: Fetching news...")
        print("-" * 70)
        news_fetcher = GeminiNewsFetcher(config)
        articles = news_fetcher.fetch_top_business_news(keyword="Tesla")

        if not articles:
            print("✗ No articles found")
            return 1

        article = articles[0]
        print(f"✓ Article: {article.title[:60]}...")
        print()

        # Method 1: Gemini generates Korean directly (NEW)
        print("Method 1: Gemini generates Korean directly (asking in Korean)")
        print("-" * 70)
        gemini_generator = GeminiScriptGenerator(config)
        gemini_script = gemini_generator.generate_korean_script([article], target_duration=60)

        print("✓ Gemini Korean Script:")
        print()
        print(gemini_script)
        print()
        print(f"  Length: {len(gemini_script)} chars, {len(gemini_script.split())} words")
        korean_chars_gemini = sum(1 for c in gemini_script if '\uac00' <= c <= '\ud7a3')
        print(f"  Korean ratio: {korean_chars_gemini / len(gemini_script) * 100:.1f}%")
        print()

        # Method 2: Claude generates Korean from English (OLD)
        print("Method 2: Claude generates Korean from English (current method)")
        print("-" * 70)
        context_enricher = ContextEnricher(config)
        enriched_context = context_enricher.enrich_article_context(article)

        claude_generator = ScriptGenerator(config)
        claude_script = claude_generator.generate_korean_script(
            [article],
            target_duration=60,
            enriched_context=enriched_context
        )

        print("✓ Claude Korean Script:")
        print()
        print(claude_script)
        print()
        print(f"  Length: {len(claude_script)} chars, {len(claude_script.split())} words")
        korean_chars_claude = sum(1 for c in claude_script if '\uac00' <= c <= '\ud7a3')
        print(f"  Korean ratio: {korean_chars_claude / len(claude_script) * 100:.1f}%")
        print()

        # Comparison
        print("=" * 70)
        print("COMPARISON")
        print("=" * 70)
        print()
        print("Gemini (Native Korean):")
        print(f"  - Searches Korean sources directly")
        print(f"  - Generates natural Korean script")
        print(f"  - Single API call to Gemini")
        print(f"  - Cost: Lower (Gemini pricing)")
        print()
        print("Claude (English → Korean):")
        print(f"  - Works with English sources")
        print(f"  - Translates/generates Korean from English")
        print(f"  - Multiple API calls (Gemini enrichment + Claude)")
        print(f"  - Cost: Higher (Gemini + Claude)")
        print()
        print("Recommendation: Use Gemini for native Korean quality!")
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
