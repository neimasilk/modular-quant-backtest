"""
Shadow Trading Test for EXP-2025-008

This script runs the SanityChecker in "shadow mode" - it prints what it WOULD do
without actually executing trades. Use this to validate the LLM's judgment.

Run with: python experiments/active/EXP-2025-008-llm-sanity-check/shadow_test.py
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path - handle both script execution and module import
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Also try parent directory of experiments
EXPERIMENTS_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
if EXPERIMENTS_ROOT not in sys.path:
    sys.path.insert(0, EXPERIMENTS_ROOT)

from src.llm.sanity_checker import NewsSanityChecker
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()


# ============== TEST SCENARIOS ==============

REAL_WORLD_SCENARIOS = [
    {
        "name": "AI Washing Hype",
        "ticker": "XYZ",
        "price_change_pct": 0.08,  # +8%
        "volume_spike": 2.5,
        "news": "XYZ Corp announces strategic AI initiative to revolutionize business operations",
        "expected": "SHORT_SCALP",  # Should fade the hype
        "description": "Classic buzzword pump - no actual product or revenue mentioned"
    },
    {
        "name": "Panic Selling on Minor Issue",
        "ticker": "TSLA",
        "price_change_pct": -0.05,  # -5%
        "volume_spike": 1.8,
        "news": "Tesla factory in Germany pauses production for 3 days due to local protests",
        "expected": "BUY_DIP",  # Should buy the overreaction
        "description": "Temporary disruption, irrelevant to long-term thesis"
    },
    {
        "name": "Legitimate Earnings Beat",
        "ticker": "NVDA",
        "price_change_pct": 0.10,  # +10%
        "volume_spike": 3.0,
        "news": "NVIDIA Q4 earnings: Revenue $26B vs est $22B, Data Center revenue up 400% YoY",
        "expected": "BUY_TREND",  # Should follow the real move
        "description": "Hard numbers, massive beat - justified rally"
    },
    {
        "name": "Real Trouble - Accounting Fraud",
        "ticker": "ABC",
        "price_change_pct": -0.20,  # -20%
        "volume_spike": 5.0,
        "news": "DOJ opens criminal investigation into ABC Corp accounting practices",
        "expected": "HARD_EXIT",  # Should get out immediately
        "description": "Structural problem - don't catch this knife"
    },
    {
        "name": "Merger Rumor (Unconfirmed)",
        "ticker": "META",
        "price_change_pct": 0.06,  # +6%
        "volume_spike": 2.0,
        "news": "Sources say META in talks to acquire XYZ, no official confirmation",
        "expected": "SHORT_SCALP",  # Should fade unconfirmed rumors
        "description": "Rumor-based pump often reverses"
    },
    {
        "name": "Fed Rate Cut (Macro Event)",
        "ticker": "SPY",
        "price_change_pct": 0.025,  # +2.5%
        "volume_spike": 1.5,
        "news": "Federal Reserve cuts interest rates by 25 bps as expected",
        "expected": "FOLLOW",  # Should follow the macro trend
        "description": "Priced-in event, slight move justified"
    },
    {
        "name": "CEO Resigns Suddenly",
        "ticker": "OKTA",
        "price_change_pct": -0.08,  # -8%
        "volume_spike": 3.5,
        "news": "Okta CEO resigns effective immediately, no replacement named",
        "expected": "HARD_EXIT",  # Leadership vacuum is serious
        "description": "Uncertainty is high - avoid catching"
    },
    {
        "name": "Product Recall (Limited Scope)",
        "ticker": "CPST",
        "price_change_pct": -0.04,  # -4%
        "volume_spike": 1.8,
        "news": "Company recalls 50,000 units due to minor labeling issue, cost estimated $2M",
        "expected": "BUY_DIP",  # Minor issue, overreaction likely
        "description": "$2M is nothing for large cap - overreaction"
    }
]


# ============== SHADOW TRADER CLASS ==============

class ShadowTrader:
    """
    Simulates trading decisions using SanityChecker without actual execution.
    Tracks what WOULD have happened for analysis.
    """

    def __init__(self):
        self.checker = None
        self.trades = []
        self.correct_calls = 0
        self.wrong_calls = 0

    def run_scenario(self, scenario: dict) -> dict:
        """Run a single scenario through the sanity checker."""
        print("\n" + "=" * 70)
        print(f"SCENARIO: {scenario['name']}")
        print("=" * 70)

        print(f"Ticker:        {scenario['ticker']}")
        print(f"Price Move:    {scenario['price_change_pct']:+.1%}")
        print(f"Volume Spike:  {scenario['volume_spike']:.1f}x average")
        print(f"News:          {scenario['news']}")
        print(f"Description:   {scenario['description']}")
        print(f"Expected:      {scenario['expected']}")

        # Initialize checker if needed
        if self.checker is None:
            try:
                self.checker = NewsSanityChecker()
            except ValueError as e:
                print(f"\nERROR: {e}")
                print("\nTo run this test, set DEEPSEEK_API_KEY in your .env file")
                return {"error": str(e)}

        # Get LLM analysis
        result = self.checker.check_signal(
            ticker=scenario['ticker'],
            price_change_pct=scenario['price_change_pct'],
            news_text=scenario['news'],
            verbose=True
        )

        # Compare with expected
        expected = scenario['expected']
        actual = result['signal']
        match = "[OK] CORRECT" if expected == actual else "[X] WRONG"

        print(f"\nExpected Signal: {expected}")
        print(f"Actual Signal:   {actual}")
        print(f"Match:           {match}")

        if expected == actual:
            self.correct_calls += 1
        else:
            self.wrong_calls += 1

        return {
            "scenario": scenario['name'],
            "expected": expected,
            "actual": actual,
            "match": expected == actual,
            "substance_score": result['substance_score'],
            "verdict": result['verdict']
        }

    def run_all_scenarios(self, scenarios: list) -> pd.DataFrame:
        """Run all test scenarios."""
        results = []

        for scenario in scenarios:
            result = self.run_scenario(scenario)
            if "error" not in result:
                results.append(result)

        # Create summary DataFrame
        df = pd.DataFrame(results)

        print("\n" + "=" * 70)
        print("SHADOW TRADING SUMMARY")
        print("=" * 70)
        print(f"\nTotal Scenarios:  {len(results)}")
        print(f"Correct Calls:    {self.correct_calls} ({self.correct_calls/len(results)*100:.1f}%)")
        print(f"Wrong Calls:      {self.wrong_calls} ({self.wrong_calls/len(results)*100:.1f}%)")

        # Show breakdown by signal type
        print("\nBreakdown by Signal:")
        signal_counts = df['actual'].value_counts()
        for signal, count in signal_counts.items():
            print(f"  {signal}: {count}")

        # Show missed scenarios
        missed = df[df['match'] == False]
        if not missed.empty:
            print("\nMissed Scenarios:")
            for _, row in missed.iterrows():
                print(f"  - {row['scenario']}: Expected {row['expected']}, got {row['actual']}")

        # Accuracy threshold
        accuracy = self.correct_calls / len(results) if len(results) > 0 else 0
        print(f"\nOverall Accuracy: {accuracy:.1%}")

        if accuracy >= 0.70:
            print(">>> EXCELLENT! LLM shows strong judgment accuracy.")
        elif accuracy >= 0.50:
            print(">>> ACCEPTABLE. LLM is better than random, but needs tuning.")
        else:
            print(">>> POOR. LLM needs significant prompt tuning.")

        return df


# ============== LIVE MONITORING MODE ==============

class LiveMonitor:
    """
    Monitors live price moves and suggests actions based on news.
    For use with real-time data feeds (future implementation).
    """

    def __init__(self, tickers: list):
        self.tickers = tickers
        self.checker = None
        self.price_history = {}

    def fetch_latest_data(self):
        """Fetch latest price data for monitored tickers."""
        for ticker in self.tickers:
            try:
                data = yf.Ticker(ticker).history(period="5d", interval="1h")
                if not data.empty:
                    self.price_history[ticker] = data
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")

    def check_for_volatility_spikes(self) -> list:
        """
        Check for volatility spikes that would trigger LLM analysis.

        Returns list of scenarios that need LLM validation.
        """
        triggers = []

        for ticker, data in self.price_history.items():
            if len(data) < 2:
                continue

            # Calculate recent move
            latest_close = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
            change_pct = (latest_close - prev_close) / prev_close

            # Check volume spike
            latest_volume = data['Volume'].iloc[-1]
            avg_volume = data['Volume'].mean()

            if abs(change_pct) > 0.03:  # 3% threshold
                triggers.append({
                    'ticker': ticker,
                    'price_change_pct': change_pct,
                    'volume': latest_volume,
                    'avg_volume': avg_volume
                })

        return triggers


# ============== MAIN ==============

def main():
    """Run shadow trading test."""
    print("\n")
    print("=" * 70)
    print(" " * 15 + "SHADOW TRADING TEST")
    print(" " * 10 + "EXP-2025-008: LLM Sanity Check")
    print(" " * 20 + "'The Bullshit Detector'")
    print("=" * 70)

    print("\nMode: SHADOW (no real trades)")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check for API key
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("\nWARNING: DEEPSEEK_API_KEY not found in .env")
        print("To run this test:")
        print("  1. Create a .env file in the project root")
        print("  2. Add: DEEPSEEK_API_KEY=your_key_here")
        print("  3. Run this script again")
        return

    # Run scenarios
    trader = ShadowTrader()
    results_df = trader.run_all_scenarios(REAL_WORLD_SCENARIOS)

    # Save results
    output_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(output_dir, f"shadow_test_{timestamp}.csv")
    results_df.to_csv(results_file, index=False)
    print(f"\nResults saved to: {results_file}")

    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    accuracy = trader.correct_calls / len(results_df) if len(results_df) > 0 else 0

    if accuracy >= 0.70:
        print("\n[OK] LLM accuracy is GOOD. Ready for paper trading phase.")
        print("  Next steps:")
        print("  1. Set up paper trading account")
        print("  2. Connect to real-time news feed")
        print("  3. Start with small position sizes")
    elif accuracy >= 0.50:
        print("\n[!] LLM accuracy is MODERATE. Consider:")
        print("  1. Adjusting the system prompt to be more/less skeptical")
        print("  2. Fine-tuning substance score thresholds")
        print("  3. Running more test scenarios")
    else:
        print("\n[X] LLM accuracy is POOR. Recommendations:")
        print("  1. Significant prompt engineering needed")
        print("  2. Consider different LLM model")
        print("  3. May need to change approach entirely")


if __name__ == "__main__":
    main()
