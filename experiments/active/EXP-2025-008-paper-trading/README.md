# EXP-2025-008: Paper Trading - LLM Sanity Check

**Status:** 🔄 Active
**Started:** 2025-01-13
**Phase:** Paper Trading Validation

## Overview

This experiment takes the successful **LLM Sanity Check** strategy (87.5% shadow test accuracy) into live paper trading mode. The system will:

1. Fetch real-time market data daily
2. Detect extreme price moves (>3% threshold)
3. Use LLM to validate if the move is justified or "market being stupid"
4. Execute trades based on LLM verdict
5. Track performance with full logging

## Hypothesis

> "The LLM Sanity Check strategy will generate positive risk-adjusted returns in live market conditions by avoiding FOMO-driven trades and fading overreactions."

## Strategy Summary

| Signal Type | Trigger | Action | Expected Outcome |
|-------------|---------|--------|------------------|
| **BUY_DIP** | Price drops >3% + Low substance score | Buy the dip | Market overreacting to bad news |
| **BUY_TREND** | Price rises >3% + High substance score | Follow the trend | Justified move, go with flow |
| **SHORT_SCALP** | Price rises >3% + Low substance score | Sell the rip | FOMO-driven pump, fade it |
| **HARD_EXIT** | Price drops >3% + High substance score | Exit/avoid | Real problems, stay away |

## Risk Management

- **Position Size:** 25% of portfolio per trade
- **Max Positions:** 3 concurrent
- **Stop Loss:** 15% (25% for trend-following)
- **Take Profit:** 30% (45% for trend-following)
- **Max Drawdown:** 20% (trading pause if hit)

## Setup

### Prerequisites

```bash
# Install dependencies
pip install yfinance pandas numpy openai python-dotenv

# Set up API keys
cp .env.example .env
# Edit .env and add:
# DEEPSEEK_API_KEY=your_key_here
```

### Directory Structure

```
experiments/active/EXP-2025-008-paper-trading/
├── README.md              # This file
├── state.json             # Persistent state (auto-generated)
├── logs/                  # Daily logs
│   └── paper_trading_YYYYMMDD.log
└── results/               # Trade exports
    ├── trades_YYYYMMDD.csv
    ├── equity_curve_YYYYMMDD.csv
    └── report_YYYYMMDD_HHMMSS.txt
```

## Usage

### Basic Commands

```bash
# Run daily check (fetch data, check signals, execute trades)
python paper_trade.py

# Show current status (positions, P&L, metrics)
python paper_trade.py --status

# Generate detailed performance report
python paper_trade.py --report

# Reset state and start fresh
python paper_trade.py --reset
```

### Advanced Options

```bash
# Trade different ticker
python paper_trade.py --ticker AAPL

# Start with different capital
python paper_trade.py --cash 50000

# Adjust position size (default 25%)
python paper_trade.py --pos-size 0.20
```

### Scheduled Execution (Linux/Mac)

Add to crontab for daily execution:

```bash
# Run every weekday at 9:30 AM (market open)
30 9 * * 1-5 cd /path/to/modular-quant-backtest && python paper_trade.py >> logs/cron.log 2>&1

# Run every weekday at 4:00 PM (market close)
0 16 * * 1-5 cd /path/to/modular-quant-backtest && python paper_trade.py >> logs/cron.log 2>&1
```

### Scheduled Execution (Windows)

Use Task Scheduler to run:
```cmd
cd D:\document\modular-quant-backtest
python paper_trade.py
```

## Success Criteria

| Metric | Target | Current |
|--------|--------|---------|
| Win Rate | >55% | TBD |
| Sharpe Ratio | >1.0 | TBD |
| Max Drawdown | <20% | TBD |
| Total Return | >10% | TBD |

## Shadow Test Results (Baseline)

From EXP-008 shadow testing:
- **Accuracy:** 87.5% (7/8 correct predictions)
- **Avoided FOMO traps:** 3 times
- **Caught fake rallies:** 2 times
- **Identified real breakdowns:** 2 times

## Daily Operations Checklist

Each trading day:

- [ ] Run `python paper_trade.py --status` to check positions
- [ ] Review any new signals generated
- [ ] Check stop loss / take profit hits
- [ ] Review daily log file for any errors
- [ ] Weekly: Generate report with `--report` flag

## Known Limitations

1. **News Source:** Currently using mock news generator based on price action
   - Production should use real news API (NewsAPI, etc.)

2. **Execution:** Paper trading assumes immediate fill at market price
   - Real trading would have slippage and partial fills

3. **Single Asset:** Only trading one ticker at a time
   - Could expand to multi-asset portfolio

4. **No Shorting:** Currently long-only for simplicity
   - SHORT_SCALP signal exists but not fully implemented

## Next Steps

- [ ] 1 week of paper trading data
- [ ] Compare performance vs buy-and-hold
- [ ] Analyze win rate by signal type
- [ ] Implement real news feed
- [ ] Add short selling capability
- [ ] Expand to multiple tickers

## State Persistence

The paper trading engine maintains persistent state in `state.json`:

```json
{
  "cash": 100000.00,
  "positions": [...],
  "trades": [...],
  "total_equity": 100000.00,
  "peak_equity": 100000.00,
  "daily_snapshots": [...]
}
```

This allows the system to resume after restarts without losing position data.

## Troubleshooting

### No API Key Error
```
ValueError: DEEPSEEK_API_KEY not found
```
Solution: Set up `.env` file with your API key

### No Data Retrieved
```
WARNING: No data retrieved for NVDA
```
Solution: Check internet connection, try during market hours

### State File Corrupted
```
Error loading state: ...
```
Solution: Run `python paper_trade.py --reset` to start fresh

## Links

- [Shadow Test Results](../../archived/successful/EXP-2025-008-llm-sanity-check/)
- [LLM Sanity Checker Code](../../../src/llm/sanity_checker.py)
- [Experiment Workflow](../../EXPERIMENT_WORKFLOW.md)

---

**Last Updated:** 2025-01-13
**Next Review:** 2025-01-20 (after 1 week)
