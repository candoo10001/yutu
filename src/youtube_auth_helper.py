"""
Simplified YouTube Authentication Helper

This module makes OAuth authentication easier for automation by using
a refresh token that never expires (or can be easily refreshed).
"""

import os
import json
from pathlib import Path
from typing import Optional
import structlog

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


class YouTubeAuthHelper:
    """Simplified YouTube authentication using refresh tokens."""

    def __init__(self, logger: Optional[structlog.BoundLogger] = None):
        self.logger = logger or structlog.get_logger()

    def get_credentials_from_env(self) -> Optional[Credentials]:
        """
        Get credentials from environment variables.

        This is the easiest method for automation - just set environment variables
        and you're done. No file management needed!

        Required environment variables:
        - YOUTUBE_CLIENT_ID
        - YOUTUBE_CLIENT_SECRET
        - YOUTUBE_REFRESH_TOKEN

        Returns:
            Credentials object or None if env vars not set
        """
        client_id = os.getenv('YOUTUBE_CLIENT_ID')
        client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
        refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')

        if not all([client_id, client_secret, refresh_token]):
            self.logger.warning(
                "youtube_env_vars_not_set",
                missing_vars=[
                    k for k, v in {
                        'YOUTUBE_CLIENT_ID': client_id,
                        'YOUTUBE_CLIENT_SECRET': client_secret,
                        'YOUTUBE_REFRESH_TOKEN': refresh_token
                    }.items() if not v
                ]
            )
            return None

        # Create credentials from refresh token
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES
        )

        # Refresh to get access token
        try:
            creds.refresh(Request())
            self.logger.info("credentials_refreshed_successfully")
            return creds
        except Exception as e:
            self.logger.error("failed_to_refresh_credentials", error=str(e))
            return None

    def generate_refresh_token(self,
                              client_id: str,
                              client_secret: str,
                              port: int = 8080) -> str:
        """
        Generate a refresh token using OAuth flow.

        This only needs to be run ONCE to get the refresh token.
        After that, you can use the refresh token indefinitely.

        IMPORTANT: Before running this, you must add the redirect URI to Google Cloud Console:
        1. Go to https://console.cloud.google.com/
        2. Navigate to: APIs & Services > Credentials
        3. Click on your OAuth 2.0 Client ID (Desktop app)
        4. Under "Authorized redirect URIs", add: http://localhost:8080/
        5. Click "Save"

        Args:
            client_id: OAuth client ID from Google Cloud Console
            client_secret: OAuth client secret from Google Cloud Console
            port: Port number for local server (default: 8080)

        Returns:
            Refresh token string
        """
        # Create OAuth flow manually without file
        # For Desktop apps, use http://localhost:PORT/ as redirect URI
        redirect_uri = f"http://localhost:{port}/"
        
        flow = InstalledAppFlow.from_client_config(
            client_config={
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            },
            scopes=SCOPES
        )

        # Run local server for OAuth on specified port
        # Use prompt='consent' and access_type='offline' to force refresh token
        creds = flow.run_local_server(
            port=port, 
            open_browser=True,
            authorization_prompt_message='Please visit this URL to authorize this application: {url}',
            success_message='The authentication flow has completed. You may close this window.',
            # Force consent screen to get refresh token
            prompt='consent'
        )

        # Check if we got a refresh token
        if not creds.refresh_token:
            raise ValueError(
                "No refresh token received. This usually means:\n"
                "1. You've already authorized this app before (Google doesn't return refresh token again)\n"
                "2. The OAuth consent screen needs configuration\n"
                "Solution: Go to Google Cloud Console → APIs & Services → OAuth consent screen\n"
                "Make sure your account is added as a test user if the app is in testing mode.\n"
                "Or revoke access first: https://myaccount.google.com/permissions"
            )

        return creds.refresh_token


def main():
    """Interactive setup to get refresh token."""
    import sys

    print("=" * 70)
    print("YouTube Authentication Helper - Get Refresh Token")
    print("=" * 70)
    print()
    print("This script helps you get a REFRESH TOKEN that never expires.")
    print("You only need to run this ONCE!")
    print()
    print("Prerequisites:")
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create OAuth 2.0 credentials (Desktop app)")
    print("3. Copy the Client ID and Client Secret")
    print("4. IMPORTANT: Add redirect URI to your OAuth client:")
    print("   - Go to: APIs & Services > Credentials")
    print("   - Click your OAuth 2.0 Client ID (Desktop app)")
    print("   - Under 'Authorized redirect URIs', add: http://localhost:8080/")
    print("   - Click 'Save'")
    print()

    # Get client credentials
    print("Enter your OAuth credentials:")
    print()
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()

    if not client_id or not client_secret:
        print("\n❌ Error: Client ID and Secret are required!")
        sys.exit(1)

    print()
    print("Generating refresh token...")
    print("Your browser will open for authorization.")
    print()

    auth_helper = YouTubeAuthHelper()

    try:
        refresh_token = auth_helper.generate_refresh_token(
            client_id=client_id,
            client_secret=client_secret
        )

        print()
        print("=" * 70)
        print("✓ SUCCESS!")
        print("=" * 70)
        print()
        print("Your refresh token (save this!):")
        print(f"  {refresh_token}")
        print()
        print("=" * 70)
        print("GitHub Secrets Setup")
        print("=" * 70)
        print()
        print("Add these 3 secrets to your GitHub repository:")
        print()
        print("1. Secret: YOUTUBE_CLIENT_ID")
        print(f"   Value: {client_id}")
        print()
        print("2. Secret: YOUTUBE_CLIENT_SECRET")
        print(f"   Value: {client_secret}")
        print()
        print("3. Secret: YOUTUBE_REFRESH_TOKEN")
        print(f"   Value: {refresh_token}")
        print()
        print("=" * 70)
        print()
        print("That's it! Your automation is now ready to upload to YouTube!")
        print("The refresh token will work indefinitely (or until you revoke it).")
        print()

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ Error!")
        print("=" * 70)
        print()
        print(f"Error: {e}")
        print()
        sys.exit(1)


if __name__ == '__main__':
    main()
