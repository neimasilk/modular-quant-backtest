"""
Main Entry Point - Modular Quantitative Backtesting Framework
=============================================================

This is the main orchestration script that demonstrates:
1. Data Generation (with AI Signals)
2. Strategy Execution (Adaptive based on Regime)
3. Backtesting & Reporting

Usage:
    python main.py                    # Run default backtest
    python main.py --compare          # Compare strategies
    python main.py --days 500         # Custom data length
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import modules
from src.data.data_generator import prepare_data, get_regime_distribution, validate_dataframe
from src.strategies.adaptive_strategy import (
    AdaptiveStrategy,
    BuyAndHoldStrategy,
    SimpleMomentumStrategy,
    print_strategy_rules
)
from src.engines.backtest_engine import (
    BacktestEngine,
    compare_strategies,
    print_comparison_table
)


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Central configuration for the backtesting framework."""

    # Data parameters
    DEFAULT_DAYS = 252          # 1 year of trading days
    START_PRICE = 100.0
    VOLATILITY = 0.02

    # Backtest parameters
    INITIAL_CASH = 100_000
    COMMISSION = 0.001          # 0.1% per trade

    # Output settings
    OUTPUT_DIR = "output"
    SAVE_PLOT = True


# ============================================================================
# MAIN EXECUTION FLOW
# ============================================================================

def run_single_backtest(
    n_days: int = Config.DEFAULT_DAYS,
    data_file: str = None,
    plot: bool = True,
    verbose: bool = True
) -> dict:
    """
    Run a single backtest with the Adaptive Strategy.

    Args:
        n_days: Number of trading days to generate
        data_file: Path to CSV data file (optional)
        plot: Whether to generate plots
        verbose: Whether to print detailed output

    Returns:
        Dictionary of metrics
    """
    if verbose:
        print("\n" + "=" * 70)
        print("MODULAR QUANTITATIVE BACKTESTING FRAMEWORK".center(70))
        print("=" * 70)
        print("\nInitializing...")

    # ========================================================================
    # STEP 1: DATA GENERATION / LOADING
    # ========================================================================
    if data_file:
        if verbose:
            print(f"\n[Step 1] Loading Real Data from {data_file}...")
        
        import pandas as pd
        data = pd.read_csv(data_file)
        data['Date'] = pd.to_datetime(data['Date'])
        data.set_index('Date', inplace=True)
        
        # Ensure required columns exist
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'AI_Regime_Score', 'AI_Stock_Sentiment']
        missing = [c for c in required_cols if c not in data.columns]
        if missing:
            print(f"[WARNING] Missing columns in data file: {missing}")
            # If AI columns missing, maybe fill with defaults? 
            # But for now let's assume data_miner output which has them.
    else:
        if verbose:
            print("\n[Step 1] Generating Mock Data with AI Signals...")

        # CRITICAL FIX: Removed add_signal_impact=True to prevent self-fulfilling prophecy
        # We want to test if the signals work on UNMODIFIED price data
        data = prepare_data(
            n_days=n_days,
            start_price=Config.START_PRICE,
            volatility=Config.VOLATILITY,
            add_signal_impact=False
        )

    # Validate data
    validate_dataframe(data)

    if verbose:
        print(f"  [OK] Generated {len(data)} days of OHLCV data")
        print(f"  [OK] Date Range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")

        # Print regime distribution
        regime_stats = get_regime_distribution(data)
        print(f"\n  Regime Distribution:")
        print(f"    Bullish Days:  {regime_stats['Bullish_Days']}")
        print(f"    Bearish Days:  {regime_stats['Bearish_Days']}")
        print(f"    Sideways Days: {regime_stats['Sideways_Days']}")
        print(f"    Avg Regime:    {regime_stats['Avg_Regime']:.4f}")
        print(f"    Avg Sentiment: {regime_stats['Avg_Sentiment']:.4f}")

    # ========================================================================
    # STEP 2: DISPLAY STRATEGY RULES
    # ========================================================================
    if verbose:
        print("\n[Step 2] Strategy Configuration...")
        print_strategy_rules()

    # ========================================================================
    # STEP 3: RUN BACKTEST
    # ========================================================================
    if verbose:
        print("\n[Step 3] Running Backtest...")

    engine = BacktestEngine(
        data=data,
        strategy_class=AdaptiveStrategy,
        initial_cash=Config.INITIAL_CASH,
        commission=Config.COMMISSION
    )

    engine.run()

    # ========================================================================
    # STEP 4: PRINT REPORT
    # ========================================================================
    if verbose:
        print("\n[Step 4] Backtest Complete!")
        engine.print_report()

    # ========================================================================
    # STEP 5: SAVE PLOT
    # ========================================================================
    if plot:
        if verbose:
            print("\n[Step 5] Generating Visualizations...")
        engine.save_plot(output_dir=Config.OUTPUT_DIR)

    return engine.get_metrics()


# ============================================================================
# COMPARISON MODE
# ============================================================================

def run_strategy_comparison(
    n_days: int = Config.DEFAULT_DAYS,
    verbose: bool = True
):
    """
    Compare multiple strategies side by side.

    Strategies to compare:
    1. Adaptive Strategy (AI-driven)
    2. Buy and Hold (Benchmark)
    3. Simple Momentum (No AI)
    """
    if verbose:
        print("\n" + "=" * 70)
        print("STRATEGY COMPARISON MODE".center(70))
        print("=" * 70)

    # Generate data
    if verbose:
        print("\nGenerating data...")

    data = prepare_data(
        n_days=n_days,
        start_price=Config.START_PRICE,
        volatility=Config.VOLATILITY
    )

    # Define strategies
    strategies = [
        ("Adaptive (AI)", AdaptiveStrategy),
        ("Buy & Hold", BuyAndHoldStrategy),
        ("Momentum", SimpleMomentumStrategy),
    ]

    # Run comparison
    if verbose:
        print("Running backtests for all strategies...\n")

    comparison_df = compare_strategies(
        data=data,
        strategies=strategies,
        initial_cash=Config.INITIAL_CASH
    )

    # Print results
    print_comparison_table(comparison_df)

    # Find winner
    best_sharpe = comparison_df['sharpe_ratio'].idxmax()
    best_return = comparison_df['total_return'].idxmax()

    print(f"\nBest Sharpe Ratio: {best_sharpe}")
    print(f"Best Total Return: {best_return}")


# ============================================================================
# PARAMETER OPTIMIZATION (Optional)
# ============================================================================

def run_optimization(n_days: int = Config.DEFAULT_DAYS):
    """
    Run parameter optimization for the Adaptive Strategy.

    This tests different threshold values to find optimal settings.
    """
    print("\n" + "=" * 70)
    print("PARAMETER OPTIMIZATION".center(70))
    print("=" * 70)

    # Generate data
    data = prepare_data(n_days=n_days, start_price=Config.START_PRICE)

    # Define parameter grid
    # Note: This can be computationally intensive
    print("\nDefining parameter grid...")

    # For demonstration, we'll do a limited grid search
    from backtesting import Backtest

    bt = Backtest(
        data,
        AdaptiveStrategy,
        cash=Config.INITIAL_CASH,
        commission=Config.COMMISSION
    )

    # Optimize aggressive mode thresholds
    print("\nRunning optimization (this may take a while)...")

    stats, heatmap = bt.optimize(
        aggr_entry_thresh=[0.1, 0.2, 0.3],
        aggr_exit_thresh=[-0.2, -0.3, -0.4],
        maximize='Sharpe Ratio',
        return_heatmap=True
    )

    print("\nOptimization Complete!")
    print(f"\nBest Sharpe Ratio: {stats['Sharpe Ratio']:.4f}")
    print(f"Best Return: {stats['Return [%]']:.2f}%")

    print("\nOptimal Parameters:")
    print(f"  aggr_entry_thresh: {stats['_strategy'].aggr_entry_thresh}")
    print(f"  aggr_exit_thresh: {stats['_strategy'].aggr_exit_thresh}")

    # Save heatmap
    heatmap.to_csv(f"{Config.OUTPUT_DIR}/optimization_heatmap.csv")


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Modular Quantitative Backtesting Framework"
    )

    parser.add_argument(
        '--days', '-d',
        type=int,
        default=Config.DEFAULT_DAYS,
        help=f'Number of trading days (default: {Config.DEFAULT_DAYS})'
    )

    parser.add_argument(
        '--data-file', '-f',
        type=str,
        help='Path to CSV data file (skips mock data generation)'
    )

    parser.add_argument(
        '--compare', '-c',
        action='store_true',
        help='Run strategy comparison mode'
    )

    parser.add_argument(
        '--optimize', '-o',
        action='store_true',
        help='Run parameter optimization'
    )

    parser.add_argument(
        '--no-plot',
        action='store_true',
        help='Skip generating plots'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Minimal output'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output and debug info'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    try:
        args = parse_args()

        # Create output directory
        Path(Config.OUTPUT_DIR).mkdir(exist_ok=True)

        # Route to appropriate mode
        if args.compare:
            run_strategy_comparison(
                n_days=args.days,
                verbose=not args.quiet
            )
        elif args.optimize:
            run_optimization(n_days=args.days)
        else:
            # Default: Run single backtest
            metrics = run_single_backtest(
                n_days=args.days,
                data_file=args.data_file,
                plot=not args.no_plot,
                verbose=not args.quiet
            )

            if not args.quiet:
                print("\n" + "=" * 70)
                print("[OK] Backtest Complete!")
                print("=" * 70)
                
    except KeyboardInterrupt:
        print("\n[INFO] Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
