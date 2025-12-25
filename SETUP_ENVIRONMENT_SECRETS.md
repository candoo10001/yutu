# Setup Environment Secrets for GitHub Actions

## Workflow Updated ✅

The workflow has been updated to use an environment called `production`. This means it will now read secrets from **Environment secrets** instead of Repository secrets.

## Next Steps

### Step 1: Create the Environment (if it doesn't exist)

1. Go to: `https://github.com/candoo10001/yutu/settings/environments`
2. If you don't see `production`, click **"New environment"**
3. Name it: `production`
4. Click **"Configure environment"**

### Step 2: Add Secrets to the Environment

1. Still on the environment page: `https://github.com/candoo10001/yutu/settings/environments/production`
2. Scroll down to **"Environment secrets"** section
3. Click **"Add secret"** (or verify your existing secrets are there)
4. Make sure you have:
   - `NEWS_API_KEY`
   - `CLAUDE_API_KEY`
   - `GOOGLE_API_KEY`
   - `ELEVENLABS_API_KEY`
   - `YOUTUBE_CLIENT_ID` (optional, for YouTube upload)
   - `YOUTUBE_CLIENT_SECRET` (optional, for YouTube upload)
   - `YOUTUBE_REFRESH_TOKEN` (optional, for YouTube upload)

### Step 3: Verify Environment Configuration

Your environment page should show:
- **Environment name:** `production`
- **Environment secrets:** (list of all your secrets)

## How It Works Now

### Before (Repository Secrets):
```yaml
jobs:
  generate-video:
    runs-on: ubuntu-latest
    # No environment specified
    # Secrets read from: Repository secrets
```

### After (Environment Secrets):
```yaml
jobs:
  generate-video:
    runs-on: ubuntu-latest
    environment: production  # <-- Added this
    # Secrets read from: Environment secrets (production)
```

The workflow will now:
1. Look for the `production` environment
2. Read secrets from that environment's secrets
3. Use those secrets when running the workflow

## Benefits of Using Environments

1. **Better organization** - Group secrets by environment (dev, staging, production)
2. **Environment protection** - Can require approvals before running
3. **Different secrets per environment** - Use different API keys for dev vs production
4. **Better access control** - Control who can access which environment

## Change Environment Name

If you want to use a different environment name:

1. Update the workflow file:
   ```yaml
   environment: your-env-name  # Change this
   ```

2. Create/configure that environment in GitHub settings

## Testing

After setting up the environment and secrets:

1. Go to: `https://github.com/candoo10001/yutu/actions`
2. Run the workflow manually (if `workflow_dispatch` is enabled)
3. Check the logs - it should now find the secrets from the environment

## Troubleshooting

### Error: "Environment 'production' not found"

**Fix:** Create the environment first:
- Go to: `https://github.com/candoo10001/yutu/settings/environments`
- Click "New environment"
- Name it `production`

### Error: "Missing required environment variable: NEWS_API_KEY"

**Fix:** Make sure the secret exists in the environment:
- Go to: `https://github.com/candoo10001/yutu/settings/environments/production`
- Check "Environment secrets" section
- Add `NEWS_API_KEY` if it's missing

### Want to use a different environment name?

Just change `environment: production` to any name you want in the workflow file, then create that environment in GitHub settings.

