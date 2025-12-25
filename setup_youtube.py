"""
YouTube OAuth Setup Script

Run this script locally to authenticate with YouTube and generate tokens.
"""

import os
import pickle
import base64
from pathlib import Path

from src.youtube_uploader import YouTubeUploader
import structlog


def main():
    """Setup YouTube authentication."""
    logger = structlog.get_logger()

    print("=" * 60)
    print("YouTube OAuth Setup")
    print("=" * 60)
    print()
    print("This script will help you set up YouTube authentication.")
    print()
    print("Prerequisites:")
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select existing project")
    print("3. Enable YouTube Data API v3")
    print("4. Create OAuth 2.0 credentials (Desktop application)")
    print("5. Download the client secrets JSON file")
    print("6. Save it as 'client_secrets.json' in this directory")
    print()

    # Check if client_secrets.json exists
    if not os.path.exists('client_secrets.json'):
        print("❌ ERROR: client_secrets.json not found!")
        print()
        print("Please download your OAuth credentials and save as:")
        print("  -> client_secrets.json")
        print()
        return

    print("✓ Found client_secrets.json")
    print()

    # Authenticate
    uploader = YouTubeUploader(logger=logger)

    print("Starting OAuth flow...")
    print("Your browser will open to authorize this application.")
    print()

    try:
        uploader.authenticate(
            credentials_file='client_secrets.json',
            token_file='token.pickle'
        )

        print()
        print("=" * 60)
        print("✓ Authentication successful!")
        print("=" * 60)
        print()

        # Read token.pickle and encode as base64
        with open('token.pickle', 'rb') as f:
            token_data = f.read()
            token_base64 = base64.b64encode(token_data).decode('utf-8')

        # Read client_secrets.json
        with open('client_secrets.json', 'r') as f:
            client_secrets = f.read()

        print("Setup complete! Now add these secrets to your GitHub repository:")
        print()
        print("GitHub Repository → Settings → Secrets and variables → Actions")
        print()
        print("1. Create secret: YOUTUBE_CLIENT_SECRETS")
        print("   Value:")
        print(f"   {client_secrets}")
        print()
        print("2. Create secret: YOUTUBE_TOKEN")
        print("   Value:")
        print(f"   {token_base64}")
        print()
        print("=" * 60)
        print()
        print("After adding these secrets, your GitHub Actions workflow")
        print("will automatically upload videos to YouTube!")
        print()

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Authentication failed!")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()


if __name__ == '__main__':
    main()
