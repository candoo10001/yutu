#!/usr/bin/env python3
"""
Quick script to check the status of your predefined media library.
"""
from pathlib import Path
from collections import defaultdict


def check_media_library():
    """Check and display the status of predefined media library."""
    media_dir = Path("predefined_media")

    if not media_dir.exists():
        print("❌ predefined_media/ folder not found")
        return

    print("=" * 60)
    print("📁 PREDEFINED MEDIA LIBRARY STATUS")
    print("=" * 60)
    print()

    # Get all category folders
    categories = sorted([d for d in media_dir.iterdir() if d.is_dir() and not d.name.startswith('.')])

    if not categories:
        print("⚠️  No category folders found in predefined_media/")
        print()
        print("To get started, create folders for common topics:")
        print("  mkdir -p predefined_media/{ai,crypto,stock-market,economy}")
        return

    # Count files in each category
    total_files = 0
    category_stats = []

    for category in categories:
        # Count images
        images = list(category.glob("*.jpg")) + list(category.glob("*.jpeg")) + \
                 list(category.glob("*.png")) + list(category.glob("*.webp"))
        # Count videos
        videos = list(category.glob("*.mp4")) + list(category.glob("*.mov")) + \
                 list(category.glob("*.avi"))

        total = len(images) + len(videos)
        total_files += total

        category_stats.append({
            'name': category.name,
            'images': len(images),
            'videos': len(videos),
            'total': total
        })

    # Display statistics
    print(f"Total Categories: {len(categories)}")
    print(f"Total Media Files: {total_files}")
    print()

    # Display by category
    print("-" * 60)
    print(f"{'Category':<25} {'Images':<10} {'Videos':<10} {'Total':<10}")
    print("-" * 60)

    for stat in sorted(category_stats, key=lambda x: x['total'], reverse=True):
        status = "✓" if stat['total'] > 0 else "○"
        print(f"{status} {stat['name']:<23} {stat['images']:<10} {stat['videos']:<10} {stat['total']:<10}")

    print("-" * 60)
    print()

    # Provide recommendations
    empty_categories = [s['name'] for s in category_stats if s['total'] == 0]

    if empty_categories:
        print("📌 RECOMMENDATIONS:")
        print()
        print(f"You have {len(empty_categories)} empty categories.")
        print("Consider adding media files to these high-priority categories:")
        print()

        priority_categories = ['ai', 'stock-market', 'crypto', 'economy', 'bitcoin', 'tesla', 'technology']
        empty_priority = [c for c in priority_categories if c in empty_categories]

        if empty_priority:
            for cat in empty_priority[:5]:
                print(f"  • {cat}/")
            print()
            print("Visit https://www.pexels.com/ and search for:")
            for cat in empty_priority[:5]:
                if cat == 'ai':
                    print(f"  - '{cat}' → 'artificial intelligence technology'")
                elif cat == 'stock-market':
                    print(f"  - '{cat}' → 'stock market trading'")
                elif cat == 'bitcoin' or cat == 'crypto':
                    print(f"  - '{cat}' → 'cryptocurrency bitcoin'")
                else:
                    print(f"  - '{cat}'")
    else:
        print("✅ Great! All categories have media files.")
        print()
        print("Consider adding more variety to popular categories:")
        top_5 = sorted(category_stats, key=lambda x: x['total'], reverse=True)[:5]
        for stat in top_5:
            print(f"  • {stat['name']}: {stat['total']} files")

    print()
    print("=" * 60)
    print()
    print("💡 TIP: Aim for 5-10 files per category for good variety")
    print("📖 For more info, see predefined_media/README.md")
    print()


if __name__ == "__main__":
    check_media_library()
