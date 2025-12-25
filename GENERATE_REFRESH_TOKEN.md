# Generate YouTube Refresh Token

## Issue

Your `YOUTUBE_REFRESH_TOKEN` is set to "None" (the string) or is empty. You need a real refresh token to authenticate.

## Quick Solution

### Step 1: Get Your OAuth Credentials

If you don't have Client ID and Secret:

1. Go to: https://console.cloud.google.com/
2. Select your project (or create one)
3. Enable **YouTube Data API v3**:
   - Go to "APIs & Services" → "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create OAuth credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: **"Desktop app"**
   - Name: "YouTube Uploader"
   - Click "Create"
   - **Copy the Client ID and Client Secret**

### Step 2: Configure Redirect URI

**IMPORTANT:** Before generating the token:

1. In Google Cloud Console, go to your OAuth client settings
2. Under "Authorized redirect URIs", add:
   ```
   http://localhost:8080/
   ```
3. Click "Save"

### Step 3: Generate Refresh Token

Run this command in your terminal (it will ask for input):

```bash
source venv/bin/activate
python -m src.youtube_auth_helper
```

When prompted:
1. Paste your **Client ID** (press Enter)
2. Paste your **Client Secret** (press Enter)
3. Your browser will open - sign in and authorize
4. Copy the refresh token that's displayed

### Step 4: Update .env File

Open your `.env` file and update:

```env
YOUTUBE_CLIENT_ID=your_actual_client_id_here
YOUTUBE_CLIENT_SECRET=your_actual_client_secret_here
YOUTUBE_REFRESH_TOKEN=the_long_refresh_token_string_you_just_got
```

**Important:** The refresh token should be a long string (100+ characters), NOT "None" or empty!

### Step 5: Test

```bash
python test_youtube_upload.py
```

You should see:
```
✅ Authentication successful!
```

## What a Valid Refresh Token Looks Like

A valid refresh token is a long string like:
```
1//0gXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

It's typically 100-200+ characters long.

## If You Get "invalid_grant" Error

This usually means:
1. The refresh token was revoked or expired
2. The Client ID/Secret don't match the token
3. The OAuth app settings changed

**Fix:** Generate a new refresh token following the steps above.

## After It Works Locally

Once authentication works locally, add the same values to GitHub Actions secrets:

1. Go to: `https://github.com/candoo10001/yutu/settings/secrets/actions`
2. Click "Repository secrets" tab
3. Add/update:
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `YOUTUBE_REFRESH_TOKEN`

Then your GitHub Actions workflow will be able to upload videos too!

