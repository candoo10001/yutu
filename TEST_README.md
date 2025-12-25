# Test Script for Video Changes

## Purpose

This test script allows you to verify the recent video composition changes without calling any external APIs (Gemini, ElevenLabs, etc.). It creates a complete test video using:
- Pre-generated test images (colored backgrounds)
- Silent audio files (simulating TTS output)
- Korean subtitle text

## What It Tests

1. **Subtitle Sync Fix**: Verifies that subtitles are properly synced with the 1.2x sped-up audio
2. **Enhanced Title Visibility**: Tests the larger font size (80px), taller background box (220px), and increased top padding for mobile visibility

## Usage

```bash
python test_video_changes.py
```

## What Happens

1. **Creates 4 test segments**:
   - Blue segment: Tests subtitle sync
   - Green segment: Tests title visibility
   - Orange segment: Tests mobile optimization
   - Red segment: Final verification

2. **Generates test media**:
   - 4 colored test images (1080x1920 portrait)
   - 4 silent audio files (5-6 seconds each)

3. **Composes final video**:
   - Creates video clips with titles
   - Adds Korean subtitles
   - Applies 1.2x audio speed
   - Burns in subtitles
   - Adds background music

## Output

The test creates a final video in `test_output/final_shorts_*.mp4`

To view the video:
```bash
open test_output/final_shorts_*.mp4
```

## What to Check

When watching the test video:

### 1. Subtitle Sync
- Subtitles should appear and disappear at the right times
- With 1.2x audio speed, subtitles should be faster than normal
- No lag or delay between audio and subtitle timing

### 2. Title Visibility
- **Font size**: Should be noticeably larger (80px instead of 56px)
- **Background box**: Taller black background (220px instead of 140px)
- **Top padding**: More space from the top edge (~70px from top instead of ~40px)
- **Mobile ready**: Should be clearly visible even on small screens

### 3. Korean Text Rendering
- Korean characters should render correctly in both titles and subtitles
- No broken or missing characters

## Test Segments

Each segment tests specific aspects:

1. **Segment 1 (Blue)**: "첫 번째 테스트 세그먼트입니다 자막 동기화를 확인합니다"
   - Title: "테스트 1: 자막 동기화"
   - Duration: 5 seconds

2. **Segment 2 (Green)**: "두 번째 테스트 세그먼트입니다 제목 가시성을 확인합니다"
   - Title: "테스트 2: 제목 표시"
   - Duration: 5 seconds

3. **Segment 3 (Orange)**: "세 번째 테스트 세그먼트입니다 모바일 환경에서 잘 보이는지 확인합니다"
   - Title: "테스트 3: 모바일 최적화"
   - Duration: 6 seconds

4. **Segment 4 (Red)**: "마지막 테스트 세그먼트입니다 모든 변경사항이 잘 적용되었습니다"
   - Title: "테스트 4: 최종 확인"
   - Duration: 6 seconds

## Cleanup

Test files are created in `test_output/` directory. You can delete this directory after testing:

```bash
rm -rf test_output/
```

## Technical Details

- **No API calls**: This test script doesn't call any external APIs
- **Silent audio**: Uses ffmpeg to generate silent audio files that simulate TTS output
- **Test images**: Creates simple colored backgrounds with PIL/Pillow
- **Real composition**: Uses the actual VideoComposer class with all the recent changes
- **Speed factor**: Audio is sped up by 1.2x (same as production)
- **Subtitle timing**: Subtitles are adjusted to match the 1.2x speed

## Requirements

All dependencies are already in requirements.txt:
- PIL/Pillow (for test images)
- ffmpeg (for audio/video processing)
- structlog (for logging)
