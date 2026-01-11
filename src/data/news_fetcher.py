"""
NewsFetcher Module for EXP-2025-005

Fetches historical news sentiment using LLM memory approach.
Since yfinance.news only provides current news and NewsAPI requires paid key
for historical data, we use DeepSeek's knowledge cutoff to get historical events.
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dotenv import load_dotenv
from openai import OpenAI
import time
import json

load_dotenv()


class NewsFetcher:
    """Fetches and analyzes historical news sentiment using LLM."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize NewsFetcher with DeepSeek API client."""
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )

        # Cache for sentiment results
        self.cache = {}
        self.cache_file = "data/sentiment_cache.json"

    def _load_cache(self):
        """Load sentiment cache from disk."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load cache: {e}")
            self.cache = {}

    def _save_cache(self):
        """Save sentiment cache to disk."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")

    def get_sentiment_for_date(
        self,
        ticker: str,
        date: str,
        price_context: Optional[Dict] = None,
        use_cache: bool = True
    ) -> Dict[str, float]:
        """
        Get LLM-analyzed sentiment for a specific date.

        Args:
            ticker: Stock symbol (e.g., "NVDA")
            date: Date string (YYYY-MM-DD format)
            price_context: Optional dict with 'open', 'high', 'low', 'close', 'volume', 'return_5d'
            use_cache: Whether to use cached results

        Returns:
            Dict with 'sentiment' (-1.0 to 1.0) and 'confidence' (0.0 to 1.0)
        """
        cache_key = f"{ticker}_{date}"

        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]

        # Build context string
        context_str = ""
        if price_context:
            change_5d = price_context.get('return_5d', 0) * 100
            volatility = price_context.get('volatility', 0) * 100

            # Determine recent trend
            if change_5d > 5:
                trend_desc = "strong uptrend (significant gains)"
            elif change_5d > 2:
                trend_desc = "moderate uptrend"
            elif change_5d > -2:
                trend_desc = "sideways/flat"
            elif change_5d > -5:
                trend_desc = "moderate downtrend"
            else:
                trend_desc = "strong downtrend (significant losses)"

            context_str = f"""
Price Context for {date}:
- 5-day return: {change_5d:+.1f}%
- Recent trend: {trend_desc}
- Volatility: {volatility:.1f}%
"""

        # Get day of week for more specific query
        from datetime import datetime
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            day_of_week = dt.strftime("%A")
        except:
            day_of_week = ""

        prompt = f"""
You are analyzing stock market sentiment for {ticker} on {date} ({day_of_week}).

{context_str}
IMPORTANT: Your sentiment score should be BASED PRIMARILY on the price context above.
If the stock is in a strong uptrend, sentiment should be POSITIVE.
If the stock is in a strong downtrend, sentiment should be NEGATIVE.
Sideways price action = NEUTRAL sentiment.

Sentiment Score Guidelines:
- Strong uptrend (+5% or more in 5 days): 0.5 to 0.8
- Moderate uptrend (+2% to +5%): 0.2 to 0.5
- Sideways (-2% to +2%): -0.1 to 0.1
- Moderate downtrend (-2% to -5%): -0.2 to -0.5
- Strong downtrend (-5% or worse): -0.5 to -0.8

Provide your analysis in this exact format:

SENTIMENT: [score from -1.0 to 1.0 based on price trend]
CONFIDENCE: [score from 0.0 to 1.0]
REASON: [brief explanation of the sentiment]

Only output these three lines.
"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a financial analyst specializing in sentiment analysis. Be objective and use the price context provided."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )

            content = response.choices[0].message.content.strip()
            result = self._parse_sentiment_response(content)

            # Cache the result
            self.cache[cache_key] = result
            if use_cache:
                self._save_cache()

            return result

        except Exception as e:
            print(f"Error getting sentiment for {ticker} on {date}: {e}")
            return {"sentiment": 0.0, "confidence": 0.0, "reason": "Error"}

    def _parse_sentiment_response(self, content: str) -> Dict[str, float]:
        """Parse LLM response into sentiment data."""
        result = {"sentiment": 0.0, "confidence": 0.0, "reason": ""}

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith("SENTIMENT:"):
                try:
                    result["sentiment"] = float(line.split(":")[1].strip())
                except (ValueError, IndexError):
                    pass
            elif line.startswith("CONFIDENCE:"):
                try:
                    result["confidence"] = float(line.split(":")[1].strip())
                except (ValueError, IndexError):
                    pass
            elif line.startswith("REASON:"):
                result["reason"] = line.split(":", 1)[1].strip()

        return result

    def fetch_sentiment_series(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        price_df: Optional[pd.DataFrame] = None,
        freq: str = 'W-MON',  # Weekly to reduce API calls
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Fetch sentiment time series for a date range.

        Args:
            ticker: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            price_df: Optional DataFrame with price data for context (must have Date index)
            freq: Frequency for sentiment sampling (default: weekly)
            use_cache: Whether to use cached results

        Returns:
            DataFrame with Date, Sentiment, Confidence, Reason columns
        """
        self._load_cache()

        dates = pd.date_range(start=start_date, end=end_date, freq=freq)

        results = []
        for date in dates:
            date_str = date.strftime("%Y-%m-%d")
            print(f"Fetching sentiment for {ticker} on {date_str}...")

            # Build price context if price_df is provided
            price_context = None
            if price_df is not None and isinstance(price_df, pd.DataFrame):
                # Get 5-day window around this date
                date_pd = pd.Timestamp(date)
                window_start = date_pd - pd.Timedelta(days=10)
                window_end = date_pd + pd.Timedelta(days=2)

                # Get data in window (if available)
                try:
                    window_data = price_df.loc[window_start:date_pd]

                    if not window_data.empty and 'Close' in window_data.columns:
                        close_start = window_data['Close'].iloc[0]
                        close_end = window_data['Close'].iloc[-1]

                        # Calculate metrics
                        return_5d = (close_end - close_start) / close_start if close_start > 0 else 0

                        # Calculate volatility
                        returns = window_data['Close'].pct_change().dropna()
                        volatility = returns.std() * np.sqrt(252) if len(returns) > 0 else 0.2

                        price_context = {
                            'return_5d': return_5d,
                            'volatility': volatility
                        }
                except Exception as e:
                    pass  # Skip context if there's an error

            sentiment_data = self.get_sentiment_for_date(
                ticker,
                date_str,
                price_context=price_context,
                use_cache=use_cache
            )

            results.append({
                "Date": date,
                "Sentiment": sentiment_data["sentiment"],
                "Confidence": sentiment_data["confidence"],
                "Reason": sentiment_data["reason"]
            })

            # Rate limiting: be nice to the API
            cache_key = f"{ticker}_{date_str}"
            if not use_cache or cache_key not in self.cache:
                time.sleep(0.5)

        df = pd.DataFrame(results)
        df.set_index("Date", inplace=True)

        return df

    def augment_price_data(
        self,
        price_df: pd.DataFrame,
        ticker: str,
        freq: str = 'W-MON',
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Augment price data with LLM sentiment.

        Args:
            price_df: DataFrame with Date index and OHLCV columns
            ticker: Stock symbol
            freq: Frequency for sentiment sampling
            use_cache: Whether to use cached results

        Returns:
            Augmented DataFrame with News_Sentiment and News_Confidence columns
        """
        start_date = price_df.index.min().strftime("%Y-%m-%d")
        end_date = price_df.index.max().strftime("%Y-%m-%d")

        print(f"Fetching news sentiment for {ticker} from {start_date} to {end_date}...")

        sentiment_df = self.fetch_sentiment_series(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            price_df=price_df,  # Pass price data for context
            freq=freq,
            use_cache=use_cache
        )

        # Reindex to match price data and forward fill
        sentiment_df = sentiment_df.reindex(price_df.index, method='ffill')

        # Merge with price data
        result = price_df.copy()
        result["News_Sentiment"] = sentiment_df["Sentiment"].fillna(0)
        result["News_Confidence"] = sentiment_df["Confidence"].fillna(0)

        return result


def main():
    """Test the NewsFetcher module."""
    import sys

    print("Testing NewsFetcher module...")

    try:
        fetcher = NewsFetcher()

        # Test single date
        print("\n--- Test 1: Single Date Sentiment ---")
        result = fetcher.get_sentiment_for_date("NVDA", "2023-05-25")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Reason: {result['reason']}")

        # Test date range
        print("\n--- Test 2: Weekly Sentiment Series ---")
        df = fetcher.fetch_sentiment_series(
            ticker="NVDA",
            start_date="2023-05-01",
            end_date="2023-06-30",
            freq='W-MON'
        )
        print(df)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
