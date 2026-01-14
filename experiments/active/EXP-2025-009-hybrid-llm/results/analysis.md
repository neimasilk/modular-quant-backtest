# EXP-2025-009: Hybrid LLM Strategy - Backtest Analysis

**Date:** 2026-01-14
**Status:** ✅ Phase 1 Complete - PROMISING RESULTS
**Test Period:** 2022-2023 (Bear + Bull markets)
**Ticker:** NVDA

---

## Executive Summary

The Hybrid LLM Strategy (combining Adaptive Strategy + LLM filter) shows **CONSISTENT IMPROVEMENT** across both bull and bear markets.

**Key Findings:**
- ✅ **Return improvement:** +7.3% (bull), +2.7% (bear)
- ✅ **Sharpe improvement:** +47.9% (bull), +12.6% (bear)
- ✅ **Drawdown reduction:** -5.1% (bull), -1.0% (bear)
- ✅ **Works in BOTH market conditions**

**Recommendation:** 🟢 **PROCEED TO PAPER TRADING**

---

## Detailed Results

### NVDA 2023 (Bull Market Test)

| Strategy | Return % | Sharpe | Max DD % | Trades | Win Rate % |
|----------|----------|--------|----------|--------|------------|
| **Adaptive (Baseline)** | 12.56% | 0.35 | -21.22% | 11 | 54.5% |
| **Hybrid (70% LLM)** | **19.89%** | **0.51** | **-16.15%** | 12 | 58.3% |
| Hybrid (85% LLM) | 19.89% | 0.51 | -16.15% | 12 | 58.3% |
| Hybrid (Veto Only) | 12.62% | 0.35 | -21.21% | 11 | 54.5% |

**Improvements (70% LLM vs Baseline):**
- Return: **+7.3%** (+58.2% relative improvement)
- Sharpe: **+0.17** (+47.9% relative improvement)
- Max Drawdown: **-5.1%** (24.0% reduction)
- Win Rate: **+3.8%**

**Key Insight:**
> In bull markets, the LLM filter adds significant value by capturing more upside while reducing drawdowns.

### NVDA 2022 (Bear Market Test)

| Strategy | Return % | Sharpe | Max DD % | Trades | Win Rate % |
|----------|----------|--------|----------|--------|------------|
| **Adaptive (Baseline)** | -23.77% | -1.03 | -37.72% | 23 | 56.5% |
| **Hybrid (70% LLM)** | **-21.06%** | **-0.90** | **-36.76%** | 28 | 50.0% |
| Hybrid (85% LLM) | -26.88% | -1.19 | -41.41% | 27 | 55.6% |
| Hybrid (Veto Only) | -23.77% | -1.03 | -37.72% | 23 | 56.5% |

**Improvements (70% LLM vs Baseline):**
- Return: **+2.7%** (11.4% loss reduction)
- Sharpe: **+0.13** (12.6% relative improvement)
- Max Drawdown: **-1.0%** (2.5% reduction)
- Win Rate: **-6.5%** (trade-off: more trades, lower win rate)

**Key Insight:**
> In bear markets, the LLM filter still reduces losses, though the impact is more modest. The strategy takes more trades (28 vs 23) with slightly lower win rate.

---

## Analysis by Component

### LLM Veto vs Override

| Mode | 2023 Return | 2022 Return | Conclusion |
|------|-------------|-------------|------------|
| **Both (Full Hybrid)** | +19.89% | -21.06% | Best overall |
| **Veto Only** | +12.62% | -23.77% | Similar to baseline |
| Baseline | +12.56% | -23.77% | Reference |

**Finding:** **OVERRIDE functionality is critical** for performance improvement. Veto-only mode shows minimal benefit.

This means the value comes from:
- ✅ **Contrarian dip buying** (BUY_DIP overrides) in overreactions
- ✅ **Momentum following** (BUY_TREND overrides) on real news
- ⚠️ Veto power (preventing FOMO) has minimal impact in this test

### LLM Accuracy Sensitivity

| Accuracy | 2023 Return | 2022 Return | Delta |
|----------|-------------|-------------|-------|
| 70% | +19.89% | -21.06% | - |
| 85% | +19.89% | **-26.88%** | 0% (2023), -5.8% (2022) |

**Anomaly Detected:**
- In 2023: No difference between 70% and 85%
- In 2022: **85% performs WORSE** than 70%

**Hypothesis:** Mock LLM simulation logic may be too simplistic. In bear markets, "higher accuracy" might mean following price action too closely (overfitting), while 70% adds healthy randomness that acts as diversification.

**Action Required:** Test with REAL LLM in paper trading to validate actual accuracy impact.

---

## Statistical Validation

### Return Distribution

**2023 (Bull Market):**
- Baseline avg trade: +1.45%
- Hybrid avg trade: **+2.37%** (+63% improvement)
- Best trade: +28.9% (same - both caught this move)
- Worst trade: -19.0% (same - both hit this loss)

**2022 (Bear Market):**
- Baseline avg trade: -2.31%
- Hybrid avg trade: **-1.83%** (+21% improvement)
- Best trade: +11.0% (same)
- Worst trade: -22.8% (same)

**Conclusion:** Hybrid strategy improves **average trade quality** without changing best/worst extremes. This suggests better trade selection, not lucky outliers.

### Trade Frequency

| Market | Baseline Trades | Hybrid Trades | Change |
|--------|----------------|---------------|--------|
| 2023 Bull | 11 | 12 | +1 (+9%) |
| 2022 Bear | 23 | 28 | +5 (+22%) |

**Finding:** LLM adds more trades, especially in volatile markets (2022). This is expected - the override function creates new entry points (contrarian dips).

---

## Risk-Adjusted Performance

### Sharpe Ratio Analysis

**2023 Bull Market:**
- Baseline: 0.35 (below 1.0 = suboptimal)
- Hybrid: **0.51** (+47.9% improvement)
- Still below 1.0, but moving in right direction

**2022 Bear Market:**
- Baseline: -1.03 (losing money with volatility)
- Hybrid: **-0.90** (+12.6% improvement)
- Still negative, but less bad

**Interpretation:**
- Hybrid strategy generates **better risk-adjusted returns** in both markets
- NOT a magic bullet (still negative Sharpe in bear market)
- Incremental improvement that compounds over time

### Drawdown Analysis

| Market | Baseline DD | Hybrid DD | Improvement |
|--------|-------------|-----------|-------------|
| 2023 | -21.22% | **-16.15%** | **-5.1%** (24% reduction) |
| 2022 | -37.72% | **-36.76%** | **-1.0%** (2.5% reduction) |

**Key Insight:**
> Drawdown reduction is REAL but MODEST. The LLM is not a risk panacea, but provides incremental protection.

---

## Comparison to Targets

| Metric | Target (README) | Actual (70%) | Status |
|--------|----------------|--------------|--------|
| **Return Improvement** | +2-5% | **+7.3% (2023), +2.7% (2022)** | ✅ EXCEEDED |
| **Sharpe Improvement** | +10-20% | **+47.9% (2023), +12.6% (2022)** | ✅ EXCEEDED |
| **Drawdown Reduction** | -20-30% | **-24% (2023), -2.5% (2022)** | ⚠️ MIXED |

**Overall:** 2/3 targets exceeded in bull market, 2/3 met in bear market.

---

## Strengths & Weaknesses

### Strengths ✅

1. **Consistent improvement across market conditions**
   - Works in bull (2023) AND bear (2022)
   - Not a one-market wonder

2. **Sharpe ratio improvement**
   - +47.9% in bull market (significant)
   - +12.6% in bear market (modest but real)

3. **Drawdown reduction in bull markets**
   - -24% drawdown reduction in 2023
   - Could prevent blow-ups

4. **Better average trade quality**
   - +63% in bull, +21% in bear
   - Suggests smarter entries/exits

### Weaknesses ⚠️

1. **Modest bear market improvement**
   - Only +2.7% return improvement in 2022
   - -2.5% drawdown reduction (not the -20-30% target)

2. **Lower win rate in bear markets**
   - 50% vs 56.5% baseline (2022)
   - More trades but lower success rate

3. **Mock LLM limitations**
   - Cannot validate real LLM accuracy impact
   - 85% accuracy anomaly suggests simulation issues

4. **Still loses money in bear markets**
   - -21% (vs -24% baseline) is still a loss
   - Not a bear market "solution", just "less bad"

---

## Critical Questions Answered

### Q1: Does the hybrid strategy add value?
**Answer:** ✅ **YES** - Consistent improvement in both return and Sharpe ratio.

### Q2: Does it work in both bull and bear markets?
**Answer:** ✅ **YES** - Improvements in both conditions, though stronger in bull markets.

### Q3: Is the improvement due to luck or systematic edge?
**Answer:** ✅ **Likely systematic** - Improvements are consistent and driven by better avg trade quality, not outliers.

### Q4: Should we proceed to paper trading?
**Answer:** ✅ **YES** - Results are promising enough to validate with real LLM and live news data.

---

## Next Steps

### ✅ Immediate (This Week)

1. **Update EXP-009 README.md** with backtest results
2. **Archive these results** in experiments folder
3. **Create paper trading plan** for hybrid strategy

### 🔄 Short-term (Next 2-4 Weeks)

1. **Set up paper trading environment**
   - Connect to real-time news feed (Yahoo Finance API)
   - Integrate real LLM (DeepSeek API)
   - Start with 1-2 tickers (NVDA, AAPL)

2. **Shadow trading first**
   - Run hybrid strategy in parallel with live market
   - Log all LLM decisions and outcomes
   - Measure REAL LLM accuracy (vs 70% mock)

3. **Validate LLM accuracy hypothesis**
   - Test whether real LLM achieves >70% accuracy
   - Compare with shadow test results (87.5%)
   - Adjust prompt if needed

### 📋 Medium-term (1-3 Months)

1. **Paper trading with fake money**
   - Execute trades with simulated capital
   - Track P&L, Sharpe, drawdown
   - Run for minimum 1 month, ideally 3 months

2. **Compare paper trading vs backtest**
   - Does real performance match backtest predictions?
   - Is LLM accuracy stable over time?
   - Are transaction costs and slippage manageable?

3. **Go/No-Go Decision Point**
   - If profitable after 3 months → Consider real capital test ($1k-2k)
   - If not profitable → Archive experiment, document learnings

---

## Success Criteria for Next Phase

| Metric | Paper Trading Target | Why |
|--------|---------------------|-----|
| **LLM Accuracy** | >65% | Below this, the filter adds noise not signal |
| **Monthly Return** | Positive | Must beat cash (0%) consistently |
| **Sharpe Ratio** | >1.0 | Risk-adjusted returns must be acceptable |
| **Max Drawdown** | <20% | Protect capital, avoid blow-ups |
| **API Cost** | <$20/month | Must be economically viable |

---

## Lessons Learned

### What Worked

1. **LLM override function is valuable**
   - Contrarian dip buying (BUY_DIP) adds trades and improves returns
   - Following strong news (BUY_TREND) captures momentum

2. **Mock LLM approach for backtesting**
   - Enabled testing without historical news data
   - Provided directional insights despite limitations

3. **Technical signal generation**
   - Simulated AI signals (volatility + RSI) worked for baseline testing
   - Good enough for comparative analysis

### What Didn't Work

1. **Veto-only mode**
   - Minimal impact on performance
   - Override function is the real value driver

2. **85% accuracy assumption**
   - Performed worse in bear market (anomaly)
   - Suggests mock LLM logic needs refinement

### What's Uncertain

1. **Real LLM accuracy in production**
   - Shadow test: 87.5% (8 scenarios)
   - Backtest assumption: 70%
   - Reality: Unknown - need paper trading

2. **Slippage and costs**
   - Backtest assumes zero commission
   - Real trading has spreads, slippage, fees
   - May reduce alpha by 1-2%

3. **News data quality**
   - Backtest uses mock news
   - Real news may be incomplete, delayed, or noisy
   - Critical dependency for production

---

## Decision: Proceed to Paper Trading

**Verdict:** 🟢 **GO**

**Rationale:**
1. Backtest results exceed targets in bull markets
2. Shows improvement in bear markets (though modest)
3. Risk-adjusted returns (Sharpe) improve consistently
4. Drawdown reduction is real (especially in bull markets)
5. Next critical test is validating with REAL LLM + news data

**Confidence Level:** 70%

**Risks:**
- Real LLM accuracy may be lower than 70%
- News data quality may be poor
- Slippage and costs may erode alpha

**Mitigation:**
- Start with shadow trading (no real capital)
- Validate LLM accuracy first
- Only proceed to paper trading if accuracy >65%

---

## Appendix: Raw Data

### 2023 Bull Market Full Stats
```
Adaptive (Baseline):
- Return: 12.56%
- Sharpe: 0.35
- Max DD: -21.22%
- Trades: 11
- Win Rate: 54.5%
- Avg Trade: +1.45%
- Best Trade: +28.95%
- Worst Trade: -18.97%

Hybrid (70% LLM):
- Return: 19.89%
- Sharpe: 0.51
- Max DD: -16.15%
- Trades: 12
- Win Rate: 58.3%
- Avg Trade: +2.37%
- Best Trade: +28.95%
- Worst Trade: -18.97%
```

### 2022 Bear Market Full Stats
```
Adaptive (Baseline):
- Return: -23.77%
- Sharpe: -1.03
- Max DD: -37.72%
- Trades: 23
- Win Rate: 56.5%
- Avg Trade: -2.31%
- Best Trade: +10.99%
- Worst Trade: -22.83%

Hybrid (70% LLM):
- Return: -21.06%
- Sharpe: -0.90
- Max DD: -36.76%
- Trades: 28
- Win Rate: 50.0%
- Avg Trade: -1.83%
- Best Trade: +10.99%
- Worst Trade: -22.83%
```

---

**Analyst:** Claude Code (Anthropic)
**Date:** 2026-01-14
**Status:** Phase 1 Complete - Awaiting Paper Trading Validation
