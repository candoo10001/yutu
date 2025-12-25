"""
Media matcher for finding pre-defined images/videos based on keywords.
"""
import random
from pathlib import Path
from typing import Optional, List
import structlog


class MediaMatcher:
    """Matches segment content to pre-defined media files based on keywords."""

    def __init__(self, media_dir: str = "predefined_media", logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize the Media Matcher.

        Args:
            media_dir: Directory containing pre-defined media files
            logger: Logger instance
        """
        self.media_dir = Path(media_dir)
        self.logger = logger or structlog.get_logger()

        # Define keyword mappings to folder names
        self.keyword_mappings = {
            # AI and Technology (specific terms only)
            'artificial intelligence': ['ai'],
            '인공지능': ['ai'],
            'machine learning': ['ai'],
            '머신러닝': ['ai'],  # Machine learning in Korean
            '기계학습': ['ai'],  # Machine learning in Korean
            'deep learning': ['ai'],
            '딥러닝': ['ai'],  # Deep learning in Korean
            'neural network': ['ai'],
            '신경망': ['ai'],  # Neural network in Korean
            'chatgpt': ['ai'],
            'openai': ['ai'],
            'claude': ['ai'],
            'gemini': ['ai'],
            'generative ai': ['ai'],
            '생성형ai': ['ai'],  # Generative AI in Korean
            'llm': ['ai'],
            'large language model': ['ai'],
            '거대언어모델': ['ai'],  # Large language model in Korean
            'robot': ['technology'],
            '로봇': ['technology'],  # Robot in Korean
            'robotics': ['technology'],
            '로봇공학': ['technology'],  # Robotics in Korean
            'semiconductor': ['technology'],
            '반도체': ['technology'],  # Semiconductor in Korean
            'chip manufacturing': ['technology'],
            '반도체 제조': ['technology'],  # Chip manufacturing in Korean
            '5g': ['technology'],
            'cloud computing': ['technology'],
            '클라우드': ['technology'],  # Cloud in Korean
            'data center': ['technology'],
            '데이터센터': ['technology'],  # Data center in Korean
            'quantum computing': ['technology'],
            '양자컴퓨터': ['technology'],  # Quantum computer in Korean

            # Cryptocurrency (specific only)
            'bitcoin': ['bitcoin', 'crypto'],
            'btc': ['bitcoin', 'crypto'],
            '비트코인': ['bitcoin', 'crypto'],  # Bitcoin in Korean
            'ethereum': ['ethereum', 'crypto'],
            'eth': ['ethereum', 'crypto'],
            '이더리움': ['ethereum', 'crypto'],  # Ethereum in Korean
            'cryptocurrency': ['crypto'],
            '암호화폐': ['crypto'],  # Cryptocurrency in Korean
            '가상화폐': ['crypto'],  # Virtual currency in Korean
            'blockchain': ['crypto'],
            '블록체인': ['crypto'],  # Blockchain in Korean
            'nft': ['crypto'],
            'dogecoin': ['crypto'],
            '도지코인': ['crypto'],  # Dogecoin in Korean
            'ripple': ['crypto'],
            '리플': ['crypto'],  # Ripple in Korean

            # Companies
            'tesla': ['tesla', 'electric-vehicles', 'cars'],
            '테슬라': ['tesla', 'electric-vehicles', 'cars'],  # Tesla in Korean
            'apple': ['apple', 'technology', 'tech'],
            '애플': ['apple', 'technology', 'tech'],  # Apple in Korean
            'nvidia': ['nvidia', 'ai', 'technology', 'chips'],
            '엔비디아': ['nvidia', 'ai', 'technology', 'chips'],  # Nvidia in Korean
            'google': ['google', 'technology', 'ai'],
            '구글': ['google', 'technology', 'ai'],  # Google in Korean
            'microsoft': ['microsoft', 'technology', 'ai'],
            '마이크로소프트': ['microsoft', 'technology', 'ai'],  # Microsoft in Korean
            'amazon': ['amazon', 'technology', 'ecommerce'],
            '아마존': ['amazon', 'technology', 'ecommerce'],  # Amazon in Korean
            'meta': ['meta', 'technology', 'social-media'],
            '메타': ['meta', 'technology', 'social-media'],  # Meta in Korean
            'facebook': ['meta', 'technology', 'social-media'],
            '페이스북': ['meta', 'technology', 'social-media'],  # Facebook in Korean

            # Markets and Economy (specific terms only)
            'stock market': ['stock-market'],
            '주식시장': ['stock-market'],  # Stock market in Korean (specific)
            '주식': ['stock-market'],  # Stock in Korean
            'stock price': ['stock-market'],
            '주가': ['stock-market'],  # Stock price in Korean
            'share price': ['stock-market'],
            'wall street': ['stock-market'],
            '월스트리트': ['stock-market'],  # Wall Street in Korean
            'nasdaq': ['stock-market'],
            '나스닥': ['stock-market'],  # NASDAQ in Korean
            'dow jones': ['stock-market'],
            '다우존스': ['stock-market'],  # Dow Jones in Korean
            's&p 500': ['stock-market'],
            'bull market': ['stock-market'],
            'bear market': ['stock-market'],
            '증시': ['stock-market'],  # Stock market in Korean (short form)
            'market crash': ['stock-market', 'crisis'],
            '시장붕괴': ['stock-market', 'crisis'],  # Market crash in Korean
            '주식폭락': ['stock-market', 'crisis'],  # Stock crash in Korean
            'dividend': ['stock-market'],
            '배당': ['stock-market'],  # Dividend in Korean

            # Finance (specific institutions/terms only)
            'federal reserve': ['banking'],
            'fed': ['banking'],
            '연준': ['banking'],  # Fed in Korean
            'central bank': ['banking'],
            '중앙은행': ['banking'],  # Central bank in Korean
            'bank of japan': ['banking'],
            '일본은행': ['banking'],  # Bank of Japan in Korean
            'interest rate hike': ['banking'],
            '금리인상': ['banking'],  # Interest rate hike in Korean
            'interest rate cut': ['banking'],
            '금리인하': ['banking'],  # Interest rate cut in Korean
            'rate hike': ['banking'],
            'rate cut': ['banking'],
            '기준금리': ['banking'],  # Base rate in Korean

            # Money & Currency (specific only)
            'inflation rate': ['money'],
            '인플레이션율': ['money'],  # Inflation rate in Korean
            'consumer price': ['money'],
            '소비자물가': ['money'],  # Consumer price in Korean
            'hyperinflation': ['money', 'crisis'],
            '초인플레이션': ['money', 'crisis'],  # Hyperinflation in Korean
            'deflation': ['money'],
            '디플레이션': ['money'],  # Deflation in Korean
            'currency exchange': ['money'],
            '환율': ['money'],  # Exchange rate in Korean
            'foreign exchange': ['money'],
            '외환': ['money'],  # Foreign exchange in Korean
            'forex': ['money'],
            'us dollar': ['money'],
            'dollar index': ['money'],
            'korean won': ['money'],
            '원화': ['money'],  # Korean won in Korean
            'japanese yen': ['money'],
            'euro': ['money'],
            '유로': ['money'],  # Euro in Korean
            'yuan': ['money'],
            '위안': ['money'],  # Yuan in Korean

            # Business (specific terms only)
            'startup': ['business'],
            '스타트업': ['business'],  # Startup in Korean
            'merger': ['business'],
            '인수합병': ['business'],  # M&A in Korean
            'ipo': ['business', 'stock-market'],
            '기업공개': ['business', 'stock-market'],  # IPO in Korean

            # Energy (specific terms only)
            'crude oil': ['energy'],
            'oil price': ['energy'],
            '원유': ['energy'],  # Crude oil in Korean
            '유가': ['energy'],  # Oil price in Korean
            'opec': ['energy'],
            'electricity': ['energy'],
            '전력': ['energy'],  # Electric power in Korean
            'power grid': ['energy'],
            '전력망': ['energy'],  # Power grid in Korean
            'power shortage': ['energy'],
            '전력난': ['energy'],  # Power shortage in Korean
            '정전': ['energy'],  # Blackout in Korean
            'renewable energy': ['energy'],
            '재생에너지': ['energy'],  # Renewable energy in Korean
            'solar power': ['energy'],
            '태양광발전': ['energy'],  # Solar power in Korean
            'wind power': ['energy'],
            '풍력발전': ['energy'],  # Wind power in Korean
            'nuclear power': ['energy'],
            '원자력': ['energy'],  # Nuclear power in Korean
            'electric vehicle': ['electric-vehicles'],
            'ev': ['electric-vehicles'],
            '전기차': ['electric-vehicles'],  # EV in Korean
            '전기자동차': ['electric-vehicles'],  # Electric vehicle in Korean

            # Real Estate (specific terms only)
            'real estate': ['real-estate'],
            '부동산': ['real-estate'],  # Real estate in Korean
            'housing market': ['real-estate'],
            '주택시장': ['real-estate'],  # Housing market in Korean
            'property market': ['real-estate'],
            '부동산시장': ['real-estate'],  # Property market in Korean
            'property price': ['real-estate'],
            '집값': ['real-estate'],  # House price in Korean
            'housing price': ['real-estate'],
            '주택가격': ['real-estate'],  # Housing price in Korean
            'mortgage': ['real-estate'],
            '주택담보대출': ['real-estate'],  # Mortgage in Korean
            'housing bubble': ['real-estate', 'crisis'],
            '부동산거품': ['real-estate', 'crisis'],  # Housing bubble in Korean
            'property bubble': ['real-estate', 'crisis'],
            'rent': ['real-estate'],
            '임대료': ['real-estate'],  # Rent in Korean
            '전세': ['real-estate'],  # Korean housing deposit system

            # Crisis & Economy (specific terms only)
            'financial crisis': ['crisis'],
            '금융위기': ['crisis'],  # Financial crisis in Korean
            'economic crisis': ['crisis'],
            '경제위기': ['crisis'],  # Economic crisis in Korean
            'recession': ['crisis'],
            '경기침체': ['crisis'],  # Recession in Korean
            'debt crisis': ['crisis'],
            '부채위기': ['crisis'],  # Debt crisis in Korean
            'banking crisis': ['crisis', 'banking'],
            '은행위기': ['crisis', 'banking'],  # Banking crisis in Korean
            'default': ['crisis'],
            '채무불이행': ['crisis'],  # Default in Korean
            'bankruptcy': ['crisis'],
            '파산': ['crisis'],  # Bankruptcy in Korean
            'gdp growth': ['growth', 'economy'],
            'gdp': ['economy'],
            '경제성장률': ['growth', 'economy'],  # GDP growth rate in Korean
            'economic growth': ['growth', 'economy'],
            'climate change': ['environment'],
            '기후변화': ['environment'],  # Climate change in Korean
        }

    def find_matching_media(self, text: str, title: str = "", used_media: Optional[set] = None) -> Optional[str]:
        """
        Find a pre-defined media file that matches the segment content.
        Excludes already-used videos to prevent duplicates in the same video.

        Args:
            text: Segment text to analyze
            title: Segment title (optional, for additional context)
            used_media: Set of already-used media file paths (absolute paths) to exclude

        Returns:
            Path to matching media file, or None if no match found or all matching videos already used
        """
        if used_media is None:
            used_media = set()
        
        # Combine text and title for keyword extraction
        combined_text = f"{title} {text}".lower()

        # Find matching keywords
        matched_folders = set()
        for keyword, folders in self.keyword_mappings.items():
            if keyword in combined_text:
                matched_folders.update(folders)
                self.logger.debug("keyword_matched", keyword=keyword, folders=folders)

        if not matched_folders:
            self.logger.debug("no_keywords_matched", text_preview=combined_text[:100])
            return None

        # Search for media files in matched folders
        media_files = []
        video_files = []
        image_files = []
        
        for folder in matched_folders:
            folder_path = self.media_dir / folder
            if folder_path.exists() and folder_path.is_dir():
                # Support images and videos
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.mp4', '*.mov', '*.avi']:
                    files = list(folder_path.glob(ext))
                    media_files.extend(files)
                    # Separate videos from images
                    for f in files:
                        if f.suffix.lower() in ['.mp4', '.mov', '.avi']:
                            video_files.append(f)
                        else:
                            image_files.append(f)

        if not media_files:
            self.logger.debug("no_media_files_found", folders=list(matched_folders))
            return None

        # Convert used_media to absolute Path objects for comparison
        used_media_paths = {Path(p).resolve() for p in used_media}

        # Filter out already-used videos (but allow images to be reused)
        available_videos = [f for f in video_files if f.resolve() not in used_media_paths]
        available_images = image_files  # Images can be reused
        
        # Prioritize unused videos, but allow images if no videos available
        available_media = available_videos if available_videos else available_images

        if not available_media:
            # All matching videos have been used - return None to trigger image generation
            self.logger.info(
                "all_matching_videos_already_used",
                matched_keywords=list(matched_folders),
                total_matches=len(media_files),
                used_count=len([f for f in video_files if f.resolve() in used_media_paths]),
                action="will_generate_image_instead"
            )
            return None

        # Randomly select one of the available files
        selected_file = random.choice(available_media)

        self.logger.info(
            "predefined_media_matched",
            matched_keywords=list(matched_folders),
            selected_file=str(selected_file),
            total_matches=len(media_files),
            available_matches=len(available_media),
            is_video=selected_file.suffix.lower() in ['.mp4', '.mov', '.avi']
        )

        return str(selected_file)

    def get_available_categories(self) -> List[str]:
        """
        Get list of available media categories (folders).

        Returns:
            List of category names
        """
        if not self.media_dir.exists():
            return []

        categories = [
            d.name for d in self.media_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]

        return sorted(categories)
