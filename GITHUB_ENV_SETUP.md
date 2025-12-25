# How to Configure .env in GitHub

This guide explains how to securely manage environment variables in GitHub for your Vidmore project.

## Table of Contents

1. [Local Development (.env file)](#local-development)
2. [GitHub Secrets (for CI/CD)](#github-secrets)
3. [GitHub Actions Workflow](#github-actions-workflow)
4. [Best Practices](#best-practices)

## Local Development

### 1. Create Your Local .env File

Copy the example file:

```bash
cp .env.example .env
```

### 2. Edit .env with Your API Keys

Open `.env` and add your actual API keys:

```env
NEWS_API_KEY=your_actual_news_api_key
CLAUDE_API_KEY=your_actual_claude_api_key
GOOGLE_API_KEY=your_actual_google_api_key
KLING_ACCESS_KEY=your_actual_kling_access_key
KLING_SECRET_KEY=your_actual_kling_secret_key
ELEVENLABS_API_KEY=your_actual_elevenlabs_api_key
```

### 3. Verify .env is in .gitignore

The `.env` file is already configured to be ignored by git (check `.gitignore`). **Never commit your `.env` file!**

## GitHub Secrets (for CI/CD)

If you want to run your pipeline via GitHub Actions, you need to store secrets in GitHub.

### Step 1: Go to Repository Settings

1. Go to your GitHub repository: `https://github.com/candoo10001/yutu`
2. Click **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**

### Step 2: Add Repository Secrets

Click **"New repository secret"** and add each of these secrets:

#### Required Secrets:

1. **Name:** `NEWS_API_KEY`
   - **Value:** Your News API key

2. **Name:** `CLAUDE_API_KEY`
   - **Value:** Your Claude API key from Anthropic

3. **Name:** `GOOGLE_API_KEY`
   - **Value:** Your Google Cloud API key

4. **Name:** `KLING_ACCESS_KEY`
   - **Value:** Your Kling AI access key

5. **Name:** `KLING_SECRET_KEY`
   - **Value:** Your Kling AI secret key

6. **Name:** `ELEVENLABS_API_KEY`
   - **Value:** Your ElevenLabs API key

#### Optional Secrets:

7. **Name:** `ELEVENLABS_VOICE_ID` (optional)
   - **Value:** Your preferred Korean voice ID

8. **Name:** `NEWS_CATEGORY` (optional, defaults to "business")
   - **Value:** `business`, `technology`, etc.

9. **Name:** `NEWS_COUNTRY` (optional, defaults to "us")
   - **Value:** `us`, `kr`, `gb`, etc.

### Step 3: Verify Secrets

After adding all secrets, you should see them listed under **"Repository secrets"**:

- ✅ NEWS_API_KEY
- ✅ CLAUDE_API_KEY
- ✅ GOOGLE_API_KEY
- ✅ KLING_ACCESS_KEY
- ✅ KLING_SECRET_KEY
- ✅ ELEVENLABS_API_KEY
- (and any optional ones you added)

## GitHub Actions Workflow

If you have a GitHub Actions workflow (`.github/workflows/daily_video_generation.yml`), it should reference these secrets like this:

```yaml
env:
  NEWS_API_KEY: ${{ secrets.NEWS_API_KEY }}
  CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
  GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
  KLING_ACCESS_KEY: ${{ secrets.KLING_ACCESS_KEY }}
  KLING_SECRET_KEY: ${{ secrets.KLING_SECRET_KEY }}
  ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
```

### Example Workflow File

Create or update `.github/workflows/daily_video_generation.yml`:

```yaml
name: Daily Video Generation

on:
  schedule:
    - cron: '0 9 * * *'  # Run daily at 9 AM UTC (6 PM KST)
  workflow_dispatch:  # Allow manual runs

jobs:
  generate-video:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Install ffmpeg
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg
      
      - name: Run video generation pipeline
        env:
          NEWS_API_KEY: ${{ secrets.NEWS_API_KEY }}
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
          KLING_ACCESS_KEY: ${{ secrets.KLING_ACCESS_KEY }}
          KLING_SECRET_KEY: ${{ secrets.KLING_SECRET_KEY }}
          ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
          ELEVENLABS_VOICE_ID: ${{ secrets.ELEVENLABS_VOICE_ID }}
          NEWS_CATEGORY: ${{ secrets.NEWS_CATEGORY || 'business' }}
          NEWS_COUNTRY: ${{ secrets.NEWS_COUNTRY || 'us' }}
        run: |
          python main.py
      
      - name: Upload video artifact
        uses: actions/upload-artifact@v3
        with:
          name: generated-video
          path: output/*.mp4
          retention-days: 7
```

## Best Practices

### ✅ Do:

1. **Keep `.env` in `.gitignore`** (already done)
2. **Commit `.env.example`** as a template (already done)
3. **Use GitHub Secrets** for CI/CD workflows
4. **Rotate secrets regularly** for security
5. **Use different API keys** for development and production if possible

### ❌ Don't:

1. **Never commit `.env`** file to git
2. **Never share API keys** in code, issues, or pull requests
3. **Never hardcode secrets** in your Python files
4. **Don't print API keys** in logs (use `Config.__repr__()` which hides them)

## Verifying Your Setup

### Local Development

```bash
# Check if .env exists and is ignored
ls -la .env
git status  # Should NOT show .env

# Test that config loads
python -c "from src.config import Config; c = Config.from_env(); print('✅ Config loaded')"
```

### GitHub Secrets

1. Go to: `https://github.com/candoo10001/yutu/settings/secrets/actions`
2. Verify all required secrets are listed
3. Check that values are set (you won't see the actual values, just that they exist)

### GitHub Actions

1. Go to: `https://github.com/candoo10001/yutu/actions`
2. Run a workflow manually (if `workflow_dispatch` is enabled)
3. Check the logs to verify secrets are being used

## Troubleshooting

### "Missing required environment variable" Error

**Local:**
- Check that `.env` file exists: `ls -la .env`
- Verify the variable name matches exactly (case-sensitive)
- Check for typos or extra spaces

**GitHub Actions:**
- Verify the secret exists in repository settings
- Check that the secret name in workflow matches exactly
- Ensure `${{ secrets.SECRET_NAME }}` syntax is correct

### Secrets Not Working in GitHub Actions

1. Check repository settings → Secrets and variables → Actions
2. Verify secrets are named correctly (case-sensitive)
3. Check workflow YAML syntax
4. Look at workflow logs for specific error messages

## Quick Reference

| Location | Purpose | File/Setting |
|----------|---------|--------------|
| Local dev | Your actual API keys | `.env` (not in git) |
| Template | Example structure | `.env.example` (in git) |
| CI/CD | Secrets for workflows | GitHub Settings → Secrets |
| Workflow | Use secrets | `.github/workflows/*.yml` |

## Need Help?

- Check the main README.md for more details
- Review `.env.example` for all available variables
- Check `src/config.py` for default values and validation rules

