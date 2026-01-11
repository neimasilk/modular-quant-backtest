# EXP-2025-001: Fix Look-Ahead Bias in Sentiment Generation

**Status:** Active
**Created:** 2025-01-11
**Author:** [Your Name]
**Tags:** data-pipeline, bias-fix, critical

---

## Hypothesis

**Current Problem:** The strategy shows unrealistically good performance (Sharpe 1.79) because `AI_Stock_Sentiment` is generated from `Daily_Return` - meaning the strategy "knows" the future price movement.

**Hypothesis:** If we fix the look-ahead bias by either:
1. Removing the fake sentiment entirely, OR
2. Implementing true lagged sentiment based on actual news

...then the backtest results will show true (lower) performance, providing a realistic baseline for further improvements.

---

## Problem Definition

### Location of Bug
File: `data_miner.py`, function `add_ai_stock_sentiment()` (lines 320-340)

### Current Code (Problematic)
```python
# Create sentiment based on daily return
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
- [ ] Bug fix
- [ ] Data pipeline validation
- [ ] Baseline establishment

### Approach Options

#### Option A: Remove Fake Sentiment (Recommended First Step)
```python
# Simply set all sentiment to 0 or remove the column
df['AI_Stock_Sentiment'] = 0.0
```
**Pros:** Simple, immediate, establishes true baseline
**Cons:** Strategy will underperform (intentionally)

#### Option B: Implement Lagged Sentiment
```python
# Shift sentiment by 1 day so it uses yesterday's return for today's decision
df['AI_Stock_Sentiment'] = np.select(conditions, choices, default=0.0)
df['AI_Stock_Sentiment'] = df['AI_Stock_Sentiment'].shift(1)
```
**Pros:** More realistic, some signal preserved
**Cons:** Still using price-based sentiment (not true news sentiment)

#### Option C: Implement Real News Sentiment (Future Work)
- Integrate NewsAPI or Yahoo Finance news
- Send headlines to DeepSeek for actual sentiment scoring
- Store with proper timestamps

---

## Parameters

```python
# Backtest Configuration
ticker = "NVDA"
start_date = "2023-01-01"
end_date = "2024-01-01"
initial_cash = 10000
commission = 0.001

# Fix Parameters
approach = "A"  # A, B, or C (see above)
verify_no_bias = True
```

---

## Data

| Source | Ticker(s) | Timeframe | Notes |
|--------|-----------|-----------|-------|
| Yahoo Finance | NVDA | Daily | Existing data in `data/` |

---

## Success Criteria

| Metric | Before Fix (Expected) | After Fix (Target) |
|--------|----------------------|-------------------|
| Sharpe Ratio | ~1.79 (fake) | < 1.0 (realistic) |
| No Look-Ahead Bias | FALSE | TRUE |
| Reproducible | Maybe | YES |

**Primary Goal:** Establish realistic baseline, NOT achieve high returns

---

## Execution Plan

### Step 1: Verify Current Bias
```bash
# Run current (biased) version to confirm baseline
python main.py --ticker NVDA --start 2023-01-01 --end 2024-01-01
```

### Step 2: Apply Fix
Edit `data_miner.py` based on chosen approach (A, B, or C)

### Step 3: Run Fixed Version
```bash
# Run fixed version
python main.py --ticker NVDA --start 2023-01-01 --end 2024-01-01
```

### Step 4: Compare Results
Document the difference between biased and unbiased results

---

## Results

### Before Fix (Current/Biased)
```
Sharpe Ratio: _____
Max Drawdown: _____%
Total Return: _____%
```

### After Fix (Unbiased)
```
Sharpe Ratio: _____
Max Drawdown: _____%
Total Return: _____%
```

### Comparison
| Metric | Before Fix | After Fix | Change |
|--------|-----------|-----------|--------|
| Sharpe Ratio | | | |
| Total Return | | | |
| Max Drawdown | | | |

---

## Analysis

### What We Learned
[Fill after execution]

### Is This Fix Sufficient?
- [ ] Yes - This establishes a good baseline
- [ ] No - Need to implement real news sentiment (Option C)

---

## Decision

- [ ] **Fix is sufficient** - Use this as new baseline for future experiments
- [ ] **Need real sentiment** - Proceed to implement news-based sentiment
- [ ] **Other:** ___________

**Decision Date:** YYYY-MM-DD

---

## Next Steps

Based on results:
1. [ ] Document unbiased baseline in `LESSONS_LEARNED.md`
2. [ ] Update main code with fix
3. [ ] If needed, create `EXP-2025-002` for real news sentiment
4. [ ] Begin strategy improvements from realistic baseline

---

## Lessons Learned

[What did this experiment teach you about backtesting and bias?]

---

## References

- Source: `review.md` - Initial code review identifying this issue
- Related: "Look-Ahead Bias" in quantitative finance literature
- Next: `EXP-2025-002` (real news sentiment - if needed)
