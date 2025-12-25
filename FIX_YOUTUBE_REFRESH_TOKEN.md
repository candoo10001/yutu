# Fix YouTube Refresh Token Issue

## Issue Found

Your refresh token is invalid. The error `invalid_grant: Bad Request` means:
- The refresh token has expired or been revoked
- The token was generated with incorrect credentials
- The OAuth app settings changed

## Solution: Generate a New Refresh Token

### Step 1: Run the Auth Helper

```bash
source venv/bin/activate
python -m src.youtube_auth_helper
```

### Step 2: Enter Your Credentials

When prompted, enter:
1. **Client ID** - From Google Cloud Console
2. **Client Secret** - From Google Cloud Console

### Step 3: Authorize in Browser

1. Your browser will open automatically
2. Sign in to the Google account that owns the YouTube channel
3. Click "Allow" to grant permissions
4. The script will generate a new refresh token

### Step 4: Copy the Refresh Token

The script will display:
```
Your refresh token (save this!):
  [long_token_string]
```

### Step 5: Update Your .env File

Add/update the refresh token in your `.env` file:

```env
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_client_secret
YOUTUBE_REFRESH_TOKEN=the_new_refresh_token_here
```

### Step 6: Test Again

```bash
python test_youtube_upload.py
```

You should now see:
```
✅ Authentication successful!
```

## If You Don't Have Client ID and Secret

1. Go to: https://console.cloud.google.com/
2. Select your project (or create one)
3. Enable YouTube Data API v3
4. Go to: APIs & Services → Credentials
5. Click "Create Credentials" → "OAuth client ID"
6. Application type: "Desktop app"
7. Name it (e.g., "YouTube Uploader")
8. Click "Create"
9. Copy the Client ID and Client Secret

**Important:** Make sure to add the redirect URI:
- Go to your OAuth client settings
- Under "Authorized redirect URIs", add: `http://localhost:8080/`
- Click "Save"

## After Local Testing Works

Once authentication works locally:

1. Go to: `https://github.com/candoo10001/yutu/settings/secrets/actions`
2. Click "Repository secrets" tab
3. Update these secrets with your current values:
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `YOUTUBE_REFRESH_TOKEN` (the new one!)

Then GitHub Actions will be able to upload videos too.

