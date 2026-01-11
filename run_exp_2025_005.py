"""
EXP-2025-005: Real News Sentiment Analysis

This script compares heuristic sentiment vs LLM-analyzed news sentiment.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data.news_fetcher import NewsFetcher
from src.engines.backtest_engine import BacktestEngine
from src.strategies.adaptive_strategy import AdaptiveStrategy, BuyAndHoldStrategy
from backtesting import Backtest

# Import strategy components for creating news sentiment variant
from backtesting import Strategy
from backtesting.lib import crossover
from src.strategies.adaptive_strategy import (
    calculate_volatility,
    calculate_support_resistance,
    detect_regime,
    RegimeThreshold,
    AggressiveMode,
    DefensiveMode,
    MeanReversionMode
)


class NewsSentimentStrategy(Strategy):
    """
    Adaptive Strategy using LLM-analyzed News Sentiment instead of heuristic.

    Uses News_Sentiment column (from LLM) instead of AI_Stock_Sentiment (heuristic).
    """

    # Strategy parameters
    regime_bullish_threshold = RegimeThreshold.BULLISH_MIN
    regime_bearish_threshold = RegimeThreshold.BEARISH_MAX

    # Aggressive mode parameters
    aggr_entry_thresh = 0.0  # More permissive for news sentiment
    aggr_exit_thresh = -0.5
    aggr_size = AggressiveMode.POSITION_SIZE

    # Defensive mode parameters
    def_short_thresh = -0.3
    def_cover_thresh = 0.0
    def_size = DefensiveMode.POSITION_SIZE

    # Mean reversion mode parameters
    mr_lookback = MeanReversionMode.LOOKBACK_PERIOD
    mr_size = MeanReversionMode.POSITION_SIZE

    # Risk Management
    stop_loss_pct = 0.20

    # Minimum confidence to act on news sentiment
    min_confidence = 0.5  # Only trade if LLM confidence >= 0.5

    def init(self):
        """Initialize strategy indicators."""
        self.volatility = self.I(calculate_volatility, self.data.Close)
        self.support, self.resistance = self.I(
            calculate_support_resistance,
            self.data.Close,
            self.mr_lookback
        )
        self.current_regime = 'SIDEWAYS'
        self.regime_trades = {'BULLISH': 0, 'BEARISH': 0, 'SIDEWAYS': 0}

    def get_regime(self) -> str:
        """Get current regime based on AI_Regime_Score."""
        latest_regime = self.data.AI_Regime_Score[-1]
        return detect_regime(latest_regime)

    def get_news_sentiment(self) -> tuple:
        """
        Get news sentiment and confidence.

        Returns:
            Tuple of (sentiment, confidence) or (0.0, 0.0) if below threshold
        """
        if hasattr(self.data, 'News_Sentiment'):
            sentiment = self.data.News_Sentiment[-1]
            confidence = self.data.News_Confidence[-1]

            # Only use sentiment if confidence is high enough
            if confidence >= self.min_confidence:
                return sentiment, confidence
        return 0.0, 0.0

    def execute_aggressive_mode(self):
        """Execute Aggressive (Bullish) strategy."""
        sentiment, confidence = self.get_news_sentiment()

        # ENTRY LOGIC
        if sentiment > self.aggr_entry_thresh and confidence >= self.min_confidence:
            if not self.position:
                size = self.aggr_size
                current_price = self.data.Close[-1]
                sl_price = current_price * (1 - self.stop_loss_pct)
                self.buy(size=min(size, 0.95), sl=sl_price)
                self.regime_trades['BULLISH'] += 1

        # EXIT LOGIC
        elif sentiment < self.aggr_exit_thresh:
            if self.position and self.position.is_long:
                self.position.close()

    def execute_defensive_mode(self):
        """Execute Defensive (Bearish) strategy."""
        sentiment, confidence = self.get_news_sentiment()

        # SHORT ENTRY LOGIC
        if sentiment < self.def_short_thresh and confidence >= self.min_confidence:
            if not self.position:
                size = self.def_size
                current_price = self.data.Close[-1]
                sl_price = current_price * (1 + self.stop_loss_pct)
                self.sell(size=size, sl=sl_price)
                self.regime_trades['BEARISH'] += 1

        # COVER LOGIC
        elif sentiment > self.def_cover_thresh:
            if self.position and self.position.is_short:
                self.position.close()

    def execute_mean_reversion_mode(self):
        """Execute Mean Reversion (Sideways) strategy."""
        current_support = self.support[-1]
        current_resistance = self.resistance[-1]
        mid_point = (current_support + current_resistance) / 2
        current_price = self.data.Close[-1]

        # BUY ENTRY: Price near support
        if current_price <= current_support * (1 + 0.03):
            if not self.position or self.position.is_short:
                if self.position:
                    self.position.close()

                sl_price = current_price * (1 - self.stop_loss_pct)
                if mid_point <= current_price * 1.005:
                    target_price = current_resistance
                else:
                    target_price = mid_point

                if target_price <= current_price * 1.005:
                    target_price = current_price * 1.05

                self.buy(size=self.mr_size, sl=sl_price, tp=target_price)
                self.regime_trades['SIDEWAYS'] += 1

        # SELL ENTRY: Price near resistance
        elif current_price >= current_resistance * (1 - 0.03):
            if not self.position or self.position.is_long:
                if self.position:
                    self.position.close()

                sl_price = current_price * (1 + self.stop_loss_pct)

                if mid_point >= current_price * 0.995:
                    target_price = current_support
                else:
                    target_price = mid_point

                if target_price >= current_price * 0.995:
                    target_price = current_price * 0.95

                self.sell(size=self.mr_size, sl=sl_price, tp=target_price)
                self.regime_trades['SIDEWAYS'] += 1

    def next(self):
        """Main strategy logic."""
        regime = self.get_regime()
        self.current_regime = regime

        if regime == 'BULLISH':
            self.execute_aggressive_mode()
        elif regime == 'BEARISH':
            self.execute_defensive_mode()
        else:
            self.execute_mean_reversion_mode()


def prepare_data_with_news_sentiment(
    ticker: str,
    start_date: str,
    end_date: str,
    use_cached_news: bool = True
) -> pd.DataFrame:
    """
    Prepare price data with LLM news sentiment.

    Args:
        ticker: Stock symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        use_cached_news: Whether to use cached sentiment

    Returns:
        DataFrame with OHLCV + AI_Regime_Score + News_Sentiment columns
    """
    import yfinance as yf

    print(f"\nFetching price data for {ticker}...")
    price_data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if price_data.empty:
        raise ValueError(f"No data found for {ticker}")

    # Handle MultiIndex from yfinance (single ticker case)
    if isinstance(price_data.columns, pd.MultiIndex):
        price_data.columns = price_data.columns.get_level_values(0)

    # Reset index to get Date as column
    price_data = price_data.reset_index()
    price_data['Date'] = pd.to_datetime(price_data['Date'])

    # Calculate VIX (proxy using realized volatility)
    price_data['VIX'] = price_data['Close'].pct_change().rolling(20).std() * np.sqrt(252)

    # Calculate AI_Regime_Score based on VIX (same as data_miner.py)
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

    # Create heuristic sentiment for comparison
    price_data['AI_Stock_Sentiment'] = (
        price_data['Close'].pct_change(5).fillna(0) * 2
    ).clip(-1, 1).shift(1)  # Lag to avoid look-ahead

    # Fetch LLM news sentiment
    print(f"\nFetching LLM news sentiment for {ticker}...")
    fetcher = NewsFetcher()

    # Prepare price data for augmentation
    price_data_indexed = price_data.set_index('Date')

    # Augment with news sentiment (weekly sampling, then forward fill)
    augmented_data = fetcher.augment_price_data(
        price_df=price_data_indexed,
        ticker=ticker,
        freq='W-MON',  # Weekly to reduce API calls
        use_cache=use_cached_news
    )

    # Reset index and return
    result = augmented_data.reset_index()
    result = result.rename(columns={'index': 'Date'})

    return result


def run_comparison(
    ticker: str = "NVDA",
    start_date: str = "2023-01-01",
    end_date: str = "2024-01-01",
    initial_cash: float = 100_000,
    commission: float = 0.001
):
    """
    Run backtest comparison between heuristic and news sentiment strategies.
    """
    print("=" * 70)
    print("EXP-2025-005: Real News Sentiment Analysis")
    print("=" * 70)
    print(f"\nTicker: {ticker}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Initial Cash: ${initial_cash:,.0f}")
    print(f"Commission: {commission * 100}%")

    # Prepare data with news sentiment
    df = prepare_data_with_news_sentiment(ticker, start_date, end_date)

    # Display sentiment data
    print("\n" + "-" * 50)
    print("Sample News Sentiment Data:")
    print("-" * 50)

    # Select columns, handling potential MultiIndex
    display_cols = ['Date', 'Close', 'AI_Stock_Sentiment', 'News_Sentiment', 'News_Confidence']
    available_cols = [c for c in display_cols if c in df.columns]
    print(df[available_cols].tail(10).to_string(index=False))

    # Save data for review
    os.makedirs("experiments/active/EXP-2025-005-real-news-sentiment/data", exist_ok=True)
    df.to_csv("experiments/active/EXP-2025-005-real-news-sentiment/data/news_sentiment_data.csv", index=False)
    print(f"\nData saved to: experiments/active/EXP-2025-005-real-news-sentiment/data/news_sentiment_data.csv")

    # Prepare data for backtesting (set Date as index)
    df_backtest = df.set_index('Date')

    # Run backtests
    results = {}

    # 1. Buy & Hold (Benchmark)
    print("\n" + "=" * 50)
    print("Running Buy & Hold backtest...")
    print("=" * 50)
    bt_bh = Backtest(
        df_backtest,
        BuyAndHoldStrategy,
        cash=initial_cash,
        commission=commission,
        exclusive_orders=True
    )
    stats_bh = bt_bh.run()
    results['Buy & Hold'] = stats_bh

    # 2. Heuristic Sentiment Strategy (Original)
    print("\n" + "=" * 50)
    print("Running Heuristic Sentiment Strategy...")
    print("=" * 50)
    bt_heuristic = Backtest(
        df_backtest,
        AdaptiveStrategy,
        cash=initial_cash,
        commission=commission,
        exclusive_orders=True
    )
    stats_heuristic = bt_heuristic.run()
    results['Heuristic Sentiment'] = stats_heuristic

    # 3. News Sentiment Strategy (LLM)
    print("\n" + "=" * 50)
    print("Running News Sentiment Strategy (LLM)...")
    print("=" * 50)
    bt_news = Backtest(
        df_backtest,
        NewsSentimentStrategy,
        cash=initial_cash,
        commission=commission,
        exclusive_orders=True
    )
    stats_news = bt_news.run()
    results['News Sentiment (LLM)'] = stats_news

    # Print comparison
    print("\n" + "=" * 70)
    print("BACKTEST COMPARISON RESULTS")
    print("=" * 70)

    comparison_data = []
    for name, stats in results.items():
        comparison_data.append({
            'Strategy': name,
            'Return %': f"{stats['Return [%]']:.2f}",
            'Sharpe': f"{stats['Sharpe Ratio']:.2f}",
            'Max DD %': f"{stats['Max. Drawdown [%]']:.2f}",
            'Win Rate %': f"{stats['Win Rate [%]']:.2f}",
            '# Trades': stats['# Trades']
        })

    comparison_df = pd.DataFrame(comparison_data)
    print(comparison_df.to_string(index=False))

    # Calculate correlation between sentiment types
    print("\n" + "=" * 70)
    print("SENTIMENT CORRELATION ANALYSIS")
    print("=" * 70)
    correlation = df['AI_Stock_Sentiment'].corr(df['News_Sentiment'])
    print(f"\nCorrelation (Heuristic vs News): {correlation:.3f}")

    if abs(correlation) < 0.3:
        print("-> LOW correlation: News sentiment provides UNCORRELATED signals!")
    elif abs(correlation) < 0.7:
        print("-> MODERATE correlation: Some overlap in signals")
    else:
        print("-> HIGH correlation: Signals are similar")

    # Save results
    output_dir = "experiments/active/EXP-2025-005-real-news-sentiment/results"
    os.makedirs(output_dir, exist_ok=True)

    # Save comparison
    comparison_df.to_csv(f"{output_dir}/comparison.csv", index=False)

    # Save equity curves
    equity_df = pd.DataFrame({
        'Buy & Hold': results['Buy & Hold']['_equity_curve']['Equity'],
        'Heuristic': results['Heuristic Sentiment']['_equity_curve']['Equity'],
        'News (LLM)': results['News Sentiment (LLM)']['_equity_curve']['Equity']
    })
    equity_df.to_csv(f"{output_dir}/equity_curves.csv", index=False)

    print(f"\nResults saved to: {output_dir}/")

    return results, df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="EXP-2025-005: Real News Sentiment Analysis")
    parser.add_argument("--ticker", default="NVDA", help="Stock ticker symbol")
    parser.add_argument("--start", default="2023-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default="2024-01-01", help="End date (YYYY-MM-DD)")
    parser.add_argument("--cash", type=float, default=100_000, help="Initial cash")
    parser.add_argument("--commission", type=float, default=0.001, help="Commission rate")
    parser.add_argument("--no-cache", action="store_true", help="Ignore sentiment cache")

    args = parser.parse_args()

    try:
        results, df = run_comparison(
            ticker=args.ticker,
            start_date=args.start,
            end_date=args.end,
            initial_cash=args.cash,
            commission=args.commission
        )
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
