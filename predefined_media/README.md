# Pre-Defined Media Library

This folder contains pre-defined images and videos that can be used instead of generating new ones, saving on API costs.

## How It Works

The system automatically matches segment content to media files based on keywords:

1. **Keyword Detection**: The system analyzes segment text and title for keywords
2. **Folder Matching**: Maps keywords to appropriate media folders
3. **Random Selection**: Randomly picks one file from matching folders
4. **Duration Matching**: Automatically adjusts video/image duration to match audio
5. **Fallback**: If no match found, generates a new image using Gemini API

### Video Duration Handling

**For Pre-defined Videos:**
- **Video shorter than audio** → Automatically loops the video until it matches audio duration
- **Video longer than audio** → Automatically trims the video to match audio duration
- **Example**: 3-second video + 7-second audio → video loops 3 times and trims to 7 seconds

**For Images:**
- Applies dynamic Ken Burns effect (zoom + pan) to match audio duration
- Creates engaging motion even from static images

This means you can use videos of **any length** - the system will automatically adjust them!

## Folder Structure

Create subfolders for different topics/keywords. Each folder can contain multiple images or videos:

```
predefined_media/
├── ai/                    # AI, artificial intelligence, machine learning
├── crypto/                # Cryptocurrency, Bitcoin, blockchain
├── bitcoin/               # Bitcoin-specific content
├── ethereum/              # Ethereum-specific content
├── tesla/                 # Tesla motors, electric vehicles
├── stock-market/          # Stock market, trading, Wall Street
├── economy/               # Economic trends, GDP, growth
├── banking/               # Banks, Federal Reserve, finance
├── technology/            # General tech, innovation
├── electric-vehicles/     # EVs, electric cars
├── energy/                # Oil, renewable energy
├── real-estate/           # Housing, property, real estate
├── business/              # General business, corporate
├── office/                # Office scenes, workspace
├── money/                 # Currency, cash, finance
├── growth/                # Growth charts, success
├── crisis/                # Economic crisis, downturns
└── ...
```

## Supported Formats

- **Images**: JPG, JPEG, PNG, WEBP
- **Videos**: MP4, MOV, AVI

## Keyword Mappings

The system recognizes these keywords and maps them to folders:

### AI & Technology
- `ai`, `artificial intelligence`, `machine learning` → ai/, technology/
- `tech`, `technology`, `robot`, `automation` → technology/, ai/
- `nvidia` → nvidia/, ai/, chips/

### Cryptocurrency
- `bitcoin`, `btc` → bitcoin/, crypto/
- `ethereum`, `eth` → ethereum/, crypto/
- `crypto`, `cryptocurrency`, `blockchain` → crypto/

### Companies
- `tesla` → tesla/, electric-vehicles/
- `apple` → apple/, technology/
- `google`, `microsoft`, `amazon`, `meta` → respective folders + technology/

### Markets & Economy
- `stock`, `market`, `trading`, `wall street` → stock-market/, trading/
- `economy`, `economic`, `gdp`, `growth` → economy/, market/
- `recession`, `inflation`, `crisis` → economy/, crisis/

### Finance
- `bank`, `banking`, `fed`, `federal reserve` → banking/, finance/
- `investment`, `investor` → finance/, stock-market/
- `money`, `dollar`, `currency` → money/, finance/

### Business
- `business`, `corporate`, `company`, `ceo` → business/, office/
- `startup` → business/, technology/
- `earnings`, `revenue`, `profit` → business/, finance/

### Energy & Vehicles
- `oil`, `energy`, `renewable`, `solar` → energy/
- `electric`, `ev` → electric-vehicles/

### Real Estate
- `real estate`, `housing`, `property`, `mortgage` → real-estate/

## Where to Download Free Stock Media

### 1. **Pexels** (Recommended)
- **URL**: https://www.pexels.com/
- **License**: Free for commercial use, no attribution required
- **Content**: High-quality photos and videos
- **Best for**: Business, technology, finance visuals
- **Format**: JPG (photos), MP4 (videos)

**How to use:**
1. Search for keywords (e.g., "stock market", "bitcoin", "AI technology")
2. Filter by "Videos" for dynamic content
3. Download in HD or 4K
4. Save to appropriate folder in `predefined_media/`

### 2. **Pixabay**
- **URL**: https://pixabay.com/
- **License**: Free for commercial use, no attribution required
- **Content**: Photos, videos, illustrations
- **Best for**: Cryptocurrency, technology, abstract concepts
- **Format**: JPG, PNG, MP4

### 3. **Unsplash**
- **URL**: https://unsplash.com/
- **License**: Free for commercial use, no attribution required
- **Content**: High-quality photos only (no videos)
- **Best for**: Professional business photos, tech, office scenes
- **Format**: JPG

### 4. **Videvo**
- **URL**: https://www.videvo.net/
- **License**: Mixed (check individual clips - many are free)
- **Content**: Stock videos, motion graphics, music
- **Best for**: Dynamic backgrounds, animated graphics
- **Format**: MP4, MOV

### 5. **Coverr**
- **URL**: https://coverr.co/
- **License**: Free for commercial use
- **Content**: Short video clips (7-25 seconds)
- **Best for**: Business, technology, lifestyle videos
- **Format**: MP4

### 6. **Mixkit**
- **URL**: https://mixkit.co/
- **License**: Free for commercial use
- **Content**: Videos, music, templates
- **Best for**: Tech animations, business videos
- **Format**: MP4

## Recommended Search Keywords

When downloading media, use these search terms:

### AI & Technology
- "artificial intelligence"
- "robot arm"
- "circuit board"
- "data center"
- "technology innovation"
- "neural network visualization"

### Cryptocurrency
- "bitcoin coin"
- "ethereum logo"
- "cryptocurrency trading"
- "blockchain network"
- "crypto mining"
- "digital currency"

### Stock Market
- "stock market chart"
- "trading floor"
- "wall street"
- "stock ticker"
- "financial graph"
- "bull market"

### Economy & Finance
- "money bills"
- "economic growth"
- "inflation chart"
- "federal reserve"
- "currency exchange"
- "financial planning"

### Business
- "corporate meeting"
- "office workspace"
- "business handshake"
- "startup team"
- "ceo presentation"
- "earnings report"

### Companies
- "tesla car"
- "apple store"
- "nvidia graphics card"
- "google office"
- "amazon warehouse"

### Energy
- "oil refinery"
- "solar panels"
- "wind turbines"
- "electric car charging"
- "renewable energy"

## Tips for Building Your Library

1. **Variety**: Download 5-10 different media files per category
2. **Quality**: Prefer 1080p or higher resolution
3. **Vertical Format**: For YouTube Shorts, download vertical (9:16) videos when possible
4. **No Text**: Avoid images/videos with embedded text (titles are added separately)
5. **Professional**: Choose professional, news-appropriate content
6. **Relevant**: Keep content directly related to business/finance news
7. **Timeless**: Avoid dated content that will look old quickly
8. **Any Duration**: Videos can be any length - they'll be automatically looped or trimmed
9. **Short Clips Work Best**: 3-10 second clips are ideal (loop seamlessly if needed)

## Example Setup

Here's a quick start setup (30 minutes):

### Step 1: Create Core Folders
```bash
mkdir -p predefined_media/{ai,crypto,bitcoin,ethereum,tesla,stock-market,economy,banking,technology,money,business}
```

### Step 2: Download Essential Media

Visit Pexels and download:

1. **AI** (5 videos):
   - Search "artificial intelligence"
   - Download vertical videos of robots, circuits, data

2. **Stock Market** (5 videos):
   - Search "stock market trading"
   - Download charts, trading floors, financial data

3. **Cryptocurrency** (5 videos):
   - Search "bitcoin cryptocurrency"
   - Download crypto coins, blockchain visualizations

4. **Tesla/EVs** (5 images):
   - Search "tesla electric car"
   - Download Tesla vehicles, charging stations

5. **Economy** (5 videos):
   - Search "economic growth money"
   - Download money, growth charts, business scenes

### Step 3: Organize Files

Save files with descriptive names:
```
predefined_media/
├── ai/
│   ├── robot-arm-1.mp4
│   ├── circuit-board-1.mp4
│   └── data-center-1.mp4
├── bitcoin/
│   ├── bitcoin-coin-1.jpg
│   ├── bitcoin-mining-1.mp4
│   └── crypto-trading-1.mp4
└── stock-market/
    ├── trading-floor-1.mp4
    ├── stock-chart-1.mp4
    └── wall-street-1.mp4
```

## Usage Statistics

The system logs when pre-defined media is used:
- Check `logs/pipeline.log` for "predefined_media_matched" entries
- Monitor cost savings vs. generating new images
- Identify which categories need more content

## Cost Savings

- **Gemini Image Generation**: ~$0.04 per image
- **Pre-defined Media**: $0.00
- **Potential Savings**: 100% cost reduction for matched content

If 50% of your segments use pre-defined media:
- 100 videos × 6 segments = 600 images
- 300 matched = $0 (saved $12)
- 300 generated = $12
- **Total savings: $12 (50%)**

## Maintenance

1. **Monitor Matches**: Check logs to see which keywords match frequently
2. **Add Popular Categories**: Download more media for frequently matched keywords
3. **Update Variety**: Refresh old content periodically
4. **Remove Unused**: Delete categories that never match

---

**Pro Tip**: Start with 5-10 videos for the most common topics (AI, stock market, crypto, economy) and expand based on your actual news topics!
