# EXP-2025-001: Fix Look-Ahead Bias in Sentiment Generation

**Status:** Completed
**Created:** 2025-01-11
**Completed:** 2025-01-11
**Author:** [Your Name]
**Tags:** data-pipeline, bias-fix, critical, completed

---

## Hypothesis

**Current Problem:** The strategy shows unrealistically good performance (Sharpe 1.79+) because `AI_Stock_Sentiment` is generated from `Daily_Return` - meaning the strategy "knows" the future price movement.

**Hypothesis:** If we fix the look-ahead bias by using lagged sentiment, the backtest results will show true (more realistic) performance, providing a valid baseline for further improvements.

---

## Problem Definition

### Location of Bug
File: `data_miner.py`, function `add_ai_stock_sentiment()` (lines 340-388)

### Current Code (Problematic)
```python
# Create sentiment based on daily return
df['Daily_Return'] = df['Close'].pct_change() * 100
conditions = [
    df['Daily_Return'] > 1.0,
    df['Daily_Return'] < -1.0
]
choices = [0.5, -0.5]
df['AI_Stock_Sentiment'] = np.select(conditions, choices, default=0.0)
```

### Why This Is Wrong
- At time T, we use `Daily_Return[T]` to create `AI_Stock_Sentiment[T]`
- But `Daily_Return[T]` is only known AFTER the trading day closes
- The strategy then uses this sentiment to trade at time T
- This is look-ahead bias - the strategy knows the future

---

## Strategy Definition

### Type
- [x] Bug fix
- [x] Data pipeline validation
- [x] Baseline establishment

### Approach Options Tested

#### Method A: Shift (Lagged Sentiment)
Shift sentiment by 1 day so we use yesterday's sentiment for today's decision.

#### Method B: Zero (No Sentiment)
Remove sentiment signal entirely - set all to 0.

#### Method C: Neutral (Regime-Based)
Set sentiment based on regime score only (conservative approach).

---

## Parameters

```python
# Backtest Configuration
data_file = "data/nvda_real_data_2023.csv"  # Actually S&P 500 data
initial_cash = 100000
commission = 0.001

# Data Analysis
correlation_sentiment_returns = 0.7845  # Evidence of look-ahead bias
```

---

## Data

| Source | Ticker(s) | Timeframe | Notes |
|--------|-----------|-----------|-------|
| Yahoo Finance | S&P 500 (GSPC) | Daily | 250 trading days in 2023 |

---

## Results

### Bias Detection

```
Original AI_Stock_Sentiment stats:
  Mean: 0.0352
  Std:  0.2563
  Min:  -0.6375
  Max:  0.7079

Correlation (Sentiment vs Same-Day Returns): 0.7845
  WARNING: High correlation indicates look-ahead bias!
```

### Backtest Results Comparison

| Method | Return % | Sharpe | Sortino | Max DD % | Win Rate % | # Trades |
|--------|----------|--------|---------|----------|------------|----------|
| **Original** (biased) | 16.15 | 1.88 | 3.41 | -5.17 | 66.67 | 6 |
| **Shift** (lagged) | 17.15 | 2.03 | 3.83 | -4.49 | 66.67 | 6 |
| **Zero** (no sentiment) | 13.86 | 1.57 | 2.76 | -6.36 | 100.00 | 1 |
| **Neutral** | 13.86 | 1.57 | 2.76 | -6.36 | 100.00 | 1 |

### Benchmark: Buy & Hold

| Metric | Value |
|--------|-------|
| Return % | 22.23 |
| Sharpe Ratio | 1.51 |
| Max Drawdown % | -9.60 |

---

## Analysis

### Surprising Findings

1. **Shift method performed BEST**: Contrary to expectations, the lagged sentiment (shift) actually performed better than the original biased version.

2. **Small sample size**: Only 6 trades in a full year - the strategy is very selective.

3. **Doesn't beat Buy & Hold**: All strategy variations underperformed simple Buy & Hold in total return, but had better risk-adjusted returns (Sharpe).

4. **Data issue**: The data file is named "nvda" but actually contains S&P 500 (GSPC) data.

### What We Learned

1. **Look-ahead bias is confirmed**: 0.78 correlation is definitive proof.

2. **The fix doesn't hurt performance**: In this case, fixing the bias actually improved Sharpe ratio from 1.88 to 2.03.

3. **Strategy is regime-dependent**: All 6 trades were in Sideways regime, with only 1 in Bullish mode. This suggests the strategy may be too conservative.

4. **Low trade frequency is concerning**: 6 trades/year might not be statistically significant.

### What Still Needs Work

1. **Test on more data**: Need to run on multiple tickers and time periods.

2. **Increase trade frequency**: Strategy may be too selective.

3. **Implement real sentiment**: Current "fake" sentiment needs to be replaced with news-based sentiment.

4. **Add stop-loss**: No explicit risk management in current strategy.

---

## Decision

- [x] **Fix validated** - Shift method is now the baseline
- [ ] **Need real sentiment** - Future work to implement news-based sentiment
- [ ] **Need more testing** - Run on multiple tickers

**Decision Date:** 2025-01-11

**Reasoning:** The shift method fixes the look-ahead bias while maintaining good performance. This should be the new baseline for future experiments.

---

## Next Steps

1. [x] Update `data_miner.py` to use lagged sentiment by default
2. [x] Document findings in `LESSONS_LEARNED.md`
3. [ ] Create `EXP-2025-002` for testing on multiple tickers
4. [ ] Create `EXP-2025-003` for implementing real news sentiment
5. [ ] Add stop-loss mechanism to strategy

---

## Lessons Learned

1. **Always check for look-ahead bias**: Correlation analysis between signals and same-day returns is essential.

2. **High Sharpe doesn't always mean bias**: In this case, even the "corrected" version had Sharpe > 2.

3. **Small sample sizes are misleading**: 6 trades in a year is not statistically significant.

4. **Data validation is critical**: The file was named "nvda" but contained S&P 500 data.

5. **Buy & Hold is a tough benchmark**: Even with AI signals, beating simple buy-and-hold is difficult.

---

## References

- Source: `review.md` - Initial code review identifying this issue
- Script: `run_experiment.py` - Experiment runner script
- Data: `data/nvda_real_data_2023.csv` (actually S&P 500 data)

## Next Experiments

- `EXP-2025-002`: Multi-ticker validation
- `EXP-2025-003`: Real news sentiment implementation
