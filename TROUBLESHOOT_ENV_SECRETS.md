# Troubleshooting Environment Secrets Not Working

## Current Issue

The workflow is reporting "Missing required environment variable: NEWS_API_KEY" even though you've set up environment secrets.

## Possible Causes

### 1. Environment Name Mismatch

The workflow uses `environment: production`, but your environment might have a different name.

**Check:**
- Go to: `https://github.com/candoo10001/yutu/settings/environments`
- What is the exact name of your environment? (case-sensitive!)

**Fix:**
- Either rename the environment to `production`
- Or update the workflow to match your environment name:
  ```yaml
  environment: your-environment-name
  ```

### 2. Secrets Not in the Right Environment

Secrets might be in a different environment or in Repository secrets instead.

**Check:**
1. Go to: `https://github.com/candoo10001/yutu/settings/environments/production` (or your env name)
2. Scroll to **"Environment secrets"** section
3. Verify these secrets exist:
   - `NEWS_API_KEY`
   - `CLAUDE_API_KEY`
   - `GOOGLE_API_KEY`
   - `ELEVENLABS_API_KEY`

**Note:** Secret names are **case-sensitive** and must match exactly!

### 3. Environment Doesn't Exist

The `production` environment might not exist yet.

**Check:**
- Go to: `https://github.com/candoo10001/yutu/settings/environments`
- Do you see `production` in the list?

**Fix:**
- Click **"New environment"**
- Name it: `production`
- Click **"Configure environment"**
- Add your secrets in the "Environment secrets" section

### 4. Secret Names Don't Match

The secret names in GitHub must match exactly what's in the workflow.

**Workflow expects:**
- `NEWS_API_KEY` (uppercase, with underscore)
- `CLAUDE_API_KEY`
- `GOOGLE_API_KEY`
- `ELEVENLABS_API_KEY`

**Check:**
- Make sure there are no typos
- Make sure there are no extra spaces
- Make sure case matches exactly

## Debug Steps Added

I've added a debug step to the workflow that will:
1. Check if secrets are accessible from the environment
2. Show which secrets are missing
3. Show which secrets are set (without revealing values)

Run the workflow and check the "Verify Environment Secrets" step output.

## Quick Checklist

- [ ] Environment `production` exists in GitHub
- [ ] Environment name in workflow matches exactly: `environment: production`
- [ ] Secrets are in the correct environment (not Repository secrets)
- [ ] Secret names match exactly (case-sensitive):
  - [ ] `NEWS_API_KEY`
  - [ ] `CLAUDE_API_KEY`
  - [ ] `GOOGLE_API_KEY`
  - [ ] `ELEVENLABS_API_KEY`
- [ ] Secrets have values (not empty)
- [ ] Workflow has been re-run after adding secrets

## Alternative: Use Repository Secrets Instead

If environment secrets continue to be problematic, you can switch back to Repository secrets:

1. **Remove the environment from workflow:**
   ```yaml
   jobs:
     generate-video:
       runs-on: ubuntu-latest
       # Remove this line: environment: production
   ```

2. **Add secrets to Repository secrets:**
   - Go to: `https://github.com/candoo10001/yutu/settings/secrets/actions`
   - Click **"Repository secrets"** tab
   - Add all secrets there

This is simpler and will work immediately.

## Verify Secrets Are Set

After adding/checking secrets, verify they exist:

1. Go to the environment page: `https://github.com/candoo10001/yutu/settings/environments/production`
2. Under "Environment secrets", you should see:
   - ✅ NEWS_API_KEY
   - ✅ CLAUDE_API_KEY
   - ✅ GOOGLE_API_KEY
   - ✅ ELEVENLABS_API_KEY

**Note:** You won't be able to see the values (for security), only that they exist.

## Next Steps

1. Run the workflow with the new debug step
2. Check the "Verify Environment Secrets" step output
3. It will tell you which secrets are missing
4. Fix any missing secrets
5. Re-run the workflow


