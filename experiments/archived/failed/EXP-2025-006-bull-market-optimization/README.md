# EXP-2025-006: Bull Market Optimization

**Status:** Failed | **Completed:** 2025-01-11
**Author:** Trae
**Tags:** bull-market, trailing-stop, ADX, trend-filter

---

## Hypothesis

Implementing trailing stop (5% from peak) + ADX trend filter will significantly improve bull market performance WITHOUT sacrificing bear market protection.

**Expected Outcome:**
- NVDA 2023 Return: >150% (from 94% in EXP-003)
- SPY 2022 Return: >10% (maintain bear market protection)

---

## Actual Results

### Primary Target: NVDA 2023

| Metric | Original | Optimized | Buy&Hold | Target | Result |
|--------|----------|-----------|----------|--------|--------|
| Return % | -9.52 | **-20.46** | 229.45 | >150 | **FAIL** |
| Sharpe Ratio | -0.40 | **-1.11** | 1.41 | >1.5 | **FAIL** |
| Max Drawdown % | -26.93 | **-29.58** | -18.01 | <15 | OK |
| # Trades | 25 | **10** | 0 | - | Lower |

### Bear Market Validation: SPY 2022

| Metric | Original | Optimized | Buy&Hold | Target | Result |
|--------|----------|-----------|----------|--------|--------|
| Return % | -8.55 | **-0.65** | -17.68 | >10 | FAIL |
| Sharpe Ratio | -0.67 | **-0.07** | -0.93 | >0 | Improved |
| Max Drawdown % | -13.59 | **-9.95** | -23.23 | <10 | OK |
| # Trades | 28 | **12** | 0 | - | Lower |

### Multi-Ticker 2023 Summary

| Ticker | Return % | Sharpe | Max DD % | Trades | vs B&H |
|--------|----------|-------|----------|--------|--------|
| NVDA | **-20.46** | -1.11 | -29.58 | 10 | -249.91% |
| AAPL | -8.02 | -0.72 | -13.26 | 10 | -57.50% |
| SPY | -8.09 | -1.04 | -12.04 | 9 | -32.99% |

---

## Decision: FAILED

### What Went Wrong

1. **Trailing Stop Too Tight**
   - 5% trailing stop triggered too frequently in volatile markets
   - NVDA 2023 had many 5%+ pullbacks during uptrend
   - Each pullback caused exit, missing continuation

2. **Skipping Mean Reversion in Strong Trends**
   - ADX > 25 disabled mean reversion mode
   - This reduced trade opportunities significantly
   - Many profitable mean reversion trades were missed

3. **Trade Frequency Plummeted**
   - NVDA: 25 trades → 10 trades (-60%)
   - Less trades = fewer opportunities to profit

4. **Bear Market Improvement Was Minimal**
   - SPY 2022: -8.55% → -0.65% (+7.9% improvement)
   - But still negative, and trades dropped from 28 to 12

### Root Cause Analysis

The approach of "letting winners run" with trailing stop backfired because:
- NVDA 2023 was volatile (many swings >5%)
- Strategy would buy, then get stopped out on pullback
- By the time trend resumed, no position was open
- This is "whipsaw" hell

The ADX filter to skip mean reversion also backfired because:
- Even in strong trends, there are mean reversion opportunities
- By disabling MR mode, we missed profitable trades
- ADX threshold of 25 may be too low

---

## Lessons Learned

1. **Trailing stops are tricky in volatile markets**
   - 5% is too tight for volatile stocks like NVDA
   - Need wider stops or different approach

2. **Disabling strategies reduces opportunities**
   - Skipping mean reversion in "trend" mode was wrong
   - Better to keep all modes active

3. **The original strategy's "conservative" nature is a feature, not a bug**
   - The strategy is designed for capital preservation
   - It shines in bear markets, lags in mega-bull markets
   - This is acceptable for a defensive strategy

4. **NVDA 2023 was an exceptional year**
   - +229% is outlier territory
   - Even Buy&Hold is hard to beat in such markets
   - Strategy performed poorly in absolute terms but protected downside better than most

---

## Conclusion

**Status: FAILED - Archive**

The BullOptimizedStrategy with ADX filter and trailing stop **performed worse** than the original AdaptiveStrategy:

- NVDA 2023: -10.94 percentage points worse
- Trade frequency: -60% reduction
- Bear market improvement minimal

**Recommendation:**
1. **Abandon this approach** - trailing stop + ADX filter is not the right direction
2. **Accept original strategy limitations** - it's a defensive/capital preservation strategy
3. **Focus on bear/sideways performance** - this is where the strategy shines
4. **Consider separate bull market strategy** - rather than modifying existing one

---

## Alternative Approaches (Not Tested)

1. **Wider trailing stop** (10-15% instead of 5%)
2. **Time-based exit** (hold for minimum X bars)
3. **Volatility-adjusted trailing stop** (wider in volatile markets)
4. **Separate bull/sideways strategies** (not adaptive)

**Decision:** Do NOT pursue these for now. Accept original strategy as-is.

---

## Files

- Strategy: `src/strategies/bull_optimized_strategy.py` (DO NOT USE)
- Test script: `run_exp_2025_006.py`
- Results: `experiments/active/EXP-2025-006-bull-market-optimization/results/`

**Note:** BullOptimizedStrategy is kept for reference but should NOT be used in production.
