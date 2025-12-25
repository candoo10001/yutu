"""
Main entry point for the daily Korean news video generator.
"""
import argparse
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.pipeline import VideoPipeline
from src.utils.error_handler import ConfigurationError


def main():
    """Main entry point for the application."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Korean Business News Video Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Generate video from hottest topic
  python main.py --keyword Tesla    # Generate video about Tesla
  python main.py --keyword 금리인상   # Generate video about interest rate hikes
  python main.py --keyword 암호화폐   # Generate video about cryptocurrency
        """
    )
    parser.add_argument(
        '--keyword',
        type=str,
        help='Custom keyword for topic search (e.g., "Tesla", "Nvidia", "금리인상", "암호화폐")'
    )
    args = parser.parse_args()

    exit_code = 0

    try:
        print("=" * 60)
        print("Daily Korean News Video Generator")
        print("=" * 60)
        print()

        if args.keyword:
            print(f"Custom keyword: {args.keyword}")
            print()

        # Load configuration
        print("Loading configuration...")
        try:
            config = Config.from_env()
            config.validate()
            print("✓ Configuration loaded successfully")
            print()
        except ConfigurationError as e:
            print(f"✗ Configuration error: {e}")
            print()
            print("Please check your .env file and ensure all required")
            print("environment variables are set correctly.")
            return 1

        # Initialize and run pipeline
        print("Initializing video generation pipeline...")
        pipeline = VideoPipeline(config)
        print("✓ Pipeline initialized")
        print()

        print("Running pipeline (this may take several minutes)...")
        print("-" * 60)
        result = pipeline.run(keyword=args.keyword)
        print("-" * 60)
        print()

        # Display results
        if result.success:
            print("=" * 60)
            print("✓ SUCCESS - Videos generated successfully!")
            print("=" * 60)
            print()
            print(f"News articles processed: {result.news_articles_count}")
            print(f"Successful videos: {len([v for v in result.videos if v.success])}")
            print(f"Failed videos: {len([v for v in result.videos if not v.success])}")
            print(f"Execution time: {result.execution_time_seconds:.1f} seconds")
            print()

            # Display successful videos
            successful_videos = [v for v in result.videos if v.success]
            if successful_videos:
                print("Generated Videos:")
                print("-" * 60)
                for video in successful_videos:
                    print(f"\n{video.article_index}. {video.article_title[:60]}...")
                    print(f"   Video: {video.final_video_path}")
                    print(f"   Metadata: {video.metadata_path}")

            # Display failed videos
            failed_videos = [v for v in result.videos if not v.success]
            if failed_videos:
                print()
                print("Failed Videos:")
                print("-" * 60)
                for video in failed_videos:
                    print(f"\n{video.article_index}. {video.article_title[:60]}...")
                    print(f"   Error: {video.error}")

            print()
            print("The videos are ready to download from GitHub Actions artifacts!")
            exit_code = 0
        else:
            print("=" * 60)
            print("✗ FAILED - Video generation failed")
            print("=" * 60)
            print()
            print(f"Error: {result.error}")
            print(f"Error category: {result.error_category}")
            print(f"Execution time: {result.execution_time_seconds:.1f} seconds")
            print()
            print("Check the logs for more details.")

            # Set appropriate exit code based on error category
            error_codes = {
                "configuration": 1,
                "news_api": 2,
                "claude_api": 3,
                "translation": 3,
                "script_generation": 3,
                "prompt_generation": 3,
                "kling_api": 4,
                "elevenlabs_api": 5,
                "video_composition": 6,
                "unknown": 7
            }
            exit_code = error_codes.get(result.error_category, 7)

    except KeyboardInterrupt:
        print()
        print("✗ Pipeline interrupted by user")
        exit_code = 130

    except Exception as e:
        print()
        print("=" * 60)
        print("✗ UNEXPECTED ERROR")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        print("This is an unexpected error. Please check the logs for details.")
        exit_code = 255

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
