#!/usr/bin/env python3
"""
Test YouTube upload functionality locally.

This script tests YouTube authentication and upload using environment variables.
"""
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
import structlog

from src.youtube_uploader import YouTubeUploader

# Load environment variables from .env file
load_dotenv()


def test_authentication():
    """Test YouTube authentication."""
    print("=" * 70)
    print("Testing YouTube Authentication")
    print("=" * 70)
    print()
    
    # Check environment variables
    client_id = os.getenv('YOUTUBE_CLIENT_ID')
    client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
    refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    
    print("Environment variables check:")
    print(f"  YOUTUBE_CLIENT_ID: {'✓ Set' if client_id else '✗ Missing'}")
    print(f"  YOUTUBE_CLIENT_SECRET: {'✓ Set' if client_secret else '✗ Missing'}")
    print(f"  YOUTUBE_REFRESH_TOKEN: {'✓ Set' if refresh_token else '✗ Missing'}")
    print()
    
    if not all([client_id, client_secret, refresh_token]):
        print("❌ ERROR: Missing required environment variables!")
        print()
        print("Please add these to your .env file:")
        print("  YOUTUBE_CLIENT_ID=your_client_id")
        print("  YOUTUBE_CLIENT_SECRET=your_client_secret")
        print("  YOUTUBE_REFRESH_TOKEN=your_refresh_token")
        print()
        print("To get a refresh token, run:")
        print("  python -m src.youtube_auth_helper")
        return False
    
    logger = structlog.get_logger()
    uploader = YouTubeUploader(logger=logger)
    
    try:
        print("Attempting authentication...")
        uploader.authenticate()
        print("✅ Authentication successful!")
        print()
        return True
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print()
        return False


def test_upload(metadata_file: str):
    """Test YouTube video upload."""
    print("=" * 70)
    print("Testing YouTube Video Upload")
    print("=" * 70)
    print()
    
    if not os.path.exists(metadata_file):
        print(f"❌ ERROR: Metadata file not found: {metadata_file}")
        return False
    
    logger = structlog.get_logger()
    uploader = YouTubeUploader(logger=logger)
    
    try:
        print("Authenticating...")
        uploader.authenticate()
        print("✓ Authenticated")
        print()
        
        print(f"Uploading video from metadata: {metadata_file}")
        video_id = uploader.upload_from_metadata(metadata_file)
        print()
        print("✅ Video uploaded successfully!")
        print(f"  Video ID: {video_id}")
        print(f"  URL: https://www.youtube.com/shorts/{video_id}")
        print()
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        print()
        return False


def main():
    """Main test function."""
    if len(sys.argv) > 1:
        # Test upload with metadata file
        metadata_file = sys.argv[1]
        if test_authentication():
            test_upload(metadata_file)
    else:
        # Just test authentication
        test_authentication()
        print()
        print("To test upload, run:")
        print("  python test_youtube_upload.py <path_to_metadata.json>")


if __name__ == '__main__':
    main()


