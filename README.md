# Modular Quantitative Backtesting Framework

> **Status:** Active Development (v1.0)
> **Last Updated:** 2025-01-11

Framework backtesting modular untuk strategi trading kuantitatif dengan dua family strategi:

1. **Adaptive Strategy (FROZEN)** - Technical, regime-based, defensive
2. **Value Investing Strategy (ACTIVE)** - Fundamental, long-term

---

## Quick Stats

| Strategy | Type | Status | Best For |
|----------|------|--------|----------|
| Adaptive (FROZEN) | Technical | Production-ready | Bear markets, volatile conditions |
| Value Investing | Fundamental | Testing | Long-term, 5-10 year horizon |

---

## Strategies

### 1. Adaptive Strategy (FROZEN)

**Location:** `src/strategies/adaptive_strategy.py`

**Type:** Technical, regime-based, defensive

**Key Results (2022 Bear Market):**
- Portfolio: **+13.1%** vs Buy&Hold **-30.8%**
- **+43.9% outperformance!**
- Max DD: 9.70% vs 36.28% B&H

**Identity:** Capital preservation strategy
- Protects in bear markets
- Underperforms in mega-bull markets (by design)
- See: `docs/FROZEN_STRATEGY.md`

### 2. Value Investing Strategy (ACTIVE)

**Location:** `src/strategies/value_investing_strategy.py`

**Type:** Fundamental, bottom-up, long-term

**Key Results (2023 Initial Test):**
- Portfolio: **+2.62%** vs Benchmark **+42.76%**
- Underperformed in growth market (expected)
- See: `experiments/active/EXP-2025-007-value-investing/`

---

## Project Structure

```
modular-quant-backtest/
├── main.py                           # Entry point
├── data_miner.py                     # ETL Pipeline
├── requirements.txt
├── .env.example
│
├── docs/                             # Documentation
│   ├── FROZEN_STRATEGY.md            # Adaptive strategy docs
│   └── VALUE_INVESTING_ROADMAP.md    # Value strategy plan
│
├── src/
│   ├── data/
│   │   ├── data_generator.py
│   │   └── fundamental_fetcher.py   # NEW: Fundamental data
│   ├── strategies/
│   │   ├── adaptive_strategy.py      # FROZEN: Technical strategy
│   │   ├── regime_threshold.py
│   │   ├── aggressive_mode.py
│   │   ├── defensive_mode.py
│   │   ├── mean_reversion_mode.py
│   │   ├── bull_optimized_strategy.py # FAILED: Do not use
│   │   └── value_investing_strategy.py # NEW: Value strategy
│   └── engines/
│       └── backtest_engine.py
│
├── experiments/                      # Experiment tracking
│   ├── EXPERIMENT_INDEX.md
│   ├── LESSONS_LEARNED.md
│   ├── completed/
│   │   ├── EXP-2025-001-fix-look-ahead-bias/
│   │   └── EXP-2025-002-critical-fixes/
│   ├── active/
│   │   ├── EXP-2025-003-multi-ticker-test/
│   │   ├── EXP-2025-004-bear-market-2022/
│   │   ├── EXP-2025-005-real-news-sentiment/
│   │   └── EXP-2025-007-value-investing/
│   └── archived/
│       └── failed/
│           └── EXP-2025-006-bull-market-optimization/
│
├── data/                             # Generated data files
└── output/                           # Backtest results
```

---

## Installation

```bash
git clone https://github.com/neimasilk/modular-quant-backtest.git
cd modular-quant-backtest
pip install -r requirements.txt
```

---

## Usage

### Adaptive Strategy (FROZEN)

```python
from backtesting import Backtest
from src.strategies.adaptive_strategy import AdaptiveStrategy
import pandas as pd
import yfinance as yf

# Fetch data
df = yf.download('NVDA', start='2022-01-01', end='2023-01-01')
df['AI_Regime_Score'] = ...  # Your regime score
df['AI_Stock_Sentiment'] = ...  # Your sentiment signal

# Run backtest
bt = Backtest(df, AdaptiveStrategy, cash=100_000, commission=0.001)
stats = bt.run()
print(stats)
```

### Value Investing Strategy

```python
from src.data.fundamental_fetcher import FundamentalDataFetcher, ValueScreener
from src.strategies.value_investing_strategy import ValueBacktester

# Define universe
universe = ['AAPL', 'MSFT', 'GOOGL', 'JPM', 'JNJ', 'BRK-B', ...]

# Run value backtest
backtester = ValueBacktester(
    universe=universe,
    start_date='2020-01-01',
    end_date='2024-01-01',
    initial_cash=100_000
)
results = backtester.run()
```

---

## Experiment Summary

| EXP | Title | Result | Status |
|-----|-------|--------|--------|
| 001 | Look-Ahead Bias Fix | Sharpe 2.03 vs 1.88 | ✅ Success |
| 002 | Critical Fixes | Stop-loss, validation | ✅ Success |
| 003 | Multi-Ticker Test | Avg Sharpe 1.82 | ✅ Success |
| 004 | Bear Market 2022 | **+44% outperformance** | ✅ Success |
| 005 | LLM News Sentiment | Underperformed | ⚠️ Partial |
| 006 | Bull Market Optimization | Made performance worse | ❌ Failed |
| 007 | Value Investing | Testing | 🔄 Active |

---

## Key Learnings

1. **Adaptive Strategy CRUSHES bear markets** - Proven 44% outperformance
2. **Trailing stop approach is DEAD** - EXP-006 proved this hurts performance
3. **LLM sentiment needs real news** - Price-based sentiment is insufficient
4. **Value investing needs long timeframe** - 2023 test showed expected underperformance

---

## Next Sessions

1. **Value Investing** - Test longer timeframe (2018-2024)
2. **Value vs Bear Market** - Validate outperformance in downturns
3. **Paper Trading** - When strategies are validated

---

## License

MIT License

---

## Author

Built with Claude Code (Anthropic)
