# Experiment Index

> **Purpose:** Master index of all experiments conducted in this project
> **Last Updated:** 2025-01-11

---

## Quick Stats

| Metric | Count |
|--------|-------|
| Total Experiments | 3 |
| Successful | 3 |
| Failed | 0 |
| Partial | 0 |
| Active | 2 |
| Completed | 1 |

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

---

## Search Tags

| Tag | Description | Experiments |
|-----|-------------|-------------|
| `nvda` | NVIDIA-specific tests | (actually S&P 500 data) |
| `spy` | S&P 500 tests | EXP-2025-001 |
| `vix` | VIX-based strategies | EXP-2025-001 |
| `sentiment` | Sentiment-based strategies | EXP-2025-001 |
| `look-ahead-fix` | Bias fixing experiments | EXP-2025-001 |
| `stop-loss` | Risk management tests | |
| `walk-forward` | Walk-forward optimization | |

---

## Quick Reference

### Best Performing Experiments
1. EXP-2025-001: Sharpe 2.03, Return 17.15% (shifted sentiment)

### Most Informative Failures
None yet - keep experimenting!

### Experiments to Revisit
- EXP-2025-001: Need to test with real news sentiment
