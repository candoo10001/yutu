# Fix: Refresh Token is None

## Issue

When running the auth helper, you got `None` as the refresh token. This happens because:

1. **You've already authorized the app before** - Google doesn't return a refresh token on subsequent authorizations
2. **The consent screen wasn't shown** - Google skips it if you've already authorized

## Solution: Revoke Access First

Before running the auth helper again, you need to revoke previous access:

### Step 1: Revoke Access

1. Go to: https://myaccount.google.com/permissions
2. Find "YouTube Uploader" or your app name
3. Click **"Remove Access"** or **"Revoke Access"**

### Step 2: Run Auth Helper Again

```bash
source venv/bin/activate
python -m src.youtube_auth_helper
```

Enter your Client ID and Client Secret when prompted.

### Step 3: Authorize

When the browser opens:
1. Make sure you see the consent screen (not just auto-approved)
2. Click **"Allow"** to grant permissions
3. The refresh token should now be generated

## Alternative: Force Consent Screen

I've updated the code to force the consent screen. But you still need to revoke access first if you've already authorized.

## Verify OAuth Consent Screen Settings

Make sure your OAuth app is configured correctly:

1. Go to: https://console.cloud.google.com/
2. Navigate to: **APIs & Services** → **OAuth consent screen**
3. Check:
   - App is in **"Testing"** mode (for development)
   - Your email is added as a **test user**
   - Scopes include: `https://www.googleapis.com/auth/youtube.upload`

## If Still Getting None

If you still get `None` after revoking and re-authorizing:

1. **Check OAuth consent screen mode:**
   - If in "Testing", add your email as a test user
   - If in "Production", make sure app is verified (or keep it in Testing for now)

2. **Try a different Google account** (one that hasn't authorized this app)

3. **Check the authorization URL** - it should include `access_type=offline&prompt=consent`

4. **Check browser console** - look for any errors during authorization

## Updated Code

The code now forces `prompt='consent'` which should show the consent screen every time, but you still need to revoke access first if you've already authorized.

## Quick Steps Summary

1. ✅ Revoke access: https://myaccount.google.com/permissions
2. ✅ Run: `python -m src.youtube_auth_helper`
3. ✅ Enter Client ID and Secret
4. ✅ Authorize in browser (should see consent screen)
5. ✅ Copy the refresh token
6. ✅ Add to `.env` file
7. ✅ Test: `python test_youtube_upload.py`

