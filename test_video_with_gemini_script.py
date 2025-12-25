"""
Test full video generation with Gemini's native Korean script.
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.gemini_news_fetcher import GeminiNewsFetcher
from src.gemini_script_generator import GeminiScriptGenerator
from src.script_segmenter import ScriptSegmenter
from src.segment_image_prompt_generator import SegmentImagePromptGenerator
from src.image_generator import ImageGenerator
from src.audio_generator import AudioGenerator
from src.video_composer import VideoComposer


def main():
    print("=" * 70)
    print("Testing Full Video Generation with Gemini Korean Script")
    print("=" * 70)
    print()

    try:
        # Load config
        config = Config.from_env()
        print("✓ Config loaded")
        print()

        # Step 1: Fetch news
        print("Step 1: Fetching news with Gemini...")
        print("-" * 70)
        news_fetcher = GeminiNewsFetcher(config)
        articles = news_fetcher.fetch_top_business_news(keyword="Tesla")

        if not articles:
            print("✗ No articles found")
            return 1

        article = articles[0]
        print(f"✓ Fetched article: {article.title[:60]}...")
        print()

        # Step 2: Generate Korean script with Gemini
        print("Step 2: Generating Korean script with Gemini (native Korean)...")
        print("-" * 70)
        script_generator = GeminiScriptGenerator(config)
        korean_script = script_generator.generate_korean_script([article], target_duration=60)

        print("✓ Korean script generated:")
        print()
        print(korean_script)
        print()
        print(f"  Length: {len(korean_script)} chars")
        print()

        # Step 3: Segment script
        print("Step 3: Segmenting script...")
        print("-" * 70)
        segmenter = ScriptSegmenter(config)
        script_segments = segmenter.segment_script(korean_script)
        print(f"✓ Created {len(script_segments)} segments")
        for i, seg in enumerate(script_segments, 1):
            print(f"  Segment {i}: {seg.text[:50]}...")
        print()

        # Step 4: Generate image prompts
        print("Step 4: Generating image prompts...")
        print("-" * 70)
        prompt_generator = SegmentImagePromptGenerator(config)
        context_summary = f"Business news about: {article.title}"

        segments_with_prompts = []
        for i, segment in enumerate(script_segments):
            image_prompt = prompt_generator.generate_image_prompt(
                segment=segment,
                context=context_summary
            )
            segments_with_prompts.append({
                'segment': segment,
                'image_prompt': image_prompt
            })
            print(f"  Segment {i+1} prompt: {image_prompt[:60]}...")

        print()

        # Step 5: Generate images
        print("Step 5: Generating images with Gemini Imagen...")
        print("-" * 70)
        image_generator = ImageGenerator(config)

        segments_data = []
        for i, item in enumerate(segments_with_prompts):
            segment = item['segment']
            prompt = item['image_prompt']

            print(f"  Generating image {i+1}/{len(segments_with_prompts)}...")

            try:
                image_path = image_generator.generate_image(
                    prompt=prompt,
                    aspect_ratio="9:16"
                )

                segments_data.append({
                    'segment': segment,
                    'image_path': image_path,
                    'duration': 4.0
                })

                print(f"    ✓ Image saved: {image_path}")

            except Exception as e:
                print(f"    ✗ Image generation failed: {e}")
                # Use a placeholder or skip
                continue

        print()

        if not segments_data:
            print("✗ No images generated, cannot create video")
            return 1

        # Step 6: Generate audio
        print("Step 6: Generating Korean audio with ElevenLabs...")
        print("-" * 70)
        audio_generator = AudioGenerator(config)

        audio_path = audio_generator.generate_korean_audio(korean_script)
        print(f"✓ Audio generated: {audio_path}")
        print()

        # Step 7: Compose video
        print("Step 7: Composing final video...")
        print("-" * 70)
        video_composer = VideoComposer(config)

        final_video_path = video_composer.create_slideshow_with_subtitles(
            segments_data=segments_data,
            output_dir="output"
        )

        print(f"✓ Video created: {final_video_path}")
        print()

        # Summary
        print("=" * 70)
        print("✓ TEST VIDEO GENERATION SUCCESSFUL!")
        print("=" * 70)
        print()
        print(f"Video file: {final_video_path}")
        print(f"Duration: ~60 seconds")
        print(f"Segments: {len(segments_data)}")
        print()
        print("Next steps:")
        print("  1. Watch the video and check Korean script quality")
        print("  2. Verify audio pronunciation is natural")
        print("  3. If good, update pipeline to use GeminiScriptGenerator")
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
