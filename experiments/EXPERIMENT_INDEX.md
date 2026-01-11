# Experiment Index

> **Purpose:** Master index of all experiments conducted in this project
> **Last Updated:** 2025-01-11

---

## Quick Stats

| Metric | Count |
|--------|-------|
| Total Experiments | 7 |
| Successful | 4 |
| Failed | 1 |
| Partial | 1 |
| Active | 4 |
| Completed | 3 |

---

## All Experiments

## EXP-2025-001: Fix Look-Ahead Bias in Sentiment Generation

- **Date:** 2025-01-11
- **Hypothesis:** Fixing look-ahead bias by using lagged sentiment will provide realistic baseline performance
- **Result:** Sharpe 2.03 (shifted) vs 1.88 (biased), Return 17.15% vs 16.15%
- **Outcome:** Success
- **Key Learning:** Look-ahead bias confirmed (0.78 correlation); fix improved performance
- **Link:** [./completed/EXP-2025-001-fix-look-ahead-bias/](./completed/EXP-2025-001-fix-look-ahead-bias/)

## EXP-2025-002: Critical Fixes from Review

- **Date:** 2025-01-11
- **Hypothesis:** Applying critical fixes (stop-loss, validation, bias fix) will make strategy safer
- **Result:** All fixes applied to codebase
- **Outcome:** Success
- **Key Learning:** Code now has 20% stop-loss, data validation, and lagged sentiment
- **Link:** [./completed/EXP-2025-002-critical-fixes/](./completed/EXP-2025-002-critical-fixes/)

## EXP-2025-003: Multi-Ticker Test with Lowered Thresholds

- **Date:** 2025-01-11
- **Hypothesis:** Lowering entry thresholds will increase trade frequency while maintaining risk-adjusted returns
- **Result:** Avg 15.3 trades/ticker, Avg Sharpe 1.82 (vs 1.60 for B&H)
- **Outcome:** Success
- **Key Learning:** Lowered thresholds improved trade frequency and Sharpe ratio
- **Link:** [./active/EXP-2025-003-multi-ticker-test/](./active/EXP-2025-003-multi-ticker-test/)

## EXP-2025-004: Bear Market 2022 Test

- **Date:** 2025-01-11
- **Hypothesis:** Adaptive strategy will outperform Buy&Hold in bear market by protecting capital
- **Result:** Avg +13.13% vs -30.80% for B&H (+43.93% outperformance!)
- **Outcome:** Success
- **Key Learning:** Strategy CRUSHES in bear markets - positive returns while market crashes
- **Link:** [./active/EXP-2025-004-bear-market-2022/](./active/EXP-2025-004-bear-market-2022/)

## EXP-2025-005: Real News Sentiment Analysis

- **Date:** 2025-01-11
- **Hypothesis:** LLM-analyzed sentiment will provide uncorrelated signals that improve Sharpe ratio
- **Result:** LLM -15.05% vs Heuristic -9.52% vs B&H +229%; Correlation 0.152 (uncorrelated)
- **Outcome:** Partial
- **Key Learning:** LLM provides uncorrelated signals but underperforms; weekly sampling creates lag
- **Link:** [./active/EXP-2025-005-real-news-sentiment/](./active/EXP-2025-005-real-news-sentiment/)

## EXP-2025-006: Bull Market Optimization (ADX + Trailing Stop)

- **Date:** 2025-01-11
- **Hypothesis:** ADX trend filter + 5% trailing stop will improve bull market returns
- **Result:** Optimized -20.46% vs Original -9.52% (WORSE!); Trades dropped 60%
- **Outcome:** Failed
- **Key Learning:** Trailing stop too tight for volatile stocks; skipping mean reversion reduced opportunities
- **Link:** [./archived/failed/EXP-2025-006-bull-market-optimization/](./archived/failed/EXP-2025-006-bull-market-optimization/)

## EXP-2025-007: Value Investing Strategy

- **Date:** 2025-01-11
- **Hypothesis:** Fundamental value strategy will generate alpha vs benchmark
- **Result:** +2.62% vs +42.76% benchmark (2023 - underperformed in growth market)
- **Outcome:** Active (Testing phase)
- **Key Learning:** Value underperforms in strong bull markets (expected); needs longer timeframe validation
- **Link:** [./active/EXP-2025-007-value-investing/](./active/EXP-2025-007-value-investing/)

---

## Template for New Entries

```markdown
## EXP-YYYY-NNN: [Title]

- **Date:** YYYY-MM-DD
- **Hypothesis:** [One-line summary]
- **Result:** Sharpe: X.XX, CAGR: XX%, MaxDD: XX%
- **Outcome:** [Success/Failed/Partial]
- **Key Learning:** [One sentence]
- **Link:** [./archived/.../EXP-YYYY-NNN/](./archived/.../EXP-YYYY-NNN/)
```

---

## Categories

### Momentum Strategies
*Experiments focused on trend-following and momentum signals*
- None yet

### Mean Reversion Strategies
*Experiments focused on counter-trend and mean reversion signals*
- EXP-2025-001: Mean reversion tested in sideways regime

### Regime-Based Strategies
*Experiments using market regime detection (VIX, volatility, etc.)*
- EXP-2025-001: VIX-based regime classification with AI signals

### Hybrid Strategies
*Experiments combining multiple approaches*
- None yet

### Risk Management Tests
*Experiments focused on stop-loss, position sizing, etc.*
- None yet

### Data Pipeline Tests
*Experiments testing data sources, bias detection, etc.*
- EXP-2025-001: Look-ahead bias detection and fix
- EXP-2025-005: LLM sentiment integration via DeepSeek API

---

## Search Tags

| Tag | Description | Experiments |
|-----|-------------|-------------|
| `nvda` | NVIDIA-specific tests | EXP-2025-005 |
| `spy` | S&P 500 tests | EXP-2025-001 |
| `vix` | VIX-based strategies | EXP-2025-001 |
| `sentiment` | Sentiment-based strategies | EXP-2025-001, EXP-2025-005 |
| `llm` | LLM/DeepSeek integration | EXP-2025-005 |
| `look-ahead-fix` | Bias fixing experiments | EXP-2025-001 |
| `stop-loss` | Risk management tests | |
| `walk-forward` | Walk-forward optimization | |

---

## Quick Reference

### Best Performing Experiments
1. EXP-2025-001: Sharpe 2.03, Return 17.15% (shifted sentiment)

### Most Informative Failures
- EXP-2025-006: Trailing stop + ADX filter made performance WORSE (important negative result)

### Experiments to Revisit
- EXP-2025-005: Test LLM sentiment in bear/sideways markets (may perform better)
- ~~EXP-2025-006~~: DO NOT revisit - approach proven ineffective
