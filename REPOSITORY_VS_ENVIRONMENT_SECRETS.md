# Repository Secrets vs Environment Secrets

## The Issue

You set up secrets in **"Environment secrets"** but the workflow is looking for **"Repository secrets"**.

## Difference

### Repository Secrets
- Accessible to all workflows in the repository
- Referenced as: `${{ secrets.SECRET_NAME }}`
- Location: Settings → Secrets and variables → Actions → **Repository secrets**

### Environment Secrets
- Only accessible when a workflow uses a specific environment
- Referenced as: `${{ secrets.SECRET_NAME }}` (but only if environment is set)
- Location: Settings → Environments → [Environment Name] → **Environment secrets**

## Solution 1: Use Repository Secrets (Recommended - Simplest)

**Copy your secrets from Environment secrets to Repository secrets:**

1. Go to: `https://github.com/candoo10001/yutu/settings/secrets/actions`
2. Click **"Repository secrets"** tab (NOT "Environments")
3. Click **"New repository secret"**
4. Add each secret:
   - NEWS_API_KEY
   - CLAUDE_API_KEY
   - GOOGLE_API_KEY
   - ELEVENLABS_API_KEY
   - (and any others you need)

This is the simplest solution and matches your current workflow configuration.

## Solution 2: Use Environment Secrets (Keep Current Setup)

If you want to keep using Environment secrets, you need to:

1. **Create an environment** (if you haven't already):
   - Go to: `https://github.com/candoo10001/yutu/settings/environments`
   - Click **"New environment"**
   - Name it: `production` (or any name)

2. **Add the secrets to that environment:**
   - Go to: `https://github.com/candoo10001/yutu/settings/environments/production` (or your env name)
   - Add all the secrets there

3. **Update the workflow to use the environment:**

```yaml
jobs:
  generate-video:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    environment: production  # <-- Add this line
    
    permissions:
      contents: read
      issues: write
      pull-requests: read
    
    steps:
      # ... rest of workflow
```

## Recommendation

**Use Solution 1 (Repository Secrets)** because:
- ✅ Simpler - no need to create/manage environments
- ✅ Your workflow already uses `${{ secrets.NAME }}` syntax (which defaults to repository secrets)
- ✅ Works immediately without workflow changes
- ✅ Sufficient for most use cases

**Use Solution 2 (Environment Secrets)** only if:
- You need different secrets for different environments (dev/staging/production)
- You want environment-specific protection rules
- You're using environment protection rules (required reviewers, etc.)

## Quick Fix Steps (Solution 1)

1. Go to: `https://github.com/candoo10001/yutu/settings/secrets/actions`
2. Make sure you're on the **"Repository secrets"** tab
3. Click **"New repository secret"**
4. Add:
   - `NEWS_API_KEY` = [your value]
   - `CLAUDE_API_KEY` = [your value]
   - `GOOGLE_API_KEY` = [your value]
   - `ELEVENLABS_API_KEY` = [your value]
5. Save each one

Your workflow will immediately be able to access these!

## How to Check

After adding Repository secrets, you should see them listed under:
**Settings → Secrets and variables → Actions → Repository secrets**

You'll see:
- ✅ NEWS_API_KEY
- ✅ CLAUDE_API_KEY
- ✅ GOOGLE_API_KEY
- ✅ ELEVENLABS_API_KEY

Note: You can't see the values (for security), only that they exist.


