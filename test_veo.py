#!/usr/bin/env python3
"""
Test script for Veo 3 video generator.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import Config
from src.veo_generator import VeoGenerator
from src.utils.logger import setup_logger


def test_veo_generator():
    """Test Veo 3 video generation."""
    print("Testing Veo 3 Video Generator...")
    print("=" * 50)
    
    try:
        # Load configuration
        print("\n1. Loading configuration...")
        config = Config.from_env()
        config.validate()
        print("   ✓ Configuration loaded successfully")
        
        # Setup logger
        logger = setup_logger(
            log_level=config.log_level,
            log_dir=config.log_dir,
            log_file="test_veo.log"
        )
        
        # Initialize Veo generator
        print("\n2. Initializing Veo generator...")
        veo_generator = VeoGenerator(config, logger)
        print(f"   ✓ Veo generator initialized with model: {veo_generator.model}")
        
        # Test with a simple prompt
        print("\n3. Generating test video...")
        test_prompt = "A serene landscape with mountains in the background and a calm lake in the foreground, cinematic quality, natural lighting"
        test_korean_script = "이것은 테스트 비디오입니다."  # "This is a test video" in Korean
        
        print(f"   Prompt: {test_prompt[:60]}...")
        print(f"   Korean script: {test_korean_script}")
        print("   This may take a few minutes...")
        
        video_path = veo_generator.generate_video(
            prompt=test_prompt,
            korean_script=test_korean_script,
            aspect_ratio="16:9",
            resolution="720p",
            output_dir="output"
        )
        
        print(f"\n   ✓ Video generated successfully!")
        print(f"   Video path: {video_path}")
        
        # Verify file exists
        if Path(video_path).exists():
            file_size = Path(video_path).stat().st_size
            print(f"   File size: {file_size / (1024 * 1024):.2f} MB")
        else:
            print(f"   ⚠ Warning: Video file not found at {video_path}")
        
        print("\n" + "=" * 50)
        print("Test completed successfully! ✓")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error:")
        print(f"  {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_veo_generator()
    sys.exit(0 if success else 1)

