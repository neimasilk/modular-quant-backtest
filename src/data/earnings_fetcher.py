"""
Earnings Call Transcript Fetcher

Fetches earnings call transcripts from various sources for sentiment analysis.

Sources:
1. Seeking Alpha (free, web scraping)
2. SEC 8-K filings (official, may not have full transcript)
3. Manual transcript files (as fallback)

Usage:
    fetcher = EarningsTranscriptFetcher()
    transcripts = fetcher.fetch_transcripts('NVDA', quarters=8)
"""

import os
import re
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup


class EarningsTranscriptFetcher:
    """Fetch earnings call transcripts from multiple sources."""

    def __init__(self, cache_dir: str = "./data/earnings_calls"):
        """
        Initialize the fetcher.

        Args:
            cache_dir: Directory to cache downloaded transcripts
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # User agent to avoid being blocked
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_transcripts(self, ticker: str, quarters: int = 8,
                         source: str = 'seekingalpha') -> List[Dict]:
        """
        Fetch earnings transcripts for a ticker.

        Args:
            ticker: Stock symbol (e.g., 'NVDA')
            quarters: Number of recent quarters to fetch
            source: Data source ('seekingalpha', 'sec', 'manual')

        Returns:
            List of transcript dicts with {date, quarter, text, url, source}
        """
        ticker = ticker.upper()

        # Check cache first
        cache_file = self.cache_dir / ticker / f"{ticker}_transcripts.json"
        if cache_file.exists():
            print(f"✅ Loading {ticker} transcripts from cache: {cache_file}")
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
                # Filter to requested number of quarters
                return cached_data[:quarters]

        # Fetch from source
        if source == 'seekingalpha':
            transcripts = self._fetch_from_seeking_alpha(ticker, quarters)
        elif source == 'sec':
            transcripts = self._fetch_from_sec(ticker, quarters)
        elif source == 'manual':
            transcripts = self._load_manual_transcripts(ticker, quarters)
        else:
            raise ValueError(f"Unknown source: {source}")

        # Cache the results
        if transcripts:
            ticker_dir = self.cache_dir / ticker
            ticker_dir.mkdir(parents=True, exist_ok=True)

            with open(cache_file, 'w') as f:
                json.dump(transcripts, f, indent=2)

            print(f"💾 Cached {len(transcripts)} transcripts to {cache_file}")

        return transcripts

    def _fetch_from_seeking_alpha(self, ticker: str, quarters: int) -> List[Dict]:
        """
        Fetch transcripts from Seeking Alpha (web scraping).

        Note: This is a basic scraper. Seeking Alpha may block automated requests.
        Consider using their API if available or manual download as fallback.
        """
        print(f"🔍 Fetching {ticker} earnings from Seeking Alpha...")

        transcripts = []

        # Seeking Alpha earnings transcripts page
        base_url = f"https://seekingalpha.com/symbol/{ticker}/earnings/transcripts"

        try:
            response = requests.get(base_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find transcript links
            # Note: This is a simplified example. Actual selectors may need adjustment
            # based on Seeking Alpha's current HTML structure
            transcript_links = soup.find_all('a', href=re.compile(r'/article/\d+-.*-earnings-call-transcript'))

            print(f"📄 Found {len(transcript_links)} transcript links")

            for idx, link in enumerate(transcript_links[:quarters]):
                if idx > 0:
                    time.sleep(2)  # Rate limiting

                transcript_url = "https://seekingalpha.com" + link['href']

                try:
                    # Fetch full transcript
                    transcript_data = self._fetch_single_transcript(transcript_url, ticker)
                    if transcript_data:
                        transcripts.append(transcript_data)
                        print(f"  ✅ Fetched: {transcript_data['quarter']}")

                except Exception as e:
                    print(f"  ⚠️ Failed to fetch {transcript_url}: {e}")
                    continue

        except Exception as e:
            print(f"❌ Failed to fetch from Seeking Alpha: {e}")
            print("💡 Suggestion: Use manual transcript download or SEC filings instead")

        return transcripts

    def _fetch_single_transcript(self, url: str, ticker: str) -> Optional[Dict]:
        """Fetch a single transcript from Seeking Alpha."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract transcript text
            # Note: Selectors may need adjustment based on actual HTML
            article_body = soup.find('div', {'data-test-id': 'article-content'})
            if not article_body:
                article_body = soup.find('div', class_=re.compile(r'article.*content'))

            if not article_body:
                return None

            # Extract text
            text = article_body.get_text(separator='\n', strip=True)

            # Extract date and quarter from title or content
            title = soup.find('h1')
            title_text = title.get_text() if title else ""

            # Parse quarter (e.g., "Q4 2023")
            quarter_match = re.search(r'Q([1-4])\s+(\d{4})', title_text)
            if quarter_match:
                q, year = quarter_match.groups()
                quarter = f"{year}_Q{q}"
                date = f"{year}-{int(q)*3:02d}-01"  # Approximate
            else:
                # Fallback to current date
                now = datetime.now()
                quarter = f"{now.year}_Q{(now.month-1)//3+1}"
                date = now.strftime('%Y-%m-%d')

            return {
                'ticker': ticker,
                'date': date,
                'quarter': quarter,
                'title': title_text,
                'text': text,
                'url': url,
                'source': 'seekingalpha',
                'fetched_at': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"⚠️ Error fetching transcript: {e}")
            return None

    def _fetch_from_sec(self, ticker: str, quarters: int) -> List[Dict]:
        """
        Fetch earnings info from SEC 8-K filings.

        Note: SEC filings may not have full earnings call transcripts,
        but they do have earnings press releases.
        """
        print(f"🏛️ Fetching {ticker} from SEC EDGAR...")
        print("⚠️ Note: SEC filings may not include full transcripts")

        # TODO: Implement SEC EDGAR API integration
        # For now, return empty list
        return []

    def _load_manual_transcripts(self, ticker: str, quarters: int) -> List[Dict]:
        """
        Load manually downloaded transcripts from local files.

        Expected structure:
        data/earnings_calls/TICKER/
        ├── 2023_Q4.txt
        ├── 2023_Q3.txt
        └── ...
        """
        print(f"📂 Loading manual transcripts for {ticker}...")

        ticker_dir = self.cache_dir / ticker
        if not ticker_dir.exists():
            print(f"⚠️ No manual transcripts found in {ticker_dir}")
            return []

        transcripts = []

        # Find all .txt files
        transcript_files = sorted(ticker_dir.glob("*.txt"), reverse=True)

        for file_path in transcript_files[:quarters]:
            # Parse filename (e.g., "2023_Q4.txt")
            quarter = file_path.stem

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

                # Extract year and quarter for date
                year_q = quarter.split('_')
                if len(year_q) == 2:
                    year, q = year_q
                    q_num = q.replace('Q', '')
                    date = f"{year}-{int(q_num)*3:02d}-01"
                else:
                    date = datetime.now().strftime('%Y-%m-%d')

                transcripts.append({
                    'ticker': ticker,
                    'date': date,
                    'quarter': quarter,
                    'title': f"{ticker} {quarter} Earnings Call",
                    'text': text,
                    'url': str(file_path),
                    'source': 'manual',
                    'fetched_at': datetime.now().isoformat()
                })

                print(f"  ✅ Loaded: {quarter} ({len(text)} chars)")

            except Exception as e:
                print(f"  ⚠️ Failed to load {file_path}: {e}")
                continue

        return transcripts

    def save_transcript(self, ticker: str, quarter: str, text: str,
                       metadata: Optional[Dict] = None) -> Path:
        """
        Manually save a transcript (for manual downloads).

        Args:
            ticker: Stock symbol
            quarter: Quarter label (e.g., "2023_Q4")
            text: Full transcript text
            metadata: Optional metadata dict

        Returns:
            Path to saved file
        """
        ticker_dir = self.cache_dir / ticker.upper()
        ticker_dir.mkdir(parents=True, exist_ok=True)

        # Save transcript text
        txt_file = ticker_dir / f"{quarter}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(text)

        # Save metadata if provided
        if metadata:
            meta_file = ticker_dir / f"{quarter}_metadata.json"
            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)

        print(f"💾 Saved transcript: {txt_file}")
        return txt_file


# Example usage and testing
if __name__ == "__main__":
    # Example: Fetch NVDA earnings transcripts
    fetcher = EarningsTranscriptFetcher()

    # Try manual loading first (safest option)
    print("\n" + "="*60)
    print("TESTING: Manual Transcript Loading")
    print("="*60)

    transcripts = fetcher.fetch_transcripts('NVDA', quarters=8, source='manual')

    if transcripts:
        print(f"\n✅ Successfully loaded {len(transcripts)} transcripts")
        for t in transcripts:
            print(f"  - {t['quarter']}: {len(t['text'])} characters")
    else:
        print("\n⚠️ No manual transcripts found")
        print("\n📝 To add manual transcripts:")
        print("  1. Download earnings transcripts from Seeking Alpha")
        print("  2. Save as data/earnings_calls/TICKER/YYYY_QN.txt")
        print("  3. Example: data/earnings_calls/NVDA/2023_Q4.txt")

    # You can try Seeking Alpha scraping (may be blocked)
    # print("\n" + "="*60)
    # print("TESTING: Seeking Alpha Scraping")
    # print("="*60)
    # transcripts_sa = fetcher.fetch_transcripts('NVDA', quarters=2, source='seekingalpha')
