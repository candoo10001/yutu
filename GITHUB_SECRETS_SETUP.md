# GitHub Secrets Setup Guide

## Issue Fixed

1. ✅ **Made Kling keys optional** - Since Kling is no longer being used, `KLING_ACCESS_KEY` and `KLING_SECRET_KEY` are now optional
2. ✅ **Fixed permissions** - Added `issues: write` permission to workflow
3. ⚠️ **NEWS_API_KEY missing** - Make sure this secret exists in GitHub

## Required GitHub Secrets

**Go to:** `https://github.com/candoo10001/yutu/settings/secrets/actions`

Click **"New repository secret"** and add these **required** secrets:

### Required Secrets:

1. **`NEWS_API_KEY`** ⚠️ (Currently missing - this is causing the error)
   - Get from: https://newsapi.org/
   - Value: Your News API key

2. **`CLAUDE_API_KEY`**
   - Get from: https://console.anthropic.com/
   - Value: Your Claude API key

3. **`GOOGLE_API_KEY`**
   - Get from: https://console.cloud.google.com/
   - Value: Your Google Cloud API key (for Gemini/Veo)

4. **`ELEVENLABS_API_KEY`**
   - Get from: https://elevenlabs.io/
   - Value: Your ElevenLabs API key

### Optional Secrets (for YouTube Upload):

5. **`YOUTUBE_CLIENT_ID`** (optional)
   - Get from: Google Cloud Console → OAuth 2.0 Client ID

6. **`YOUTUBE_CLIENT_SECRET`** (optional)
   - Get from: Google Cloud Console → OAuth 2.0 Client Secret

7. **`YOUTUBE_REFRESH_TOKEN`** (optional)
   - Generate using: `src/youtube_auth_helper.py`

### Optional/Deprecated:

8. **`KLING_ACCESS_KEY`** (optional, deprecated)
   - Not required - Kling is no longer used

9. **`KLING_SECRET_KEY`** (optional, deprecated)
   - Not required - Kling is no longer used

## How to Add Secrets

1. Go to: `https://github.com/candoo10001/yutu/settings/secrets/actions`
2. Click **"New repository secret"**
3. Enter the **Name** (e.g., `NEWS_API_KEY`)
4. Enter the **Secret** value (your actual API key)
5. Click **"Add secret"**
6. Repeat for all required secrets

## Verify Secrets Are Set

After adding secrets, you should see them listed:

- ✅ NEWS_API_KEY
- ✅ CLAUDE_API_KEY
- ✅ GOOGLE_API_KEY
- ✅ ELEVENLABS_API_KEY
- (and any optional ones you added)

**Note:** You cannot see the actual values after they're saved (for security), only that they exist.

## Current Workflow Configuration

The workflow expects these environment variables:

```yaml
env:
  NEWS_API_KEY: ${{ secrets.NEWS_API_KEY }}        # ⚠️ REQUIRED
  CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}    # ✅ REQUIRED
  GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}    # ✅ REQUIRED
  ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}  # ✅ REQUIRED
  LOG_LEVEL: INFO
```

## Troubleshooting

### Error: "Missing required environment variable: NEWS_API_KEY"

**Cause:** The secret doesn't exist in GitHub or is empty.

**Fix:**
1. Go to: `https://github.com/candoo10001/yutu/settings/secrets/actions`
2. Check if `NEWS_API_KEY` exists
3. If not, create it (see "How to Add Secrets" above)
4. If it exists, make sure it's not empty (delete and recreate if needed)

### Error: "Missing required environment variable: CLAUDE_API_KEY"

Same process - verify the secret exists and has a value.

### Secret exists but still getting errors?

1. **Check secret name** - Must match exactly (case-sensitive)
2. **Verify secret value** - Delete and recreate the secret with the correct value
3. **Check workflow file** - Ensure `${{ secrets.SECRET_NAME }}` matches the secret name exactly
4. **Re-run workflow** - Secrets are read when the workflow runs, so you need to trigger a new run

## Code Changes Made

### `src/config.py`

**Before:**
```python
kling_access_key: str  # Required
kling_secret_key: str  # Required

required_keys = {
    "KLING_ACCESS_KEY": "kling_access_key",  # Required
    "KLING_SECRET_KEY": "kling_secret_key",  # Required
}
```

**After:**
```python
kling_access_key: Optional[str] = None  # Optional
kling_secret_key: Optional[str] = None  # Optional

# Kling keys removed from required_keys
# Added as optional: os.getenv("KLING_ACCESS_KEY")
```

## Summary

- ✅ Kling keys are now optional (no longer required)
- ✅ Workflow has correct permissions
- ⚠️ **Make sure `NEWS_API_KEY` secret exists in GitHub**
- ⚠️ **Make sure all required secrets are set**

The workflow should work once all required secrets are added!

