# Background Music Setup

## Local Development

Place your royalty-free background music files (`.mp3`, `.wav`, `.m4a`, etc.) in this folder.

The files in this folder are **not committed** to git (they're in `.gitignore`) to avoid copyright issues and keep the repository small.

## GitHub Actions (Production)

To add background music in GitHub Actions, edit `.github/workflows/daily_video_generation.yml` and add download URLs:

```yaml
- name: Setup background music folder
  run: |
    mkdir -p background_music

    # Download royalty-free background music
    curl -L "YOUR_MUSIC_URL_1.mp3" -o background_music/bgm1.mp3
    curl -L "YOUR_MUSIC_URL_2.mp3" -o background_music/bgm2.mp3
```

### Free Royalty-Free Music Sources

- **YouTube Audio Library**: https://www.youtube.com/audiolibrary
- **Free Music Archive**: https://freemusicarchive.org/
- **Incompetech**: https://incompetech.com/music/royalty-free/
- **Bensound**: https://www.bensound.com/
- **Purple Planet**: https://www.purple-planet.com/

Make sure the music is:
- ✅ Royalty-free or Creative Commons licensed
- ✅ Suitable for YouTube monetization
- ✅ Upbeat/energetic for news content

## Fallback Behavior

If no music files are found in this folder, the system will automatically generate **synthetic background music** using ffmpeg sine waves. This ensures videos always have background music, even if no files are provided.

## Current Files

Locally, you may have:
- `upbeat-promo-music-dynamic-energetic-stomp-drum-background-intro-284461.mp3`
- `Sigma Slide - The Soundlings.mp3`

These files are **not** in git and need to be added to GitHub Actions manually or via download URLs.
