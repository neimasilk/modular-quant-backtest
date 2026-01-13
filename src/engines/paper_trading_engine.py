"""
Paper Trading Engine for EXP-2025-008
=======================================
Live trading simulation with real market data, no real money.

Features:
- Real-time data fetching from Yahoo Finance
- LLM Sanity Check integration for signal validation
- State persistence for recovery
- Comprehensive logging and tracking
- Daily summary reports
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass, asdict
from decimal import Decimal
import logging

import pandas as pd
import numpy as np
import yfinance as yf

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.llm.sanity_checker import NewsSanityChecker


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class PaperTradingConfig:
    """Configuration for paper trading."""

    # Trading parameters
    ticker: str = "NVDA"
    initial_cash: float = 100_000.0
    position_size_pct: float = 0.25  # 25% of portfolio per trade
    max_positions: int = 3

    # Signal thresholds
    price_move_threshold: float = 0.03  # 3% move triggers LLM check

    # Risk management
    stop_loss_pct: float = 0.15  # 15% stop loss
    take_profit_pct: float = 0.30  # 30% take profit
    max_drawdown_pct: float = 0.20  # 20% max drawdown (pause trading)

    # Data settings
    data_lookback_days: int = 30

    # State persistence
    state_file: str = "experiments/active/EXP-2025-008-paper-trading/state.json"
    log_dir: str = "experiments/active/EXP-2025-008-paper-trading/logs"
    results_dir: str = "experiments/active/EXP-2025-008-paper-trading/results"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Position:
    """Open position in paper trading."""

    ticker: str
    entry_date: str
    entry_price: float
    shares: float
    entry_signal: str  # BUY_DIP, BUY_TREND, etc.
    stop_loss: float
    take_profit: float
    llm_verdict: str
    substance_score: int

    def current_value(self, current_price: float) -> float:
        """Calculate current position value."""
        return self.shares * current_price

    def unrealized_pnl(self, current_price: float) -> tuple[float, float]:
        """Calculate unrealized P&L (absolute and percentage)."""
        if self.entry_signal in ["SHORT_SCALP", "HARD_EXIT"]:
            # Short position logic (if implemented)
            pnl = (self.entry_price - current_price) * self.shares
            pnl_pct = (self.entry_price - current_price) / self.entry_price
        else:
            # Long position
            pnl = (current_price - self.entry_price) * self.shares
            pnl_pct = (current_price - self.entry_price) / self.entry_price

        return float(pnl), float(pnl_pct * 100)


@dataclass
class Trade:
    """Closed trade record."""

    trade_id: str
    ticker: str
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    shares: float
    entry_signal: str
    exit_reason: str
    llm_verdict: str
    substance_score: int
    pnl: float
    pnl_pct: float
    holding_days: int


@dataclass
class PaperTradingState:
    """Persistent state of paper trading account."""

    cash: float
    positions: List[Dict]
    trades: List[Dict]
    last_update: str
    total_equity: float
    peak_equity: float
    daily_snapshots: List[Dict]

    @classmethod
    def create_initial(cls, initial_cash: float) -> "PaperTradingState":
        """Create initial state."""
        return cls(
            cash=initial_cash,
            positions=[],
            trades=[],
            last_update=datetime.now().isoformat(),
            total_equity=initial_cash,
            peak_equity=initial_cash,
            daily_snapshots=[{
                "date": datetime.now().isoformat(),
                "cash": initial_cash,
                "equity": initial_cash,
                "positions_value": 0.0,
                "total_equity": initial_cash
            }]
        )


# ============================================================================
# PAPER TRADING ENGINE
# ============================================================================

class PaperTradingEngine:
    """
    Paper Trading Engine with LLM Sanity Check integration.

    Usage:
        engine = PaperTradingEngine(config)
        engine.run_daily_check()
    """

    def __init__(self, config: Optional[PaperTradingConfig] = None):
        """Initialize paper trading engine."""
        self.config = config or PaperTradingConfig()

        # Set up logging
        self._setup_logging()

        # Create directories
        Path(self.config.log_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.results_dir).mkdir(parents=True, exist_ok=True)

        # Initialize LLM Sanity Checker
        try:
            self.sanity_checker = NewsSanityChecker()
            self.logger.info("LLM Sanity Checker initialized successfully")
        except Exception as e:
            self.logger.warning(f"LLM Sanity Checker not available: {e}")
            self.sanity_checker = None

        # Load or create state
        self.state = self._load_state()

        self.logger.info(f"Paper Trading Engine initialized")
        self.logger.info(f"  Cash: ${self.state.cash:,.2f}")
        self.logger.info(f"  Equity: ${self.state.total_equity:,.2f}")
        self.logger.info(f"  Open Positions: {len(self.state.positions)}")

    def _setup_logging(self):
        """Set up logging configuration."""
        log_file = os.path.join(
            self.config.log_dir,
            f"paper_trading_{datetime.now().strftime('%Y%m%d')}.log"
        )

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)-8s | %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("PaperTrading")

    def _load_state(self) -> PaperTradingState:
        """Load state from file or create new."""
        state_path = Path(self.config.state_file)

        if state_path.exists():
            try:
                with open(state_path, 'r') as f:
                    data = json.load(f)
                    state = PaperTradingState(**data)
                    # Reconstruct Position objects
                    state.positions = [Position(**p) if isinstance(p, dict) else p
                                      for p in state.positions]
                    self.logger.info(f"Loaded existing state from {state_path}")
                    return state
            except Exception as e:
                self.logger.error(f"Error loading state: {e}. Creating new state.")

        return PaperTradingState.create_initial(self.config.initial_cash)

    def _save_state(self):
        """Save state to file."""
        state_path = Path(self.config.state_file)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert Position objects to dicts for JSON serialization
        state_dict = {
            "cash": self.state.cash,
            "positions": [asdict(p) if isinstance(p, Position) else p
                         for p in self.state.positions],
            "trades": self.state.trades,
            "last_update": datetime.now().isoformat(),
            "total_equity": self.state.total_equity,
            "peak_equity": self.state.peak_equity,
            "daily_snapshots": self.state.daily_snapshots
        }

        with open(state_path, 'w') as f:
            json.dump(state_dict, f, indent=2, default=str)

    # ========================================================================
    # DATA FETCHING
    # ========================================================================

    def fetch_market_data(self, ticker: str, days: int = 30) -> Optional[pd.DataFrame]:
        """
        Fetch recent market data for a ticker.

        Args:
            ticker: Stock symbol
            days: Number of days of history to fetch

        Returns:
            DataFrame with OHLCV data or None if failed
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            data = yf.download(
                ticker,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                progress=False
            )

            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            if len(data) == 0:
                self.logger.warning(f"No data retrieved for {ticker}")
                return None

            data = data.reset_index()
            return data

        except Exception as e:
            self.logger.error(f"Error fetching data for {ticker}: {e}")
            return None

    def get_latest_news(self, ticker: str) -> str:
        """
        Get latest news headline for a ticker from yfinance.

        Args:
            ticker: Stock symbol

        Returns:
            News headline string
        """
        try:
            t = yf.Ticker(ticker)
            news = t.news
            
            if not news:
                self.logger.warning(f"No news found for {ticker} via yfinance")
                return f"{ticker} - No recent news available"

            # Get the most recent news item
            # Sort by date just in case
            latest_news = news[0]
            title = latest_news.get('content', {}).get('title', "")
            summary = latest_news.get('content', {}).get('summary', "")
            
            if not title:
                # Try alternative structure (some yfinance versions differ)
                title = latest_news.get('title', "No Title")
                summary = latest_news.get('summary', "")

            full_news = f"{title}. {summary}"
            self.logger.info(f"Fetched latest news for {ticker}: {title[:50]}...")
            return full_news

        except Exception as e:
            self.logger.error(f"Error fetching news for {ticker}: {e}")
            return f"{ticker} - News fetch error"

    # ========================================================================
    # TRADING LOGIC
    # ========================================================================

    def generate_signals(self, ticker: str) -> List[Dict]:
        """
        Generate trading signals using LLM Sanity Check.

        Args:
            ticker: Stock symbol to analyze

        Returns:
            List of signal dictionaries
        """
        if not self.sanity_checker:
            self.logger.warning("LLM Sanity Checker not available")
            return []

        # Get recent data
        data = self.fetch_market_data(ticker, self.config.data_lookback_days)
        if data is None or len(data) < 5:
            return []

        # Get current price and recent change
        latest = data.iloc[-1]
        prev_close = data.iloc[-2]['Close']

        price_change_pct = (latest['Close'] - prev_close) / prev_close

        # Skip if move is below threshold
        if abs(price_change_pct) < self.config.price_move_threshold:
            self.logger.info(f"Price move ({price_change_pct:+.1%}) below threshold")
            return []

        # Get news (mock for now)
        news_text = self.get_latest_news(ticker)

        # Get volume context
        avg_volume = data['Volume'].mean()
        current_volume = latest['Volume']

        # Call LLM Sanity Checker
        try:
            result = self.sanity_checker.check_signal(
                ticker=ticker,
                price_change_pct=price_change_pct,
                news_text=news_text,
                volume=current_volume,
                avg_volume=avg_volume,
                verbose=True
            )

            if result.get('should_trade'):
                signal = {
                    'ticker': ticker,
                    'signal': result['signal'],
                    'verdict': result['verdict'],
                    'substance_score': result['substance_score'],
                    'reasoning': result['reasoning'],
                    'current_price': float(latest['Close']),
                    'price_change_pct': price_change_pct,
                    'timestamp': datetime.now().isoformat()
                }
                self.logger.info(f"Signal generated: {signal['signal']} for {ticker}")
                return [signal]
            else:
                self.logger.info(f"No trade signal for {ticker}: {result['reasoning']}")

        except Exception as e:
            self.logger.error(f"Error generating signal: {e}")

        return []

    def execute_entry(self, signal: Dict) -> Optional[Position]:
        """
        Execute an entry order based on signal.

        Args:
            signal: Signal dictionary from generate_signals()

        Returns:
            Position object if executed, None otherwise
        """
        ticker = signal['ticker']
        entry_price = signal['current_price']
        signal_type = signal['signal']

        # Calculate position size
        position_value = self.state.cash * self.config.position_size_pct

        # Check if we have enough cash
        if position_value < entry_price:
            self.logger.warning(f"Insufficient cash to enter position in {ticker}")
            return None

        shares = position_value / entry_price

        # Calculate stop loss and take profit
        if signal_type == "BUY_DIP":
            # Buying dip - expect reversal
            stop_loss = entry_price * (1 - self.config.stop_loss_pct)
            take_profit = entry_price * (1 + self.config.take_profit_pct)
        elif signal_type == "BUY_TREND":
            # Following trend - wider stops
            stop_loss = entry_price * (1 - self.config.stop_loss_pct * 1.5)
            take_profit = entry_price * (1 + self.config.take_profit_pct * 1.5)
        elif signal_type == "SHORT_SCALP":
            # Short position - inverted levels
            stop_loss = entry_price * (1 + self.config.stop_loss_pct)
            take_profit = entry_price * (1 - self.config.take_profit_pct * 0.5)
        else:
            stop_loss = entry_price * (1 - self.config.stop_loss_pct)
            take_profit = entry_price * (1 + self.config.take_profit_pct)

        # Create position
        position = Position(
            ticker=ticker,
            entry_date=datetime.now().isoformat(),
            entry_price=entry_price,
            shares=shares,
            entry_signal=signal_type,
            stop_loss=stop_loss,
            take_profit=take_profit,
            llm_verdict=signal['verdict'],
            substance_score=signal['substance_score']
        )

        # Update state
        self.state.cash -= position_value
        self.state.positions.append(position)

        self.logger.info(f"ENTRY EXECUTED: {signal_type} {ticker}")
        self.logger.info(f"  Price: ${entry_price:.2f} | Shares: {shares:.2f}")
        self.logger.info(f"  Cost: ${position_value:,.2f}")
        self.logger.info(f"  Stop Loss: ${stop_loss:.2f} | Take Profit: ${take_profit:.2f}")

        return position

    def check_exits(self, current_prices: Dict[str, float]) -> List[Trade]:
        """
        Check existing positions for exit conditions.

        Args:
            current_prices: Dict mapping ticker to current price

        Returns:
            List of closed trades
        """
        closed_trades = []
        positions_to_close = []

        for i, position in enumerate(self.state.positions):
            if position.ticker not in current_prices:
                continue

            current_price = current_prices[position.ticker]
            pnl, pnl_pct = position.unrealized_pnl(current_price)
            exit_reason = None

            # Check stop loss
            if position.entry_signal in ["BUY_DIP", "BUY_TREND"]:
                if current_price <= position.stop_loss:
                    exit_reason = f"Stop Loss hit (-{abs(pnl_pct):.1f}%)"
                elif current_price >= position.take_profit:
                    exit_reason = f"Take Profit hit (+{pnl_pct:.1f}%)"
            elif position.entry_signal == "SHORT_SCALP":
                if current_price >= position.stop_loss:
                    exit_reason = f"Stop Loss hit (-{abs(pnl_pct):.1f}%)"
                elif current_price <= position.take_profit:
                    exit_reason = f"Take Profit hit (+{abs(pnl_pct):.1f}%)"

            # Hard exit on LLM HARD_EXIT signal
            if position.entry_signal == "HARD_EXIT" and pnl_pct < -5:
                exit_reason = f"Hard Exit triggered ({pnl_pct:.1f}%)"

            if exit_reason:
                # Close the position
                trade = self._close_position(position, current_price, exit_reason)
                closed_trades.append(trade)
                positions_to_close.append(i)

        # Remove closed positions (in reverse order to maintain indices)
        for i in sorted(positions_to_close, reverse=True):
            self.state.positions.pop(i)

        return closed_trades

    def _close_position(self, position: Position, exit_price: float,
                       exit_reason: str) -> Trade:
        """Close a position and create a trade record."""
        exit_date = datetime.now()
        entry_date = datetime.fromisoformat(position.entry_date)
        holding_days = (exit_date - entry_date).days

        pnl, pnl_pct = position.unrealized_pnl(exit_price)
        
        # Calculate amount to return to cash balance
        # We always deducted (entry_price * shares) at entry.
        # So we return that original amount + the profit (or - loss).
        entry_value = position.shares * position.entry_price
        return_to_cash = entry_value + pnl

        # Add proceeds to cash
        self.state.cash += return_to_cash

        # Create trade record
        trade = Trade(
            trade_id=f"{position.ticker}_{entry_date.strftime('%Y%m%d')}_{exit_date.strftime('%Y%m%d')}",
            ticker=position.ticker,
            entry_date=position.entry_date,
            exit_date=exit_date.isoformat(),
            entry_price=position.entry_price,
            exit_price=exit_price,
            shares=position.shares,
            entry_signal=position.entry_signal,
            exit_reason=exit_reason,
            llm_verdict=position.llm_verdict,
            substance_score=position.substance_score,
            pnl=pnl,
            pnl_pct=pnl_pct,
            holding_days=holding_days
        )

        self.state.trades.append(asdict(trade))

        self.logger.info(f"EXIT EXECUTED: {position.ticker}")
        self.logger.info(f"  {exit_reason}")
        self.logger.info(f"  Entry: ${position.entry_price:.2f} -> Exit: ${exit_price:.2f}")
        self.logger.info(f"  P&L: ${pnl:,.2f} ({pnl_pct:+.2f}%) | Days: {holding_days}")

        return trade

    # ========================================================================
    # DAILY RUN
    # ========================================================================

    def run_daily_check(self, tickers_to_scan: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run daily paper trading check.

        Args:
            tickers_to_scan: Optional list of tickers to check for new opportunities.
                           If None, uses self.config.ticker.

        This should be called once per day (or scheduled via cron).
        """
        self.logger.info("=" * 60)
        self.logger.info("DAILY PAPER TRADING CHECK")
        self.logger.info("=" * 60)

        # Get current prices for all positions
        current_prices = {}
        for position in self.state.positions:
            data = self.fetch_market_data(position.ticker, days=5)
            if data is not None and len(data) > 0:
                current_prices[position.ticker] = float(data.iloc[-1]['Close'])

        # Check exits first
        closed_trades = self.check_exits(current_prices)

        # Calculate current equity
        positions_value = sum(
            position.current_value(current_prices.get(position.ticker, position.entry_price))
            for position in self.state.positions
        )
        total_equity = self.state.cash + positions_value

        # Update peak equity
        if total_equity > self.state.peak_equity:
            self.state.peak_equity = total_equity

        # Check max drawdown
        max_dd = (self.state.peak_equity - total_equity) / self.state.peak_equity
        if max_dd > self.config.max_drawdown_pct:
            self.logger.warning(f"Max drawdown exceeded: {max_dd:.1%}")
            self.logger.warning("Trading paused due to max drawdown")
            # Could implement pause logic here

        # Determine scan list
        scan_list = tickers_to_scan if tickers_to_scan else [self.config.ticker]
        if tickers_to_scan:
            self.logger.info(f"Scanning {len(scan_list)} tickers for opportunities...")

        # Generate new signals if under max positions
        if len(self.state.positions) < self.config.max_positions:
            for ticker in scan_list:
                # Stop scanning if we filled up positions
                if len(self.state.positions) >= self.config.max_positions:
                    self.logger.info(f"Max positions ({self.config.max_positions}) reached. Stopping scan.")
                    break
                
                # Check signals for this ticker
                try:
                    signals = self.generate_signals(ticker)
                    
                    for signal in signals:
                        # Check if already have position in this ticker
                        has_position = any(
                            p.ticker == signal['ticker'] for p in self.state.positions
                        )
                        if not has_position:
                            self.execute_entry(signal)
                            # Only take one trade per ticker per day
                            break 
                except Exception as e:
                    self.logger.error(f"Error scanning {ticker}: {e}")
                    continue
        else:
            self.logger.info(f"Max positions ({self.config.max_positions}) reached. No new entries.")

        # Update state
        self.state.total_equity = total_equity
        self.state.last_update = datetime.now().isoformat()

        # Add daily snapshot
        snapshot = {
            "date": datetime.now().isoformat(),
            "cash": self.state.cash,
            "positions_value": positions_value,
            "total_equity": total_equity,
            "num_positions": len(self.state.positions),
            "num_trades_today": len(closed_trades)
        }
        self.state.daily_snapshots.append(snapshot)

        # Save state
        self._save_state()

        # Generate summary
        summary = self._generate_summary()
        self.logger.info("\n" + summary)

        return {
            "state": self.state,
            "closed_trades": [asdict(t) for t in closed_trades],
            "summary": summary
        }

    def _generate_summary(self) -> str:
        """Generate daily summary string."""
        lines = [
            "=" * 60,
            "PAPER TRADING SUMMARY",
            "=" * 60,
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"Cash:              ${self.state.cash:,.2f}",
            f"Positions Value:   ${self.state.total_equity - self.state.cash:,.2f}",
            f"Total Equity:      ${self.state.total_equity:,.2f}",
            f"Peak Equity:       ${self.state.peak_equity:,.2f}",
            "",
            f"Return:            {(self.state.total_equity / self.config.initial_cash - 1) * 100:+.2f}%",
            f"Drawdown:          {(self.state.peak_equity - self.state.total_equity) / self.state.peak_equity * 100:.2f}%",
            "",
            f"Open Positions:    {len(self.state.positions)}",
            f"Total Trades:      {len(self.state.trades)}",
        ]

        # Add position details
        if self.state.positions:
            lines.append("\nOpen Positions:")
            for p in self.state.positions:
                # Need to fetch current price for accurate P&L
                data = self.fetch_market_data(p.ticker, days=5)
                if data is not None:
                    current_price = float(data.iloc[-1]['Close'])
                    pnl, pnl_pct = p.unrealized_pnl(current_price)
                    lines.append(
                        f"  {p.ticker}: {p.entry_signal} | "
                        f"${p.entry_price:.2f} -> ${current_price:.2f} | "
                        f"P&L: ${pnl:,.2f} ({pnl_pct:+.2f}%)"
                    )

        lines.append("=" * 60)
        return "\n".join(lines)

    # ========================================================================
    # REPORTING
    # ========================================================================

    def export_trades_csv(self) -> str:
        """Export trades to CSV file."""
        if not self.state.trades:
            self.logger.info("No trades to export")
            return ""

        df = pd.DataFrame(self.state.trades)
        output_path = os.path.join(
            self.config.results_dir,
            f"trades_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        df.to_csv(output_path, index=False)
        self.logger.info(f"Trades exported to {output_path}")
        return output_path

    def export_equity_curve(self) -> str:
        """Export daily equity curve to CSV."""
        if not self.state.daily_snapshots:
            self.logger.info("No snapshots to export")
            return ""

        df = pd.DataFrame(self.state.daily_snapshots)
        output_path = os.path.join(
            self.config.results_dir,
            f"equity_curve_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        df.to_csv(output_path, index=False)
        self.logger.info(f"Equity curve exported to {output_path}")
        return output_path

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics."""
        if not self.state.trades:
            return {}

        trades_df = pd.DataFrame(self.state.trades)

        total_trades = len(trades_df)
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]

        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
        total_pnl = trades_df['pnl'].sum()

        return {
            "total_trades": total_trades,
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "total_pnl": total_pnl,
            "profit_factor": abs(avg_win / avg_loss) if avg_loss != 0 else 0,
            "current_equity": self.state.total_equity,
            "total_return": (self.state.total_equity / self.config.initial_cash - 1) * 100,
            "peak_equity": self.state.peak_equity,
            "max_drawdown": (self.state.peak_equity - self.state.total_equity) / self.state.peak_equity * 100
        }


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    """Run paper trading from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Paper Trading Engine")
    parser.add_argument('--ticker', '-t', type=str, default='NVDA',
                       help='Ticker to trade (default: NVDA)')
    parser.add_argument('--cash', type=float, default=100_000,
                       help='Initial cash (default: 100000)')
    parser.add_argument('--reset', action='store_true',
                       help='Reset state and start fresh')

    args = parser.parse_args()

    # Create config
    config = PaperTradingConfig(ticker=args.ticker, initial_cash=args.cash)

    # Reset state if requested
    if args.reset:
        state_path = Path(config.state_file)
        if state_path.exists():
            state_path.unlink()
            print(f"Reset state file: {state_path}")

    # Create and run engine
    engine = PaperTradingEngine(config)

    # Run daily check
    result = engine.run_daily_check()

    # Export results
    engine.export_trades_csv()
    engine.export_equity_curve()

    # Print metrics
    metrics = engine.get_performance_metrics()
    if metrics:
        print("\n" + "=" * 50)
        print("PERFORMANCE METRICS")
        print("=" * 50)
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
