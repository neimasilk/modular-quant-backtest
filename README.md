# Modular Quantitative Backtesting Framework

> **Status:** Active Development (v1.0)
> **Last Updated:** 2026-01-15

Framework backtesting modular untuk strategi trading kuantitatif dengan dua family strategi:

1. **Adaptive Strategy (FROZEN)** - Technical, regime-based, defensive
2. **Hybrid LLM Strategy (READY FOR TESTING)** - Adaptive + LLM filter, proven in backtest

---

## Quick Stats

| Strategy | Type | Status | Best For |
|----------|------|--------|----------|
| Adaptive (FROZEN) | Technical | Production-ready | Bear markets, volatile conditions |
| Hybrid LLM (EXP-009) | Hybrid AI | Backtest complete ✅ | Risk management, drawdown reduction |

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

### 2. Hybrid LLM Strategy - EXP-2025-009 ✅

**Location:** `src/strategies/hybrid_llm_strategy.py`

**Type:** Hybrid (Adaptive Strategy + LLM Filter)

**Focus:** Risk Management & Drawdown Reduction

**Backtest Results (NVDA 2022-2023):**
- **Bull Market (2023):** +7.3% return improvement, +47.9% Sharpe improvement
- **Bear Market (2022):** +2.7% return improvement, +12.6% Sharpe improvement
- **Drawdown Reduction:** -24% (bull), -2.5% (bear)

**How it Works:**
1. Adaptive Strategy generates baseline signal
2. If price moves >3%, LLM validates news substance
3. LLM can VETO bad trades or OVERRIDE to catch opportunities
4. Final signal = Adaptive + LLM filter

**Next Phase:** Shadow trading → Paper trading → Real capital test

**See:** `experiments/active/EXP-2025-009-hybrid-llm/`

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
│   └── FROZEN_STRATEGY.md            # Adaptive strategy docs
│
├── src/
│   ├── llm/
│   │   └── sanity_checker.py         # LLM "Bullshit Detector"
│   ├── data/
│   │   ├── data_generator.py
│   │   ├── news_fetcher.py           # News fetcher
│   │   └── fundamental_fetcher.py    # Value investing data (frozen)
│   ├── strategies/
│   │   ├── adaptive_strategy.py      # FROZEN: Technical strategy
│   │   ├── hybrid_llm_strategy.py    # NEW: Adaptive + LLM filter
│   │   ├── regime_threshold.py
│   │   ├── aggressive_mode.py
│   │   ├── defensive_mode.py
│   │   ├── mean_reversion_mode.py
│   │   ├── bull_optimized_strategy.py # FAILED: Do not use
│   │   └── value_investing_strategy.py # Frozen: Value strategy
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
│   │   ├── EXP-2025-008-llm-sanity-check/
│   │   └── EXP-2025-009-hybrid-llm/        # Phase 1 COMPLETE
│   └── archived/
│       ├── failed/
│       │   └── EXP-2025-006-bull-market-optimization/
│       └── partial/
│           └── EXP-2025-007-value-investing/  # Frozen
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
| 007 | Value Investing | Testing | ❄️ Frozen |
| 008 | LLM Sanity Check | Shadow test complete | ⚠️ Partial |
| 009 | Hybrid LLM Strategy | **+7.3% return, +47.9% Sharpe** | ✅ Backtest Success |

---

## Key Learnings

1. **Adaptive Strategy CRUSHES bear markets** - Proven 44% outperformance (EXP-004)
2. **Trailing stop approach is DEAD** - EXP-006 proved this hurts performance
3. **LLM sentiment needs real news** - EXP-005 underperformed with price-based sentiment
4. **LLM as filter > LLM as predictor** - EXP-009 shows LLM adds value when filtering technical signals, not predicting
5. **LLM override > LLM veto** - Contrarian dip buying and momentum following more valuable than preventing FOMO

---

## Next Steps

1. **Shadow Trading (EXP-009)** - Validate real LLM accuracy >65% before paper trading
2. **Earnings Call Analysis** - Implement Strategy 2 from LLM roadmap (high edge potential)
3. **Paper Trading** - When shadow trading validates LLM accuracy
4. **Multi-Signal Portfolio** - Combine Adaptive + LLM + Earnings for robust trading system

**Current Focus:** Implementing Earnings Call Sentiment Analysis (see `docs/LLM_EDGE_ROADMAP.md`)

---

## License

MIT License

---

## Author

Built with Claude Code (Anthropic)
