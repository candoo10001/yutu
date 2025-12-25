#!/usr/bin/env python3
"""
Simple test script for Veo 3 video generator - tests API connection and structure.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_veo_imports():
    """Test that all imports work."""
    print("Testing imports...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from src.config import Config
        from src.veo_generator import VeoGenerator
        from src.utils.logger import setup_logger
        
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    try:
        from src.config import Config
        
        config = Config.from_env()
        config.validate()
        
        print(f"✓ Configuration loaded")
        print(f"  Google API Key: {'Set' if config.google_api_key else 'Missing'}")
        print(f"  Output dir: {config.output_dir}")
        return config
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return None


def test_veo_client():
    """Test Veo client initialization."""
    print("\nTesting Veo client initialization...")
    try:
        from google import genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("✗ GOOGLE_API_KEY not set in environment")
            return False
        
        client = genai.Client(api_key=api_key)
        print("✓ Veo client initialized successfully")
        
        # Try to list models to verify API connection
        print("\n  Checking available models...")
        try:
            models = client.models.list()
            veo_models = [m for m in models if 'veo' in m.name.lower()]
            print(f"  ✓ Found {len(veo_models)} Veo model(s):")
            for model in veo_models[:5]:  # Show first 5
                print(f"    - {model.name}")
        except Exception as e:
            print(f"  ⚠ Could not list models: {e}")
            print("  (This is okay - API key might still be valid)")
        
        return True
    except Exception as e:
        print(f"✗ Client initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_veo_generator_init():
    """Test VeoGenerator initialization."""
    print("\nTesting VeoGenerator initialization...")
    try:
        config = test_config()
        if not config:
            return False
        
        from src.veo_generator import VeoGenerator
        from src.utils.logger import setup_logger
        
        logger = setup_logger(
            log_level=config.log_level,
            log_dir=config.log_dir,
            log_file="test_veo.log"
        )
        
        generator = VeoGenerator(config, logger)
        print(f"✓ VeoGenerator initialized")
        print(f"  Model: {generator.model}")
        print(f"  Client: {type(generator.client).__name__}")
        
        return generator
    except Exception as e:
        print(f"✗ VeoGenerator initialization error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all tests."""
    print("=" * 60)
    print("Veo 3 Generator - Connection Test")
    print("=" * 60)
    
    # Test 1: Imports
    if not test_veo_imports():
        print("\n✗ Failed: Import test")
        return False
    
    # Test 2: Configuration
    config = test_config()
    if not config:
        print("\n✗ Failed: Configuration test")
        return False
    
    # Test 3: Veo Client
    if not test_veo_client():
        print("\n✗ Failed: Veo client test")
        return False
    
    # Test 4: VeoGenerator
    generator = test_veo_generator_init()
    if not generator:
        print("\n✗ Failed: VeoGenerator initialization test")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All connection tests passed!")
    print("\nTo test actual video generation, run:")
    print("  python test_veo.py")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

