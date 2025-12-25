# Quick Fix for 403 Error

## The Issue
You're getting `403` error even though credentials are set to `candoo10001`. This usually means:

1. **The repository doesn't exist yet** (most common)
2. The token doesn't have `repo` permissions
3. The token has expired or been revoked

## Quick Solution

### Step 1: Create the Repository on GitHub

**Option A: Via Web Interface (Easiest)**
1. Go to: https://github.com/new
2. Repository name: `yutu`
3. Choose Public or Private
4. **Do NOT** initialize with README (since you already have code)
5. Click **"Create repository"**

**Option B: Via API**
```bash
# Replace YOUR_TOKEN with your Personal Access Token
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{"name":"yutu","private":false}'
```

### Step 2: Verify Token Permissions

1. Go to: https://github.com/settings/tokens
2. Find your token (the one starting with `github_pat_...`)
3. Verify it has **`repo`** scope checked
4. If not, delete it and create a new one with `repo` scope

### Step 3: Push Your Code

```bash
cd /Users/hae/Documents/Vidmore
git push -u origin main
```

## Alternative: Use SSH Instead

If HTTPS keeps giving issues, switch to SSH:

```bash
# Check if you have SSH key
ls -la ~/.ssh/id_*.pub

# If no SSH key, generate one:
ssh-keygen -t ed25519 -C "jinwkim90@gmail.com"
# Press Enter to accept default location
# (Optional: Set a passphrase or press Enter for no passphrase)

# Copy public key
cat ~/.ssh/id_ed25519.pub | pbcopy

# Add to GitHub:
# 1. Go to: https://github.com/settings/keys
# 2. Click "New SSH key"
# 3. Title: "MacBook" (or any name)
# 4. Paste the key
# 5. Click "Add SSH key"

# Change remote to SSH
git remote set-url origin git@github.com:candoo10001/yutu.git

# Test connection
ssh -T git@github.com
# Should see: "Hi candoo10001! You've successfully authenticated..."

# Push
git push -u origin main
```

## Security Note

Your Personal Access Token is currently visible in your git config. After you successfully push, consider removing it from the URL:

```bash
# Remove token from URL
git remote set-url origin https://github.com/candoo10001/yutu.git

# Let credential helper handle it securely
git config --global credential.helper osxkeychain

# Next push will prompt and save securely in Keychain
git push
```


