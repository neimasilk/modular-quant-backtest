"""
Backtest Engine Module
======================
Orchestrates the backtesting process and generates performance reports.

Responsibilities:
- Run backtests with given data and strategy
- Calculate performance metrics
- Generate reports and plots
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Type
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backtesting import Backtest
from backtesting.lib import plot_heatmaps

# Import strategies
from src.strategies.adaptive_strategy import (
    AdaptiveStrategy,
    BuyAndHoldStrategy,
    SimpleMomentumStrategy,
    print_strategy_rules
)


import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# METRICS CALCULATION
# ============================================================================

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate annualized Sharpe Ratio.

    Args:
        returns: Series of daily returns
        risk_free_rate: Annual risk-free rate (default 2%)

    Returns:
        Sharpe Ratio (annualized)
    """
    try:
        if len(returns) == 0 or returns.std() == 0:
            return 0.0

        # Daily risk-free rate
        daily_rf = risk_free_rate / 252

        # Excess returns
        excess_returns = returns - daily_rf

        # Annualized Sharpe Ratio
        sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(252)

        return float(sharpe)
    except Exception:
        return 0.0


def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate annualized Sortino Ratio (downside deviation only).

    Args:
        returns: Series of daily returns
        risk_free_rate: Annual risk-free rate

    Returns:
        Sortino Ratio (annualized)
    """
    if len(returns) == 0:
        return 0.0

    daily_rf = risk_free_rate / 252
    excess_returns = returns - daily_rf

    # Only consider negative returns for downside deviation
    downside_returns = excess_returns[excess_returns < 0]

    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return float('nan') if excess_returns.mean() > 0 else 0.0

    sortino = excess_returns.mean() / downside_returns.std() * np.sqrt(252)

    return float(sortino)


def calculate_max_drawdown(equity_curve: pd.Series) -> tuple[float, int]:
    """
    Calculate Maximum Drawdown and its duration.

    Args:
        equity_curve: Series of equity values over time

    Returns:
        Tuple of (max_drawdown_pct, duration_days)
    """
    if len(equity_curve) == 0:
        return 0.0, 0

    # Calculate running maximum
    running_max = equity_curve.cummax()

    # Calculate drawdown at each point
    drawdown = (equity_curve - running_max) / running_max

    # Maximum drawdown
    max_dd = drawdown.min()

    # Find duration of max drawdown period
    if max_dd < 0:
        dd_periods = drawdown[drawdown <= max_dd * 1.01]  # Within 1% of max DD
        if len(dd_periods) > 0:
            duration = len(dd_periods)
        else:
            duration = 1
    else:
        duration = 0

    return float(max_dd * 100), duration  # Convert to percentage


def calculate_calmar_ratio(total_return: float, max_dd: float) -> float:
    """
    Calculate Calmar Ratio (Annual Return / Max Drawdown).

    Args:
        total_return: Total return as decimal (e.g., 0.15 for 15%)
        max_dd: Maximum drawdown as positive percentage (e.g., 10 for 10%)

    Returns:
        Calmar Ratio
    """
    if max_dd == 0:
        return float('inf') if total_return > 0 else 0.0
    return abs(total_return / max_dd) * 100


def calculate_win_rate(trades: pd.DataFrame) -> tuple[float, float, float]:
    """
    Calculate win rate and average win/loss ratios using vectorized operations.

    Args:
        trades: DataFrame of trades from backtest

    Returns:
        Tuple of (win_rate_pct, avg_win_pct, avg_loss_pct)
    """
    if len(trades) == 0:
        return 0.0, 0.0, 0.0

    # ReturnPct is usually available in backtesting.py trades DataFrame
    if 'ReturnPct' in trades.columns:
        pnls = trades['ReturnPct']
    else:
        # Vectorized calculation if column missing
        entry_price = trades['EntryPrice']
        exit_price = trades['ExitPrice']
        is_long = trades['Size'] > 0
        
        pnls = np.where(is_long, 
                       (exit_price - entry_price) / entry_price, 
                       (entry_price - exit_price) / entry_price)
        pnls = pd.Series(pnls)

    winning_trades = pnls[pnls > 0]
    losing_trades = pnls[pnls < 0]

    win_rate = len(winning_trades) / len(pnls) * 100 if len(pnls) > 0 else 0
    avg_win = winning_trades.mean() * 100 if len(winning_trades) > 0 else 0
    avg_loss = losing_trades.mean() * 100 if len(losing_trades) > 0 else 0

    return float(win_rate), float(avg_win), float(avg_loss)


# ============================================================================
# REPORT GENERATION
# ============================================================================

def print_header(title: str, width: int = 70):
    """Print formatted header."""
    print("\n" + "=" * width)
    print(f"{title:^{width}}")
    print("=" * width)


def print_metrics_table(metrics: Dict[str, Any]):
    """Print metrics in a formatted table."""
    print("\n+- PERFORMANCE METRICS ----------------------------------------+")

    # Return metrics
    print(f"| Total Return:           {metrics['total_return']:>8.2f}%                      |")
    print(f"| Annual Return:          {metrics['annual_return']:>8.2f}%                      |")
    print(f"| Volatility (Ann.):      {metrics['volatility']:>8.2f}%                      |")

    print(f"|                                                              |")

    # Risk-adjusted metrics
    print(f"| Sharpe Ratio:           {metrics['sharpe_ratio']:>8.2f}                       |")
    print(f"| Sortino Ratio:          {metrics.get('sortino_ratio', 0):>8.2f}                       |")
    print(f"| Calmar Ratio:           {metrics.get('calmar_ratio', 0):>8.2f}                       |")

    print(f"|                                                              |")

    # Drawdown metrics
    print(f"| Max Drawdown:           {metrics['max_drawdown']:>8.2f}%                      |")
    print(f"| Max DD Duration:        {metrics['max_dd_duration']:>8} days                  |")

    print(f"|                                                              |")

    # Trade metrics
    print(f"| Total Trades:           {metrics['total_trades']:>8}                        |")
    print(f"| Win Rate:               {metrics['win_rate']:>8.2f}%                      |")

    if metrics['avg_win'] != 0:
        print(f"| Avg Win:                {metrics['avg_win']:>8.2f}%                      |")
    if metrics['avg_loss'] != 0:
        print(f"| Avg Loss:               {metrics['avg_loss']:>8.2f}%                      |")

    print(f"|                                                              |")
    print(f"| Profit Factor:          {metrics.get('profit_factor', 0):>8.2f}                       |")

    print("+--------------------------------------------------------------+")


def print_regime_analysis(stats: Dict[str, Any]):
    """Print analysis by regime."""
    print("\n+- REGIME ANALYSIS ---------------------------------------------+")

    if 'regime_trades' in stats:
        trades = stats['regime_trades']
        print(f"| Trades in Bullish Mode:    {trades.get('BULLISH', 0):>3}                            |")
        print(f"| Trades in Bearish Mode:    {trades.get('BEARISH', 0):>3}                            |")
        print(f"| Trades in Sideways Mode:   {trades.get('SIDEWAYS', 0):>3}                            |")

    if 'regime_distribution' in stats:
        dist = stats['regime_distribution']
        print(f"|                                                              |")
        print(f"| Bullish Days:              {dist.get('Bullish_Days', 0):>3}                            |")
        print(f"| Bearish Days:              {dist.get('Bearish_Days', 0):>3}                            |")
        print(f"| Sideways Days:             {dist.get('Sideways_Days', 0):>3}                            |")

    print("+--------------------------------------------------------------+")


# ============================================================================
# MAIN BACKTEST ENGINE
# ============================================================================

class BacktestEngine:
    """
    Main engine for running backtests and generating reports.

    Usage:
        engine = BacktestEngine(data, AdaptiveStrategy, initial_cash=100_000)
        engine.run()
        engine.print_report()
    """

    def __init__(
        self,
        data: pd.DataFrame,
        strategy_class: Type,
        initial_cash: float = 100_000,
        commission: float = 0.001,  # 0.1% per trade
        exclusive_orders: bool = True
    ):
        """
        Initialize backtest engine.

        Args:
            data: OHLCV DataFrame with AI signals
            strategy_class: Strategy class to backtest
            initial_cash: Starting capital
            commission: Commission rate per trade
            exclusive_orders: Only one order at a time
        """
        self.data = data
        self.strategy_class = strategy_class
        self.initial_cash = initial_cash
        self.commission = commission
        self.exclusive_orders = exclusive_orders

        self.backtest = None
        self.results = None
        self.metrics = {}
        self.stats = {}

    def run(self, optimize: bool = False):
        """
        Run the backtest.
        
        Args:
            optimize: Whether to run parameter optimization
        """
        logger.info(f"Running backtest for {self.strategy_class.__name__}...")
        
        try:
            # Initialize Backtest
            bt = Backtest(
                self.data, 
                self.strategy_class,
                cash=self.initial_cash,
                commission=self.commission,
                exclusive_orders=True
            )
            self.backtest = bt  # Store backtest instance
            
            if optimize and self.strategy_class == AdaptiveStrategy:
                logger.info("Running optimization...")
                # Optimization logic
                stats, heatmap = bt.optimize(
                    aggr_entry_thresh=[0.1, 0.2, 0.3],
                    aggr_exit_thresh=[-0.2, -0.3, -0.4],
                    maximize='Sharpe Ratio',
                    return_heatmap=True
                )
                self.stats = stats
                logger.info(f"Optimization complete. Best Sharpe: {stats['Sharpe Ratio']:.2f}")
            else:
                self.stats = bt.run()
                
            logger.info("Backtest complete.")
            
        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            raise

    def print_report(self):
        """Print performance report."""
        if self.stats is None:
            logger.warning("No results to print. Run backtest first.")
            return
            
        # Extract metrics
        equity_curve = self.stats['_equity_curve']['Equity']
        trades = self.stats['_trades']
        
        # Calculate custom metrics (vectorized)
        sharpe = calculate_sharpe_ratio(equity_curve)
        sortino = calculate_sortino_ratio(equity_curve)
        max_dd, _ = calculate_max_drawdown(equity_curve)
        win_rate, _, _ = calculate_win_rate(trades)
        
        logger.info("=" * 50)
        logger.info(f"BACKTEST REPORT: {self.strategy_class.__name__}")
        logger.info("=" * 50)
        logger.info(f"Return:         {self.stats['Return [%]']:.2f}%")
        logger.info(f"Buy & Hold:     {self.stats['Buy & Hold Return [%]']:.2f}%")
        logger.info(f"Sharpe Ratio:   {sharpe:.2f}")
        logger.info(f"Sortino Ratio:  {sortino:.2f}")
        logger.info(f"Max Drawdown:   {max_dd:.2f}%")
        logger.info(f"Win Rate:       {win_rate:.2f}%")
        logger.info(f"Total Trades:   {len(trades)}")
        logger.info("-" * 50)

    def get_metrics(self) -> Dict[str, Any]:
        """Return metrics as dictionary."""
        return self.metrics.copy()

    def plot(self, filename: Optional[str] = None, show: bool = True):
        """
        Plot backtest results.

        Args:
            filename: Path to save plot (optional)
            show: Whether to display plot (open browser)
        """
        if self.backtest is None:
            logger.warning("No backtest results to plot. Run run() first.")
            return

        # Map 'show' to 'open_browser' which is used by backtesting.py
        if filename:
            self.backtest.plot(filename=filename, open_browser=show)
        else:
            self.backtest.plot(open_browser=show)

    def save_plot(self, output_dir: str = "output"):
        """Save plot to file."""
        from pathlib import Path

        Path(output_dir).mkdir(exist_ok=True, parents=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/backtest_{timestamp}.html"

        self.backtest.plot(filename=filename, open_browser=False)
        logger.info(f"Plot saved to: {filename}")


# ============================================================================
# COMPARISON ENGINE
# ============================================================================

def compare_strategies(
    data: pd.DataFrame,
    strategies: list[tuple[str, Type]],
    initial_cash: float = 100_000
) -> pd.DataFrame:
    """
    Compare multiple strategies side by side.

    Args:
        data: OHLCV DataFrame
        strategies: List of (name, strategy_class) tuples
        initial_cash: Starting capital

    Returns:
        DataFrame with comparison results
    """
    results_list = []

    for name, strategy_class in strategies:
        engine = BacktestEngine(data, strategy_class, initial_cash=initial_cash)
        engine.run()
        metrics = engine.get_metrics()
        metrics['strategy'] = name
        results_list.append(metrics)

    df = pd.DataFrame(results_list)
    df = df.set_index('strategy')

    return df


def print_comparison_table(comparison_df: pd.DataFrame):
    """Print comparison table for multiple strategies."""
    print("\n" + "=" * 70)
    print("STRATEGY COMPARISON")
    print("=" * 70)

    # Key metrics to display
    cols = ['total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate', 'total_trades']

    display_df = comparison_df[cols].copy()
    display_df.columns = ['Return %', 'Sharpe', 'Max DD %', 'Win Rate %', '# Trades']

    print(display_df.to_string())
    print("=" * 70)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Quick test with sample data
    from src.data.data_generator import prepare_data

    print("Testing Backtest Engine...")

    # Generate sample data
    data = prepare_data(n_days=100)

    # Run backtest
    engine = BacktestEngine(data, AdaptiveStrategy, initial_cash=100_000)
    engine.run()
    engine.print_report()
