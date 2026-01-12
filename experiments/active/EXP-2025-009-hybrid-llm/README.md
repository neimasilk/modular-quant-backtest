# EXP-2025-009: Hybrid LLM-Adaptive Strategy

**Status:** Phase 1 - Implementation Complete, Testing Pending
**Type:** Hybrid (Regime-Based + LLM Filter)
**Focus:** Risk Management & Drawdown Reduction
**Created:** 2025-01-12
**Last Updated:** 2025-01-12
**Author:** Human + Claude

---

## Executive Summary

Kombinasi **Adaptive Strategy** (proven bear market performer) dengan **LLM Sanity Checker** untuk:
- Mengurangi drawdown 20-30% dengan memfilter FOMO trades
- Meningkatkan Sharpe ratio 10-20% melalui contrarian dip buying
- Maintain baseline performance sambil menghindari emotional trading mistakes

**Key Innovation:** LLM bukan sebagai predictor, tapi sebagai **VETO MECHANISM** untuk mencegah kebodohan.

---

## Hypothesis

Menggunakan LLM sebagai filter layer di atas Adaptive Strategy akan:

1. **Reduce Drawdown:** Veto pembelian saat hype-driven rallies (avoid FOMO traps)
2. **Improve Win Rate:** Override panic sells dengan contrarian dip buying saat LLM detect overreaction
3. **Cost Efficient:** Only call LLM on >3% volatility events (save API costs)

**Expected Results:**

| Metric | Adaptive Baseline | Hybrid Target | Improvement |
|--------|-------------------|---------------|-------------|
| Return | Varies | +2-5% | +2-5% |
| Sharpe Ratio | 1.57 (2022 SPY) | 1.73-1.88 | +10-20% |
| Max Drawdown | -4.2% (2022 SPY) | -2.9% to -3.4% | -20-30% |

---

## Methodology

### System Architecture

```
Price Data → Adaptive Strategy (Baseline Signal)
                    ↓
            [Volatility Check]
                    ↓
            If |change| > 3%:
                    ↓
            LLM Sanity Checker
          (News Substance Analysis)
                    ↓
        [Veto/Override Logic]
                    ↓
          Final Trading Signal
```

### Decision Matrix

| Adaptive Signal | LLM Assessment | Final Action | Reasoning |
|-----------------|----------------|--------------|-----------|
| BUY | SHORT_SCALP (hype detected) | **HOLD** (veto) | Avoid buying into pump |
| BUY | HARD_EXIT (real trouble) | **HOLD** (veto) | Don't buy falling knife |
| SELL/HOLD | BUY_DIP (overreaction) | **BUY** (override) | Contrarian dip buy |
| HOLD | BUY_TREND (strong news) | **BUY** (override) | Follow real momentum |
| ANY | NEUTRAL/IGNORE | Keep original | LLM inconclusive |

### LLM Trigger Conditions

**LLM only activates when:**
- Price change > 3% from previous bar (up or down)
- OR Volume > 2x average (optional)

**Cost Control:**
- Typical: 10-20 LLM calls per month per stock
- At $0.10/call: $2-5/month for 5-stock portfolio
- Total annual cost: <$100

### Mock Mode for Backtesting

**Problem:** Historical backtests don't have timestamped news data.

**Solution:** Mock LLM mode simulates decisions with configurable accuracy:

```python
# Mock LLM generates realistic substance scores
# Based on price move magnitude + randomness
# Accuracy parameter: 70% = 7/10 calls correct

bt.run(
    mock_llm_mode=True,
    mock_llm_accuracy=0.70
)
```

This allows backtesting WITHOUT real news data, estimating potential performance.

---

## Implementation

### File Structure

```
src/
├── strategies/
│   └── hybrid_llm_strategy.py       # Main implementation
├── llm/
│   └── sanity_checker.py            # LLM news validator (from EXP-008)
└── data/
    └── news_fetcher.py              # News API integration

experiments/active/EXP-2025-009-hybrid-llm/
├── README.md                        # This file
├── results/                         # Backtest results
│   ├── comparison_NVDA_2023.csv
│   ├── comparison_NVDA_2022.csv
│   └── analysis.md
└── logs/                            # LLM decision logs
```

### Key Parameters

```python
# LLM Configuration
llm_enabled = True                   # Enable LLM filter
llm_volatility_threshold = 0.03      # 3% trigger
llm_veto_enabled = True              # Allow vetoes
llm_override_enabled = True          # Allow overrides

# Mock Mode (for backtesting)
mock_llm_mode = False                # Use real LLM
mock_llm_accuracy = 0.70             # Simulated accuracy
```

### Strategy Logic (Simplified)

```python
def next(self):
    # 1. Get baseline signal from Adaptive Strategy
    adaptive_signal = self._get_adaptive_signal()

    # 2. Check volatility
    price_change_pct = self.get_price_change_pct()

    # 3. If volatile, get LLM assessment
    llm_signal = None
    if abs(price_change_pct) > 0.03:
        news = self.get_news_for_current_bar()
        llm_signal = self.get_llm_signal(price_change_pct, news)

    # 4. Apply LLM filter (veto/override)
    final_signal = self.apply_llm_filter(adaptive_signal, llm_signal)

    # 5. Execute
    self._execute_signal(final_signal, regime)
```

---

## Testing Plan

### Phase 1: Backtest Validation ✅ READY

**Test Scenarios:**

1. **NVDA 2023 (Bull Market):**
   - Adaptive baseline: +94.37%, Sharpe 1.83
   - Hybrid target: +100-110%, Sharpe 1.9-2.0
   - Goal: Improve bull market capture

2. **NVDA 2022 (Bear Market):**
   - Adaptive baseline: +18.68%, Sharpe 0.84, DD -9.95%
   - Hybrid target: +20-25%, Sharpe 0.9-1.0, DD -7-8%
   - Goal: Reduce drawdown further

3. **Accuracy Sensitivity:**
   - Test at 70%, 85% mock accuracy
   - Understand impact of LLM quality on performance

**Test Command:**

```bash
python test_hybrid_strategy.py
```

**Expected Output:**

```
RESULTS COMPARISON - NVDA 2023

Strategy                  Return      Sharpe      Max DD      Trades
--------------------------------------------------------------------------------
Adaptive (baseline)       +94.37%     1.83        -11.30%     15
Hybrid (70% accuracy)     +98.20%     1.91        -9.50%      17
Hybrid (85% accuracy)     +102.50%    1.98        -8.80%      18
Hybrid (veto only)        +96.10%     1.87        -10.20%     14

📊 KEY INSIGHTS:
   ✅ Return improved by +3.8% with LLM filter
   ✅ Sharpe ratio improved by +0.08 (4.4%)
   ✅ Drawdown reduced by -1.8% (15.9% improvement)
```

### Phase 2: Forward Testing (After Phase 1 Success)

**If backtest shows promise:**

1. **Shadow Testing (1 month):**
   - Run in parallel with real market
   - Log LLM decisions, don't execute
   - Validate accuracy in live environment

2. **Paper Trading (3 months):**
   - Execute with fake money
   - Use real news API (Benzinga or similar)
   - Track actual vs expected performance

3. **Real Capital Test ($1k-2k):**
   - Small position sizes
   - Emotional validation
   - Risk minimal capital

### Phase 3: Production Deployment (If Profitable)

**Requirements:**
- 3+ months paper trading profitability
- Sharpe > 1.5 consistently
- Drawdown < 15%
- LLM accuracy > 65% in live testing

**Production Setup:**
- Real-time news feed (Benzinga Pro ~$200/month)
- DeepSeek API or local Llama 3.1
- IBKR paper trading account
- Monitoring dashboard

---

## Success Criteria

| Phase | Metric | Target | Status |
|-------|--------|--------|--------|
| **Phase 1: Backtest** | | | |
| ├─ Return vs Baseline | +2-5% | TBD | 🔄 |
| ├─ Sharpe Improvement | +10-20% | TBD | 🔄 |
| ├─ Drawdown Reduction | -20-30% | TBD | 🔄 |
| └─ Decision: Proceed to Phase 2? | Yes/No | TBD | 🔄 |
| | | | |
| **Phase 2: Paper Trading** | | | |
| ├─ LLM Accuracy | >65% | TBD | ⏳ |
| ├─ Monthly Return | Positive | TBD | ⏳ |
| ├─ Consistency | 2/3 months profitable | TBD | ⏳ |
| └─ Decision: Proceed to Phase 3? | Yes/No | TBD | ⏳ |
| | | | |
| **Phase 3: Live Trading** | | | |
| ├─ 6-Month Return | >10% | TBD | ⏳ |
| ├─ Sharpe Ratio | >1.5 | TBD | ⏳ |
| └─ Max Drawdown | <15% | TBD | ⏳ |

---

## Risk Factors & Mitigation

### Risk 1: LLM Hallucination

**Risk:** LLM generates nonsense analysis, wrong signal

**Mitigation:**
- Constrain output to JSON schema
- Validate structure before using
- Log all LLM responses for review
- Implement sanity checks (e.g., substance_score must be 1-10)

### Risk 2: News Data Quality

**Risk:** Missing news, delayed news, fake news

**Mitigation:**
- Use multiple news sources
- Validate timestamp alignment
- Cross-check major news with official sources
- Implement news quality score

### Risk 3: Overfitting to Mock Mode

**Risk:** Backtest looks good but mock mode doesn't reflect reality

**Mitigation:**
- Test multiple accuracy levels (60%, 70%, 80%, 90%)
- Understand performance sensitivity
- Don't assume 87.5% accuracy from shadow test is real-world accuracy
- Conservative estimates (use 65-70% for planning)

### Risk 4: Cost Overruns

**Risk:** LLM API costs exceed budget

**Mitigation:**
- Hard limit on calls per day (max 5 per stock)
- Cache results to avoid duplicate calls
- Use local LLM if API costs >$50/month
- Monitor spending weekly

### Risk 5: Latency Issues

**Risk:** LLM call takes 5-10 seconds, miss optimal entry

**Mitigation:**
- Accept this limitation (we're not HFT)
- Use limit orders, not market orders
- Consider local LLM for <1s latency
- Focus on 1-hour+ holding periods (not scalping)

---

## Performance Expectations

### Conservative Scenario (70% LLM Accuracy)

**Bull Market (2023-like):**
- Baseline: +94% return, Sharpe 1.83, DD -11.3%
- Hybrid: +96-100% return, Sharpe 1.85-1.95, DD -9-10%
- **Modest improvement, still valuable**

**Bear Market (2022-like):**
- Baseline: +18.68% return, Sharpe 0.84, DD -9.95%
- Hybrid: +20-22% return, Sharpe 0.88-0.95, DD -7-8%
- **Drawdown reduction is key win**

### Optimistic Scenario (85% LLM Accuracy)

**Bull Market:**
- Hybrid: +102-108% return, Sharpe 1.95-2.05, DD -8-9%
- **Meaningful alpha generation**

**Bear Market:**
- Hybrid: +22-25% return, Sharpe 0.95-1.05, DD -6-7%
- **Significant outperformance**

### Realistic Target (Real-World)

Assuming real LLM accuracy settles at 65-70%:
- **Annual Alpha: +2-4%** over Adaptive Strategy
- **Sharpe Improvement: +0.1 to +0.2**
- **Drawdown Reduction: -10% to -20%**

**This is GOOD ENOUGH** - small improvements compound over years.

---

## Comparison to EXP-2025-008

| Aspect | EXP-008 (Sanity Checker) | EXP-009 (Hybrid) |
|--------|--------------------------|------------------|
| **Scope** | LLM only | LLM + Adaptive Strategy |
| **Use Case** | Standalone news filter | Integrated risk management |
| **Testing** | Shadow test (8 scenarios) | Full backtest (300+ bars) |
| **Complexity** | Simple | Medium |
| **Production Ready** | Maybe | Need validation |
| **Edge** | Prevent 1-2 mistakes/year | Systematic improvement |

**Relationship:**
- EXP-008 proved LLM concept (87.5% shadow test)
- EXP-009 integrates it into production strategy
- If EXP-009 succeeds → EXP-008 validated at scale

---

## Next Steps

### Immediate (This Week)

1. ✅ Implementation complete
2. 🔄 Run backtest: `python test_hybrid_strategy.py`
3. 📊 Analyze results, document in `results/analysis.md`
4. ✅/❌ Decision: Proceed to paper trading or archive?

### Short-term (Next Month)

**If backtest shows >70% confidence:**
- Set up paper trading account
- Integrate real news feed (start with free tier)
- Shadow trade for 30 days
- Compare predicted vs actual LLM performance

### Medium-term (3-6 Months)

**If paper trading profitable:**
- Fine-tune LLM prompt based on real mistakes
- Test on multiple tickers (NVDA, AAPL, TSLA, SPY)
- Scale to 5-10 stock portfolio
- Consider small real capital test

---

## Documentation & Logs

### Decision Log Format

```json
{
  "timestamp": "2025-01-12 10:30:00",
  "ticker": "NVDA",
  "bar": 150,
  "price_change": 0.045,
  "adaptive_signal": "BUY",
  "llm_signal": "SHORT_SCALP",
  "llm_substance_score": 2,
  "llm_reasoning": "AI partnership announcement - corporate buzzwords, no financials",
  "final_signal": "HOLD",
  "decision_type": "VETO",
  "outcome_7d": "+2.3%",
  "was_correct": true,
  "notes": "Avoided FOMO - stock did rally +4% then faded to +2%"
}
```

### Results CSV Schema

```csv
Strategy,Return_%,Sharpe_Ratio,Max_Drawdown_%,Num_Trades,Win_Rate_%,LLM_Calls,LLM_Vetoes,LLM_Overrides
Adaptive,94.37,1.83,-11.30,15,60.0,0,0,0
Hybrid_70,98.20,1.91,-9.50,17,62.5,12,3,2
```

---

## Lessons Learned (To Be Updated)

### What Worked

- TBD after testing

### What Didn't Work

- TBD after testing

### Surprises

- TBD after testing

### Key Insights

- TBD after testing

---

## References

- **Base Strategy:** EXP-2025-004 (Adaptive Strategy - Bear Market 2022)
- **LLM Component:** EXP-2025-008 (LLM Sanity Checker)
- **Roadmap:** `/docs/LLM_EDGE_ROADMAP.md`
- **Related:** EXP-2025-005 (Real News Sentiment - underperformed)

---

## Conclusion (Preliminary)

**Hypothesis:** LLM can add 2-5% alpha by filtering emotional mistakes.

**Status:** Implementation complete, testing required.

**Risk:** Medium - depends on LLM accuracy in production.

**Reward:** High - if successful, validates LLM approach and opens door to more advanced strategies (earnings calls, social sentiment, SEC filings).

**Next Action:** **RUN THE BACKTEST** and let data decide.

---

**Last Updated:** 2025-01-12
**Status:** ✅ Code Complete, 🔄 Testing Pending
