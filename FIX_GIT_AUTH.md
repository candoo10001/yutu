# Fix Git Authentication Error

## Problem
```
remote: Permission to candoo10001/yutu.git denied to Jin-Kredible.
fatal: unable to access 'https://github.com/candoo10001/yutu.git/': The requested URL returned error: 403
```

## Solution: Use Personal Access Token

### Step 1: Generate Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `Vidmore Project`
4. Select expiration: Choose your preference (e.g., "90 days" or "No expiration")
5. Select scopes: Check **`repo`** (this gives full control of private repositories)
6. Click **"Generate token"**
7. **Copy the token** (it looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
   - ⚠️ **Important**: You won't be able to see it again, so copy it now!

### Step 2: Update Git Credentials

**Option A: Use Keychain Access (Easiest)**

1. Open **Keychain Access** app (search in Spotlight)
2. Search for `github.com`
3. Find entries related to GitHub credentials
4. Right-click and select **Delete**
5. Close Keychain Access

**Option B: Update Remote URL with Token (Recommended)**

This will automatically use your token without needing to clear old credentials:

```bash
cd /Users/hae/Documents/Vidmore

# Replace YOUR_TOKEN with your Personal Access Token
git remote set-url origin https://YOUR_TOKEN@github.com/candoo10001/yutu.git

# Now push (no password prompt needed)
git push -u origin main
```

**Option C: Let Git Prompt for New Credentials**

If you prefer to be prompted:

```bash
cd /Users/hae/Documents/Vidmore

# Temporarily disable credential helper
git config --local --unset credential.helper

# Push - it will prompt for username and password
git push -u origin main
# Username: candoo10001
# Password: [paste your Personal Access Token]

# Re-enable credential helper
git config --local credential.helper osxkeychain
```

### Alternative: Update Remote to Include Token

You can also embed the token in the URL (less secure, but convenient):

```bash
# Replace TOKEN with your personal access token
git remote set-url origin https://TOKEN@github.com/candoo10001/yutu.git

# Now push
git push -u origin main
```

### Option 2: Use SSH (More Secure)

If you prefer SSH:

```bash
# Check if you have SSH keys
ls -la ~/.ssh/id_*.pub

# If no SSH key, generate one:
ssh-keygen -t ed25519 -C "jinwkim90@gmail.com"

# Copy public key to clipboard
cat ~/.ssh/id_ed25519.pub | pbcopy

# Add SSH key to GitHub:
# 1. Go to: https://github.com/settings/keys
# 2. Click "New SSH key"
# 3. Paste the key
# 4. Click "Add SSH key"

# Change remote to SSH
git remote set-url origin git@github.com:candoo10001/yutu.git

# Now push
git push -u origin main
```

## Verify It Works

After pushing, you should see:
```
Enumerating objects: X, done.
Counting objects: 100% (X/X), done.
...
To https://github.com/candoo10001/yutu.git
 * [new branch]      main -> main
```

## Troubleshooting

### SSL Certificate Error: "error setting certificate verify locations"

If you see this error:
```
fatal: unable to access 'https://github.com/...': error setting certificate verify locations: CAfile: /etc/ssl/cert.pem CApath: none
```

**Fix:**
```bash
cd /Users/hae/Documents/Vidmore

# Set certificate path for this repository
git config http.sslCAInfo /etc/ssl/cert.pem

# Verify it's set
git config http.sslCAInfo

# Now try pushing again
git push -u origin main
```

### "Device not configured" or "could not read Username"

If git asks for credentials but can't prompt you:

**Option 1: Add token to URL (Quick Fix)**
```bash
cd /Users/hae/Documents/Vidmore

# Replace YOUR_TOKEN with your Personal Access Token
git remote set-url origin https://YOUR_TOKEN@github.com/candoo10001/yutu.git

# Now push
git push -u origin main
```

**Option 2: Use credential helper**
```bash
cd /Users/hae/Documents/Vidmore

# Set credential helper
git config --global credential.helper osxkeychain

# Push - it will prompt once and save
git push -u origin main
# When prompted:
# Username: candoo10001
# Password: [paste your Personal Access Token]
```

### Still getting 403 error even with token

If you're still getting `403` error after setting up the token, check:

1. **Verify the repository exists:**
   ```bash
   # Check if repository exists (will fail if it doesn't)
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/repos/candoo10001/yutu
   ```

2. **Check token permissions:**
   - Go to: https://github.com/settings/tokens
   - Find your token and verify it has `repo` scope checked
   - If not, delete the old token and create a new one with `repo` scope

3. **Repository doesn't exist - Create it:**
   ```bash
   # Create repository via GitHub API
   curl -X POST \
     -H "Authorization: token YOUR_TOKEN" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/user/repos \
     -d '{"name":"yutu","private":false}'
   ```

4. **Or create via GitHub web interface:**
   - Go to: https://github.com/new
   - Repository name: `yutu`
   - Choose Public or Private
   - Click "Create repository"
   - Then push your code

5. **Token in remote URL (Security Warning):**
   - ⚠️ Your token is currently visible in `git config --list`
   - Better approach: Remove token from URL and use credential helper:
   ```bash
   # Remove token from URL
   git remote set-url origin https://github.com/candoo10001/yutu.git
   
   # Use credential helper instead
   git config --global credential.helper osxkeychain
   
   # Push - it will prompt and save securely
   git push -u origin main
   # Username: candoo10001
   # Password: [paste token]
   ```

### "Permission denied (publickey)" (SSH)
- Make sure your SSH key is added to GitHub
- Test with: `ssh -T git@github.com`

### "Authentication failed" (Token)
- Make sure you're using the token as the password, not your GitHub password
- Check that the token has `repo` scope
- Make sure the token hasn't expired
- Regenerate the token if it's not working

