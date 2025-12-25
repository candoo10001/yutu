"""
Main pipeline orchestrator for video generation.
"""
import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import structlog

from .config import Config
from .gemini_news_fetcher import GeminiNewsFetcher
from .gemini_script_generator import GeminiScriptGenerator
from .script_segmenter import ScriptSegmenter
from .segment_image_prompt_generator import SegmentImagePromptGenerator
from .title_generator import TitleGenerator
from .image_generator import ImageGenerator
from .audio_generator import AudioGenerator
from .video_composer import VideoComposer
from .media_matcher import MediaMatcher
from .utils.error_handler import VideoGenerationError, get_error_category
from .utils.logger import setup_logger, log_error


@dataclass
class VideoResult:
    """Result of generating one video."""
    success: bool
    article_index: int
    article_title: str
    final_video_path: Optional[str] = None
    metadata_path: Optional[str] = None
    error: Optional[str] = None
    steps_completed: list = None

    def __post_init__(self):
        if self.steps_completed is None:
            self.steps_completed = []


@dataclass
class PipelineResult:
    """Result of a pipeline execution."""
    success: bool
    videos: list = None  # List of VideoResult
    error: Optional[str] = None
    error_category: Optional[str] = None
    execution_time_seconds: float = 0
    news_articles_count: int = 0

    def __post_init__(self):
        if self.videos is None:
            self.videos = []


class VideoPipeline:
    """Orchestrates the entire video generation pipeline."""

    def __init__(self, config: Config):
        """
        Initialize the Video Pipeline.

        Args:
            config: Configuration instance
        """
        self.config = config

        # Setup logger
        self.logger = setup_logger(
            log_level=config.log_level,
            log_dir=config.log_dir,
            log_file="pipeline.log"
        )

        # Initialize components
        self.news_fetcher = GeminiNewsFetcher(config, self.logger)
        self.script_generator = GeminiScriptGenerator(config, self.logger)
        self.script_segmenter = ScriptSegmenter(config, self.logger)
        self.image_prompt_generator = SegmentImagePromptGenerator(config, self.logger)
        self.title_generator = TitleGenerator(config, self.logger)
        self.image_generator = ImageGenerator(config, self.logger)
        self.audio_generator = AudioGenerator(config, self.logger)
        self.video_composer = VideoComposer(config, self.logger)
        self.media_matcher = MediaMatcher(media_dir="predefined_media", logger=self.logger)

        self.logger.info("pipeline_initialized", config=str(config))


    def run(self, keyword: Optional[str] = None) -> PipelineResult:
        """
        Run the complete YouTube Shorts generation pipeline.
        Generates one video per news article.

        Args:
            keyword: Optional custom keyword for topic search (e.g., "Tesla", "금리인상")
                    If not provided, randomly selects from predefined media keywords

        Returns:
            PipelineResult with execution details
        """
        start_time = time.time()
        video_results = []

        # If no keyword provided, randomly select from business/finance/crypto/tech keywords
        if not keyword:
            import random
            # Priority keywords in business/finance/crypto/technology that typically have good news coverage
            # Ordered by likelihood of having recent news
            priority_keywords = [
                'Bitcoin', 'cryptocurrency', 'stock market', 'AI', 'Tesla',
                'Apple', 'economy', 'inflation', 'Fed', 'Ethereum',
                'tech', 'startup', 'electric vehicle', 'Nvidia', 'Samsung'
            ]
            keyword = random.choice(priority_keywords)
            self.logger.info(
                "auto_selected_keyword",
                keyword=keyword,
                reason="no_keyword_provided_using_business_finance_crypto_tech_keywords"
            )

        self.logger.info("pipeline_started", mode="YouTube Shorts Generation (Keyword)", keyword=keyword)

        try:
            # Step 1: Fetch top business news using Gemini with Google Search
            self.logger.info("step_1_fetch_news_with_keyword", keyword=keyword)
            news_articles = self.news_fetcher.fetch_top_business_news(keyword=keyword)

            # If no articles found with keyword, try fallback keywords (business/finance/crypto/tech)
            if not news_articles and keyword:
                self.logger.warning(
                    "no_articles_for_keyword",
                    keyword=keyword,
                    action="trying_fallback_keywords"
                )
                fallback_keywords = ['Bitcoin', 'cryptocurrency', 'stock market', 'AI', 'economy', 'Tesla']
                for fallback_keyword in fallback_keywords:
                    if fallback_keyword == keyword:
                        continue  # Skip the one we already tried
                    self.logger.info("trying_fallback_keyword", keyword=fallback_keyword)
                    news_articles = self.news_fetcher.fetch_top_business_news(keyword=fallback_keyword)
                    if news_articles:
                        self.logger.info("fallback_keyword_success", keyword=fallback_keyword)
                        keyword = fallback_keyword  # Update keyword for logging
                        break

            # If still no articles, try fetching top headlines without keyword
            if not news_articles:
                self.logger.warning("no_articles_with_keywords", action="fetching_top_headlines")
                news_articles = self.news_fetcher.fetch_top_business_news(keyword=None)

            if not news_articles:
                raise VideoGenerationError("No news articles found")

            self.logger.info("step_1_completed", article_count=len(news_articles))

            # Step 2: Process the top news article
            top_article = news_articles[0]
            self.logger.info(
                "processing_top_article",
                article_title=top_article.title
            )

            video_result = self._process_single_article(top_article, 1)
            video_results.append(video_result)

            if video_result.success:
                self.logger.info(
                    "top_article_video_completed",
                    video_path=video_result.final_video_path
                )
            else:
                self.logger.warning(
                    "top_article_video_failed",
                    error=video_result.error
                )

            # Calculate execution time
            execution_time = time.time() - start_time

            # Check if at least one video was generated successfully
            successful_videos = [v for v in video_results if v.success]
            overall_success = len(successful_videos) > 0

            self.logger.info(
                "pipeline_completed",
                execution_time_seconds=round(execution_time, 2),
                total_articles=len(news_articles),
                successful_videos=len(successful_videos),
                failed_videos=len(video_results) - len(successful_videos)
            )

            return PipelineResult(
                success=overall_success,
                videos=video_results,
                execution_time_seconds=execution_time,
                news_articles_count=len(news_articles)
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_category = get_error_category(e)

            log_error(self.logger, e, "pipeline.run")

            self.logger.error(
                "pipeline_failed",
                error=str(e),
                error_category=error_category,
                execution_time_seconds=round(execution_time, 2)
            )

            return PipelineResult(
                success=False,
                error=str(e),
                error_category=error_category,
                execution_time_seconds=execution_time,
                videos=video_results
            )

    def _process_single_article(self, article, article_index: int) -> VideoResult:
        """
        Process a single news article and generate a video for it.

        Args:
            article: News article to process
            article_index: Index of the article (for logging/naming)

        Returns:
            VideoResult with processing details
        """
        steps_completed = []

        try:
            # Step 2: Generate Korean narration script using Gemini with Google Search
            # Gemini searches Korean sources and generates natural Korean script directly
            self.logger.info("generating_korean_script_with_gemini", article_index=article_index)
            target_video_duration = self.config.video_duration
            korean_script = self.script_generator.generate_korean_script(
                [article],
                target_duration=target_video_duration
            )

            if not korean_script:
                raise VideoGenerationError("Script generation failed")

            steps_completed.append("generate_script")

            # Step 3: Segment script into timed chunks
            self.logger.info("segmenting_script", article_index=article_index)
            script_segments = self.script_segmenter.segment_script(korean_script)

            if not script_segments:
                raise VideoGenerationError("Script segmentation failed")

            steps_completed.append("segment_script")

            # Step 4: Generate content for each segment (images and audio)
            self.logger.info("generating_segment_content", article_index=article_index)
            segments_data = []

            # Create context summary for better image generation
            context_summary = f"Business news about: {article.title}"

            # Track used media files (videos) to prevent duplicates in the same video
            used_media_paths = set()

            for segment in script_segments:
                # Generate catchy title for this segment
                segment_title = self.title_generator.generate_title(
                    segment,
                    context=context_summary
                )

                if not segment_title:
                    raise VideoGenerationError(f"Title generation failed for segment {segment.segment_number}")

                # Generate image prompt for this segment
                image_prompt = self.image_prompt_generator.generate_image_prompt(
                    segment,
                    context=context_summary
                )

                if not image_prompt:
                    raise VideoGenerationError(f"Image prompt generation failed for segment {segment.segment_number}")

                # Try to find pre-defined media first (excluding already-used videos)
                image_path = self.media_matcher.find_matching_media(
                    text=segment.text,
                    title=segment_title,
                    used_media=used_media_paths
                )

                # If no pre-defined media found, generate new image
                if not image_path:
                    self.logger.info(
                        "generating_new_image",
                        segment_number=segment.segment_number,
                        reason="no_predefined_media_match"
                    )
                    try:
                        image_path = self.image_generator.generate_image(
                            prompt=image_prompt,
                            output_dir=self.config.output_dir,
                            aspect_ratio=self.config.video_aspect_ratio
                        )
                    except VideoGenerationError as e:
                        # If image generation fails with NO_IMAGE, try to use a generic fallback image
                        if "NO_IMAGE" in str(e):
                            self.logger.warning(
                                "image_generation_failed_no_image",
                                segment_number=segment.segment_number,
                                error=str(e),
                                action="retrying_with_simplified_prompt"
                            )
                            # Try once more with a simplified prompt
                            simplified_prompt = f"A professional business-related image representing: {segment_title}"
                            try:
                                image_path = self.image_generator.generate_image(
                                    prompt=simplified_prompt,
                                    output_dir=self.config.output_dir,
                                    aspect_ratio=self.config.video_aspect_ratio
                                )
                                self.logger.info(
                                    "image_generation_retry_success",
                                    segment_number=segment.segment_number
                                )
                            except VideoGenerationError:
                                # If retry also fails, re-raise the original error
                                self.logger.error(
                                    "image_generation_retry_failed",
                                    segment_number=segment.segment_number,
                                    original_error=str(e)
                                )
                                raise VideoGenerationError(
                                    f"Image generation failed after retry with simplified prompt for segment {segment.segment_number}. "
                                    f"Original error: {str(e)}. "
                                    f"Consider adding predefined media for this topic."
                                )
                        else:
                            # For other errors, just re-raise
                            raise
                else:
                    self.logger.info(
                        "using_predefined_media",
                        segment_number=segment.segment_number,
                        media_path=image_path
                    )
                    # Track used video files (not images, as images can be reused)
                    media_path_obj = Path(image_path).resolve()
                    if media_path_obj.suffix.lower() in ['.mp4', '.mov', '.avi']:
                        used_media_paths.add(str(media_path_obj))
                        self.logger.debug(
                            "tracking_used_video",
                            video_path=str(media_path_obj),
                            total_used=len(used_media_paths)
                        )

                if not image_path or not Path(image_path).exists():
                    raise VideoGenerationError(f"Image/media acquisition failed for segment {segment.segment_number}")

                # Generate audio for this segment
                audio_path, audio_duration = self.audio_generator.generate_segment_audio(
                    script_text=segment.text,
                    segment_number=segment.segment_number,
                    output_dir=self.config.output_dir
                )

                if not audio_path or not Path(audio_path).exists():
                    raise VideoGenerationError(f"Audio generation failed for segment {segment.segment_number}")

                # Store segment data
                segments_data.append({
                    'segment_number': segment.segment_number,
                    'text': segment.text,
                    'title': segment_title,
                    'image_path': image_path,
                    'audio_path': audio_path,
                    'audio_duration': audio_duration,
                    'image_prompt': image_prompt
                })

            steps_completed.append("generate_segment_content")

            # Step 5: Create slideshow video with subtitles
            self.logger.info("creating_slideshow", article_index=article_index)
            final_video_path = self.video_composer.create_slideshow_with_subtitles(
                segments_data=segments_data,
                output_dir=self.config.output_dir
            )

            if not final_video_path or not Path(final_video_path).exists():
                raise VideoGenerationError("Slideshow creation failed")

            steps_completed.append("create_slideshow")

            # Step 6: Generate Korean title for YouTube
            self.logger.info("generating_korean_title", article_index=article_index)
            korean_title = self._generate_korean_title(korean_script, article)
            if not korean_title:
                # Fallback: extract from script
                korean_title = self._extract_title_from_script(korean_script)

            # Step 7: Save metadata
            self.logger.info("saving_metadata", article_index=article_index)
            metadata = self._create_metadata_single_article(
                article=article,
                korean_script=korean_script,
                script_segments=script_segments,
                segments_data=segments_data,
                final_video_path=final_video_path,
                korean_title=korean_title
            )

            metadata_path = self._save_metadata(metadata)
            steps_completed.append("save_metadata")

            return VideoResult(
                success=True,
                article_index=article_index,
                article_title=article.title,
                final_video_path=final_video_path,
                metadata_path=metadata_path,
                steps_completed=steps_completed
            )

        except Exception as e:
            log_error(self.logger, e, f"pipeline._process_single_article (article {article_index})")

            return VideoResult(
                success=False,
                article_index=article_index,
                article_title=article.title,
                error=str(e),
                steps_completed=steps_completed
            )

    def _generate_korean_title(self, korean_script: str, article) -> str:
        """
        Generate a Korean title for YouTube from the Korean script using Gemini API.

        Args:
            korean_script: Korean narration script
            article: News article object

        Returns:
            Korean title string
        """
        try:
            from .gemini_client import GeminiClient
            
            # Create prompt for title generation
            prompt = f"""Create a short, catchy Korean title (3-8 words) for a YouTube Shorts video based on this Korean news script:

{korean_script[:500]}

Requirements:
1. Title must be in Korean
2. Short and catchy (3-8 words)
3. Summarizes the main news topic
4. Suitable for YouTube Shorts
5. No hashtags or emojis

Output ONLY the title, nothing else. No quotes, no explanations."""

            gemini_client = GeminiClient(self.config, self.logger)
            title = gemini_client.generate_text(prompt, "generate_korean_title")
            
            # Clean up title
            title = title.strip().strip('"').strip("'").strip()
            return title[:60]  # Limit length
            
        except Exception as e:
            self.logger.warning("korean_title_generation_failed", error=str(e))
            return None
    
    def _extract_title_from_script(self, korean_script: str) -> str:
        """
        Extract a title from Korean script as fallback.
        
        Args:
            korean_script: Korean narration script
            
        Returns:
            Extracted title string
        """
        if not korean_script:
            return "오늘의 뉴스"
        
        # Remove common greetings
        text = korean_script.replace('안녕하세요, ', '').replace('안녕하세요 ', '')
        text = text.replace('오늘의 ', '').replace('진스 뉴스 소식입니다.', '').replace('뉴스 소식입니다.', '')
        text = text.strip()
        
        # Take first sentence or first 40 characters
        if '\n\n' in text:
            text = text.split('\n\n')[0]
        
        if '。' in text:
            title = text.split('。')[0].strip()
        elif '.' in text:
            title = text.split('.')[0].strip()
        else:
            title = text[:40].strip()
        
        if not title or len(title) < 5:
            return "오늘의 뉴스"
        
        return title[:60]

    def _create_metadata_single_article(
        self,
        article,
        korean_script: str,
        script_segments: list,
        segments_data: list,
        final_video_path: str,
        korean_title: str = None
    ) -> dict:
        """
        Create metadata for a single article video.

        Returns:
            Metadata dictionary
        """
        return {
            "generated_at": datetime.now().isoformat(),
            "config": {
                "news_category": self.config.news_category,
                "news_country": self.config.news_country,
                "video_duration": self.config.video_duration,
                "segment_duration": self.config.segment_duration,
                "video_aspect_ratio": self.config.video_aspect_ratio,
                "video_resolution": self.config.video_resolution,
                "enable_subtitles": self.config.enable_subtitles,
                "subtitle_font_size": self.config.subtitle_font_size,
                "background_music_volume": self.config.background_music_volume,
                "claude_model": self.config.claude_model,
                "video_generator": "Image Slideshow with Gemini 2.5 Flash Image",
                "audio_generator": "ElevenLabs"
            },
            "news_article": {
                "title": article.title,
                "description": article.description,
                "source": article.source,
                "published_at": article.published_at.isoformat()
            },
            "korean_script": korean_script,
            "segments": [
                {
                    "segment_number": seg['segment_number'],
                    "text": seg['text'],
                    "audio_duration": seg['audio_duration'],
                    "image_prompt": seg['image_prompt']
                }
                for seg in segments_data
            ],
            "final_video_path": final_video_path,
            "title": korean_title or "오늘의 뉴스",  # Korean title for YouTube
            "description": korean_script[:500] if korean_script else "",  # Korean description
            "generation_method": "Gemini native Korean script generation with Google Search + Imagen + ElevenLabs audio + subtitles + background music"
        }

    def _save_metadata(self, metadata: dict) -> str:
        """
        Save metadata to a JSON file.

        Args:
            metadata: Metadata dictionary

        Returns:
            Path to the metadata file
        """
        output_path = Path(self.config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        metadata_file = output_path / f"metadata_{int(time.time())}.json"

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        return str(metadata_file)
