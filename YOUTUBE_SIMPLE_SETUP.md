# Simplified YouTube Setup Guide

## Why OAuth Instead of API Key?

**Short answer:** YouTube API **requires** OAuth 2.0 for uploads. API keys only work for reading public data.

### Authentication Methods Comparison:

| Method | Read Data | Upload Videos | YouTube Support |
|--------|-----------|---------------|-----------------|
| **API Key** | ✅ Yes | ❌ No | Read-only |
| **OAuth 2.0** | ✅ Yes | ✅ Yes | Required for uploads |
| **Service Account** | ❌ No | ❌ No | Not supported by YouTube |

Since we need to **upload videos**, OAuth is the only option.

## Simplified Setup (3 Simple Secrets)

I've made it **much easier**! Instead of managing JSON files and pickle files, you now only need **3 environment variables**.

### Quick Setup (5 Minutes)

#### Step 1: Get OAuth Credentials (One-time)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select project → Enable "YouTube Data API v3"
3. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
4. Choose **Desktop app** → Create
5. You'll get:
   - ✅ **Client ID** (looks like: `123456789-abc.apps.googleusercontent.com`)
   - ✅ **Client Secret** (looks like: `GOCSPX-abc123xyz`)
6. **IMPORTANT**: Add redirect URI:
   - Click on your newly created OAuth client ID to edit it
   - Under **"Authorized redirect URIs"**, click **"Add URI"**
   - Add: `http://localhost:8080/`
   - Click **"Save"**

#### Step 2: Generate Refresh Token (One-time)

Run the simplified setup script:

```bash
# In your project directory
python src/youtube_auth_helper.py
```

This will:
1. Ask for your Client ID and Client Secret
2. Open your browser for authorization
3. Give you a **Refresh Token**

Copy the refresh token - it looks like: `1//abc123xyz...`

#### Step 3: Add to GitHub Secrets

Add these **3 secrets** to GitHub:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `YOUTUBE_CLIENT_ID` | Your client ID | `123456789-abc.apps.googleusercontent.com` |
| `YOUTUBE_CLIENT_SECRET` | Your client secret | `GOCSPX-abc123xyz` |
| `YOUTUBE_REFRESH_TOKEN` | Your refresh token | `1//abc123xyz...` |

**That's it!** ✅

## How It Works

### The Magic of Refresh Tokens:

```
┌─────────────────────────────────────────────────┐
│ Traditional OAuth (Complex)                     │
├─────────────────────────────────────────────────┤
│ 1. Store client_secrets.json file              │
│ 2. Store token.pickle file                      │
│ 3. Base64 encode for GitHub                     │
│ 4. Decode in GitHub Actions                     │
│ 5. Hope pickle file doesn't break               │
└─────────────────────────────────────────────────┘

vs.

┌─────────────────────────────────────────────────┐
│ Simplified OAuth (Easy!)                        │
├─────────────────────────────────────────────────┤
│ 1. Set 3 environment variables                  │
│ 2. Refresh token auto-generates access tokens   │
│ 3. Just works! ✨                               │
└─────────────────────────────────────────────────┘
```

### What's a Refresh Token?

- **Never expires** (unless you revoke it)
- **Automatically generates** new access tokens
- **No file management** needed
- **Perfect for automation**

### Authentication Flow:

```
GitHub Actions runs
    ↓
Loads 3 environment variables
    ↓
Uses refresh token to get access token
    ↓
Uploads video to YouTube
    ↓
Done! ✅
```

## Why This Is Better:

### Old Method (Complex):
- ❌ Manage multiple files
- ❌ Base64 encoding/decoding
- ❌ File format issues
- ❌ Pickle serialization problems
- ❌ 2 GitHub secrets (large JSON + base64)

### New Method (Simple):
- ✅ Just 3 simple text values
- ✅ No file management
- ✅ No encoding needed
- ✅ Works reliably
- ✅ Easy to update

## Testing Locally

### Option 1: Use Environment Variables (Recommended)

```bash
# Set in your .env file (don't commit!)
YOUTUBE_CLIENT_ID=your-client-id
YOUTUBE_CLIENT_SECRET=your-client-secret
YOUTUBE_REFRESH_TOKEN=your-refresh-token

# Run uploader
python src/youtube_uploader.py output/final_shorts_*.mp4
```

### Option 2: Use OAuth Flow

```bash
# Will open browser for authorization
python src/youtube_uploader.py output/final_shorts_*.mp4
```

## Troubleshooting

### "redirect_uri_mismatch" or "Error 400: redirect_uri_mismatch"

**Cause:** The redirect URI in your code doesn't match what's configured in Google Cloud Console

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to: **APIs & Services** > **Credentials**
3. Click on your OAuth 2.0 Client ID (Desktop app)
4. Under **"Authorized redirect URIs"**, make sure `http://localhost:8080/` is listed
5. If not, click **"Add URI"**, add `http://localhost:8080/`, and click **"Save"**
6. Try running the script again

### "Refresh token invalid"

**Cause:** Token was revoked or expired (rare)

**Solution:**
1. Run `python src/youtube_auth_helper.py` again
2. Get new refresh token
3. Update `YOUTUBE_REFRESH_TOKEN` secret in GitHub

### "Client ID not found"

**Cause:** Environment variables not set

**Solution:** Verify all 3 secrets are added to GitHub:
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

### "Quota exceeded"

**Cause:** Uploaded too many videos (limit: ~6-7 per day on free tier)

**Solution:**
- Wait 24 hours for quota reset
- Or reduce frequency (run once per day instead of twice)

## Security Notes

### Is This Secure?

**Yes!** ✅

- Refresh tokens are stored as **GitHub Secrets** (encrypted)
- Never logged or exposed in workflow output
- Only works for YouTube uploads (limited scope)
- Can be revoked anytime from Google account

### Revoking Access

If you need to revoke access:

1. Go to [myaccount.google.com/permissions](https://myaccount.google.com/permissions)
2. Find "Korean News Shorts Generator" (or your app name)
3. Click **Remove Access**
4. Generate new refresh token if you want to re-enable

## Comparison: API Key vs OAuth

Since YouTube requires OAuth, here's why:

### Why YouTube Doesn't Allow API Keys for Uploads:

1. **User Authorization**: Uploading to a channel requires user consent
2. **Channel Ownership**: API doesn't know which channel to upload to
3. **Liability**: OAuth ensures explicit user permission
4. **Quota Management**: Per-user quota tracking

### If You Really Want API-Key-Like Simplicity:

The **refresh token** is as close as you can get:
- ✅ Set once, use forever
- ✅ Just a simple string value
- ✅ No interactive login needed after setup
- ✅ Works great for automation

## Advanced: Rotating Tokens

For extra security, rotate refresh tokens monthly:

```bash
# Every month (optional)
python src/youtube_auth_helper.py

# Update GitHub secret
# Go to GitHub → Settings → Secrets → YOUTUBE_REFRESH_TOKEN
# Paste new value
```

## FAQ

**Q: Can I use the same refresh token across multiple projects?**
A: Yes! The refresh token is account-based, not project-based.

**Q: Will the refresh token expire?**
A: No, unless you manually revoke it or Google detects suspicious activity.

**Q: Can I generate videos without YouTube upload?**
A: Yes! Just don't set the YouTube secrets. Videos will be saved to GitHub artifacts.

**Q: Can I upload to multiple YouTube channels?**
A: Yes, create separate GitHub secrets for each channel:
- `YOUTUBE_CHANNEL_1_REFRESH_TOKEN`
- `YOUTUBE_CHANNEL_2_REFRESH_TOKEN`

**Q: Is there really no way to use an API key?**
A: Correct. YouTube Data API v3 **requires OAuth for all write operations**. This is a YouTube restriction, not a limitation of this implementation.

---

**Ready?** Run `python src/youtube_auth_helper.py` to get started!
