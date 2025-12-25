# Korean News YouTube Shorts Generator

Automated system that generates engaging YouTube Shorts videos from business/finance news with AI-generated images, Korean audio narration, and synchronized subtitles.

## Overview

This project automatically creates YouTube Shorts-style videos by:
1. Fetching latest business/finance news from News API
2. Translating news to Korean using Claude API
3. Generating a Korean narration script
4. Segmenting the script into timed chunks (3-5 seconds each)
5. Generating AI images for each segment using Gemini Imagen 3
6. Creating Korean audio narration for each segment using ElevenLabs TTS
7. Combining images, audio, and subtitles into a vertical video (9:16) using ffmpeg
8. Uploading the final video to GitHub Artifacts (scheduled daily via GitHub Actions)

## Features

- **Automated Daily Execution**: Runs automatically via GitHub Actions
- **Multi-API Integration**: News API, Claude API, Gemini (Flash + Imagen 3), ElevenLabs
- **YouTube Shorts Optimized**: Vertical 9:16 aspect ratio, perfect for mobile viewing
- **AI-Generated Visuals**: Unique images for each script segment using Gemini Imagen 3
- **Synchronized Subtitles**: Auto-generated captions overlaid on images
- **Korean Localization**: Full translation and Korean audio narration
- **Professional Quality**: High-quality images and natural Korean TTS
- **Comprehensive Logging**: Structured logging for debugging
- **Error Handling**: Robust error handling with retry logic
- **Metadata Tracking**: Detailed metadata for each generated video

## Technology Stack

- **Python 3.11**
- **News API**: Business/finance news
- **Claude API (Anthropic)**: Translation & script generation
- **Gemini 2.5 Flash API**: Image prompt generation (cost-effective)
- **Gemini Imagen 3 API**: AI image generation
- **ElevenLabs API**: Korean text-to-speech
- **ffmpeg**: Video composition & subtitle rendering
- **GitHub Actions**: Daily automation

## Prerequisites

Before setting up the project, you'll need API keys for:

1. **News API**: Sign up at [newsapi.org](https://newsapi.org/)
2. **Claude API**: Get key at [console.anthropic.com](https://console.anthropic.com/)
3. **Google Cloud API (for Gemini Imagen 3)**: Get key at [console.cloud.google.com](https://console.cloud.google.com/)
4. **ElevenLabs API**: Sign up at [elevenlabs.io](https://elevenlabs.io/)

## Local Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Vidmore
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### 5. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
NEWS_API_KEY=your_news_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Optional: Configure voice ID for Korean TTS
ELEVENLABS_VOICE_ID=your_korean_voice_id
```

### 6. Test Locally

```bash
python main.py
```

The script will:
- Fetch latest business news
- Generate Korean translation and script
- Create video with Korean audio
- Save output to `output/` directory

## GitHub Actions Setup

### 1. Enable GitHub Actions

Make sure GitHub Actions is enabled in your repository settings.

### 2. Add Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add the following secrets:
- `NEWS_API_KEY`
- `CLAUDE_API_KEY`
- `GOOGLE_API_KEY`
- `ELEVENLABS_API_KEY`

### 3. Workflow Schedule

The workflow runs daily at 9 AM UTC (6 PM KST). To change the schedule, edit `.github/workflows/daily_video_generation.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'  # Change time here
```

### 4. Manual Trigger

You can manually trigger the workflow:
1. Go to Actions tab
2. Select "Daily Korean News Video Generation"
3. Click "Run workflow"

### 5. Download Generated Videos

After the workflow completes:
1. Go to Actions tab
2. Click on the latest workflow run
3. Scroll to Artifacts section
4. Download:
   - `korean-news-video-<run-number>` (video file)
   - `video-metadata-<run-number>` (metadata JSON)
   - `execution-logs-<run-number>` (logs)

## Project Structure

```
Vidmore/
├── .github/
│   └── workflows/
│       └── daily_video_generation.yml  # GitHub Actions workflow
├── src/
│   ├── __init__.py
│   ├── config.py                       # Configuration management
│   ├── news_fetcher.py                 # News API integration
│   ├── translator.py                   # Korean translation (Claude)
│   ├── script_generator.py             # Narration script (Claude)
│   ├── prompt_generator.py             # Video prompt (Claude)
│   ├── video_generator.py              # Video generation (Kling O1)
│   ├── audio_generator.py              # Korean TTS (ElevenLabs)
│   ├── video_composer.py               # Video/audio composition (ffmpeg)
│   ├── pipeline.py                     # Main orchestration
│   └── utils/
│       ├── logger.py                   # Structured logging
│       ├── error_handler.py            # Custom exceptions
│       └── retry.py                    # Retry logic
├── output/                             # Generated videos (gitignored)
├── logs/                               # Log files (gitignored)
├── .env.example                        # Example environment variables
├── .gitignore                          # Git ignore rules
├── requirements.txt                    # Python dependencies
├── main.py                             # Entry point
└── README.md                           # This file
```

## Configuration

Edit `.env` to customize:

### News Settings
```env
NEWS_CATEGORY=business          # business, technology, etc.
NEWS_COUNTRY=us                 # us, gb, kr, etc.
MAX_NEWS_ARTICLES=5             # Number of articles to process
```

### Video Settings
```env
VIDEO_DURATION=30               # Total video duration in seconds
SEGMENT_DURATION=4              # Duration per image segment (3-5 seconds recommended)
VIDEO_ASPECT_RATIO=9:16         # Aspect ratio (9:16 for Shorts, 16:9 for landscape, 1:1 for square)
VIDEO_RESOLUTION=1080p          # Video resolution
```

### Subtitle Settings
```env
ENABLE_SUBTITLES=true           # Enable/disable subtitles
SUBTITLE_FONT_SIZE=60           # Font size for subtitles
SUBTITLE_FONT_COLOR=white       # Subtitle text color
SUBTITLE_BACKGROUND_COLOR=black@0.6  # Background color with transparency (0.6 = 60% transparent)
SUBTITLE_POSITION=center        # Position: top, center, or bottom
```

### Audio Settings
```env
ELEVENLABS_VOICE_ID=            # Korean voice ID (optional)
AUDIO_STABILITY=0.5             # Voice stability (0-1)
AUDIO_SIMILARITY=0.75           # Voice similarity (0-1)
AUDIO_STYLE=0.5                 # Voice style (0-1)
```

### Application Settings
```env
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
OUTPUT_DIR=output               # Output directory
LOG_DIR=logs                    # Log directory
```

## Workflow

```
┌──────────────────────────────────────────────────────────────┐
│  1. Fetch English Business News (News API)                   │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  2. Translate to Korean (Claude API)                         │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  3. Generate Korean Narration Script (Claude API)            │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  4. Segment Script into Timed Chunks (3-5 sec each)          │
└──────────────────────────────────────────────────────────────┘
                              ↓
      ┌───────────────────────┴───────────────────────┐
      ↓                                               ↓
┌─────────────────────┐                    ┌──────────────────────┐
│  For Each Segment:  │                    │  Generate Image      │
│                     │────────────────────→  Prompt (Gemini)     │
└─────────────────────┘                    └──────────────────────┘
                                                      ↓
                                           ┌──────────────────────┐
                                           │  Generate AI Image   │
                                           │  (Gemini Imagen 3)   │
                                           └──────────────────────┘
                                                      ↓
                                           ┌──────────────────────┐
                                           │  Generate Audio      │
                                           │  (ElevenLabs TTS)    │
                                           └──────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  5. Create Slideshow: Combine Images + Audio + Subtitles    │
│     (ffmpeg - 9:16 vertical format)                          │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  6. Upload to GitHub Artifacts                               │
└──────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### API Errors

**News API 429 (Rate Limit)**:
- Free tier limited to 100 requests/day
- Upgrade to paid plan or reduce frequency

**Claude API Errors**:
- Check API key is valid
- Ensure sufficient credits
- Check rate limits

**Gemini API Errors**:
- Ensure Google Cloud API key is valid
- Check that Imagen 3 API is enabled in your project
- Verify billing is enabled for your Google Cloud project

**ElevenLabs Quota Exceeded**:
- Check remaining character quota
- Upgrade plan or wait for quota reset

### Local Execution Issues

**ffmpeg not found**:
```bash
# Install ffmpeg (see installation instructions above)
ffmpeg -version  # Verify installation
```

**Missing dependencies**:
```bash
pip install -r requirements.txt
```

**Environment variables not loaded**:
- Ensure `.env` file exists in project root
- Check file has correct format (no spaces around `=`)

### GitHub Actions Issues

**Secrets not working**:
- Verify secrets are added in repository settings
- Check secret names match exactly (case-sensitive)

**Workflow not triggering**:
- Ensure workflow file is in `.github/workflows/`
- Check cron syntax is correct
- Verify GitHub Actions is enabled

**Artifact upload fails**:
- Check `output/` directory exists and contains files
- Verify file patterns in upload steps

## Cost Estimation

**Per video (estimated for 30-second shorts with ~7 segments)**:
- News API: $0 (free tier)
- Claude API: ~$0.01 (script generation only, ~2000 tokens)
- Gemini 2.5 Flash: ~$0.001 (7 image prompt generations, ~3500 tokens)
- Gemini Imagen 3: ~$0.28 (7 images × $0.04 per image)
- ElevenLabs: ~$0.05 (30-second audio)
- GitHub Actions: $0 (free tier)

**Total per day**: ~$0.34
**Monthly**: ~$10.20

**Note**: Using Gemini for image prompts instead of Claude saves ~50% on prompt generation costs!

## Development

### Run Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests (if implemented)
pytest tests/
```

### Code Formatting

```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
```

## License

[Specify your license here]

## Contributing

[Contribution guidelines]

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in `logs/` directory
3. Check GitHub Issues
4. Contact maintainers

---

Built with Python, Claude, Kling O1, and ElevenLabs
