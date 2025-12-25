# Test YouTube Upload Locally

## Quick Test

Run the test script to verify YouTube authentication:

```bash
python test_youtube_upload.py
```

This will check if your environment variables are set correctly.

## Test with Upload

To test an actual upload:

```bash
python test_youtube_upload.py output/metadata_*.json
```

Replace `metadata_*.json` with the actual metadata file path from your last video generation.

## Prerequisites

### 1. Add YouTube Credentials to .env

Make sure your `.env` file has:

```env
YOUTUBE_CLIENT_ID=your_client_id_here
YOUTUBE_CLIENT_SECRET=your_client_secret_here
YOUTUBE_REFRESH_TOKEN=your_refresh_token_here
```

### 2. Get Refresh Token (if you don't have one)

If you don't have a refresh token yet:

```bash
python -m src.youtube_auth_helper
```

Follow the prompts to:
1. Enter your Client ID
2. Enter your Client Secret
3. Authorize in your browser
4. Copy the refresh token to your `.env` file

See `YOUTUBE_SIMPLE_SETUP.md` for detailed instructions.

## What the Test Does

1. **Checks environment variables** - Verifies all 3 YouTube credentials are set
2. **Tests authentication** - Tries to authenticate with YouTube API
3. **Tests upload** (if metadata file provided) - Uploads a video to YouTube

## Common Issues

### "Missing required environment variables"

**Fix:** Add the variables to your `.env` file and make sure you're in the project directory.

### "Authentication failed"

**Possible causes:**
- Invalid credentials
- Refresh token expired or revoked
- OAuth app not configured correctly

**Fix:**
- Regenerate refresh token: `python -m src.youtube_auth_helper`
- Check OAuth app settings in Google Cloud Console

### "Video file not found"

**Fix:** Make sure the video file path in the metadata JSON exists and is correct.

## After Local Testing Works

Once local testing works, make sure the same environment variables are set in GitHub Actions:

1. Go to: `https://github.com/candoo10001/yutu/settings/secrets/actions`
2. Add Repository secrets:
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `YOUTUBE_REFRESH_TOKEN`

Then the workflow should work too!


