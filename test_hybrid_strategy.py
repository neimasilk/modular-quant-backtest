"""
Test Script for Hybrid LLM Strategy - EXP-2025-009
===================================================

Compares:
1. Adaptive Strategy (baseline)
2. Hybrid Strategy with Mock LLM (70% accuracy)
3. Hybrid Strategy with different accuracy levels

Goal: Demonstrate LLM filter value in reducing drawdown and improving Sharpe.

Usage:
    python test_hybrid_strategy.py
"""

import pandas as pd
from backtesting import Backtest
from src.strategies.adaptive_strategy import AdaptiveStrategy
from src.strategies.hybrid_llm_strategy import HybridLLMStrategy
import os


def load_test_data(ticker: str = 'NVDA', year: int = 2023):
    """
    Load historical data for backtesting.

    Args:
        ticker: Stock ticker (NVDA, AAPL, SPY)
        year: Year to test (2022, 2023)

    Returns:
        DataFrame with OHLCV + AI signals
    """
    filename = f"data/{ticker}_{year}.csv"

    if not os.path.exists(filename):
        print(f"[ERROR] File not found: {filename}")
        print("Available data files:")
        for f in os.listdir('data'):
            if f.endswith('.csv'):
                print(f"  - data/{f}")
        raise FileNotFoundError(f"Data file {filename} not found")

    df = pd.read_csv(filename)

    # Ensure required columns exist
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'AI_Regime_Score', 'AI_Stock_Sentiment']
    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Convert date to datetime index
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
    elif 'Datetime' in df.columns:
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df.set_index('Datetime', inplace=True)

    return df


def run_comparison_backtest(ticker: str = 'NVDA', year: int = 2023, cash: float = 10000):
    """
    Run comparison backtest between Adaptive and Hybrid strategies.

    Args:
        ticker: Stock ticker
        year: Year to test
        cash: Starting cash

    Returns:
        Dictionary of results
    """
    print("=" * 80)
    print(f"HYBRID LLM STRATEGY TEST - {ticker} {year}")
    print("=" * 80)

    # Load data
    print(f"\n[1/5] Loading data for {ticker} {year}...")
    df = load_test_data(ticker, year)
    print(f"      Loaded {len(df)} bars from {df.index[0]} to {df.index[-1]}")

    results = {}

    # === TEST 1: Baseline (Adaptive Strategy) ===
    print("\n[2/5] Running Adaptive Strategy (baseline)...")
    bt_adaptive = Backtest(
        df,
        AdaptiveStrategy,
        cash=cash,
        commission=0.0,  # No commission for fair comparison
        exclusive_orders=True
    )

    stats_adaptive = bt_adaptive.run()
    results['Adaptive'] = stats_adaptive

    print(f"      Return: {stats_adaptive['Return [%]']:.2f}%")
    print(f"      Sharpe: {stats_adaptive['Sharpe Ratio']:.2f}")
    print(f"      Max DD: {stats_adaptive['Max. Drawdown [%]']:.2f}%")
    print(f"      Trades: {stats_adaptive['# Trades']}")

    # === TEST 2: Hybrid with Mock LLM (70% accuracy) ===
    print("\n[3/5] Running Hybrid Strategy (mock LLM, 70% accuracy)...")
    bt_hybrid_70 = Backtest(
        df,
        HybridLLMStrategy,
        cash=cash,
        commission=0.0,
        exclusive_orders=True
    )

    stats_hybrid_70 = bt_hybrid_70.run(
        llm_enabled=True,
        mock_llm_mode=True,
        mock_llm_accuracy=0.70,
        llm_veto_enabled=True,
        llm_override_enabled=True
    )
    results['Hybrid_70'] = stats_hybrid_70

    print(f"      Return: {stats_hybrid_70['Return [%]']:.2f}%")
    print(f"      Sharpe: {stats_hybrid_70['Sharpe Ratio']:.2f}")
    print(f"      Max DD: {stats_hybrid_70['Max. Drawdown [%]']:.2f}%")
    print(f"      Trades: {stats_hybrid_70['# Trades']}")

    # === TEST 3: Hybrid with Mock LLM (85% accuracy - optimistic) ===
    print("\n[4/5] Running Hybrid Strategy (mock LLM, 85% accuracy - optimistic)...")
    bt_hybrid_85 = Backtest(
        df,
        HybridLLMStrategy,
        cash=cash,
        commission=0.0,
        exclusive_orders=True
    )

    stats_hybrid_85 = bt_hybrid_85.run(
        llm_enabled=True,
        mock_llm_mode=True,
        mock_llm_accuracy=0.85,
        llm_veto_enabled=True,
        llm_override_enabled=True
    )
    results['Hybrid_85'] = stats_hybrid_85

    print(f"      Return: {stats_hybrid_85['Return [%]']:.2f}%")
    print(f"      Sharpe: {stats_hybrid_85['Sharpe Ratio']:.2f}")
    print(f"      Max DD: {stats_hybrid_85['Max. Drawdown [%]']:.2f}%")
    print(f"      Trades: {stats_hybrid_85['# Trades']}")

    # === TEST 4: Hybrid with only veto (no override) ===
    print("\n[5/5] Running Hybrid Strategy (veto only, no override)...")
    bt_hybrid_veto = Backtest(
        df,
        HybridLLMStrategy,
        cash=cash,
        commission=0.0,
        exclusive_orders=True
    )

    stats_hybrid_veto = bt_hybrid_veto.run(
        llm_enabled=True,
        mock_llm_mode=True,
        mock_llm_accuracy=0.70,
        llm_veto_enabled=True,
        llm_override_enabled=False  # Only veto, no overrides
    )
    results['Hybrid_VetoOnly'] = stats_hybrid_veto

    print(f"      Return: {stats_hybrid_veto['Return [%]']:.2f}%")
    print(f"      Sharpe: {stats_hybrid_veto['Sharpe Ratio']:.2f}")
    print(f"      Max DD: {stats_hybrid_veto['Max. Drawdown [%]']:.2f}%")
    print(f"      Trades: {stats_hybrid_veto['# Trades']}")

    return results


def print_comparison_table(results: dict, ticker: str, year: int):
    """
    Print formatted comparison table.

    Args:
        results: Dictionary of backtest results
        ticker: Stock ticker
        year: Year tested
    """
    print("\n" + "=" * 80)
    print(f"RESULTS COMPARISON - {ticker} {year}")
    print("=" * 80)

    # Extract metrics
    strategies = ['Adaptive', 'Hybrid_70', 'Hybrid_85', 'Hybrid_VetoOnly']
    metrics = ['Return [%]', 'Sharpe Ratio', 'Max. Drawdown [%]', '# Trades', 'Win Rate [%]']

    # Build table
    print(f"\n{'Strategy':<25} {'Return':<10} {'Sharpe':<10} {'Max DD':<10} {'Trades':<10} {'Win Rate':<10}")
    print("-" * 80)

    baseline_return = results['Adaptive']['Return [%]']
    baseline_sharpe = results['Adaptive']['Sharpe Ratio']
    baseline_dd = results['Adaptive']['Max. Drawdown [%]']

    for strategy in strategies:
        if strategy not in results:
            continue

        stats = results[strategy]

        ret = stats['Return [%]']
        sharpe = stats['Sharpe Ratio']
        dd = stats['Max. Drawdown [%]']
        trades = stats['# Trades']
        win_rate = stats['Win Rate [%]']

        # Format with improvement indicators
        ret_str = f"{ret:>6.2f}%"
        if strategy != 'Adaptive':
            diff = ret - baseline_return
            ret_str += f" ({diff:+.1f}%)" if diff != 0 else ""

        sharpe_str = f"{sharpe:>6.2f}"
        if strategy != 'Adaptive':
            diff = sharpe - baseline_sharpe
            sharpe_str += f" ({diff:+.2f})" if diff != 0 else ""

        dd_str = f"{dd:>6.2f}%"
        if strategy != 'Adaptive':
            # Better = smaller drawdown (more positive difference is good)
            diff = baseline_dd - dd
            dd_str += f" ({diff:+.1f}%)" if diff != 0 else ""

        # Strategy name mapping
        name_map = {
            'Adaptive': 'Adaptive (baseline)',
            'Hybrid_70': 'Hybrid (70% accuracy)',
            'Hybrid_85': 'Hybrid (85% accuracy)',
            'Hybrid_VetoOnly': 'Hybrid (veto only)'
        }

        print(f"{name_map.get(strategy, strategy):<25} {ret_str:<15} {sharpe_str:<15} {dd_str:<15} {trades:<10} {win_rate:>6.1f}%")

    print("-" * 80)

    # Summary insights
    print("\n📊 KEY INSIGHTS:")

    hybrid_70 = results['Hybrid_70']
    ret_diff = hybrid_70['Return [%]'] - baseline_return
    sharpe_diff = hybrid_70['Sharpe Ratio'] - baseline_sharpe
    dd_diff = baseline_dd - hybrid_70['Max. Drawdown [%]']

    if ret_diff > 0:
        print(f"   ✅ Return improved by {ret_diff:.1f}% with LLM filter")
    else:
        print(f"   ⚠️  Return decreased by {abs(ret_diff):.1f}% (trade-off for risk reduction)")

    if sharpe_diff > 0:
        print(f"   ✅ Sharpe ratio improved by {sharpe_diff:.2f} ({sharpe_diff/baseline_sharpe*100:.1f}%)")
    else:
        print(f"   ⚠️  Sharpe ratio decreased by {abs(sharpe_diff):.2f}")

    if dd_diff > 0:
        print(f"   ✅ Drawdown reduced by {dd_diff:.1f}% ({dd_diff/abs(baseline_dd)*100:.1f}% improvement)")
    else:
        print(f"   ⚠️  Drawdown increased by {abs(dd_diff):.1f}%")

    # Compare 70% vs 85% to show accuracy sensitivity
    ret_diff_acc = results['Hybrid_85']['Return [%]'] - hybrid_70['Return [%]']
    print(f"\n   📈 Accuracy Impact: 85% vs 70% accuracy improves return by {ret_diff_acc:.1f}%")
    print(f"      → This shows LLM accuracy MATTERS - invest in prompt engineering!")

    print("\n" + "=" * 80)


def save_results_to_csv(results: dict, ticker: str, year: int):
    """
    Save comparison results to CSV file.

    Args:
        results: Dictionary of backtest results
        ticker: Stock ticker
        year: Year tested
    """
    # Create output directory
    output_dir = "experiments/active/EXP-2025-009-hybrid-llm"
    os.makedirs(f"{output_dir}/results", exist_ok=True)

    # Build comparison dataframe
    comparison_data = []

    for strategy_name, stats in results.items():
        comparison_data.append({
            'Strategy': strategy_name,
            'Return_%': stats['Return [%]'],
            'Sharpe_Ratio': stats['Sharpe Ratio'],
            'Max_Drawdown_%': stats['Max. Drawdown [%]'],
            'Num_Trades': stats['# Trades'],
            'Win_Rate_%': stats['Win Rate [%]'],
            'Avg_Trade_%': stats.get('Avg. Trade [%]', 0),
            'Best_Trade_%': stats.get('Best Trade [%]', 0),
            'Worst_Trade_%': stats.get('Worst Trade [%]', 0)
        })

    df_comparison = pd.DataFrame(comparison_data)

    # Save to CSV
    filename = f"{output_dir}/results/comparison_{ticker}_{year}.csv"
    df_comparison.to_csv(filename, index=False)

    print(f"\n💾 Results saved to: {filename}")


def main():
    """Run complete hybrid strategy test."""

    # Test configurations
    test_configs = [
        {'ticker': 'NVDA', 'year': 2023},  # Bull market
        {'ticker': 'NVDA', 'year': 2022},  # Bear market
    ]

    for config in test_configs:
        try:
            # Run backtest
            results = run_comparison_backtest(
                ticker=config['ticker'],
                year=config['year'],
                cash=10000
            )

            # Print comparison
            print_comparison_table(results, config['ticker'], config['year'])

            # Save results
            save_results_to_csv(results, config['ticker'], config['year'])

            print("\n" + "=" * 80 + "\n")

        except FileNotFoundError as e:
            print(f"\n⚠️  Skipping {config['ticker']} {config['year']}: {e}\n")
            continue
        except Exception as e:
            print(f"\n❌ Error testing {config['ticker']} {config['year']}: {e}\n")
            import traceback
            traceback.print_exc()
            continue

    print("\n✅ All tests completed!")
    print("\nNext steps:")
    print("  1. Review results in experiments/active/EXP-2025-009-hybrid-llm/results/")
    print("  2. If results are promising, proceed to paper trading with real LLM")
    print("  3. Fine-tune LLM prompt to achieve >70% accuracy in shadow tests")
    print("  4. Document findings in experiments/active/EXP-2025-009-hybrid-llm/README.md")


if __name__ == "__main__":
    main()
