"""
AI Data Mining Script (ETL Pipeline)
=====================================
Pipeline untuk mengambil market data asli dan menganotasi dengan AI Signals.

Flow:
1. Extract: Fetch NVDA & VIX data dari Yahoo Finance
2. Transform: AI Annotation Loop via DeepSeek API (weekly batch)
3. Load: Simpan ke CSV & upload ke Google Drive via rclone

Usage:
    python data_miner.py
    python data_miner.py --start 2022-01-01 --end 2023-01-01
    python data_miner.py --no-upload  # Skip rclone upload
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Tuple
import time

import pandas as pd
import numpy as np
import yfinance as yf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Central configuration for Data Mining Pipeline."""

    # Market Data Settings
    TICKER = "NVDA"
    VIX_TICKER = "^VIX"
    DEFAULT_START = "2023-01-01"
    DEFAULT_END = "2024-01-01"

    # AI Annotation Settings
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"
    DEEPSEEK_MODEL = "deepseek-chat"
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds

    # Resampling Settings
    RESAMPLE_FREQ = "W-MON"  # Weekly on Monday

    # Output Settings
    OUTPUT_DIR = Path("data")
    OUTPUT_FILENAME = "nvda_real_data_2023.csv"

    # Rclone Settings
    RCLONE_REMOTE = os.getenv("RCLONE_REMOTE_NAME", "drive")
    RCLONE_PATH = os.getenv("RCLONE_REMOTE_PATH", "quant_backtest_data")


# ============================================================================
# STEP 1: EXTRACT - Fetch Market Data
# ============================================================================

def fetch_market_data(
    ticker: str = Config.TICKER,
    vix_ticker: str = Config.VIX_TICKER,
    start_date: str = Config.DEFAULT_START,
    end_date: str = Config.DEFAULT_END
) -> pd.DataFrame:
    """
    Fetch historical market data dari Yahoo Finance.

    Args:
        ticker: Stock symbol (default: NVDA)
        vix_ticker: VIX symbol (default: ^VIX)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        DataFrame with OHLCV data + VIX column
    """
    print(f"\n[Step 1] Fetching Market Data...")
    print(f"  Ticker: {ticker}")
    print(f"  VIX: {vix_ticker}")
    print(f"  Period: {start_date} to {end_date}")

    # Download stock data
    stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    # Download VIX data
    vix_data = yf.download(vix_ticker, start=start_date, end=end_date, progress=False)

    # Flatten MultiIndex columns BEFORE reset_index
    # yfinance returns MultiIndex with names=['Price', 'Ticker']
    if isinstance(stock_data.columns, pd.MultiIndex):
        stock_data.columns = stock_data.columns.get_level_values(0)
    if isinstance(vix_data.columns, pd.MultiIndex):
        vix_data.columns = vix_data.columns.get_level_values(0)

    # Merge VIX into stock data
    stock_data['VIX'] = vix_data['Close']

    # Reset index to make Date a column
    stock_data = stock_data.reset_index()

    # After reset_index, flatten again if still MultiIndex (Date column becomes ('Date', ''))
    if isinstance(stock_data.columns, pd.MultiIndex):
        stock_data.columns = stock_data.columns.get_level_values(0)

    print(f"  [OK] Fetched {len(stock_data)} rows of data")
    print(f"  Columns: {stock_data.columns.tolist()}")
    print(f"  Date Range: {stock_data['Date'].min()} to {stock_data['Date'].max()}")

    return stock_data


# ============================================================================
# STEP 2: TRANSFORM - AI Annotation Loop
# ============================================================================

def create_weekly_sample(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resample daily data ke weekly (Senin setiap minggu).

    Args:
        df: Daily DataFrame

    Returns:
        Weekly DataFrame with Monday dates
    """
    # Set Date as index
    df_temp = df.set_index('Date')

    # Resample to weekly (Monday)
    weekly = df_temp.resample('W-MON').last().dropna()

    # Reset index
    weekly = weekly.reset_index()

    return weekly


def call_deepseek_api(
    vix_value: float,
    pct_change: float,
    api_key: str,
    max_retries: int = Config.MAX_RETRIES
) -> Optional[float]:
    """
    Panggil DeepSeek API untuk klasifikasi regime pasar.

    Args:
        vix_value: Current VIX value
        pct_change: Weekly price change percentage
        api_key: DeepSeek API key
        max_retries: Number of retries on failure

    Returns:
        Float score (-1.0 to 1.0) or None if failed
    """
    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url=Config.DEEPSEEK_BASE_URL
    )

    prompt = f"""VIX is {vix_value:.2f}, NVDA price change last week was {pct_change:.2f}%.
Classify the market regime as a float:
- -1.0 = Crash/Bear market
- 0.0 = Neutral/Sideways
- 1.0 = Bull/Rally

Return ONLY the number (e.g., -1.0, 0.0, or 1.0). No explanation."""

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=Config.DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": "You are a quantitative market analyst. Output ONLY numeric values."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent output
                max_tokens=10
            )

            result = response.choices[0].message.content.strip()

            # Parse result to float
            score = float(result)

            # Validate range
            if -1.0 <= score <= 1.0:
                return score
            else:
                # Clamp to valid range
                return max(-1.0, min(1.0, score))

        except Exception as e:
            print(f"    [Retry {attempt + 1}/{max_retries}] Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(Config.RETRY_DELAY)

    print(f"    [FAILED] Could not get AI score for this week")
    return None


def ai_annotate_loop(
    weekly_df: pd.DataFrame,
    api_key: Optional[str] = None,
    progress_interval: int = 5
) -> pd.DataFrame:
    """
    Loop melalui data mingguan dan panggil DeepSeek API untuk setiap minggu.

    Args:
        weekly_df: Weekly DataFrame
        api_key: DeepSeek API key
        progress_interval: Print progress every N weeks

    Returns:
        DataFrame dengan kolom AI_Regime_Score
    """
    if api_key is None:
        api_key = Config.DEEPSEEK_API_KEY

    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not found. Please set it in .env file.")

    print(f"\n[Step 2] AI Annotation Loop (DeepSeek)")
    print(f"  Processing {len(weekly_df)} weeks...")
    print(f"  This will take ~{len(weekly_df) * 2} seconds...")

    ai_scores = []

    for i, row in weekly_df.iterrows():
        week_num = i + 1

        # Calculate metrics for prompt
        vix_value = row['VIX']
        close_price = row['Close']

        # Calculate weekly change (using Open as reference)
        pct_change = (close_price - row['Open']) / row['Open'] * 100

        # Print progress
        if week_num % progress_interval == 0 or week_num == 1:
            print(f"  Week {week_num}/{len(weekly_df)}: VIX={vix_value:.2f}, Change={pct_change:.2f}%")

        # Call DeepSeek API
        score = call_deepseek_api(vix_value, pct_change, api_key)

        if score is not None:
            ai_scores.append(score)
            print(f"    -> AI Score: {score:.2f}")
        else:
            # Fallback: Use simple rule-based classification
            if pct_change > 2:
                fallback_score = 1.0
            elif pct_change < -2:
                fallback_score = -1.0
            else:
                fallback_score = 0.0
            ai_scores.append(fallback_score)
            print(f"    -> Fallback Score: {fallback_score:.2f} (rule-based)")

        # Rate limiting - small delay between calls
        time.sleep(0.5)

    # Add AI scores to DataFrame
    weekly_df = weekly_df.copy()
    weekly_df['AI_Regime_Score'] = ai_scores

    print(f"\n  [OK] AI Annotation complete!")
    print(f"  Avg Regime Score: {np.mean(ai_scores):.4f}")
    print(f"  Bullish Weeks: {sum(1 for s in ai_scores if s > 0.5)}")
    print(f"  Bearish Weeks: {sum(1 for s in ai_scores if s < -0.5)}")
    print(f"  Neutral Weeks: {sum(1 for s in ai_scores if -0.5 <= s <= 0.5)}")

    return weekly_df


def forward_fill_daily(
    daily_df: pd.DataFrame,
    weekly_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge weekly AI scores ke daily data menggunakan forward fill.

    Args:
        daily_df: Original daily DataFrame
        weekly_df: Weekly DataFrame dengan AI_Regime_Score

    Returns:
        Daily DataFrame dengan AI_Regime_Score (forward filled)
    """
    print(f"\n[Step 3] Forward Fill (Merge Weekly -> Daily)")

    # Create mapping of week dates to AI scores
    weekly_scores = weekly_df[['Date', 'AI_Regime_Score']].copy()
    weekly_scores = weekly_scores.rename(columns={'Date': 'Week_Date'})

    # Merge with daily data
    daily_df_merged = daily_df.copy()

    # Find which week each daily row belongs to
    daily_df_merged['Week_Date'] = daily_df_merged['Date'].apply(
        lambda x: x - pd.Timedelta(days=x.weekday())
    )

    # Merge AI scores
    daily_df_merged = daily_df_merged.merge(
        weekly_scores,
        on='Week_Date',
        how='left'
    )

    # Forward fill untuk mengisi NaN
    daily_df_merged['AI_Regime_Score'] = daily_df_merged['AI_Regime_Score'].ffill()

    # Backward fill untuk baris pertama yang mungkin NaN
    daily_df_merged['AI_Regime_Score'] = daily_df_merged['AI_Regime_Score'].bfill()

    # Drop Week_Date column
    daily_df_merged = daily_df_merged.drop(columns=['Week_Date'])

    print(f"  [OK] Forward fill complete!")
    print(f"  Final rows: {len(daily_df_merged)}")

    return daily_df_merged


def add_ai_stock_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tambahkan kolom AI_Stock_Sentiment (mockup/placeholder).

    Di production, ini bisa diisi dengan:
    - News sentiment analysis
    - Social media sentiment
    - Analyst ratings

    Untuk sekarang, kita gunakan simple heuristic:
    - Daily return > 1% = Positive
    - Daily return < -1% = Negative
    - Else = Neutral

    Args:
        df: DataFrame dengan AI_Regime_Score

    Returns:
        DataFrame dengan tambahan AI_Stock_Sentiment
    """
    print(f"\n[Step 4] Adding AI_Stock_Sentiment (heuristic)")

    # Calculate daily returns
    df = df.copy()
    df['Daily_Return'] = df['Close'].pct_change() * 100

    # Create sentiment based on daily return
    conditions = [
        df['Daily_Return'] > 1.0,
        df['Daily_Return'] < -1.0
    ]
    choices = [0.5, -0.5]

    df['AI_Stock_Sentiment'] = np.select(conditions, choices, default=0.0)

    # Add some noise for realism
    noise = np.random.randn(len(df)) * 0.1
    df['AI_Stock_Sentiment'] = np.clip(
        df['AI_Stock_Sentiment'] + noise,
        -1.0, 1.0
    )

    # Drop Daily_Return column
    df = df.drop(columns=['Daily_Return'])

    print(f"  [OK] Sentiment added!")
    print(f"  Avg Sentiment: {df['AI_Stock_Sentiment'].mean():.4f}")

    return df


# ============================================================================
# STEP 3: LOAD - Save & Upload
# ============================================================================

def save_to_csv(
    df: pd.DataFrame,
    output_path: Path
) -> Path:
    """
    Simpan DataFrame ke CSV file.

    Args:
        df: DataFrame to save
        output_path: Output file path

    Returns:
        Path to saved file
    """
    print(f"\n[Step 5] Saving to CSV...")

    # Create output directory if not exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save to CSV
    df.to_csv(output_path, index=False)

    print(f"  [OK] Saved to: {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024:.2f} KB")

    return output_path


def upload_to_gdrive(
    local_path: Path,
    remote_name: str = Config.RCLONE_REMOTE,
    remote_path: str = Config.RCLONE_PATH
) -> bool:
    """
    Upload file ke Google Drive menggunakan rclone.

    Args:
        local_path: Local file path
        remote_name: Rclone remote name (from config)
        remote_path: Remote path in Google Drive

    Returns:
        True if successful, False otherwise
    """
    print(f"\n[Step 6] Uploading to Google Drive...")

    # Check if rclone is available
    try:
        subprocess.run(
            ["rclone", "version"],
            capture_output=True,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"  [SKIP] rclone not found. Please install rclone:")
        print(f"         https://rclone.org/downloads/")
        return False

    # Build remote path
    remote_file = f"{remote_name}:{remote_path}/{local_path.name}"

    # Run rclone copy
    try:
        result = subprocess.run(
            ["rclone", "copy", str(local_path), f"{remote_name}:{remote_path}"],
            capture_output=True,
            text=True,
            check=True
        )

        print(f"  [OK] Uploaded to: {remote_file}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Upload failed:")
        print(f"    {e.stderr}")
        return False


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_pipeline(
    start_date: str = Config.DEFAULT_START,
    end_date: str = Config.DEFAULT_END,
    ticker: str = Config.TICKER,
    upload: bool = True
) -> pd.DataFrame:
    """
    Jalankan full ETL pipeline.

    Args:
        start_date: Start date
        end_date: End date
        ticker: Stock ticker
        upload: Whether to upload to Google Drive

    Returns:
        Final DataFrame with AI annotations
    """
    print("\n" + "=" * 60)
    print("AI DATA MINING PIPELINE".center(60))
    print("=" * 60)

    # Validate API key
    if not Config.DEEPSEEK_API_KEY:
        raise ValueError(
            "DEEPSEEK_API_KEY not found!\n"
            "1. Copy .env.example to .env\n"
            "2. Add your API key: DEEPSEEK_API_KEY=your_key_here"
        )

    # Step 1: Extract - Fetch market data
    daily_data = fetch_market_data(ticker, Config.VIX_TICKER, start_date, end_date)

    # Step 2a: Resample to weekly
    weekly_data = create_weekly_sample(daily_data)
    print(f"\n  Resampled to {len(weekly_data)} weeks")

    # Step 2b: AI Annotation Loop
    weekly_annotated = ai_annotate_loop(weekly_data, Config.DEEPSEEK_API_KEY)

    # Step 3: Forward fill to daily
    daily_with_ai = forward_fill_daily(daily_data, weekly_annotated)

    # Step 4: Add stock sentiment
    final_data = add_ai_stock_sentiment(daily_with_ai)

    # Reorder columns to match backtesting format
    cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'VIX',
            'AI_Regime_Score', 'AI_Stock_Sentiment']
    final_data = final_data[cols]

    # Step 5: Save to CSV
    # Create dynamic filename based on ticker and year
    ticker_clean = ticker.replace('^', '').replace('.', '_')
    year = start_date[:4]
    filename = f"{ticker_clean}_real_data_{year}.csv"
    output_path = Config.OUTPUT_DIR / filename
    save_to_csv(final_data, output_path)

    # Step 6: Upload to Google Drive
    if upload:
        upload_to_gdrive(output_path)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE!")
    print("=" * 60)
    print(f"\nOutput: {output_path}")
    print(f"Rows: {len(final_data)}")
    print(f"Columns: {list(final_data.columns)}")

    return final_data


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI Data Mining Pipeline - Fetch & Annotate Market Data"
    )

    parser.add_argument(
        '--start', '-s',
        type=str,
        default=Config.DEFAULT_START,
        help=f'Start date (default: {Config.DEFAULT_START})'
    )

    parser.add_argument(
        '--end', '-e',
        type=str,
        default=Config.DEFAULT_END,
        help=f'End date (default: {Config.DEFAULT_END})'
    )

    parser.add_argument(
        '--ticker', '-t',
        type=str,
        default=Config.TICKER,
        help=f'Stock ticker (default: {Config.TICKER})'
    )

    parser.add_argument(
        '--no-upload',
        action='store_true',
        help='Skip upload to Google Drive'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Fetch data only, skip AI annotation'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    if args.dry_run:
        print("\n[DRY RUN] Fetching data only...")
        df = fetch_market_data(args.ticker, Config.VIX_TICKER, args.start, args.end)
        print("\nFirst 5 rows:")
        print(df.head())
        return

    # Run full pipeline
    df = run_pipeline(
        start_date=args.start,
        end_date=args.end,
        ticker=args.ticker,
        upload=not args.no_upload
    )

    # Preview
    print("\nPreview (last 5 rows):")
    print(df[['Date', 'Close', 'VIX', 'AI_Regime_Score', 'AI_Stock_Sentiment']].tail())


if __name__ == "__main__":
    main()
