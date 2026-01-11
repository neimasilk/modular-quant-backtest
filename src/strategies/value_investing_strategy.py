"""
Value Investing Strategy for EXP-2025-007

A fundamental-based value investing strategy:
1. Screen stocks by value metrics (P/E, P/B, ROE, etc.)
2. Rank by combined value score
3. Buy top N stocks
4. Hold for minimum period
5. Rebalance monthly

Note: This is a long-term strategy, not suitable for short-term trading.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from backtesting import Strategy

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.fundamental_fetcher import FundamentalDataFetcher, ValueScreener


class ValueInvestingStrategy(Strategy):
    """
    Value investing strategy using fundamental metrics.

    This strategy:
    1. Screens stocks by value criteria
    2. Ranks by combined value score
    3. Buys top N stocks
    4. Holds for minimum period
    5. Rebalances monthly
    """

    # Screening criteria
    max_pe = 25.0  # Increased from 15 for more candidates
    max_pb = 3.0
    max_debt_to_equity = 1.0  # Relaxed
    min_roe = 0.10  # 10% minimum ROE
    require_positive_fcf = True

    # Portfolio parameters
    max_positions = 10  # Number of stocks to hold
    position_size = 0.95  # 95% invested (keep 5% cash)
    min_hold_days = 30  # Minimum holding period
    rebalance_interval = 'monthly'  # Rebalance frequency

    # Scoring weights
    pe_weight = 0.3
    pb_weight = 0.3
    roe_weight = 0.2
    fcf_weight = 0.2

    # Internal state
    universe: List[str] = None
    fetcher: FundamentalDataFetcher = None
    screener: ValueScreener = None
    selected_stocks: List[str] = None
    last_rebalance_date: Optional[datetime] = None
    entry_dates: Dict[str, datetime] = None

    def init(self):
        """Initialize the strategy."""
        # Default universe (DOW Jones components)
        if self.universe is None:
            from data.fundamental_fetcher import DOW_JONES
            self.universe = DOW_JONES

        self.fetcher = FundamentalDataFetcher()
        self.screener = ValueScreener(self.fetcher)
        self.entry_dates = {}
        self.selected_stocks = []

        # Perform initial screening
        print(f"\n[{self.__class__.__name__}] Screening {len(self.universe)} stocks...")
        self._screen_and_rank()

    def _screen_and_rank(self):
        """Screen stocks and select top N by value score."""
        # Screen by value criteria
        screened = self.screener.screen(
            self.universe,
            max_pe=self.max_pe,
            max_pb=self.max_pb,
            max_debt_to_equity=self.max_debt_to_equity,
            min_roe=self.min_roe,
            require_positive_fcf=self.require_positive_fcf
        )

        print(f"  Screened to {len(screened)} stocks by value criteria")

        if len(screened) == 0:
            print("  WARNING: No stocks passed screen! Using fallback...")
            # Fallback: get top N by P/E regardless of other criteria
            all_data = self.fetcher.get_batch_fundamental_data(self.universe)
            screened = all_data.dropna(subset=['pe_ratio'])
            screened = screened.sort_values('pe_ratio')

        # Score and rank
        scored = self.screener.score_stocks(screened.index.tolist())
        top_n = scored.head(self.max_positions)

        self.selected_stocks = top_n.index.tolist()

        print(f"  Selected top {len(self.selected_stocks)} stocks:")
        for i, ticker in enumerate(self.selected_stocks, 1):
            pe = scored.loc[ticker, 'pe_ratio']
            pb = scored.loc[ticker, 'pb_ratio']
            score = scored.loc[ticker, 'combined_score']
            print(f"    {i}. {ticker}: P/E={pe:.2f}, P/B={pb:.2f}, Score={score:.3f}")

    def _should_rebalance(self) -> bool:
        """Check if it's time to rebalance."""
        if self.last_rebalance_date is None:
            return True

        current_date = pd.Timestamp(self.data.index[-1]).date()
        days_since_rebalance = (current_date - self.last_rebalance_date).days

        if self.rebalance_interval == 'monthly':
            return days_since_rebalance >= 28  # ~1 month
        elif self.rebalance_interval == 'weekly':
            return days_since_rebalance >= 7
        else:
            return days_since_rebalance >= 30

    def _can_exit_position(self, ticker: str) -> bool:
        """Check if position can be exited (minimum hold period)."""
        if ticker not in self.entry_dates:
            return True

        entry_date = self.entry_dates[ticker]
        current_date = pd.Timestamp(self.data.index[-1]).date()
        days_held = (current_date - entry_date).days

        return days_held >= self.min_hold_days

    def next(self):
        """
        Main strategy logic.

        Note: This is a simplified implementation for demonstration.
        A full implementation would need:
        1. Multi-asset backtesting support
        2. Portfolio-level position management
        3. Proper handling of stock universe changes
        """
        # For this demo, we'll use a proxy approach:
        # Trade the first stock in our universe as a representative
        # Real implementation would require multi-asset backtesting framework

        pass  # Placeholder - see ValueBacktester for full implementation


class SimpleValueStrategy(Strategy):
    """
    Simplified value strategy for single-stock backtesting.

    This is a demonstration version that works with the existing
    backtesting framework. It shows how value metrics could be
    incorporated into entry/exit decisions.

    For true value investing with multiple positions, use
    ValueBacktester instead.
    """

    # Use fundamental metrics as filters
    max_pe = 25.0
    max_pb = 3.0
    min_roe = 0.10

    # Technical entry/exit (for demo)
    entry_period = 20  # Lookback period
    exit_rsi = 70  # Exit when RSI overbought

    def init(self):
        """Initialize indicators."""
        # Simple technical indicators for demo
        self.close = self.data.Close

        # RSI for exit signals
        delta = pd.Series(self.close).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.rsi = 100 - (100 / (1 + rs))

    def next(self):
        """
        Simplified logic: buy when stock is "cheap" technically,
        sell when overbought.

        This is NOT true value investing - it's a demo of how
        the framework could be extended.
        """
        if len(self.close) < self.entry_period:
            return

        # Entry: Price below 20-day moving average (simplified "value" signal)
        sma = pd.Series(self.close).rolling(self.entry_period).mean().iloc[-1]
        current_price = self.close[-1]

        # Exit: RSI overbought
        current_rsi = self.rsi.iloc[-1]

        if not self.position:
            if current_price < sma:
                # Buy with 20% stop loss
                self.buy(size=0.95, sl=current_price * 0.8)
        else:
            if current_rsi > self.exit_rsi:
                self.position.close()


class ValueBacktester:
    """
    Custom backtester for value investing strategies.

    This is a simplified backtesting engine designed specifically
    for value investing with multi-stock portfolios.
    """

    def __init__(
        self,
        universe: List[str],
        start_date: str,
        end_date: str,
        initial_cash: float = 100_000,
        commission: float = 0.001
    ):
        """Initialize the backtester."""
        self.universe = universe
        self.start_date = start_date
        self.end_date = end_date
        self.initial_cash = initial_cash
        self.commission = commission

        self.fetcher = FundamentalDataFetcher()
        self.screener = ValueScreener(self.fetcher)

    def run(self) -> Dict:
        """
        Run value investing backtest.

        Note: This is a simplified version that:
        1. Fetches price data for all stocks
        2. Selects top N by value score at start
        3. Simulates buy-and-hold for the period
        4. Compares to equal-weight benchmark

        A full implementation would:
        - Handle monthly rebalancing
        - Track entry/exit dates
        - Apply minimum holding periods
        - Handle corporate actions
        """
        import yfinance as yf

        print("=" * 70)
        print("Value Investing Backtest")
        print("=" * 70)
        print(f"\nUniverse: {len(self.universe)} stocks")
        print(f"Period: {self.start_date} to {self.end_date}")
        print(f"Initial Cash: ${self.initial_cash:,.0f}")

        # Get fundamental data and select top stocks
        print("\nStep 1: Screening and ranking stocks...")
        top_stocks = self.screener.get_top_n(self.universe, n=10)

        print(f"\nTop 10 Value Stocks:")
        print(top_stocks[['pe_ratio', 'pb_ratio', 'roe', 'fcf_yield', 'combined_score']].to_string())

        selected = top_stocks.head(5).index.tolist()  # Top 5 for demo
        print(f"\nSelected: {', '.join(selected)}")

        # Fetch price data
        print("\nStep 2: Fetching price data...")
        price_data = {}
        for ticker in selected:
            data = yf.download(
                ticker,
                start=self.start_date,
                end=self.end_date,
                progress=False
            )
            price_data[ticker] = data

        # Calculate returns
        print("\nStep 3: Calculating performance...")
        returns = {}

        for ticker in selected:
            if len(price_data[ticker]) > 0:
                total_return = (
                    price_data[ticker]['Close'].iloc[-1] /
                    price_data[ticker]['Close'].iloc[0] - 1
                )
                returns[ticker] = total_return

        # Equal-weight portfolio return
        portfolio_return = np.mean(list(returns.values()))

        # Get benchmark return (equal-weight all universe)
        benchmark_data = {}
        for ticker in self.universe:
            try:
                data = yf.download(
                    ticker,
                    start=self.start_date,
                    end=self.end_date,
                    progress=False
                )
                if len(data) > 0:
                    ret = data['Close'].iloc[-1] / data['Close'].iloc[0] - 1
                    benchmark_data[ticker] = ret
            except:
                pass

        benchmark_return = np.mean(list(benchmark_data.values()))

        # Print results
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)

        print(f"\nIndividual Stock Returns:")
        for ticker, ret in returns.items():
            ret_val = float(ret) if hasattr(ret, 'item') else ret
            if pd.isna(ret_val):
                ret_val = 0.0
            print(f"  {ticker}: {ret_val:>7.2%}")

        print(f"\nPortfolio Return: {portfolio_return:>7.2%}")
        print(f"Benchmark Return: {benchmark_return:>7.2%}")
        print(f"Alpha: {portfolio_return - benchmark_return:>+7.2%}")

        # Calculate final value
        final_value = self.initial_cash * (1 + portfolio_return)
        benchmark_value = self.initial_cash * (1 + benchmark_return)

        print(f"\nFinal Portfolio Value: ${final_value:,.0f}")
        print(f"Final Benchmark Value: ${benchmark_value:,.0f}")

        return {
            'portfolio_return': portfolio_return,
            'benchmark_return': benchmark_return,
            'alpha': portfolio_return - benchmark_return,
            'final_value': final_value,
            'stocks': returns,
            'selected': selected
        }


def main():
    """Test the ValueInvestingStrategy."""
    print("=" * 70)
    print("Testing Value Investing Strategy")
    print("=" * 70)

    from data.fundamental_fetcher import DOW_JONES

    # Run backtest
    backtester = ValueBacktester(
        universe=DOW_JONES[:20],  # First 20 DOW stocks for demo
        start_date='2023-01-01',
        end_date='2024-01-01',
        initial_cash=100_000
    )

    results = backtester.run()

    print("\n[OK] Backtest complete!")


if __name__ == "__main__":
    main()
