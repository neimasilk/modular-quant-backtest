#!/usr/bin/env python
"""
Paper Trading Runner for EXP-2025-008
======================================
Easy-to-use script for running paper trading with LLM Sanity Check.

Usage:
    python paper_trade.py                    # Run daily check
    python paper_trade.py --status           # Show current status
    python paper_trade.py --reset            # Reset state
    python paper_trade.py --ticker AAPL      # Trade different ticker
    python paper_trade.py --report           # Generate detailed report
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.engines.paper_trading_engine import (
    PaperTradingEngine,
    PaperTradingConfig
)


def print_banner():
    """Print welcome banner."""
    print("\n" + "=" * 65)
    print("  PAPER TRADING - EXP-2025-008: LLM Sanity Check")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 65 + "\n")


def show_status(config: PaperTradingConfig):
    """Show current paper trading status."""
    print("[*] Loading current status...\n")

    engine = PaperTradingEngine(config)
    state = engine.state

    print(f"Cash Balance:        ${state.cash:,.2f}")
    print(f"Total Equity:        ${state.total_equity:,.2f}")
    print(f"Peak Equity:         ${state.peak_equity:,.2f}")
    print(f"Total Return:        {(state.total_equity / config.initial_cash - 1) * 100:+.2f}%")
    print(f"Open Positions:      {len(state.positions)}")
    print(f"Closed Trades:       {len(state.trades)}")

    # Drawdown
    dd = (state.peak_equity - state.total_equity) / state.peak_equity * 100
    print(f"Max Drawdown:        {dd:.2f}%")

    # Show open positions
    if state.positions:
        print("\n--- OPEN POSITIONS ---")
        for p in state.positions:
            # Fetch current price
            data = engine.fetch_market_data(p.ticker, days=5)
            if data is not None:
                current_price = float(data.iloc[-1]['Close'])
                pnl, pnl_pct = p.unrealized_pnl(current_price)
                print(f"  {p.ticker}: {p.entry_signal}")
                print(f"    Entry: ${p.entry_price:.2f} | Current: ${current_price:.2f}")
                print(f"    P&L: ${pnl:,.2f} ({pnl_pct:+.2f}%)")
                print(f"    Stop: ${p.stop_loss:.2f} | Target: ${p.take_profit:.2f}")
                print(f"    Entry Date: {p.entry_date[:10]}")

    # Show recent trades
    if state.trades:
        print("\n--- RECENT TRADES (Last 5) ---")
        recent = state.trades[-5:][::-1]  # Last 5, reversed
        for t in recent:
            print(f"  {t['ticker']}: {t['entry_signal']}")
            print(f"    {t['entry_date'][:10]} -> {t['exit_date'][:10]}")
            print(f"    P&L: ${t['pnl']:,.2f} ({t['pnl_pct']:+.2f}%) - {t['exit_reason']}")

    # Performance metrics
    metrics = engine.get_performance_metrics()
    if metrics:
        print("\n--- PERFORMANCE METRICS ---")
        print(f"  Win Rate:           {metrics.get('win_rate', 0):.1f}%")
        print(f"  Avg Win:            ${metrics.get('avg_win', 0):,.2f}")
        print(f"  Avg Loss:           ${metrics.get('avg_loss', 0):,.2f}")
        print(f"  Profit Factor:      {metrics.get('profit_factor', 0):.2f}")


def generate_report(config: PaperTradingConfig):
    """Generate detailed performance report."""
    print("[*] Generating detailed report...\n")

    engine = PaperTradingEngine(config)

    # Create report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = Path(config.results_dir) / f"report_{timestamp}.txt"

    with open(report_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("PAPER TRADING REPORT - EXP-2025-008\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")

        # Configuration
        f.write("CONFIGURATION\n")
        f.write("-" * 40 + "\n")
        f.write(f"Ticker:              {config.ticker}\n")
        f.write(f"Initial Cash:        ${config.initial_cash:,.2f}\n")
        f.write(f"Position Size:       {config.position_size_pct * 100:.0f}%\n")
        f.write(f"Stop Loss:           {config.stop_loss_pct * 100:.0f}%\n")
        f.write(f"Take Profit:         {config.take_profit_pct * 100:.0f}%\n\n")

        # Current State
        state = engine.state
        f.write("CURRENT STATUS\n")
        f.write("-" * 40 + "\n")
        f.write(f"Cash:                ${state.cash:,.2f}\n")
        f.write(f"Total Equity:        ${state.total_equity:,.2f}\n")
        f.write(f"Peak Equity:         ${state.peak_equity:,.2f}\n")
        f.write(f"Total Return:        {(state.total_equity / config.initial_cash - 1) * 100:+.2f}%\n")
        f.write(f"Open Positions:      {len(state.positions)}\n")
        f.write(f"Total Trades:        {len(state.trades)}\n\n")

        # Performance Metrics
        metrics = engine.get_performance_metrics()
        if metrics:
            f.write("PERFORMANCE METRICS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Win Rate:           {metrics.get('win_rate', 0):.2f}%\n")
            f.write(f"Average Win:        ${metrics.get('avg_win', 0):,.2f}\n")
            f.write(f"Average Loss:       ${metrics.get('avg_loss', 0):,.2f}\n")
            f.write(f"Profit Factor:      {metrics.get('profit_factor', 0):.2f}\n")
            f.write(f"Total P&L:          ${metrics.get('total_pnl', 0):,.2f}\n")
            f.write(f"Max Drawdown:       {metrics.get('max_drawdown', 0):.2f}%\n\n")

        # Trade Breakdown
        if state.trades:
            f.write("TRADE BREAKDOWN BY SIGNAL TYPE\n")
            f.write("-" * 40 + "\n")

            signal_groups = {}
            for t in state.trades:
                sig = t['entry_signal']
                if sig not in signal_groups:
                    signal_groups[sig] = []
                signal_groups[sig].append(t)

            for sig, trades in signal_groups.items():
                wins = sum(1 for t in trades if t['pnl'] > 0)
                total_pnl = sum(t['pnl'] for t in trades)
                f.write(f"{sig}:\n")
                f.write(f"  Trades:     {len(trades)}\n")
                f.write(f"  Wins:       {wins}/{len(trades)} ({wins/len(trades)*100:.0f}%)\n")
                f.write(f"  Total P&L:  ${total_pnl:,.2f}\n")
                if len(trades) > 0:
                    f.write(f"  Avg P&L:   ${total_pnl/len(trades):,.2f}\n")
                f.write("\n")

        # Individual Trades
        if state.trades:
            f.write("ALL TRADES\n")
            f.write("-" * 40 + "\n")
            f.write(f"{'Date':<12} {'Ticker':<8} {'Signal':<15} {'P&L':>12} {'Return':>10} {'Reason':<20}\n")
            f.write("-" * 90 + "\n")
            for t in state.trades:
                exit_date = t['exit_date'][:10]
                f.write(f"{exit_date:<12} {t['ticker']:<8} {t['entry_signal']:<15} "
                       f"${t['pnl']:>10.2f} {t['pnl_pct']:>9.2f}% {t['exit_reason']:<20}\n")

    print(f"[OK] Report saved to: {report_path}")

    # Also save CSV exports
    engine.export_trades_csv()
    engine.export_equity_curve()

    return report_path


def reset_state(config: PaperTradingConfig):
    """Reset paper trading state."""
    state_path = Path(config.state_file)

    if state_path.exists():
        confirm = input(f"Confirm reset state file? (y/N): ")
        if confirm.lower() == 'y':
            state_path.unlink()
            print("[OK] State reset complete")
            print("     Run paper trading again to start fresh")
        else:
            print("[SKIP] Reset cancelled")
    else:
        print("[INFO] No existing state file found")


def main():
    """Main entry point."""

    # List of tickers to scan for opportunities
    SCAN_LIST = [
        'NVDA', 'AMD', 'TSLA', 'META', 'GOOGL', 'AMZN', 'MSFT', 'AAPL',
        'COIN', 'MSTR', 'MARA', 'RIOT'
    ]

    parser = argparse.ArgumentParser(
        description="Paper Trading Runner - EXP-2025-008",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python paper_trade.py              # Run daily scan across multiple tickers
  python paper_trade.py --status     # Show current status
  python paper_trade.py --report     # Generate detailed report
  python paper_trade.py --reset      # Reset state
  python paper_trade.py --cash 50000
        """
    )

    parser.add_argument(
        '--cash', '-c',
        type=float,
        default=100_000,
        help='Initial cash (default: 100000)'
    )

    parser.add_argument(
        '--pos-size',
        type=float,
        default=0.25,
        help='Position size as decimal (default: 0.25 = 25%%)'
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        '--status',
        action='store_true',
        help='Show current status only'
    )
    mode.add_argument(
        '--report',
        action='store_true',
        help='Generate detailed report'
    )
    mode.add_argument(
        '--reset',
        action='store_true',
        help='Reset state and start fresh'
    )

    args = parser.parse_args()

    # Create config (ticker is now a placeholder)
    config = PaperTradingConfig(
        ticker="MULTI_SCAN", 
        initial_cash=args.cash,
        position_size_pct=args.pos_size
    )

    print_banner()

    # Route to appropriate function
    if args.status:
        show_status(config)
    elif args.report:
        generate_report(config)
    elif args.reset:
        reset_state(config)
    else:
        # Pass the full list to the trading engine
        print(f"[*] Scanning {len(SCAN_LIST)} tickers...")
        engine = PaperTradingEngine(config)
        engine.run_daily_check(tickers_to_scan=SCAN_LIST)
        
        # Export results after the scan
        trades_file = engine.export_trades_csv()
        equity_file = engine.export_equity_curve()

        print("\n[OK] Daily scan complete!")
        if trades_file:
            print(f"     Trades: {trades_file}")
        if equity_file:
            print(f"     Equity: {equity_file}")


if __name__ == "__main__":
    main()
