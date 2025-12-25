"""
YouTube Uploader for Korean News Shorts

Uploads generated videos to YouTube as Shorts.
"""

import os
import json
import pickle
from pathlib import Path
from typing import Optional
import structlog

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

try:
    from .youtube_auth_helper import YouTubeAuthHelper
except ImportError:
    # Fallback for when running as a script directly
    from youtube_auth_helper import YouTubeAuthHelper


# If modifying these scopes, delete the token.pickle file
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


class YouTubeUploader:
    """Handles uploading videos to YouTube."""

    def __init__(self, logger: Optional[structlog.BoundLogger] = None):
        self.logger = logger or structlog.get_logger()
        self.youtube = None
        self.auth_helper = YouTubeAuthHelper(logger=logger)

    def authenticate(self, credentials_file: str = 'client_secrets.json',
                    token_file: str = 'token.pickle') -> None:
        """
        Authenticate with YouTube API.

        Tries authentication methods in this order:
        1. Environment variables (easiest for automation)
        2. Token file (if exists)
        3. OAuth flow with credentials file

        Args:
            credentials_file: Path to OAuth client secrets JSON file
            token_file: Path to save/load token pickle file
        """
        creds = None

        # Method 1: Try environment variables first (best for automation)
        self.logger.info("trying_env_var_authentication")
        creds = self.auth_helper.get_credentials_from_env()

        if creds:
            self.logger.info("authenticated_via_env_vars")
            self.youtube = build('youtube', 'v3', credentials=creds)
            return

        # Method 2: Load token from file if it exists
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("refreshing_expired_credentials")
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_file):
                    raise FileNotFoundError(
                        f"OAuth credentials file not found: {credentials_file}\n"
                        "Download it from Google Cloud Console and save as client_secrets.json\n"
                        "OR set environment variables: YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN"
                    )

                self.logger.info("initiating_oauth_flow")
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

            self.logger.info("credentials_saved", token_file=token_file)

        # Build YouTube API client
        self.youtube = build('youtube', 'v3', credentials=creds)
        self.logger.info("youtube_api_authenticated")

    def upload_video(self,
                    video_path: str,
                    title: str,
                    description: str,
                    tags: list[str] = None,
                    category_id: str = "25",  # News & Politics
                    privacy_status: str = "public") -> str:
        """
        Upload a video to YouTube as a Short.

        Args:
            video_path: Path to video file
            title: Video title (max 100 chars)
            description: Video description
            tags: List of tags
            category_id: YouTube category (25 = News & Politics)
            privacy_status: 'public', 'private', or 'unlisted'

        Returns:
            Video ID of uploaded video
        """
        if not self.youtube:
            raise ValueError("Not authenticated. Call authenticate() first.")

        # Validate video path
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Add #Shorts to title and description for YouTube Shorts
        if '#Shorts' not in title and len(title) < 92:
            title = f"{title} #Shorts"

        if '#Shorts' not in description:
            description = f"{description}\n\n#Shorts #KoreanNews #뉴스"

        # Prepare video metadata
        body = {
            'snippet': {
                'title': title[:100],  # YouTube limit
                'description': description[:5000],  # YouTube limit
                'tags': tags or ['Shorts', 'News', 'Korean', '뉴스', '한국뉴스'],
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False,
            }
        }

        # Create MediaFileUpload object
        media = MediaFileUpload(
            video_path,
            mimetype='video/mp4',
            resumable=True,
            chunksize=1024*1024  # 1MB chunks
        )

        try:
            self.logger.info("uploading_video_to_youtube",
                           video_path=video_path,
                           title=title[:50])

            # Execute upload request
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    self.logger.info("upload_progress",
                                   progress_percent=progress)

            video_id = response['id']
            video_url = f"https://www.youtube.com/shorts/{video_id}"

            self.logger.info("video_uploaded_successfully",
                           video_id=video_id,
                           video_url=video_url)

            return video_id

        except HttpError as e:
            self.logger.error("youtube_upload_failed",
                            error=str(e),
                            video_path=video_path)
            raise

    def upload_from_metadata(self, metadata_path: str) -> str:
        """
        Upload video using metadata JSON file.

        Args:
            metadata_path: Path to metadata JSON file

        Returns:
            Video ID of uploaded video
        """
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        video_path = metadata.get('video_path')
        if not video_path or not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found from metadata: {video_path}")

        # Extract title and description from metadata
        title = metadata.get('title', 'Korean News Short')
        description = metadata.get('description', '')

        # Add article source to description
        if 'article' in metadata:
            article = metadata['article']
            description += f"\n\nSource: {article.get('source', {}).get('name', 'Unknown')}"
            if article.get('url'):
                description += f"\nRead more: {article['url']}"

        # Extract tags from metadata
        tags = metadata.get('tags', [])
        tags.extend(['Shorts', 'News', 'Korean', '뉴스', '한국뉴스'])

        return self.upload_video(
            video_path=video_path,
            title=title,
            description=description,
            tags=list(set(tags))  # Remove duplicates
        )


def main():
    """Test YouTube uploader."""
    import sys

    logger = structlog.get_logger()

    if len(sys.argv) < 2:
        print("Usage: python youtube_uploader.py <video_file_or_metadata_json>")
        sys.exit(1)

    file_path = sys.argv[1]

    uploader = YouTubeUploader(logger=logger)
    uploader.authenticate()

    if file_path.endswith('.json'):
        video_id = uploader.upload_from_metadata(file_path)
    elif file_path.endswith('.mp4'):
        video_id = uploader.upload_video(
            video_path=file_path,
            title="Korean News Short #Shorts",
            description="Latest Korean news in short format.\n\n#Shorts #News #Korean"
        )
    else:
        print("File must be .mp4 or .json")
        sys.exit(1)

    print(f"✓ Video uploaded successfully!")
    print(f"  Video ID: {video_id}")
    print(f"  URL: https://www.youtube.com/shorts/{video_id}")


if __name__ == '__main__':
    main()
