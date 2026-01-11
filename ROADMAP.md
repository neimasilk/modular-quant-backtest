# Modular Quant Backtest - Project Roadmap

> **Status:** Prototype / Experimental Phase
> **Last Updated:** 2025-01-11
> **Nature:** Iterative experimentation with frequent failures and successes

---

## Overview

This is an **experimental quantitative trading project** using AI for market regime detection and stock sentiment analysis. The project nature means:
- Experiments will fail frequently
- Successful approaches may be forgotten without proper tracking
- Iterations are rapid and continuous
- Documentation is critical for knowledge preservation

---

## Current Status (Phase 0)

### Completed
- [x] Basic backtest engine with modular architecture
- [x] Adaptive strategy with AI regime detection
- [x] Data pipeline from Yahoo Finance
- [x] DeepSeek API integration for AI signals
- [x] Basic documentation (README.md)

### Known Critical Issues (from review.md)
- [ ] **Look-ahead bias in sentiment generation** - Uses `Daily_Return` to create sentiment
- [ ] **No fundamental data** - Claims "Value Investing" but code is 100% technical
- [ ] **No stop-loss mechanism** - Risk management is naive
- [ ] **No real news sentiment** - AI only sees VIX, not actual news/earnings
- [ ] **No experiment tracking** - Results are lost after each run

---

## Phase 1: Fix Critical Foundation Issues (Priority: CRITICAL)

> **Goal:** Make backtest results valid and trustworthy

### 1.1 Eliminate Look-Ahead Bias
- [x] Remove `add_ai_stock_sentiment()` that uses `Daily_Return`
- [x] Implement true lagged sentiment (news must come BEFORE price action)
- [x] Add temporal validation to prevent future data leakage
- [x] Document all data dependencies and timing

### 1.2 Implement Real Sentiment Analysis
- [ ] Integrate NewsAPI or Yahoo Finance news scraper
- [ ] Send actual headlines to DeepSeek for sentiment scoring
- [ ] Store sentiment with proper timestamps
- [ ] Add sentiment decay logic (old news matters less)

### 1.3 Add Risk Management
- [ ] Implement hard stop-loss (configurable, e.g., -15%)
- [ ] Add position sizing based on volatility
- [ ] Implement maximum drawdown limit
- [ ] Add per-trade and portfolio-level risk controls

### 1.4 Fundamental Data Integration (Optional, for "Value Investing" claim)
- [ ] Fetch PE, PBV, Debt/Equity via `yfinance`
- [ ] Add fundamental filters to strategy
- [ ] Create fundamental scoring system

**Estimated Work:** 2-3 weeks
**Success Criteria:** Backtest results are reproducible and bias-free

---

## Phase 2: Experiment Tracking System (Priority: HIGH)

> **Goal:** Ensure no successful experiment is ever lost

### 2.1 Directory Structure
```
experiments/
├── active/              # Current experiments
├── completed/           # Finished experiments
├── archived/            # Old experiments (compressed)
└── templates/           # Experiment templates
```

### 2.2 Experiment Template
Each experiment must have:
- [ ] Unique ID (e.g., `EXP-2025-001`)
- [ ] Hypothesis statement
- [ ] Parameter configuration
- [ ] Results CSV/JSON
- [ ] Conclusions (what worked, what didn't)
- [ ] Next steps

### 2.3 Automation (Optional)
- [ ] MLflow or Weights & Biases integration
- [ ] Auto-generated experiment reports
- [ ] Comparison dashboard

**Estimated Work:** 1 week
**Success Criteria:** Any experiment from 6 months ago can be reproduced

---

## Phase 3: Strategy Development Pipeline (Priority: MEDIUM)

> **Goal:** Systematic approach to developing and testing strategies

### 3.1 Development Workflow
```
Idea → Hypothesis → Experiment → Analysis → Decision
                                      ↓
                                 Archive or Iterate
```

### 3.2 Strategy Categories
- [ ] **Regime-Based** (current: VIX + trend)
- [ ] **Mean Reversion** (RSI, Bollinger Bands)
- [ ] **Momentum** (breakout, relative strength)
- [ ] **Hybrid** (combination of above)

### 3.3 Validation Framework
- [ ] Train/validation/test split (time-based)
- [ ] Walk-forward optimization
- [ ] Out-of-sample testing
- [ ] Stress testing (crash scenarios)

**Estimated Work:** 2 weeks
**Success Criteria:** Clear decision framework for each strategy

---

## Phase 4: Live Trading Preparation (Priority: LOW)

> **Goal:** Prepare for IBKR paper trading first, then live

### Prerequisites (Must Complete Phases 1-3 First)
- [ ] All Phase 1 issues resolved
- [ ] Minimum 6 months of walk-forward validation
- [ ] Sharpe Ratio > 1.0 on out-of-sample data
- [ ] Maximum drawdown < 25%
- [ ] Paper trading for 3+ months

### IBKR Integration
- [ ] IBKR API setup and testing
- [ ] Paper trading account connection
- [ ] Order execution logic
- [ ] Error handling and recovery
- [ ] Monitoring and alerts

**Estimated Work:** 3-4 weeks
**Success Criteria:** Profitable paper trading for 3+ months

---

## Phase 5: Production & Monitoring (Future)

> **Goal:** Sustainable live trading with proper monitoring

### Production Checklist
- [ ] Live trading with small position sizes
- [ ] Daily P&L monitoring
- [ ] Automated alerts for anomalies
- [ ] Monthly performance reviews
- [ ] Strategy degradation detection

### Risk Controls
- [ ] Daily loss limits
- [ ] Monthly loss limits
- [ ] Circuit breakers
- [ ] Manual override capability

---

## Experiment Workflow (See EXPERIMENT_WORKFLOW.md)

For day-to-day experimentation, follow the workflow in `EXPERIMENT_WORKFLOW.md`.

---

## Decision Matrix

| Scenario | Action |
|----------|--------|
| Backtest Sharpe < 0.5 | Reject strategy, archive experiment |
| Look-ahead bias found | Immediately halt, fix data pipeline |
| Strategy works on one stock only | Archive as "single-stock special case" |
| Strategy works on 3+ stocks | Promote to "candidate", test on more data |
| Out-of-sample Sharpe > 1.0 | Promote to "production candidate" |
| Paper trading profitable > 3 months | Consider live trading |

---

## Key Principles

1. **No trust without validation** - Every claim must be backtested on out-of-sample data
2. **Document everything** - If it's not written down, it doesn't exist
3. **Fail fast, learn faster** - Failed experiments are valuable data points
4. **Bias prevention** - Look-ahead bias destroys everything
5. **Small is beautiful** - Start simple, add complexity only if needed

---

## Next Immediate Actions (This Week)

1. [x] Read and understand the review.md completely
2. [x] Create `experiments/` directory structure
3. [x] Set up first experiment template
4. [x] Fix the look-ahead bias in `data_miner.py`
5. [x] Document the fix as `EXP-2025-001`

---

## Resources

- **Internal:** README.md, review.md, PROPOSAL_AI_TRADING_BOT_v2.md
- **External:** DeepSeek API, Yahoo Finance, IBKR API docs
- **Learning:** "Advances in Financial Machine Learning" by Marcos Lopez de Prado
