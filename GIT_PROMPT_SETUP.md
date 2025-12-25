# Git Prompt Setup - Complete

## What Was Configured

✅ **Git User Info:**
- Name: `jin` (global), `wednes` (local)
- Email: `candoo10001@gmail.com`

✅ **Remote URL:**
- Changed to: `https://github.com/candoo10001/yutu.git`
- Token removed from URL (will prompt instead)

✅ **Credential Helper:**
- Set to: `osxkeychain`
- Will prompt for credentials and save securely

✅ **Cached Credentials:**
- Cleared for fresh prompt

## How to Push Now

When you run `git push -u origin main`, git will prompt you:

```
Username for 'https://github.com': candoo10001
Password for 'https://candoo10001@github.com': [paste your Personal Access Token]
```

**Important:** 
- Username: `candoo10001`
- Password: Use your **Personal Access Token** (NOT your GitHub password)
  - Get token from: https://github.com/settings/tokens
  - Make sure it has `repo` scope checked
  - Token looks like: `ghp_...` or `github_pat_...`

## First Time Setup

If you haven't created a token with `repo` scope yet:

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: `Vidmore Project`
4. **Check `repo` scope** (very important!)
5. Generate and copy the token
6. When git prompts for password, paste the token (not your GitHub password)

## After First Push

The credentials will be saved securely in macOS Keychain, so you won't be prompted again unless the token expires.

## Verify Configuration

```bash
# Check git config
git config --list | grep -E "(user|credential|remote)"

# Check remote URL
git remote -v

# Test push (will prompt if credentials not saved)
git push -u origin main
```

