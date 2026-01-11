# EXP-2025-003: Multi-Ticker Test with Lowered Thresholds

**Status:** Completed
**Created:** 2025-01-11
**Completed:** 2025-01-11
**Tags:** multi-ticker, thresholds, trade-frequency

---

## Hypothesis

Lowering entry thresholds will increase trade frequency while maintaining risk-adjusted returns (Sharpe ratio).

---

## Changes Made

### 1. Lowered Entry Thresholds

| Parameter | Before | After | Rationale |
|-----------|--------|-------|-----------|
| `SENTIMENT_ENTRY` | 0.2 | 0.0 | Enter long even with neutral sentiment |
| `SENTIMENT_EXIT` | -0.3 | -0.5 | Wider exit range |
| `SENTIMENT_SHORT` | -0.8 | -0.3 | Easier to enter short |
| `SENTIMENT_COVER` | 0.3 | 0.0 | Easier to cover |
| `SUPPORT_THRESHOLD` | 0.02 | 0.03 | Wider buy zone |
| `RESISTANCE_THRESHOLD` | 0.02 | 0.03 | Wider sell zone |

### 2. Real Data Fetched

| Ticker | Period | Price Range |
|--------|--------|-------------|
| NVDA | 2023 | $14.25 - $50.38 |
| AAPL | 2023 | $123.16 - $196.26 |
| SPY | 2023 | $364.68 - $465.19 |

---

## Results

### Summary Table

| Strategy | Return % | Sharpe | Max DD % | Trades |
|----------|----------|--------|----------|--------|
| **NVDA Adaptive** | 93.95 | **1.83** | -9.26 | 24 |
| NVDA Buy&Hold | 230.85 | 1.42 | -18.00 | 1 |
| **AAPL Adaptive** | 33.30 | **2.10** | -8.24 | 14 |
| AAPL Buy&Hold | 49.90 | 1.75 | -14.34 | 1 |
| **SPY Adaptive** | 12.85 | 1.52 | -5.60 | 8 |
| SPY Buy&Hold | 24.31 | 1.63 | -9.29 | 1 |

### Key Findings

1. **Trade frequency improved**: Average 15.3 trades/ticker (up from 6)
2. **Better risk-adjusted returns**: Sharpe > Buy&Hold in 2/3 tickers
3. **Lower drawdown**: Max DD consistently lower than Buy&Hold
4. **Still underperforms on absolute return**: Especially NVDA (93% vs 230%)

### Analysis

| Metric | Result | Assessment |
|--------|--------|------------|
| Avg Trades | 15.3 | [OK] Above minimum of 10-20 |
| Avg Sharpe | 1.82 | [GOOD] Above 1.5 target |
| vs Buy&Hold Sharpe | 2/3 wins | [GOOD] Risk-adjusted outperformance |
| vs Buy&Hold Return | 0/3 wins | [WARNING] Lower absolute returns |

---

## Decision

- [x] **Threshold adjustment successful** - More trades, better Sharpe
- [ ] **Absolute return still lags** - Strategy too defensive for strong bull markets
- [ ] **Needs more testing** - Only 1 year of data (2023)

---

## Insights

### Why Lower Sharpe on SPY?

SPY (S&P 500 ETF) had the lowest trade frequency (8 trades). The mean reversion logic may not work as well on index ETFs which trend more smoothly.

### Why NVDA Underperformed on Return?

NVDA had a massive rally in 2023 (+230%). The strategy's stop-loss and conservative sizing caused it to exit too early, missing the bulk of the rally.

**This is expected** - the strategy prioritizes risk management (lower drawdown) over capturing 100% of upside moves.

---

## Next Steps

1. [ ] Test on bear market data (2022) to validate defensive mode
2. [ ] Test on more tickers (TSLA, MSFT, GOOGL)
3. [ ] Consider momentum filter for strong trending markets
4. [ ] Walk-forward optimization on multiple years

---

## Conclusion

The lowered thresholds successfully increased trade frequency while maintaining good risk-adjusted returns. The strategy shows promise as a **conservative, risk-managed approach** rather than a high-return momentum strategy.

**This is acceptable** - for a $350 starting account, preserving capital (lower drawdown) is more important than maximizing returns.
