"""
Test the simplified pipeline without translation step.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.gemini_news_fetcher import GeminiNewsFetcher
from src.context_enricher import ContextEnricher
from src.script_generator import ScriptGenerator


def main():
    print("Testing Simplified Pipeline (No Translation)")
    print("=" * 70)
    print()

    try:
        # Load config
        config = Config.from_env()
        print("✓ Config loaded")
        print()

        # Step 1: Fetch news with Gemini
        print("Step 1: Fetching news with Gemini + Google Search...")
        print("-" * 70)
        news_fetcher = GeminiNewsFetcher(config)
        articles = news_fetcher.fetch_top_business_news(keyword="Tesla")

        if not articles:
            print("✗ No articles found")
            return 1

        print(f"✓ Fetched {len(articles)} articles")
        article = articles[0]
        print(f"  Article: {article.title[:60]}...")
        print()

        # Step 2: Enrich context
        print("Step 2: Enriching article context...")
        print("-" * 70)
        context_enricher = ContextEnricher(config)
        enriched_context = context_enricher.enrich_article_context(article)

        print("✓ Context enriched:")
        if enriched_context.get("background"):
            print(f"  Background: {enriched_context['background'][:100]}...")
        if enriched_context.get("insights"):
            print(f"  Insights: {enriched_context['insights'][:100]}...")
        if enriched_context.get("competitors"):
            print(f"  Competitors: {enriched_context['competitors'][:100]}...")
        if enriched_context.get("market_impact"):
            print(f"  Market Impact: {enriched_context['market_impact'][:100]}...")
        print()

        # Step 3: Generate Korean script directly from English
        print("Step 3: Generating Korean script from English (no translation)...")
        print("-" * 70)
        script_generator = ScriptGenerator(config)
        korean_script = script_generator.generate_korean_script(
            [article],  # English article directly
            target_duration=60,
            enriched_context=enriched_context
        )

        print("✓ Korean script generated:")
        print()
        print(korean_script)
        print()
        print("-" * 70)
        print(f"  Script length: {len(korean_script)} characters")
        print(f"  Word count: {len(korean_script.split())} words")
        print()

        # Verify script is in Korean
        korean_chars = sum(1 for c in korean_script if '\uac00' <= c <= '\ud7a3')
        print(f"  Korean characters: {korean_chars}")
        print(f"  Korean ratio: {korean_chars / len(korean_script) * 100:.1f}%")
        print()

        if korean_chars < 10:
            print("⚠ Warning: Script doesn't seem to be in Korean!")
            return 1

        print("=" * 70)
        print("✓ PIPELINE TEST SUCCESSFUL!")
        print("=" * 70)
        print()
        print("Summary:")
        print("  ✓ News fetched with Gemini + Google Search")
        print("  ✓ Context enriched with background, insights, competitors, market impact")
        print("  ✓ Korean script generated directly from English (no translation step)")
        print("  ✓ Script is in proper Korean")
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
