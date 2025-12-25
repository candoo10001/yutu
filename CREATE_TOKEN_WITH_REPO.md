# Create Token with `repo` Scope - Step by Step

## The Problem
Your current token doesn't have the `repo` scope, so it can't push to repositories.

## Step-by-Step Instructions

### Step 1: Go to Token Settings
Open: https://github.com/settings/tokens

### Step 2: Generate New Token
1. Click the green button: **"Generate new token"**
2. Select: **"Generate new token (classic)"** (NOT fine-grained)

### Step 3: Configure Token (IMPORTANT!)

1. **Note/Name**: Enter `Vidmore Project` (or any name you want)

2. **Expiration**: Choose your preference
   - "90 days"
   - "No expiration" (if you want it to last forever)

3. **Select scopes** - THIS IS CRITICAL:
   - ✅ Scroll down and find **`repo`**
   - ✅ **CHECK the box next to `repo`**
   - When you check `repo`, it should automatically check these sub-scopes:
     - ✅ `repo:status`
     - ✅ `repo_deployment`
     - ✅ `public_repo`
     - ✅ `repo:invite`
     - ✅ `security_events`
   
   **IMPORTANT**: If you don't check `repo`, the token won't work for pushing!

### Step 4: Generate and Copy
1. Scroll down and click the green button: **"Generate token"**
2. **COPY THE TOKEN IMMEDIATELY** (you won't be able to see it again!)
   - It will look like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - Or: `github_pat_...`

### Step 5: Update Git Remote

```bash
cd /Users/hae/Documents/Vidmore

# Replace NEW_TOKEN with the token you just copied
git remote set-url origin https://NEW_TOKEN@github.com/candoo10001/yutu.git

# Verify it's set
git remote -v

# Push
git push -u origin main
```

## Visual Guide

When you're on the token creation page, you should see a list of checkboxes. Make sure you see:

```
☑️ repo
  ☑️ repo:status
  ☑️ repo_deployment  
  ☑️ public_repo
  ☑️ repo:invite
  ☑️ security_events
```

If `repo` is NOT checked, your token won't work for pushing code.

## Verify Token Has Repo Scope

After creating the token, you can verify it has the right scopes:

```bash
python3 -c "
import ssl, urllib.request, json
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
token = 'YOUR_TOKEN_HERE'
headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
req = urllib.request.Request('https://api.github.com/user', headers=headers)
with urllib.request.urlopen(req, context=ssl_context) as response:
    scopes = response.headers.get('X-OAuth-Scopes', '')
    print(f'Token scopes: {scopes}')
    if 'repo' in scopes:
        print('✅ Token HAS repo scope - ready to use!')
    else:
        print('❌ Token DOES NOT have repo scope')
"
```

## Common Mistakes

1. ❌ **Creating a fine-grained token instead of classic**
   - Use "Generate new token (classic)"

2. ❌ **Not checking the `repo` checkbox**
   - Make sure `repo` is checked (not just other scopes)

3. ❌ **Using the token before copying it**
   - Copy it immediately after generation

4. ❌ **Using your GitHub password instead of the token**
   - Use the token as the password, not your actual GitHub password

