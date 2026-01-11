# AI Trading Bot - Project Proposal

> **Version:** 3.0 (Updated based on experiment findings)
> **Status:** Experimental Prototype
> **Last Updated:** 2025-01-11

---

## Executive Summary

This is an **experimental quantitative trading project** using AI for market regime detection. After initial testing and bias correction, we have a working prototype with realistic performance expectations.

**Key Changes from v2.0:**
- Removed "Value Investing" claims (strategy is technical/regime-based)
- Fixed look-ahead bias in backtesting
- Set realistic performance expectations
- Added proper experiment tracking

---

## Project Overview

### Concept
AI-driven trading strategy that adapts based on market regime (Bullish/Bearish/Sideways) detected through VIX analysis and AI-assisted sentiment classification.

### Tech Stack
| Component | Tool |
|-----------|------|
| Language | Python 3.10+ |
| Backtesting | `backtesting` library |
| Data Source | Yahoo Finance (`yfinance`) |
| AI Integration | DeepSeek API |
| Broker | IBKR (future) |

### Current Status
- [x] Basic backtest framework
- [x] Regime-based strategy
- [x] Look-ahead bias fix (EXP-2025-002)
- [x] Hard stop-loss mechanism (20%)
- [x] Data validation
- [ ] Real news sentiment
- [ ] Paper trading
- [ ] Live trading

---

## Strategy Description

### What It Actually Does (Honest Description)

**Type:** Technical / Regime-Based Swing Trading

**NOT Value Investing** - This strategy does NOT analyze:
- Financial statements
- PE/PBV ratios
- Management quality
- Competitive moats

**What it DOES analyze:**
1. **VIX levels** - Market volatility regime
2. **Price momentum** - Trend direction
3. **Support/Resistance** - Mean reversion levels
4. **AI Regime Score** - DeepSeek classification based on VIX + price change

### Strategy Matrix

| Regime | Condition | Strategy | Position Size |
|--------|-----------|----------|---------------|
| Bullish | AI_Regime > 0.5 | Aggressive long | 95% |
| Bearish | AI_Regime < -0.5 | Defensive/Short | 50% |
| Sideways | -0.5 <= AI_Regime <= 0.5 | Mean reversion | 60% |

---

## Performance Expectations (Realistic)

### EXP-2025-001 Results (S&P 500, 2023)

| Metric | Strategy | Buy & Hold |
|--------|----------|------------|
| Return | 17.15% | 22.23% |
| Sharpe Ratio | 2.03 | 1.51 |
| Max Drawdown | -4.49% | -9.60% |
| Trades | 6 | 1 (buy) |

**Key Findings:**
- Better risk-adjusted returns (Sharpe)
- Lower maximum drawdown
- Lower absolute return than B&H
- Very low trade frequency (6/year)

### Realistic Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Sharpe Ratio | > 1.0 | Above market average |
| Max Drawdown | < 20% | Risk management |
| CAGR | 10-20% | Market-like or slightly better |
| Trade Frequency | 20-50/year | Need to increase |

---

## Capital & Costs

### Initial Capital
| Item | Amount | Notes |
|------|--------|-------|
| Starting Capital | $350 | Minimal viable amount |
| DCA | $100/month | Regular contributions |

### Cost Structure
| Item | Cost | Impact |
|------|------|--------|
| IBKR Commission | ~$1/trade | High impact on small account |
| API Costs | ~$5-10/month | DeepSeek API |
| Data Feed | Varies | IBKR data requirements |

**Note:** Trading costs are significant for small accounts. At $350 starting capital, $10 commission = 2.86% of portfolio.

---

## Roadmap

### Phase 1: Foundation (Current)
- [x] Fix look-ahead bias
- [x] Implement experiment tracking
- [x] Document realistic baseline
- [ ] Add stop-loss mechanism
- [ ] Increase trade frequency

### Phase 2: Enhancement
- [ ] Real news sentiment (NewsAPI/Alpha Vantage)
- [ ] Multi-ticker testing
- [ ] Walk-forward optimization
- [ ] Parameter tuning

### Phase 3: Validation
- [ ] Paper trading (3+ months)
- [ ] Out-of-sample testing
- [ ] Stress testing

### Phase 4: Production (Future)
- [ ] Live trading with small size
- [ ] Performance monitoring
- [ ] Strategy iteration

---

## Known Issues & Risks

### Fixed Issues (EXP-2025-002)
1. [x] **Look-ahead bias** - Fixed with `.shift(1)` on sentiment
2. [x] **No stop-loss** - Added 20% hard stop + 5% trailing stop
3. [x] **No data validation** - Added price range validation

### Remaining Issues
1. **Low Trade Frequency** - Only 6 trades/year, not statistically significant
2. **Fake Sentiment** - Current sentiment is heuristic, not from real news
3. **No Fundamental Analysis** - Purely technical (acknowledged in v3.0)

### Market Risks
- **Black Swan Events** - Strategy not tested in crash conditions
- **Regime Change** - Market structure may evolve
- **Overfitting** - Parameters tuned to specific time period

### Technical Risks
- **API Failures** - DeepSeek downtime
- **Data Errors** - Yahoo Finance data issues
- **Execution Risk** - Slippage not fully modeled

---

## Experiment Tracking

All experiments are tracked in `/experiments/` directory:

- **EXP-2025-001:** Look-ahead bias fix (Completed)
- **EXP-2025-002:** Multi-ticker validation (Pending)
- **EXP-2025-003:** Real news sentiment (Pending)

See `ROADMAP.md` and `EXPERIMENT_WORKFLOW.md` for details.

---

## Success Criteria

### Minimum Viable Strategy
- [ ] Sharpe Ratio > 1.0 on out-of-sample data
- [ ] Max Drawdown < 25%
- [ ] 20+ trades/year
- [ ] 3+ months profitable paper trading

### Stretch Goals
- [ ] Sharpe Ratio > 1.5
- [ ] Beat Buy & Hold on risk-adjusted basis
- [ ] Consistent performance across 3+ tickers

---

## Next Actions

1. [x] ~~Implement stop-loss mechanism~~ (Done: 20% hard stop)
2. [ ] Lower entry thresholds to increase trade frequency
3. [ ] Fetch actual NVDA data (currently using S&P 500)
4. [ ] Evaluate real news sentiment APIs
5. [ ] Test on multiple tickers (AAPL, SPY, TSLA)

---

## References

- **Code:** https://github.com/neimasilk/modular-quant-backtest
- **Documentation:** README.md, ROADMAP.md, EXPERIMENT_WORKFLOW.md
- **Experiments:** experiments/EXPERIMENT_INDEX.md

---

## Appendix: What Changed from v2.0

| v2.0 Claim | v3.0 Reality |
|------------|--------------|
| "Value Investing" | Technical/Regime-based trading |
| Sharpe 1.79, Return +174% | Sharpe 2.03, Return 17% (single year) |
| "Warren Buffett style" | Swing trading with AI signals |
| No testing for bias | Bias confirmed and fixed |
| No experiment tracking | Full experiment system in place |

**Why the changes?**
- Initial backtest had look-ahead bias
- Claims didn't match actual implementation
- Unrealistic performance expectations
- Lack of proper validation

This version is honest about what the strategy does and what it can realistically achieve.
