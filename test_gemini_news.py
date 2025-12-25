"""
Test script for Gemini news fetcher.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.gemini_news_fetcher import GeminiNewsFetcher

def main():
    print("Testing Gemini News Fetcher...")
    print("=" * 60)

    try:
        # Load config
        config = Config.from_env()
        print(f"✓ Config loaded")
        print(f"  Google API Key: {'✓ Set' if config.google_api_key else '✗ Missing'}")
        print()

        # Initialize news fetcher
        news_fetcher = GeminiNewsFetcher(config)
        print("✓ GeminiNewsFetcher initialized")
        print()

        # Test 1: Fetch news with keyword
        print("Test 1: Fetching news about 'Tesla'...")
        print("-" * 60)
        articles = news_fetcher.fetch_top_business_news(keyword="Tesla")

        print(f"✓ Fetched {len(articles)} articles")
        print()

        if articles:
            print("First article:")
            article = articles[0]
            print(f"  Title: {article.title}")
            print(f"  Source: {article.source}")
            print(f"  Published: {article.published_at}")
            print(f"  Description: {article.description[:200]}...")
            print(f"  URL: {article.url}")
        else:
            print("⚠ No articles found")

        print()
        print("=" * 60)
        print("✓ Test completed successfully!")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
