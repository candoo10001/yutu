# GitHub Actions Permission Fix

## Issue Fixed

The workflow was failing with:
```
HttpError: Resource not accessible by integration
status: 403
```

This was because the workflow didn't have permission to create issues.

## Solution Applied

Added `permissions` section to the workflow:

```yaml
permissions:
  contents: read
  issues: write
  pull-requests: read
```

- `contents: read` - Read repository contents (required for checkout)
- `issues: write` - Create issues when workflow fails (this was missing!)
- `pull-requests: read` - Read pull requests (if needed)

## Additional Updates

Also fixed environment variables to match `src/config.py`:

### Changed:
- ❌ `KLING_API_KEY` (old, incorrect)
- ✅ `KLING_ACCESS_KEY` (correct)
- ✅ `KLING_SECRET_KEY` (correct, added)

### Added:
- ✅ `GOOGLE_API_KEY` (was missing)

## Required GitHub Secrets

Make sure these secrets are configured in your repository:

**Settings → Secrets and variables → Actions → New repository secret**

1. `NEWS_API_KEY`
2. `CLAUDE_API_KEY`
3. `GOOGLE_API_KEY`
4. `KLING_ACCESS_KEY`
5. `KLING_SECRET_KEY`
6. `ELEVENLABS_API_KEY`
7. `YOUTUBE_CLIENT_ID` (for YouTube upload)
8. `YOUTUBE_CLIENT_SECRET` (for YouTube upload)
9. `YOUTUBE_REFRESH_TOKEN` (for YouTube upload)

## Verify the Fix

1. Commit and push the updated workflow file
2. Run the workflow manually (or wait for scheduled run)
3. If it fails, it should now successfully create an issue instead of erroring out

## What Changed

**Before:**
```yaml
jobs:
  generate-video:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      # ... no permissions defined
```

**After:**
```yaml
jobs:
  generate-video:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    permissions:
      contents: read
      issues: write
      pull-requests: read

    steps:
      # ... permissions now granted
```

The workflow can now:
- ✅ Create issues when it fails
- ✅ Read repository contents
- ✅ Access all required secrets

