"""
Demo Script: Shadow Trading Preview (No API Key Required)
==========================================================

Shows what shadow trading will do WITHOUT making real LLM calls.
Use this to preview the system before setting up DeepSeek API.

Usage:
    python test_shadow_demo.py
"""

import sys
from pathlib import Path
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


def fetch_recent_data(ticker: str, days: int = 5) -> pd.DataFrame:
    """Fetch recent market data."""
    print(f"\n📊 Fetching {days} days of data for {ticker}...")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days + 10)

    df = yf.download(
        ticker,
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        progress=False
    )

    df = df.tail(days)
    print(f"   ✅ Fetched {len(df)} bars from {df.index[0].date()} to {df.index[-1].date()}")

    return df


def analyze_price_moves(ticker: str, df: pd.DataFrame):
    """Analyze price moves and show what would trigger LLM."""
    print(f"\n🔍 Analyzing price moves for {ticker}...")
    print("=" * 80)

    THRESHOLD = 0.03  # 3%
    triggered_count = 0

    for i in range(1, len(df)):
        prev_close = df['Close'].iloc[i-1]
        curr_close = df['Close'].iloc[i]
        date = df.index[i]

        price_change_pct = (curr_close - prev_close) / prev_close

        # Check if would trigger LLM
        if abs(price_change_pct) >= THRESHOLD:
            triggered_count += 1

            direction = "📈 UP" if price_change_pct > 0 else "📉 DOWN"

            print(f"\n{date.date()} - {direction}")
            print(f"   Price change: {price_change_pct:+.2%}")
            print(f"   Close: ${prev_close:.2f} → ${curr_close:.2f}")
            print(f"   Volume: {df['Volume'].iloc[i]:,.0f}")
            print(f"   ✅ Would trigger LLM call")

            # Simulate what LLM would analyze
            if abs(price_change_pct) > 0.05:
                print(f"   💡 Large move (>5%) - likely to get FADE or FOLLOW verdict")
            else:
                print(f"   💡 Moderate move (3-5%) - substance score will determine action")

        else:
            # Below threshold - no LLM call
            pass  # Silent for non-triggered bars

    print("\n" + "=" * 80)
    print(f"📊 Summary:")
    print(f"   Total bars: {len(df) - 1}")
    print(f"   LLM triggers: {triggered_count} ({triggered_count / (len(df) - 1) * 100:.1f}%)")
    print(f"   Est. API cost: ${triggered_count * 0.20:.2f} (at $0.20/call)")

    if triggered_count == 0:
        print("\n⚠️  No significant moves detected in this period.")
        print("   Try extending --days parameter or using more volatile ticker (TSLA, MARA, etc.)")
    else:
        print(f"\n✅ {triggered_count} moves would be analyzed by real LLM in shadow trading.")


def main():
    """Run demo."""
    print("=" * 80)
    print("SHADOW TRADING DEMO - EXP-2025-009")
    print("No API key required - Preview only")
    print("=" * 80)

    tickers = ['NVDA', 'TSLA', 'AAPL']
    days = 10

    print(f"\n📋 Testing: {', '.join(tickers)}")
    print(f"📅 Period: Last {days} trading days")

    for ticker in tickers:
        try:
            df = fetch_recent_data(ticker, days)
            analyze_price_moves(ticker, df)
        except Exception as e:
            print(f"\n❌ Error with {ticker}: {e}")
            continue

    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)

    print("\nNext steps:")
    print("  1. Review SETUP_SHADOW_TRADING.md for API key setup")
    print("  2. Get DeepSeek API key from https://platform.deepseek.com/")
    print("  3. Run: python shadow_trading.py --ticker NVDA --days 5")
    print("  4. Validate LLM accuracy >65% before paper trading")


if __name__ == "__main__":
    main()
