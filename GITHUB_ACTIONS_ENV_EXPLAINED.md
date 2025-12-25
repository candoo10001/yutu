# How Environment Variables Work in GitHub Actions

## Important: `.env` Files vs GitHub Secrets

### ❌ `.env` files are NOT pushed to GitHub

This is **correct and secure**! The `.env` file is in `.gitignore` and should NEVER be committed to git.

### ✅ For GitHub Actions, use GitHub Secrets instead

GitHub Actions **cannot** read `.env` files from your repository. Instead, you need to:

1. **Set secrets in GitHub repository settings**
2. **Reference them in the workflow file** using `${{ secrets.SECRET_NAME }}`

## How It Works

### Local Development (Your Computer)

```bash
# You have a .env file locally
.env:
  NEWS_API_KEY=your_actual_key_here
  CLAUDE_API_KEY=your_actual_key_here
  ...

# This file is NOT committed to git (in .gitignore)
# Python reads it using: load_dotenv() in config.py
```

### GitHub Actions (Cloud Runner)

```yaml
# Workflow file: .github/workflows/daily_video_generation.yml
env:
  NEWS_API_KEY: ${{ secrets.NEWS_API_KEY }}    # Reads from GitHub Secrets
  CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }} # Reads from GitHub Secrets
  ...
```

**GitHub Actions:**
- ✅ Reads secrets from GitHub repository settings
- ❌ Does NOT read `.env` files (they don't exist in the cloud runner)
- ✅ Uses environment variables set in the workflow file

## Current Workflow Configuration

Your workflow file (`.github/workflows/daily_video_generation.yml`) is correctly configured:

```yaml
- name: Generate Daily Video
  env:
    NEWS_API_KEY: ${{ secrets.NEWS_API_KEY }}
    CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
    ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
    LOG_LEVEL: INFO
  run: |
    python main.py
```

This tells GitHub Actions: "Get these values from the repository secrets and set them as environment variables when running `python main.py`."

## What You Need to Do

### Step 1: Add Secrets to GitHub

1. Go to: `https://github.com/candoo10001/yutu/settings/secrets/actions`
2. Click **"New repository secret"**
3. Add each secret:

   **Name:** `NEWS_API_KEY`  
   **Secret:** `your_actual_news_api_key_value`

   **Name:** `CLAUDE_API_KEY`  
   **Secret:** `your_actual_claude_api_key_value`

   **Name:** `GOOGLE_API_KEY`  
   **Secret:** `your_actual_google_api_key_value`

   **Name:** `ELEVENLABS_API_KEY`  
   **Secret:** `your_actual_elevenlabs_api_key_value`

4. Click **"Add secret"** for each one

### Step 2: Get Your API Keys

You can copy them from your local `.env` file:

```bash
# On your local machine, check your .env file
cat .env

# Copy each value and paste it into GitHub Secrets
```

### Step 3: Verify Secrets Are Set

Go back to: `https://github.com/candoo10001/yutu/settings/secrets/actions`

You should see:
- ✅ NEWS_API_KEY
- ✅ CLAUDE_API_KEY
- ✅ GOOGLE_API_KEY
- ✅ ELEVENLABS_API_KEY

**Note:** You won't be able to see the actual values (for security), only that they exist.

## Why This Design?

### Security Reasons:

1. **`.env` files contain sensitive data** (API keys, passwords)
2. **Committing `.env` to git would expose your secrets** to anyone with repository access
3. **GitHub Secrets are encrypted** and only accessible to the repository and GitHub Actions
4. **Secrets can be rotated** without changing code
5. **Different environments** can use different secrets (dev vs production)

## Summary

| Location | Uses | Setup |
|----------|------|-------|
| **Local (your computer)** | `.env` file | Create `.env` locally (not in git) |
| **GitHub Actions (cloud)** | GitHub Secrets | Set in repository settings |

**The `.env` file:**
- ✅ Should exist locally on your computer
- ✅ Should be in `.gitignore` (not committed)
- ❌ Will NOT be used by GitHub Actions
- ✅ Is the source for copying values to GitHub Secrets

**GitHub Secrets:**
- ✅ Are set in repository settings
- ✅ Are referenced in workflow files using `${{ secrets.NAME }}`
- ✅ Are encrypted and secure
- ✅ Are used by GitHub Actions runners

## Quick Checklist

- [ ] `.env` file exists locally (for your development)
- [ ] `.env` is in `.gitignore` (check: `git check-ignore .env` should show `.env`)
- [ ] Secrets are added in GitHub repository settings
- [ ] Workflow file references secrets correctly (`${{ secrets.NAME }}`)
- [ ] All required secrets are set (NEWS_API_KEY, CLAUDE_API_KEY, GOOGLE_API_KEY, ELEVENLABS_API_KEY)

Once all secrets are added to GitHub, the workflow will be able to read them and the error will be resolved!

