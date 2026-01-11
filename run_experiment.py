"""
Experiment Runner - EXP-2025-001: Fix Look-Ahead Bias
======================================================
Run backtests before and after fixing look-ahead bias.

Usage:
    python run_experiment.py --data data/nvda_real_data_2023.csv
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backtesting import Backtest
from src.strategies.adaptive_strategy import AdaptiveStrategy, BuyAndHoldStrategy


def load_real_data(csv_path: str) -> pd.DataFrame:
    """Load real market data from CSV."""
    df = pd.read_csv(csv_path)

    # Convert Date to datetime and set as index
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')

    # Ensure required columns exist
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'VIX', 'AI_Regime_Score', 'AI_Stock_Sentiment']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    return df


def fix_look_ahead_bias(df: pd.DataFrame, method: str = "shift") -> pd.DataFrame:
    """
    Fix look-ahead bias in AI_Stock_Sentiment column.

    Methods:
    - "shift": Shift sentiment by 1 day (uses yesterday's sentiment for today's decision)
    - "zero": Set all sentiment to 0 (no sentiment signal)
    - "neutral": Set sentiment to neutral based on regime only
    """
    df_fixed = df.copy()

    if method == "shift":
        # Shift sentiment by 1 day so we use yesterday's sentiment
        # First row will be NaN, fill with 0
        df_fixed['AI_Stock_Sentiment'] = df_fixed['AI_Stock_Sentiment'].shift(1).fillna(0)
    elif method == "zero":
        # Remove sentiment signal entirely
        df_fixed['AI_Stock_Sentiment'] = 0.0
    elif method == "neutral":
        # Set sentiment based on regime only (more conservative)
        df_fixed['AI_Stock_Sentiment'] = df_fixed['AI_Regime_Score'] * 0.3
    else:
        raise ValueError(f"Unknown method: {method}")

    return df_fixed


def run_backtest(data: pd.DataFrame, strategy_class, initial_cash: float = 100000):
    """Run backtest and return metrics."""
    bt = Backtest(
        data,
        strategy_class,
        cash=initial_cash,
        commission=0.001,
        exclusive_orders=True
    )

    stats = bt.run()

    return stats


def print_results(name: str, stats, method: str = ""):
    """Print backtest results."""
    print(f"\n{'='*70}")
    print(f"{name}")
    if method:
        print(f"Method: {method}")
    print('='*70)

    print(f"Return [%]:           {stats['Return [%]']:.2f}")
    print(f"Return (Ann.) [%]:    {stats.get('Return (Ann.) [%]', 0):.2f}")
    print(f"Sharpe Ratio:         {stats['Sharpe Ratio']:.2f}")
    print(f"Sortino Ratio:        {stats.get('Sortino Ratio', 0):.2f}")
    print(f"Max Drawdown [%]:     {stats['Max. Drawdown [%]']:.2f}")
    print(f"Win Rate [%]:         {stats.get('Win Rate [%]', 0):.2f}")
    print(f"# Trades:             {stats['# Trades']}")

    # Get regime trades if available
    strategy = stats.get('_strategy')
    if strategy and hasattr(strategy, 'regime_trades'):
        print(f"\nRegime Trades:")
        print(f"  Bullish:  {strategy.regime_trades.get('BULLISH', 0)}")
        print(f"  Bearish:  {strategy.regime_trades.get('BEARISH', 0)}")
        print(f"  Sideways: {strategy.regime_trades.get('SIDEWAYS', 0)}")


def main():
    parser = argparse.ArgumentParser(description="Run EXP-2025-001: Fix Look-Ahead Bias")
    parser.add_argument('--data', '-d', default='data/nvda_real_data_2023.csv', help='Path to data CSV')
    parser.add_argument('--method', '-m', default='shift', choices=['shift', 'zero', 'neutral'],
                        help='Bias fix method')
    parser.add_argument('--compare', '-c', action='store_true', help='Compare all methods')
    args = parser.parse_args()

    print("\n" + "="*70)
    print("EXPERIMENT EXP-2025-001: Fix Look-Ahead Bias".center(70))
    print("="*70)

    # Load data
    print(f"\nLoading data from: {args.data}")
    original_data = load_real_data(args.data)
    print(f"Data shape: {original_data.shape}")
    print(f"Date range: {original_data.index[0]} to {original_data.index[-1]}")

    # Check for look-ahead bias
    print(f"\nOriginal AI_Stock_Sentiment stats:")
    print(f"  Mean: {original_data['AI_Stock_Sentiment'].mean():.4f}")
    print(f"  Std:  {original_data['AI_Stock_Sentiment'].std():.4f}")
    print(f"  Min:  {original_data['AI_Stock_Sentiment'].min():.4f}")
    print(f"  Max:  {original_data['AI_Stock_Sentiment'].max():.4f}")

    # Calculate correlation with returns (evidence of look-ahead bias)
    returns = original_data['Close'].pct_change()
    sentiment_bias_corr = original_data['AI_Stock_Sentiment'].corr(returns)
    print(f"\nCorrelation (Sentiment vs Same-Day Returns): {sentiment_bias_corr:.4f}")
    if abs(sentiment_bias_corr) > 0.3:
        print("  WARNING: High correlation indicates look-ahead bias!")

    print("\n" + "-"*70)

    if args.compare:
        # Compare all methods
        methods = ['original', 'shift', 'zero', 'neutral']
        results = []

        for method in methods:
            if method == 'original':
                data = original_data
            else:
                data = fix_look_ahead_bias(original_data, method=method)

            stats = run_backtest(data, AdaptiveStrategy)

            result = {
                'method': method,
                'return': stats['Return [%]'],
                'sharpe': stats['Sharpe Ratio'],
                'max_dd': stats['Max. Drawdown [%]'],
                'win_rate': stats.get('Win Rate [%]', 0),
                'trades': stats['# Trades']
            }
            results.append(result)

            print_results(f"Backtest Results: {method.upper()}", stats, method)

        # Print comparison table
        print(f"\n{'='*70}")
        print("COMPARISON TABLE")
        print('='*70)
        print(f"{'Method':<12} {'Return %':<12} {'Sharpe':<10} {'Max DD %':<12} {'Win Rate %':<12} {'# Trades':<10}")
        print("-"*70)
        for r in results:
            print(f"{r['method']:<12} {r['return']:<12.2f} {r['sharpe']:<10.2f} {r['max_dd']:<12.2f} {r['win_rate']:<12.2f} {r['trades']:<10}")

        # Also run Buy & Hold for comparison
        print(f"\n{'='*70}")
        print("BENCHMARK: Buy & Hold")
        print('='*70)
        bh_stats = run_backtest(original_data, BuyAndHoldStrategy)
        print_results("Buy & Hold", bh_stats)

    else:
        # Run single method
        if args.method == 'original':
            data = original_data
            print("\nRunning ORIGINAL (with look-ahead bias)")
        else:
            data = fix_look_ahead_bias(original_data, method=args.method)
            print(f"\nRunning FIXED method: {args.method}")

        stats = run_backtest(data, AdaptiveStrategy)
        print_results("Backtest Results", stats, args.method)


if __name__ == "__main__":
    main()
