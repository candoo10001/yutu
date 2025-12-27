# Fonts Directory

## Bundled Fonts

This directory contains fonts bundled with the project for cross-platform compatibility.

### NanumSquareB.ttf

- **Font Name**: NanumSquare Bold
- **Language**: Korean (Hangul)
- **Style**: Rounded, friendly, modern
- **Usage**: Video titles and subtitles
- **License**: Open source (SIL Open Font License)

## Why Bundle Fonts?

The font is bundled in the project to ensure consistent rendering across all environments:
- **Local development**: Works on macOS, Linux, and Windows
- **GitHub Actions**: Works in CI/CD without relying on system font paths
- **Consistent appearance**: Same font rendering regardless of platform

## Font Usage in Code

The font is referenced using a project-relative path:

```python
from pathlib import Path
font_path = str(Path(__file__).parent.parent / "fonts" / "NanumSquareB.ttf")
```

This ensures the font can be found regardless of where the code is running.

## GitHub Actions

The GitHub Actions workflow also installs system fonts as a fallback:

```yaml
sudo apt-get install -y fonts-nanum
```

This provides the NanumSquare font family for ASS subtitle rendering, which uses system fonts.
