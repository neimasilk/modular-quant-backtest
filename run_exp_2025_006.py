"""
EXP-2025-006: Bull Market Optimization

Tests BullOptimizedStrategy with:
1. ADX trend filter
2. Trailing stop (5% from peak)
3. Trend-aware mode switching

Goal: Improve NVDA 2023 return to >150% while maintaining SPY 2022 >10%
"""

import os
import sys
import pandas as pd
import numpy as np
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

from backtesting import Backtest
from src.strategies.bull_optimized_strategy import BullOptimizedStrategy, AdaptiveStrategy
from src.strategies.adaptive_strategy import BuyAndHoldStrategy


def prepare_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Prepare data with AI_Regime_Score and AI_Stock_Sentiment.
    """
    print(f"Fetching {ticker} data from {start_date} to {end_date}...")

    # Fetch price data
    price_data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    # Handle MultiIndex
    if isinstance(price_data.columns, pd.MultiIndex):
        price_data.columns = price_data.columns.get_level_values(0)

    price_data = price_data.reset_index()
    price_data['Date'] = pd.to_datetime(price_data['Date'])

    # Calculate VIX (realized volatility)
    price_data['VIX'] = price_data['Close'].pct_change().rolling(20).std() * np.sqrt(252)

    # Calculate AI_Regime_Score based on VIX
    def calculate_regime_score(vix):
        if pd.isna(vix):
            return 0.0
        if vix < 0.15:
            return 0.8  # Very bullish
        elif vix < 0.25:
            return 0.3  # Mildly bullish
        elif vix < 0.35:
            return 0.0  # Neutral
        elif vix < 0.50:
            return -0.3  # Mildly bearish
        else:
            return -0.8  # Very bearish

    price_data['AI_Regime_Score'] = price_data['VIX'].apply(calculate_regime_score)

    # Calculate heuristic sentiment (LAGGED to avoid look-ahead bias)
    price_data['AI_Stock_Sentiment'] = (
        price_data['Close'].pct_change(5).fillna(0) * 2
    ).clip(-1, 1).shift(1)  # Lag!

    price_data = price_data.set_index('Date')
    return price_data


def run_backtest(ticker: str, start: str, end: str, strategy_class, name: str,
                 initial_cash: float = 100_000, commission: float = 0.001):
    """Run single backtest and return stats."""
    df = prepare_data(ticker, start, end)

    bt = Backtest(
        df,
        strategy_class,
        cash=initial_cash,
        commission=commission,
        exclusive_orders=True
    )

    stats = bt.run()

    # Convert _Stats object to dict with only the metrics we need
    stats_dict = {
        'Return [%]': getattr(stats, 'Return [%]', None),
        'Sharpe Ratio': getattr(stats, 'Sharpe Ratio', None),
        'Max. Drawdown [%]': getattr(stats, 'Max. Drawdown [%]', None),
        'Win Rate [%]': getattr(stats, 'Win Rate [%]', None),
        '# Trades': getattr(stats, '# Trades', None),
        'Avg. Drawdown [%]': getattr(stats, 'Avg. Drawdown [%]', None),
        'Avg. Drawdown Duration': getattr(stats, 'Avg. Drawdown Duration', None),
        'Avg. Trade': getattr(stats, 'Avg. Trade', None),
        'Best Trade': getattr(stats, 'Best Trade', None),
        'Worst Trade': getattr(stats, 'Worst Trade', None),
    }

    return stats, stats_dict, df


def print_comparison_table(results: list):
    """Print comparison table of all results."""
    print("\n" + "=" * 80)
    print("BACKTEST COMPARISON TABLE")
    print("=" * 80)

    data = []
    for r in results:
        stats = r['stats']
        data.append({
            'Test Case': r['name'],
            'Strategy': r['strategy'],
            'Return %': f"{stats.get('Return [%]', 0):.2f}",
            'Sharpe': f"{stats.get('Sharpe Ratio', 0):.2f}",
            'Max DD %': f"{stats.get('Max. Drawdown [%]', 0):.2f}",
            '# Trades': stats.get('# Trades', 0)
        })

    df = pd.DataFrame(data)
    print(df.to_string(index=False))


def analyze_nvda_2023(results: dict):
    """Analyze NVDA 2023 results against targets."""
    print("\n" + "=" * 80)
    print("NVDA 2023 ANALYSIS (Primary Target)")
    print("=" * 80)

    original = results['nvda_2023']['original']
    optimized = results['nvda_2023']['optimized']
    bnh = results['nvda_2023']['bnh']

    print(f"\n{'Metric':<25} {'Original':<15} {'Optimized':<15} {'Buy&Hold':<15} {'Target'}")
    print("-" * 80)

    metrics = [
        ('Return %', 'Return [%]'),
        ('Sharpe Ratio', 'Sharpe Ratio'),
        ('Max Drawdown %', 'Max. Drawdown [%]'),
        ('Win Rate %', 'Win Rate [%]'),
        ('# Trades', '# Trades')
    ]

    for label, key in metrics:
        orig_val = original.get(key, 0)
        opt_val = optimized.get(key, 0)
        bnh_val = bnh.get(key, 0)

        # Color coding for return
        if key == 'Return [%]':
            status = "[OK]" if opt_val >= 150 else "[FAIL]"
            print(f"{label:<25} {orig_val:>14.2f}%   {opt_val:>14.2f}%   {bnh_val:>14.2f}%   >150% {status}")
        elif key == 'Sharpe Ratio':
            status = "[OK]" if opt_val >= 1.5 else "[FAIL]"
            print(f"{label:<25} {orig_val:>14.2f}      {opt_val:>14.2f}      {bnh_val:>14.2f}      >1.5 {status}")
        elif key == 'Max. Drawdown [%]':
            status = "[OK]" if opt_val <= 15 else "[FAIL]"
            print(f"{label:<25} {orig_val:>14.2f}%   {opt_val:>14.2f}%   {bnh_val:>14.2f}%   <15% {status}")
        else:
            print(f"{label:<25} {orig_val:>14.2f}      {opt_val:>14.2f}      {bnh_val:>14.2f}")

    # Improvement calculation
    print(f"\nIMPROVEMENTS:")
    print(f"  Return:     {optimized.get('Return [%]', 0) - original.get('Return [%]', 0):+.2f}% pts")
    print(f"  Sharpe:     {optimized.get('Sharpe Ratio', 0) - original.get('Sharpe Ratio', 0):+.2f}")
    print(f"  Max DD:     {optimized.get('Max. Drawdown [%]', 0) - original.get('Max. Drawdown [%]', 0):+.2f}% pts")

    # Gap to Buy&Hold
    gap_original = bnh.get('Return [%]', 0) - original.get('Return [%]', 0)
    gap_optimized = bnh.get('Return [%]', 0) - optimized.get('Return [%]', 0)
    print(f"\n  Gap to B&H: {gap_original:.2f}% -> {gap_optimized:.2f}% ({(gap_optimized - gap_original):+.2f}% improvement)")


def analyze_spy_2022(results: dict):
    """Analyze SPY 2022 results (must maintain bear market protection)."""
    print("\n" + "=" * 80)
    print("SPY 2022 ANALYSIS (Bear Market Validation)")
    print("=" * 80)

    original = results['spy_2022']['original']
    optimized = results['spy_2022']['optimized']
    bnh = results['spy_2022']['bnh']

    print(f"\n{'Metric':<25} {'Original':<15} {'Optimized':<15} {'Buy&Hold':<15} {'Min Target'}")
    print("-" * 80)

    metrics = [
        ('Return %', 'Return [%]'),
        ('Sharpe Ratio', 'Sharpe Ratio'),
        ('Max Drawdown %', 'Max. Drawdown [%]'),
        ('# Trades', '# Trades')
    ]

    for label, key in metrics:
        orig_val = original.get(key, 0)
        opt_val = optimized.get(key, 0)
        bnh_val = bnh.get(key, 0)

        if key == 'Return [%]':
            status = "[OK]" if opt_val >= 10 else "[FAIL]"
            print(f"{label:<25} {orig_val:>14.2f}%   {opt_val:>14.2f}%   {bnh_val:>14.2f}%   >10% {status}")
        elif key == 'Max. Drawdown [%]':
            status = "[OK]" if opt_val <= 10 else "[WARN]"
            print(f"{label:<25} {orig_val:>14.2f}%   {opt_val:>14.2f}%   {bnh_val:>14.2f}%   <10% {status}")
        else:
            print(f"{label:<25} {orig_val:>14.2f}      {opt_val:>14.2f}      {bnh_val:>14.2f}")

    print(f"\nCHANGE FROM ORIGINAL:")
    print(f"  Return:     {optimized.get('Return [%]', 0) - original.get('Return [%]', 0):+.2f}% pts")
    print(f"  Sharpe:     {optimized.get('Sharpe Ratio', 0) - original.get('Sharpe Ratio', 0):+.2f}")
    print(f"  Max DD:     {optimized.get('Max. Drawdown [%]', 0) - original.get('Max. Drawdown [%]', 0):+.2f}% pts")


def run_all_tests():
    """Run all EXP-2025-006 tests."""
    print("=" * 80)
    print("EXP-2025-006: Bull Market Optimization")
    print("=" * 80)
    print("\nTesting: BullOptimizedStrategy vs AdaptiveStrategy")
    print("Features: ADX trend filter + 5% trailing stop")
    print("-" * 80)

    results = {}

    # ========================================================================
    # TEST 1: NVDA 2023 (Bull Market - Primary Target)
    # ========================================================================
    print("\n[TEST 1/4] NVDA 2023 - Bull Market (Primary Target)")
    print("-" * 40)

    _, stats_nvda_orig, _ = run_backtest(
        'NVDA', '2023-01-01', '2024-01-01',
        AdaptiveStrategy, 'AdaptiveStrategy'
    )

    _, stats_nvda_opt, df_nvda = run_backtest(
        'NVDA', '2023-01-01', '2024-01-01',
        BullOptimizedStrategy, 'BullOptimizedStrategy'
    )

    _, stats_nvda_bnh, _ = run_backtest(
        'NVDA', '2023-01-01', '2024-01-01',
        BuyAndHoldStrategy, 'Buy&Hold'
    )

    results['nvda_2023'] = {
        'original': stats_nvda_orig,
        'optimized': stats_nvda_opt,
        'bnh': stats_nvda_bnh
    }

    # ========================================================================
    # TEST 2: SPY 2022 (Bear Market Validation)
    # ========================================================================
    print("\n[TEST 2/4] SPY 2022 - Bear Market Validation")
    print("-" * 40)

    _, stats_spy_orig, _ = run_backtest(
        'SPY', '2022-01-01', '2023-01-01',
        AdaptiveStrategy, 'AdaptiveStrategy'
    )

    _, stats_spy_opt, df_spy = run_backtest(
        'SPY', '2022-01-01', '2023-01-01',
        BullOptimizedStrategy, 'BullOptimizedStrategy'
    )

    _, stats_spy_bnh, _ = run_backtest(
        'SPY', '2022-01-01', '2023-01-01',
        BuyAndHoldStrategy, 'Buy&Hold'
    )

    results['spy_2022'] = {
        'original': stats_spy_orig,
        'optimized': stats_spy_opt,
        'bnh': stats_spy_bnh
    }

    # ========================================================================
    # TEST 3: AAPL 2023 (Additional Bull Market Validation)
    # ========================================================================
    print("\n[TEST 3/4] AAPL 2023 - Additional Bull Market Test")
    print("-" * 40)

    _, stats_aapl_orig, _ = run_backtest(
        'AAPL', '2023-01-01', '2024-01-01',
        AdaptiveStrategy, 'AdaptiveStrategy'
    )

    _, stats_aapl_opt, _ = run_backtest(
        'AAPL', '2023-01-01', '2024-01-01',
        BullOptimizedStrategy, 'BullOptimizedStrategy'
    )

    _, stats_aapl_bnh, _ = run_backtest(
        'AAPL', '2023-01-01', '2024-01-01',
        BuyAndHoldStrategy, 'Buy&Hold'
    )

    results['aapl_2023'] = {
        'original': stats_aapl_orig,
        'optimized': stats_aapl_opt,
        'bnh': stats_aapl_bnh
    }

    # ========================================================================
    # TEST 4: Multi-ticker 2023 (Consistency Check)
    # ========================================================================
    print("\n[TEST 4/4] Multi-Ticker 2023 - Consistency Check")
    print("-" * 40)

    tickers_2023 = ['NVDA', 'AAPL', 'SPY']
    multi_results = []

    for ticker in tickers_2023:
        _, stats_opt, _ = run_backtest(
            ticker, '2023-01-01', '2024-01-01',
            BullOptimizedStrategy, f'BullOpt_{ticker}'
        )
        _, stats_bnh, _ = run_backtest(
            ticker, '2023-01-01', '2024-01-01',
            BuyAndHoldStrategy, f'B&H_{ticker}'
        )

        multi_results.append({
            'ticker': ticker,
            'opt_return': stats_opt.get('Return [%]', 0),
            'opt_sharpe': stats_opt.get('Sharpe Ratio', 0),
            'opt_dd': stats_opt.get('Max. Drawdown [%]', 0),
            'opt_trades': stats_opt.get('# Trades', 0),
            'bnh_return': stats_bnh.get('Return [%]', 0),
        })

    results['multi_2023'] = multi_results

    # ========================================================================
    # PRINT ANALYSES
    # ========================================================================

    # Build comparison table
    comparison_data = []

    # NVDA 2023
    comparison_data.append({
        'name': 'NVDA 2023',
        'strategy': 'Original',
        'stats': stats_nvda_orig
    })
    comparison_data.append({
        'name': 'NVDA 2023',
        'strategy': 'Optimized',
        'stats': stats_nvda_opt
    })
    comparison_data.append({
        'name': 'NVDA 2023',
        'strategy': 'Buy&Hold',
        'stats': stats_nvda_bnh
    })

    # SPY 2022
    comparison_data.append({
        'name': 'SPY 2022',
        'strategy': 'Original',
        'stats': stats_spy_orig
    })
    comparison_data.append({
        'name': 'SPY 2022',
        'strategy': 'Optimized',
        'stats': stats_spy_opt
    })
    comparison_data.append({
        'name': 'SPY 2022',
        'strategy': 'Buy&Hold',
        'stats': stats_spy_bnh
    })

    print_comparison_table(comparison_data)
    analyze_nvda_2023(results)
    analyze_spy_2022(results)

    # Multi-ticker summary
    print("\n" + "=" * 80)
    print("MULTI-TICKER 2023 SUMMARY")
    print("=" * 80)
    print(f"\n{'Ticker':<10} {'Return %':<12} {'Sharpe':<10} {'Max DD %':<12} {'Trades':<8} {'vs B&H'}")
    print("-" * 80)

    for r in multi_results:
        vs_bnh = r['opt_return'] - r['bnh_return']
        print(f"{r['ticker']:<10} {r['opt_return']:>10.2f}%   {r['opt_sharpe']:>8.2f}   "
              f"{r['opt_dd']:>10.2f}%   {r['opt_trades']:>6}   {vs_bnh:+>7.2f}%")

    # ========================================================================
    # SAVE RESULTS
    # ========================================================================
    output_dir = "experiments/active/EXP-2025-006-bull-market-optimization/results"
    os.makedirs(output_dir, exist_ok=True)

    # Save comparison
    df_comparison = pd.DataFrame([
        {
            'Test_Case': r['name'],
            'Strategy': r['strategy'],
            'Return_Pct': r['stats'].get('Return [%]', 0),
            'Sharpe_Ratio': r['stats'].get('Sharpe Ratio', 0),
            'Max_Drawdown_Pct': r['stats'].get('Max. Drawdown [%]', 0),
            'Trades': r['stats'].get('# Trades', 0)
        }
        for r in comparison_data
    ])
    df_comparison.to_csv(f"{output_dir}/comparison.csv", index=False)

    # Save multi-ticker results
    df_multi = pd.DataFrame(multi_results)
    df_multi.to_csv(f"{output_dir}/multi_ticker_2023.csv", index=False)

    print(f"\n[OK] Results saved to: {output_dir}/")

    return results


if __name__ == "__main__":
    try:
        results = run_all_tests()

        # Final assessment
        print("\n" + "=" * 80)
        print("FINAL ASSESSMENT")
        print("=" * 80)

        nvda_opt = results['nvda_2023']['optimized'].get('Return [%]', 0)
        spy_opt = results['spy_2022']['optimized'].get('Return [%]', 0)

        print(f"\nNVDA 2023 Return: {nvda_opt:.2f}% (Target: >150%)")
        print(f"SPY 2022 Return: {spy_opt:.2f}% (Target: >10%)")

        if nvda_opt >= 150 and spy_opt >= 10:
            print("\n[SUCCESS] ALL TARGETS MET! Strategy ready for full cycle testing.")
        elif nvda_opt >= 120 and spy_opt >= 8:
            print("\n[PARTIAL] TARGETS NEARLY MET. Minor tuning may help.")
        else:
            print("\n[FAILED] TARGETS NOT MET. Further optimization needed.")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
