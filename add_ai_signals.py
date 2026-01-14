"""
Quick script to add AI signals to existing data files for backtesting.
Generates simulated AI_Regime_Score and AI_Stock_Sentiment based on technical indicators.
"""

import pandas as pd
import numpy as np

def calculate_regime_score(df):
    """
    Calculate AI_Regime_Score based on VIX-like volatility.
    Returns: -1 to +1 (bearish to bullish)
    """
    # Calculate rolling volatility (20-day)
    returns = df['Close'].pct_change()
    volatility = returns.rolling(20).std() * np.sqrt(252)

    # Normalize to -1 to +1 range
    # High volatility = bearish (-1), Low volatility = bullish (+1)
    vol_min = volatility.quantile(0.1)
    vol_max = volatility.quantile(0.9)

    regime_score = 1 - 2 * (volatility - vol_min) / (vol_max - vol_min)
    regime_score = regime_score.clip(-1, 1)

    return regime_score.fillna(0)


def calculate_stock_sentiment(df):
    """
    Calculate AI_Stock_Sentiment based on price momentum and RSI.
    Returns: -1 to +1 (bearish to bullish)

    IMPORTANT: Uses lagged signals to avoid look-ahead bias.
    """
    # Calculate RSI (14-period)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # Normalize RSI to -1 to +1
    # RSI 30 = -1 (oversold), RSI 70 = +1 (overbought)
    sentiment = (rsi - 50) / 50  # Simplified: -1 to +1 range
    sentiment = sentiment.clip(-1, 1)

    # LAG by 1 period to avoid look-ahead bias
    sentiment_lagged = sentiment.shift(1)

    return sentiment_lagged.fillna(0)


def add_ai_signals_to_file(input_file, output_file=None):
    """
    Add AI signals to CSV file.

    Args:
        input_file: Path to input CSV
        output_file: Path to output CSV (if None, overwrites input)
    """
    print(f"Processing: {input_file}")

    # Load data
    df = pd.read_csv(input_file)

    # Check if already has AI signals
    if 'AI_Regime_Score' in df.columns and 'AI_Stock_Sentiment' in df.columns:
        print(f"  ✅ Already has AI signals, skipping")
        return

    # Calculate AI signals
    df['AI_Regime_Score'] = calculate_regime_score(df)
    df['AI_Stock_Sentiment'] = calculate_stock_sentiment(df)

    # Save
    output_path = output_file or input_file
    df.to_csv(output_path, index=False)

    print(f"  ✅ Added AI signals")
    print(f"     AI_Regime_Score range: [{df['AI_Regime_Score'].min():.2f}, {df['AI_Regime_Score'].max():.2f}]")
    print(f"     AI_Stock_Sentiment range: [{df['AI_Stock_Sentiment'].min():.2f}, {df['AI_Stock_Sentiment'].max():.2f}]")


if __name__ == "__main__":
    import glob

    # Process all NVDA, AAPL, SPY 2022 and 2023 files
    files_to_process = [
        'data/NVDA_2022.csv',
        'data/NVDA_2023.csv',
        'data/AAPL_2022.csv',
        'data/AAPL_2023.csv',
        'data/SPY_2022.csv',
        'data/SPY_2023.csv'
    ]

    print("Adding AI signals to data files...")
    print("=" * 60)

    for file in files_to_process:
        try:
            add_ai_signals_to_file(file)
        except FileNotFoundError:
            print(f"  ⚠️  File not found: {file}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print("=" * 60)
    print("✅ Done!")
