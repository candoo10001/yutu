#!/usr/bin/env python3
"""
Test script to demonstrate TTS vs Subtitle number formatting.
Shows how Korean number words (for TTS) are converted to numeric symbols (for subtitles).
"""
from src.video_composer import VideoComposer
from src.config import Config
import structlog

def main():
    print("\n" + "="*60)
    print("TTS vs Subtitle Number Format Test")
    print("="*60 + "\n")

    # Initialize video composer
    config = Config(
        news_api_key="dummy",
        claude_api_key="dummy",
        google_api_key="dummy",
        elevenlabs_api_key="dummy"
    )
    composer = VideoComposer(config, structlog.get_logger())

    # Test cases: TTS format -> Subtitle format
    test_cases = [
        ("테슬라 주가가 이점오 퍼센트 상승했습니다",
         "테슬라 주가가 2.5 % 상승했습니다"),

        ("애플의 시가총액이 삼조 달러를 돌파했습니다",
         "애플의 시가총액이 삼조 $를 돌파했습니다"),

        ("삼 분기 실적이 십억 원을 기록했습니다",
         "3분기 실적이 10억 ₩을 기록했습니다"),

        ("주가가 일점오 달러에서 이점오 달러로 상승",
         "주가가 1.5 $에서 2.5 $로 상승"),

        ("일 분기부터 사 분기까지 성장세",
         "1분기부터 4분기까지 성장세"),
    ]

    print("Testing TTS to Subtitle conversion:\n")
    print("-" * 60)

    all_passed = True
    for i, (tts_text, expected_subtitle) in enumerate(test_cases, 1):
        result = composer._convert_tts_to_subtitle_format(tts_text)
        passed = result == expected_subtitle

        print(f"\nTest {i}: {'✓ PASS' if passed else '✗ FAIL'}")
        print(f"  TTS (audio):    {tts_text}")
        print(f"  Subtitle:       {result}")
        if not passed:
            print(f"  Expected:       {expected_subtitle}")
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("="*60)

    print("\nHow it works:")
    print("  • TTS audio: Uses Korean words (e.g., '이점오 퍼센트')")
    print("  • Subtitles: Shows symbols (e.g., '2.5%')")
    print("  • Result: Natural speech + Easy-to-read subtitles")
    print()

    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
