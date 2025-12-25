# Quick Start: Setting Up Your Media Library

Get your predefined media library up and running in **15 minutes**!

## Step 1: Check Current Status (30 seconds)

Run the checker script:
```bash
python check_media_library.py
```

This will show you which folders exist and which need media files.

## Step 2: Download Essential Media (10 minutes)

Visit **Pexels.com** (no account required, free for commercial use):

### Priority Downloads

1. **Stock Market** (search: "stock market trading")
   - Download 3-5 vertical videos
   - Save to: `predefined_media/stock-market/`
   - Look for: charts, trading floors, financial graphs

2. **AI/Technology** (search: "artificial intelligence")
   - Download 3-5 videos
   - Save to: `predefined_media/ai/`
   - Look for: robots, circuits, data visualization

3. **Cryptocurrency** (search: "bitcoin cryptocurrency")
   - Download 3-5 videos/images
   - Save to: `predefined_media/crypto/` and `predefined_media/bitcoin/`
   - Look for: crypto coins, blockchain, digital currency

4. **Economy** (search: "economic growth")
   - Download 3-5 videos
   - Save to: `predefined_media/economy/`
   - Look for: growth charts, money, economic indicators

5. **Business** (search: "business corporate")
   - Download 3-5 videos
   - Save to: `predefined_media/business/`
   - Look for: office, meetings, professionals

## Step 3: Organize Files (2 minutes)

Rename files with descriptive names:
```
predefined_media/
├── ai/
│   ├── robot-1.mp4
│   ├── circuit-board.mp4
│   └── data-viz.mp4
├── stock-market/
│   ├── trading-floor-1.mp4
│   ├── stock-chart-1.mp4
│   └── wall-street.mp4
└── ...
```

## Step 4: Test It! (2 minutes)

Run the checker again:
```bash
python check_media_library.py
```

You should see files in your categories now!

## Step 5: Run Generator

Generate a video and check the logs:
```bash
python main.py
```

Check `logs/pipeline.log` for lines like:
```
predefined_media_matched - selected_file=predefined_media/ai/robot-1.mp4
```

This means it's working! 🎉

## Best Websites for Quick Downloads

### 1. Pexels (Recommended)
- **URL**: https://www.pexels.com/
- **Why**: No signup, high quality, vertical videos
- **Download**: Click video → "Free Download" → Choose size

### 2. Pixabay
- **URL**: https://pixabay.com/
- **Why**: Good variety, includes illustrations
- **Download**: Click media → "Free Download"

### 3. Coverr (Great for Business Videos)
- **URL**: https://coverr.co/
- **Why**: Short clips perfect for news segments
- **Download**: Click video → "Free Download"

## Pro Tips

1. **Prefer Videos Over Images**: Videos look more dynamic
2. **Vertical Format**: Filter for "vertical" or 9:16 aspect ratio
3. **No Text**: Avoid media with embedded text
4. **HD Quality**: Download at least 1080p
5. **Batch Download**: Download 5 at once, organize later

## Common Topics to Prioritize

Based on typical business news, focus on:

1. **Stock Market** ⭐⭐⭐⭐⭐ (most common)
2. **AI/Technology** ⭐⭐⭐⭐⭐
3. **Cryptocurrency** ⭐⭐⭐⭐
4. **Economy** ⭐⭐⭐⭐
5. **Tesla/EVs** ⭐⭐⭐
6. **Business/Corporate** ⭐⭐⭐
7. **Banking/Finance** ⭐⭐
8. **Energy** ⭐⭐
9. **Real Estate** ⭐

## Troubleshooting

**Q: My videos aren't being used**
- Check file extensions (must be .mp4, .mov, .avi, .jpg, .png, .webp)
- Check file names don't have special characters
- Run `python check_media_library.py` to verify files are detected

**Q: How do I know which keywords to use?**
- See the full keyword list in `predefined_media/README.md`
- Check your logs to see what topics appear in your news

**Q: Can I add my own categories?**
- Yes! Just create a new folder and add media files
- Update `media_matcher.py` keyword mappings if needed

**Q: How many files do I need?**
- Start with 3-5 per category
- Expand to 10+ for variety
- Monitor usage in logs to prioritize

## Example: 15-Minute Setup

1. Visit https://www.pexels.com/search/videos/stock%20market/
2. Download 5 vertical videos → `predefined_media/stock-market/`
3. Visit https://www.pexels.com/search/videos/artificial%20intelligence/
4. Download 5 videos → `predefined_media/ai/`
5. Visit https://www.pexels.com/search/videos/bitcoin/
6. Download 5 videos → `predefined_media/crypto/` and `predefined_media/bitcoin/`
7. Run `python check_media_library.py` → should show 15 files
8. Run `python main.py` → watch the magic! ✨

---

You're all set! Your media library will save you money on API costs while making your videos look great! 🚀
