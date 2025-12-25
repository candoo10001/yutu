# Diagnose 403 Error

## The Error
```
remote: Permission to candoo10001/yutu.git denied to candoo10001.
fatal: unable to access 'https://github.com/candoo10001/yutu.git/': The requested URL returned error: 403
```

## Most Likely Causes

### 1. Repository Doesn't Exist (90% of cases)

**Check:** Go to https://github.com/candoo10001/yutu

If you see "404 - Not Found", the repository doesn't exist.

**Fix:** Create it:
1. Go to: https://github.com/new
2. Repository name: `yutu`
3. Choose Public or Private
4. **Do NOT** initialize with README
5. Click "Create repository"
6. Then push again

### 2. Token Doesn't Have `repo` Scope

**Check:**
1. Go to: https://github.com/settings/tokens
2. Find your token (starts with `github_pat_...`)
3. Check if it has **`repo`** scope checked

**Fix:**
- If `repo` is NOT checked, delete the token and create a new one:
  1. Click "Generate new token (classic)"
  2. Name: `Vidmore Project`
  3. **Check `repo` scope** (this is critical!)
  4. Generate and copy the token
  5. Update the remote URL:
     ```bash
     cd /Users/hae/Documents/Vidmore
     git remote set-url origin https://NEW_TOKEN@github.com/candoo10001/yutu.git
     git push -u origin main
     ```

### 3. Token Expired or Revoked

**Check:**
- Go to: https://github.com/settings/tokens
- See if your token is still listed and active

**Fix:**
- If it's missing or shows as revoked, create a new token and update the URL

### 4. Organization/Repository Settings

If `candoo10001` is an organization (not a personal account):
- You might need organization admin to grant access
- Check organization settings

## Step-by-Step Fix

### Step 1: Verify Repository Exists

Open in browser: https://github.com/candoo10001/yutu

**If 404:**
- Create repository at https://github.com/new
- Name: `yutu`
- Don't initialize with README

**If exists:**
- Continue to Step 2

### Step 2: Verify Token Permissions

1. Go to: https://github.com/settings/tokens
2. Find your token
3. Verify it has **`repo`** scope

**If missing `repo` scope:**
- Delete old token
- Create new token with `repo` scope
- Update remote URL with new token

### Step 3: Update Remote URL

```bash
cd /Users/hae/Documents/Vidmore

# Get your token from: https://github.com/settings/tokens
# Replace NEW_TOKEN with your token
git remote set-url origin https://NEW_TOKEN@github.com/candoo10001/yutu.git

# Verify
git remote -v

# Push
git push -u origin main
```

### Step 4: If Still Failing - Try SSH

```bash
cd /Users/hae/Documents/Vidmore

# Check if you have SSH key
ls -la ~/.ssh/id_*.pub

# If no SSH key, generate one:
ssh-keygen -t ed25519 -C "jinwkim90@gmail.com"
# Press Enter for defaults

# Copy public key
cat ~/.ssh/id_ed25519.pub | pbcopy

# Add to GitHub:
# 1. Go to: https://github.com/settings/keys
# 2. Click "New SSH key"
# 3. Title: "MacBook"
# 4. Paste key
# 5. Click "Add SSH key"

# Change to SSH
git remote set-url origin git@github.com:candoo10001/yutu.git

# Test
ssh -T git@github.com

# Push
git push -u origin main
```

## Quick Test Commands

Test if repository exists (replace TOKEN with your token):
```bash
curl -H "Authorization: token TOKEN" https://api.github.com/repos/candoo10001/yutu
```

Test if token works:
```bash
curl -H "Authorization: token TOKEN" https://api.github.com/user
```

If you get `{"message":"Not Found"}` for the repository, it doesn't exist.
If you get `{"message":"Bad credentials"}` for user, the token is invalid.

