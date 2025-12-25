"""
Script segmentation module for splitting scripts into timed segments.
"""
import re
from dataclasses import dataclass
from typing import List, Optional

import structlog

from .config import Config


@dataclass
class ScriptSegment:
    """Represents a single script segment with timing."""
    text: str
    segment_number: int
    estimated_duration: float  # in seconds
    word_count: int


class ScriptSegmenter:
    """Segments scripts into timed chunks for image-audio synchronization."""

    # Korean TTS speaks at approximately 4.5-5 words per second
    KOREAN_WORDS_PER_SECOND = 4.75

    def __init__(self, config: Config, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Script Segmenter.

        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or structlog.get_logger()
        self.target_segment_duration = config.segment_duration

    def segment_script(self, script: str) -> List[ScriptSegment]:
        """
        Split a script into timed segments based on target duration.

        Args:
            script: The full script text

        Returns:
            List of ScriptSegment objects

        """
        self.logger.info(
            "segmenting_script",
            script_length=len(script),
            target_duration=self.target_segment_duration
        )

        # Calculate target words per segment
        target_words_per_segment = int(self.target_segment_duration * self.KOREAN_WORDS_PER_SECOND)

        # Split by sentences (Korean uses . ! ? as sentence endings)
        sentences = self._split_into_sentences(script)

        self.logger.info(
            "script_split_into_sentences",
            sentence_count=len(sentences),
            target_words_per_segment=target_words_per_segment
        )

        # Group sentences into segments based on target word count
        segments = []
        current_segment_text = []
        current_word_count = 0
        segment_number = 1

        for sentence in sentences:
            sentence_words = len(sentence.split())

            # Check if adding this sentence would exceed target significantly
            # Allow some flexibility (±30%) for natural breaks
            if current_word_count > 0 and current_word_count + sentence_words > target_words_per_segment * 1.3:
                # Save current segment
                segment_text = ' '.join(current_segment_text).strip()
                estimated_duration = current_word_count / self.KOREAN_WORDS_PER_SECOND

                segments.append(ScriptSegment(
                    text=segment_text,
                    segment_number=segment_number,
                    estimated_duration=estimated_duration,
                    word_count=current_word_count
                ))

                # Start new segment
                current_segment_text = [sentence]
                current_word_count = sentence_words
                segment_number += 1
            else:
                # Add sentence to current segment
                current_segment_text.append(sentence)
                current_word_count += sentence_words

        # Add final segment if there's remaining text
        if current_segment_text:
            segment_text = ' '.join(current_segment_text).strip()
            estimated_duration = current_word_count / self.KOREAN_WORDS_PER_SECOND

            segments.append(ScriptSegment(
                text=segment_text,
                segment_number=segment_number,
                estimated_duration=estimated_duration,
                word_count=current_word_count
            ))

        # Log segment details
        self.logger.info(
            "script_segmented",
            num_segments=len(segments),
            segment_durations=[round(seg.estimated_duration, 1) for seg in segments],
            segment_word_counts=[seg.word_count for seg in segments]
        )

        for seg in segments:
            self.logger.debug(
                "segment_details",
                segment_number=seg.segment_number,
                text_preview=seg.text[:50] + "..." if len(seg.text) > 50 else seg.text,
                word_count=seg.word_count,
                estimated_duration=round(seg.estimated_duration, 1)
            )

        return segments

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Split by sentence endings (. ! ?)
        # Keep the punctuation with the sentence
        parts = re.split(r'([.!?])\s*', text)

        # Reconstruct sentences with their punctuation
        sentences = []
        for i in range(0, len(parts) - 1, 2):
            if i + 1 < len(parts):
                sentence = parts[i] + parts[i + 1]
                if sentence.strip():
                    sentences.append(sentence.strip())
            elif parts[i].strip():
                sentences.append(parts[i].strip())

        # Handle any remaining text
        if len(parts) % 2 == 1 and parts[-1].strip():
            sentences.append(parts[-1].strip())

        return [s for s in sentences if s]  # Filter empty strings
