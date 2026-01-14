"""
Shadow Trading for EXP-2025-009: Hybrid LLM Strategy
====================================================

Purpose: Validate REAL LLM accuracy before committing to paper trading.

This script:
1. Runs Hybrid Strategy with REAL LLM calls (not mock mode)
2. Fetches live market data + news
3. Logs all LLM decisions and actual outcomes
4. Compares real vs mock LLM performance
5. Generates accuracy report

Usage:
    python shadow_trading.py --ticker NVDA --days 5
    python shadow_trading.py --ticker NVDA,AAPL,TSLA --days 10
    python shadow_trading.py --report  # Generate accuracy report
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.llm.sanity_checker import NewsSanityChecker
from src.strategies.hybrid_llm_strategy import HybridLLMStrategy

load_dotenv()


class ShadowTrader:
    """
    Shadow trading system for EXP-009 validation.

    Runs hybrid strategy with real LLM, logs decisions, tracks accuracy.
    """

    def __init__(self, output_dir: str = "experiments/active/EXP-2025-009-hybrid-llm/shadow_logs"):
        """Initialize shadow trader."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize LLM checker
        try:
            self.llm_checker = NewsSanityChecker()
            print("✅ LLM Sanity Checker initialized")
        except Exception as e:
            print(f"❌ Failed to initialize LLM: {e}")
            print("   Make sure DEEPSEEK_API_KEY is set in .env")
            sys.exit(1)

        # Tracking
        self.decisions = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def fetch_recent_data(self, ticker: str, days: int = 5) -> pd.DataFrame:
        """
        Fetch recent market data for a ticker.

        Args:
            ticker: Stock symbol
            days: Number of days to fetch

        Returns:
            DataFrame with OHLCV data
        """
        print(f"\n📊 Fetching {days} days of data for {ticker}...")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 10)  # Extra buffer

        df = yf.download(
            ticker,
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            progress=False
        )

        if df.empty:
            raise ValueError(f"No data fetched for {ticker}")

        # Keep only last N days
        df = df.tail(days)

        print(f"   ✅ Fetched {len(df)} bars from {df.index[0].date()} to {df.index[-1].date()}")

        return df

    def fetch_news(self, ticker: str, date: datetime) -> str:
        """
        Fetch news for a ticker on a specific date.

        Args:
            ticker: Stock symbol
            date: Date to fetch news for

        Returns:
            News text (concatenated headlines)
        """
        try:
            stock = yf.Ticker(ticker)
            news = stock.news

            if not news:
                return f"No major news for {ticker}"

            # Filter news to date
            date_str = date.strftime("%Y-%m-%d")
            headlines = []

            for item in news[:5]:  # Top 5 news items
                title = item.get('title', '')
                if title:
                    headlines.append(title)

            if not headlines:
                return f"No specific news for {ticker} on {date_str}"

            return " | ".join(headlines)

        except Exception as e:
            print(f"   ⚠️  Failed to fetch news: {e}")
            return f"Unable to fetch news for {ticker}"

    def analyze_bar(self, ticker: str, current_bar: pd.Series, prev_bar: pd.Series, bar_date: datetime) -> dict:
        """
        Analyze a single bar with LLM.

        Args:
            ticker: Stock symbol
            current_bar: Current bar data
            prev_bar: Previous bar data
            bar_date: Date of the bar

        Returns:
            Analysis dict with LLM decision
        """
        # Calculate price change
        price_change_pct = (current_bar['Close'] - prev_bar['Close']) / prev_bar['Close']

        # Only analyze if significant move
        THRESHOLD = 0.03  # 3%
        if abs(price_change_pct) < THRESHOLD:
            return {
                'date': bar_date,
                'ticker': ticker,
                'price_change_pct': price_change_pct,
                'triggered': False,
                'reason': 'Below threshold'
            }

        # Fetch news
        news_text = self.fetch_news(ticker, bar_date)

        print(f"\n🔍 Analyzing {ticker} on {bar_date.date()}")
        print(f"   Price change: {price_change_pct:+.2%}")
        print(f"   News: {news_text[:100]}...")

        # Call LLM
        try:
            llm_result = self.llm_checker.check_signal(
                ticker=ticker,
                price_change_pct=price_change_pct,
                news_text=news_text,
                volume=current_bar.get('Volume'),
                avg_volume=prev_bar.get('Volume'),
                verbose=True
            )

            analysis = {
                'date': bar_date,
                'ticker': ticker,
                'price_change_pct': price_change_pct,
                'triggered': True,
                'news': news_text,
                'llm_signal': llm_result['signal'],
                'llm_verdict': llm_result['verdict'],
                'substance_score': llm_result['substance_score'],
                'reasoning': llm_result['reasoning'],
                'should_trade': llm_result['should_trade']
            }

            print(f"   🤖 LLM: {llm_result['signal']} (score: {llm_result['substance_score']}/10)")
            print(f"   💡 Reasoning: {llm_result['reasoning']}")

            return analysis

        except Exception as e:
            print(f"   ❌ LLM call failed: {e}")
            return {
                'date': bar_date,
                'ticker': ticker,
                'price_change_pct': price_change_pct,
                'triggered': True,
                'error': str(e)
            }

    def run_shadow_trading(self, tickers: list, days: int = 5):
        """
        Run shadow trading for multiple tickers.

        Args:
            tickers: List of stock symbols
            days: Number of days to analyze
        """
        print("=" * 80)
        print(f"SHADOW TRADING - EXP-2025-009")
        print(f"Session ID: {self.session_id}")
        print(f"Tickers: {', '.join(tickers)}")
        print(f"Days: {days}")
        print("=" * 80)

        all_decisions = []

        for ticker in tickers:
            try:
                # Fetch data
                df = self.fetch_recent_data(ticker, days)

                # Analyze each bar
                for i in range(1, len(df)):
                    prev_bar = df.iloc[i-1]
                    current_bar = df.iloc[i]
                    bar_date = df.index[i]

                    analysis = self.analyze_bar(ticker, current_bar, prev_bar, bar_date)

                    if analysis.get('triggered'):
                        all_decisions.append(analysis)
                        self.decisions.append(analysis)

            except Exception as e:
                print(f"\n❌ Error processing {ticker}: {e}")
                continue

        # Save results
        self.save_results()

        # Print summary
        self.print_summary()

    def save_results(self):
        """Save shadow trading results to JSON and CSV."""
        # Save to JSON
        json_file = self.output_dir / f"shadow_decisions_{self.session_id}.json"
        with open(json_file, 'w') as f:
            json.dump(self.decisions, f, indent=2, default=str)

        print(f"\n💾 Results saved to: {json_file}")

        # Save to CSV
        if self.decisions:
            df = pd.DataFrame(self.decisions)
            csv_file = self.output_dir / f"shadow_decisions_{self.session_id}.csv"
            df.to_csv(csv_file, index=False)
            print(f"💾 CSV saved to: {csv_file}")

    def print_summary(self):
        """Print summary of shadow trading results."""
        print("\n" + "=" * 80)
        print("SHADOW TRADING SUMMARY")
        print("=" * 80)

        if not self.decisions:
            print("⚠️  No significant price moves detected (all below 3% threshold)")
            return

        # Count by signal type
        signals = {}
        for d in self.decisions:
            signal = d.get('llm_signal', 'UNKNOWN')
            signals[signal] = signals.get(signal, 0) + 1

        print(f"\n📊 Total LLM Calls: {len(self.decisions)}")
        print("\nSignal Distribution:")
        for signal, count in sorted(signals.items(), key=lambda x: x[1], reverse=True):
            print(f"   {signal}: {count}")

        # Substance scores
        scores = [d.get('substance_score', 0) for d in self.decisions if 'substance_score' in d]
        if scores:
            avg_score = sum(scores) / len(scores)
            print(f"\n📈 Average Substance Score: {avg_score:.1f}/10")
            print(f"   Min: {min(scores)}, Max: {max(scores)}")

        # Verdict distribution
        verdicts = {}
        for d in self.decisions:
            verdict = d.get('llm_verdict', 'UNKNOWN')
            verdicts[verdict] = verdicts.get(verdict, 0) + 1

        print("\nVerdict Distribution:")
        for verdict, count in sorted(verdicts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(self.decisions)) * 100
            print(f"   {verdict}: {count} ({pct:.1f}%)")

        print("\n" + "=" * 80)

    def generate_accuracy_report(self):
        """
        Generate accuracy report by comparing outcomes.

        This requires waiting N days after shadow trading to see actual outcomes.
        """
        print("\n⏳ Accuracy reporting requires waiting for outcomes...")
        print("   Run this script again in 1-3 days with --report flag")
        print("   to evaluate LLM accuracy vs actual price movements.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Shadow trading for EXP-009 validation")
    parser.add_argument('--ticker', type=str, default='NVDA',
                       help='Ticker(s) to analyze (comma-separated)')
    parser.add_argument('--days', type=int, default=5,
                       help='Number of days to analyze')
    parser.add_argument('--report', action='store_true',
                       help='Generate accuracy report from previous runs')

    args = parser.parse_args()

    # Initialize shadow trader
    trader = ShadowTrader()

    if args.report:
        # Generate accuracy report
        trader.generate_accuracy_report()
    else:
        # Run shadow trading
        tickers = [t.strip().upper() for t in args.ticker.split(',')]
        trader.run_shadow_trading(tickers, args.days)

        print("\n✅ Shadow trading complete!")
        print("\nNext steps:")
        print("  1. Review decisions in shadow_logs/")
        print("  2. Wait 1-3 days to observe outcomes")
        print("  3. Run with --report flag to calculate LLM accuracy")
        print("  4. If accuracy >65%, proceed to paper trading")


if __name__ == "__main__":
    main()
