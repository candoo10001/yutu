#!/usr/bin/env python3
"""
Update metadata file with Korean title and description (Step 7).
Run this for existing videos to add Korean title/description to metadata.
"""
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from src.config import Config
from src.pipeline import VideoPipeline

load_dotenv()


def update_metadata_with_korean_title(metadata_path: str):
    """Update metadata file with Korean title and description."""
    print(f"Reading metadata from: {metadata_path}")
    
    # Load existing metadata
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print("Metadata loaded successfully")
    print(f"Existing keys: {list(metadata.keys())}")
    
    # Get Korean script
    korean_script = metadata.get('korean_script', '')
    if not korean_script:
        print("❌ ERROR: No korean_script found in metadata")
        return False
    
    print(f"Korean script found ({len(korean_script)} chars)")
    
    # Get config for Gemini API
    try:
        config = Config.from_env()
        print("✓ Config loaded")
    except Exception as e:
        print(f"❌ ERROR loading config: {e}")
        return False
    
    # Generate Korean title using pipeline method
    pipeline = VideoPipeline(config)
    
    print("Generating Korean title from script...")
    try:
        # Get korean_article for context (even if title is English)
        korean_article = metadata.get('korean_article', {})
        
        # Generate Korean title
        korean_title = pipeline._generate_korean_title(korean_script, korean_article)
        
        if not korean_title:
            print("⚠️  Title generation failed, using fallback...")
            korean_title = pipeline._extract_title_from_script(korean_script)
        
        print(f"✓ Generated Korean title: {korean_title}")
        
        # Update metadata
        metadata['title'] = korean_title
        metadata['description'] = korean_script[:500] if korean_script else ""
        
        # Save updated metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Metadata updated successfully!")
        print(f"  Title: {korean_title}")
        print(f"  Description: {metadata['description'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    if len(sys.argv) > 1:
        metadata_path = sys.argv[1]
    else:
        # Find latest metadata file
        metadata_files = sorted(Path("output").glob("metadata_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not metadata_files:
            print("❌ ERROR: No metadata files found in output/")
            return 1
        
        metadata_path = str(metadata_files[0])
        print(f"Using latest metadata file: {metadata_path}")
    
    if not Path(metadata_path).exists():
        print(f"❌ ERROR: Metadata file not found: {metadata_path}")
        return 1
    
    success = update_metadata_with_korean_title(metadata_path)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())

