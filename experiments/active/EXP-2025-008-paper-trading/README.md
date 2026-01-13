# EXP-2025-008: Paper Trading - LLM Sanity Check

**Status:** 🔄 Active
**Started:** 2025-01-13
**Last Updated:** 2025-01-13
**Phase:** Paper Trading Validation (Real News & Multi-Ticker)

## Overview

This experiment takes the successful **LLM Sanity Check** strategy (87.5% shadow test accuracy) into live paper trading mode. The system uses AI to validate "reasons" behind extreme price moves before trading.

**Key Features (v2 - Implemented 2025-01-13):**
1. **Real News Feed:** Uses Yahoo Finance (via `yfinance`) to fetch *actual* headlines, replacing mock data.
2. **Multi-Ticker Scanner:** Automatically scans 12 high-volatility tickers daily (NVDA, TSLA, MARA, MSTR, etc.).
3. **Short Selling:** Fully functional short selling logic for "SHORT_SCALP" signals (fading the hype).
4. **DeepSeek Integration:** Validates news substance on a 1-10 scale.

## Hypothesis

> "The LLM Sanity Check strategy will generate positive risk-adjusted returns in live market conditions by avoiding FOMO-driven trades and fading overreactions."

## Strategy Summary

| Signal Type | Trigger | Action | Expected Outcome |
|-------------|---------|--------|------------------|
| **BUY_DIP** | Price drops >3% + Low substance score | Buy the dip | Market overreacting to bad news |
| **BUY_TREND** | Price rises >3% + High substance score | Follow the trend | Justified move, go with flow |
| **SHORT_SCALP** | Price rises >3% + Low substance score | Sell the rip (Short) | FOMO-driven pump, fade it |
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
# Run daily scan (scans ALL 12 tickers)
python paper_trade.py

# Show current status (positions, P&L, metrics)
python paper_trade.py --status

# Generate detailed performance report
python paper_trade.py --report

# Reset state and start fresh
python paper_trade.py --reset
```

### Configuration
The scan list is hardcoded in `paper_trade.py` and includes:
`['NVDA', 'AMD', 'TSLA', 'META', 'GOOGL', 'AMZN', 'MSFT', 'AAPL', 'COIN', 'MSTR', 'MARA', 'RIOT']`

## Active Positions (as of 2026-01-13)

| Ticker | Type | Entry Price | Signal | Status |
|--------|------|-------------|--------|--------|
| **MARA** | SHORT | $10.65 | Low substance hype | Active |
| **MSTR** | SHORT | $162.23 | Insider buy noise | Active |
| **RIOT** | SHORT | $16.45 | Speculative pivot | Active |

## Success Criteria

| Metric | Target | Current |
|--------|--------|---------|
| Win Rate | >55% | TBD |
| Sharpe Ratio | >1.0 | TBD |
| Max Drawdown | <20% | TBD |
| Total Return | >10% | TBD |

## Daily Operations Checklist

Each trading day:

- [ ] Run `python paper_trade.py` to scan markets and manage positions
- [ ] Review any new signals generated
- [ ] Check stop loss / take profit hits (automatic)
- [ ] Weekly: Generate report with `--report` flag

## Known Limitations

1. **Execution:** Paper trading assumes immediate fill at market price (slippage ignored).
2. **Frequency:** Currently designed for Daily timeframe scans.

## Completed Tasks (2025-01-13)

- [x] **Real News Integration:** Replaced mock news with Yahoo Finance API.
- [x] **Short Selling:** Fixed P&L logic to support short positions.
- [x] **Multi-Ticker Scanner:** Now scans 12 tickers automatically.
- [x] **Live Validation:** Successfully detected and traded MARA, MSTR, RIOT.

## Next Steps

- [ ] 1 week of paper trading data collection
- [ ] Compare performance vs buy-and-hold
- [ ] Analyze win rate by signal type

## State Persistence

The paper trading engine maintains persistent state in `state.json`.

## Links

- [Shadow Test Results](../../archived/successful/EXP-2025-008-llm-sanity-check/)
- [LLM Sanity Checker Code](../../../src/llm/sanity_checker.py)