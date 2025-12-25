# Quick Push Instructions

## Current Status
✅ SSL certificate issue is fixed
❌ Need to add authentication

## Quick Fix (Choose One)

### Option 1: Add Token to URL (Fastest)

```bash
cd /Users/hae/Documents/Vidmore

# Replace YOUR_TOKEN with your Personal Access Token from:
# https://github.com/settings/tokens
git remote set-url origin https://YOUR_TOKEN@github.com/candoo10001/yutu.git

# Push
git push -u origin main
```

**To get your token:**
1. Go to: https://github.com/settings/tokens
2. If you don't have one, click "Generate new token (classic)"
3. Name: `Vidmore Project`
4. Check `repo` scope
5. Generate and copy the token (starts with `ghp_` or `github_pat_`)

### Option 2: Use Credential Helper (More Secure)

```bash
cd /Users/hae/Documents/Vidmore

# Set credential helper
git config --global credential.helper osxkeychain

# Push - will prompt for credentials
git push -u origin main
```

When prompted:
- **Username**: `candoo10001`
- **Password**: [paste your Personal Access Token - NOT your GitHub password]

The credentials will be saved securely in Keychain.

### Option 3: Use SSH (Most Secure)

```bash
cd /Users/hae/Documents/Vidmore

# Check if you have SSH key
ls -la ~/.ssh/id_*.pub

# If no SSH key, generate one:
ssh-keygen -t ed25519 -C "jinwkim90@gmail.com"
# Press Enter to accept defaults

# Copy public key
cat ~/.ssh/id_ed25519.pub | pbcopy

# Add to GitHub:
# 1. Go to: https://github.com/settings/keys
# 2. Click "New SSH key"
# 3. Title: "MacBook"
# 4. Paste key
# 5. Click "Add SSH key"

# Change remote to SSH
git remote set-url origin git@github.com:candoo10001/yutu.git

# Test connection
ssh -T git@github.com

# Push
git push -u origin main
```

## If Repository Doesn't Exist

**Most common cause of 403 error!**

If you get a 403 error saying "denied to candoo10001", the repository likely doesn't exist.

**Check:** Open https://github.com/candoo10001/yutu in your browser

**If you see "404 - Not Found":**
1. Go to: https://github.com/new
2. Repository name: `yutu`
3. Choose Public or Private
4. **Do NOT** initialize with README
5. Click "Create repository"
6. Then push using one of the options above

## Still Getting 403?

See `DIAGNOSE_403.md` for detailed troubleshooting:
- Verify token has `repo` scope
- Check if token is expired
- Verify repository exists
- Try SSH instead

