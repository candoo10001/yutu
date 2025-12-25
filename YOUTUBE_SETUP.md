# YouTube Shorts Auto-Upload Setup Guide

This guide will help you set up automated YouTube Shorts uploads that run twice daily.

## Overview

The system will:
- Generate videos **twice per day** (6 AM and 6 PM KST)
- Automatically upload to YouTube as **Shorts**
- Handle authentication securely via GitHub Secrets

## Schedule

- **Morning News**: 9 PM UTC / 6 AM KST
- **Evening News**: 9 AM UTC / 6 PM KST

## Prerequisites

You'll need:
1. A YouTube channel
2. Google Cloud Platform account
3. GitHub repository with Actions enabled

## Step-by-Step Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### 2. Enable YouTube Data API

1. In Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for "YouTube Data API v3"
3. Click **Enable**

### 3. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - **User Type**: External
   - **App name**: Korean News Shorts Generator
   - **User support email**: Your email
   - **Developer contact**: Your email
   - Add scope: `https://www.googleapis.com/auth/youtube.upload`
   - Add your email as a test user
4. Back to Create OAuth client ID:
   - **Application type**: Desktop app
   - **Name**: Korean News Uploader
5. Click **Create**
6. Download the JSON file (it will be named like `client_secret_xxx.json`)

### 4. Rename and Save Credentials

1. Rename the downloaded file to `client_secrets.json`
2. Move it to your project root directory:
   ```
   Vidmore/
   └── client_secrets.json
   ```

### 5. Run Local Authentication

Run the setup script to authenticate with YouTube:

```bash
# Make sure you're in the project directory
cd Vidmore

# Activate virtual environment
source venv/bin/activate

# Install dependencies (including YouTube API)
pip install -r requirements.txt

# Run setup script
python setup_youtube.py
```

This will:
1. Open your browser for OAuth consent
2. Ask you to sign in to your YouTube account
3. Request permission to upload videos
4. Generate authentication tokens
5. Display the secrets you need to add to GitHub

### 6. Add Secrets to GitHub

After running `setup_youtube.py`, copy the displayed values and add them to your GitHub repository:

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these two secrets:

#### Secret 1: YOUTUBE_CLIENT_SECRETS
- **Name**: `YOUTUBE_CLIENT_SECRETS`
- **Value**: Copy the entire content from `client_secrets.json`

#### Secret 2: YOUTUBE_TOKEN
- **Name**: `YOUTUBE_TOKEN`
- **Value**: Copy the base64-encoded token from the setup script output

### 7. Verify Existing Secrets

Make sure these secrets are already configured:
- `NEWS_API_KEY`
- `CLAUDE_API_KEY`
- `GOOGLE_API_KEY` (for Gemini)
- `ELEVENLABS_API_KEY`

### 8. Test the Workflow

#### Manual Test:
1. Go to **Actions** tab in your GitHub repository
2. Select "Daily Korean News Video Generation"
3. Click **Run workflow**
4. Select branch and click **Run workflow**
5. Wait for completion (usually 5-10 minutes)
6. Check your YouTube channel for the uploaded Short!

#### Check Logs:
- If upload fails, check the workflow logs
- Look for errors in the "Upload to YouTube" step
- Common issues:
  - Invalid credentials
  - YouTube quota exceeded
  - Video format issues

## Customization

### Change Upload Schedule

Edit `.github/workflows/daily_video_generation.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'   # Change to your preferred time (UTC)
  - cron: '0 21 * * *'  # Change to your preferred time (UTC)
```

Use [crontab.guru](https://crontab.guru/) to create custom schedules.

### Modify Video Metadata

Edit `src/youtube_uploader.py` to customize:
- Video title format
- Description template
- Tags
- Privacy settings (public/private/unlisted)
- Category

Example:
```python
def upload_video(self, ...):
    # Customize title
    title = f"📰 Korean News - {date} #Shorts"

    # Customize description
    description = f"""
    Latest Korean business news in 60 seconds!

    #Shorts #News #Korean #뉴스 #한국뉴스
    """

    # Customize tags
    tags = ['Shorts', 'News', 'Korean', 'Business', '뉴스']
```

## Quota Management

### YouTube API Quotas

The YouTube Data API has daily quotas:
- **Free tier**: 10,000 units/day
- **Video upload**: ~1,600 units per upload

With 2 uploads per day:
- Daily usage: ~3,200 units
- Well within free tier limits

### Monitor Quota Usage

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Dashboard**
3. Click on **YouTube Data API v3**
4. View quota usage and limits

## Troubleshooting

### "Invalid credentials" error

**Solution:**
1. Delete `token.pickle` from local directory
2. Re-run `python setup_youtube.py`
3. Update `YOUTUBE_TOKEN` secret in GitHub

### "Quota exceeded" error

**Solution:**
- Wait 24 hours for quota reset
- Or request quota increase from Google Cloud Console

### Video not appearing as Short

**Ensure:**
- Video is vertical (9:16 aspect ratio) ✓ Already configured
- Duration is under 60 seconds ✓ Already configured
- Title or description contains `#Shorts` ✓ Already added

### OAuth consent screen issues

**If app is in testing mode:**
- Only test users can authenticate
- Add your email as a test user in OAuth consent screen
- Or publish the app (requires verification for external users)

## Security Best Practices

1. **Never commit credentials**:
   - `client_secrets.json` is in `.gitignore`
   - `token.pickle` is in `.gitignore`

2. **Use GitHub Secrets**:
   - All sensitive data stored as GitHub Secrets
   - Secrets are encrypted and not visible in logs

3. **Rotate tokens regularly**:
   - Re-run setup script every few months
   - Update GitHub secrets with new tokens

4. **Limit OAuth scopes**:
   - Only request `youtube.upload` scope
   - Don't request unnecessary permissions

## Testing Locally

To test YouTube upload without running the full pipeline:

```bash
# Upload a single video
python src/youtube_uploader.py output/final_shorts_*.mp4

# Or upload using metadata
python src/youtube_uploader.py output/metadata_*.json
```

## Monitoring

### Check Upload Status

**Via GitHub Actions:**
1. Go to **Actions** tab
2. Click on latest workflow run
3. Check "Upload to YouTube" step logs
4. Look for video ID and URL in output

**Via YouTube Studio:**
1. Go to [YouTube Studio](https://studio.youtube.com/)
2. Click **Content**
3. Check for newly uploaded Shorts
4. Monitor views, engagement

### Set Up Notifications

**GitHub:**
- GitHub will email you if workflow fails
- Check **Settings** → **Notifications** for preferences

**YouTube:**
- Enable YouTube Studio mobile app for upload notifications

## Advanced Configuration

### Add Video Thumbnails

Modify `src/youtube_uploader.py`:

```python
# Add thumbnail upload
self.youtube.thumbnails().set(
    videoId=video_id,
    media_body=MediaFileUpload('thumbnail.jpg')
).execute()
```

### Schedule Different Content

Create multiple workflows for different news categories:
- `morning_tech_news.yml` - Tech news at 6 AM
- `evening_business_news.yml` - Business news at 6 PM

### Add Playlists

Auto-add videos to playlists:

```python
self.youtube.playlistItems().insert(
    part="snippet",
    body={
        "snippet": {
            "playlistId": "YOUR_PLAYLIST_ID",
            "resourceId": {
                "kind": "youtube#video",
                "videoId": video_id
            }
        }
    }
).execute()
```

## Support

If you encounter issues:
1. Check workflow logs in GitHub Actions
2. Review YouTube Studio for upload errors
3. Check Google Cloud Console for API errors
4. Verify all secrets are correctly configured

---

**Ready to go live?** Just push your changes and the workflow will start running on schedule!
