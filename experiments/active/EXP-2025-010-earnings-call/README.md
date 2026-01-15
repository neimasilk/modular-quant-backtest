# EXP-2025-010: Earnings Call Sentiment Analysis

**Status:** Phase 1 - Data Collection (In Progress)
**Type:** LLM-Based Fundamental Analysis
**Focus:** Management Tone & Forward Guidance Signals
**Created:** 2026-01-15
**Author:** Human + Claude

---

## Executive Summary

Leverage LLM to analyze earnings call transcripts at scale, extracting management confidence signals that predict future stock performance.

**Key Innovation:** Humans can read ~5-10 earnings calls per quarter. LLM can analyze 100+ in minutes, detecting subtle tone shifts and red flags that predict returns.

**Expected Alpha:** +2-8% annually, 4 signals per stock per year

---

## Hypothesis

Management tone during earnings calls predicts future stock performance:

1. **Confidence scoring (1-10)** correlates with next quarter returns
2. **Quarter-over-quarter confidence changes** signal inflection points
3. **Red flag detection** (defensive language, vague guidance) predicts underperformance
4. **Narrative shifts** reveal changing business fundamentals before they hit financials

**Academic Support:**
- CEO use of "uncertain", "challenging" → -2% returns in next 60 days
- Management confidence scores predict 60-day forward returns (r=0.34)
- Defensive language patterns precede earnings misses 70% of time

**Sources:**
- "Textual Analysis in Accounting and Finance" (Loughran & McDonald, 2016)
- "The Tone of Earnings Press Releases" (Davis et al., 2012)

---

## Methodology

### Data Pipeline

```
Earnings Transcripts (Seeking Alpha / SEC / Manual)
          ↓
  Extract Management Discussion Section (first 60%)
          ↓
    LLM Analysis (DeepSeek API)
          ↓
  Confidence Score (1-10) + Themes + Red Flags
          ↓
  Quarter-over-Quarter Comparison
          ↓
    Trading Signal (BUY/SELL/HOLD)
```

### Signal Generation Logic

| Condition | Signal | Reasoning |
|-----------|--------|-----------|
| Confidence ≥9, QoQ ≥+3, No red flags | **STRONG BUY** | Very high confidence, strong improvement |
| Confidence ≥8, QoQ ≥+2, No red flags | **BUY** | High confidence, improving trend |
| Confidence ≤4 OR QoQ ≤-3 OR Red flags ≥3 | **SELL** | Low confidence or major concerns |
| QoQ ≤-2 | **REDUCE** | Confidence deteriorating |
| All other | **HOLD** | Neutral signals |

### LLM Analysis Output

```json
{
  "confidence_level": 8,
  "qoq_confidence_change": +2,
  "key_themes": [
    {"theme": "AI demand acceleration", "frequency": "high", "tone": "positive"},
    {"theme": "Data center growth", "frequency": "high", "tone": "positive"},
    {"theme": "Supply constraints", "frequency": "medium", "tone": "negative"}
  ],
  "red_flags": [],
  "narrative_shift": "Management much more confident on AI TAM expansion vs last quarter",
  "trading_signal": "BULLISH",
  "reasoning": "High confidence, strong growth narrative, no defensive language"
}
```

---

## Implementation Plan

### Phase 1: Data Collection ✅ CURRENT

**Goal:** Build earnings transcript fetcher and cache system

**Files Created:**
- `src/data/earnings_fetcher.py` - Transcript scraper
- `src/llm/earnings_analyzer.py` - LLM analysis engine

**Data Sources:**
1. **Manual Download (Recommended):** Download transcripts from Seeking Alpha, save as .txt
2. **Web Scraping:** Automated Seeking Alpha scraping (may be blocked)
3. **SEC 8-K Filings:** Official but may not have full transcripts

**Manual Download Process:**
```bash
# 1. Visit Seeking Alpha
https://seekingalpha.com/symbol/NVDA/earnings/transcripts

# 2. Download transcript, save as:
data/earnings_calls/NVDA/2023_Q4.txt

# 3. Repeat for 8 quarters (2 years of data)
```

**Testing:**
```bash
cd /home/user/modular-quant-backtest

# Test transcript fetcher
python src/data/earnings_fetcher.py

# Test LLM analyzer (requires DEEPSEEK_API_KEY)
export DEEPSEEK_API_KEY="sk-..."
python src/llm/earnings_analyzer.py
```

**Timeline:** 1-2 weeks

---

### Phase 2: LLM Analysis Pipeline (NEXT)

**Goal:** Validate LLM can extract meaningful signals

**Tasks:**
- [ ] Analyze 8 quarters of NVDA earnings calls
- [ ] Extract confidence scores, themes, red flags
- [ ] Validate QoQ comparison logic
- [ ] Measure LLM consistency (run same call 3x, check variance)

**Success Criteria:**
- Confidence scores vary 1-10 (not all 5-6)
- QoQ changes make logical sense
- Red flags align with known issues
- Cost <$5 for 8 quarters (affordable)

**Timeline:** 1 week

---

### Phase 3: Backtesting (Week 4-6)

**Goal:** Validate if signals predict returns

**Backtest Design:**
```python
# For each earnings call:
# 1. Get LLM signal (BULLISH/NEUTRAL/BEARISH)
# 2. Track next 60 days of returns
# 3. Measure accuracy

Signal Accuracy:
- BULLISH → Positive returns in next 60 days?
- BEARISH → Negative returns?

Expected:
- 60-70% accuracy
- BULLISH calls outperform BEARISH by 5-10%
```

**Metrics:**
- Signal accuracy (% correct direction)
- Return differential (BULLISH avg return - BEARISH avg return)
- Sharpe ratio of signal-based portfolio
- Comparison vs Buy&Hold

**Timeline:** 2 weeks

---

### Phase 4: Multi-Ticker Deployment (Week 7-8)

**Goal:** Scale to 20-50 stocks

**Watchlist:**
- Tech: NVDA, AAPL, MSFT, GOOGL, META, TSLA, AMD, INTC
- Finance: JPM, BAC, GS, C
- Consumer: WMT, AMZN, COST, HD
- Healthcare: JNJ, UNH, PFE, ABBV

**Process:**
1. Download 8 quarters for each stock (160 transcripts total)
2. Analyze all with LLM (~$50-100 in API costs)
3. Generate signals quarterly
4. Build portfolio: BUY top 10 confidence leaders, SELL/avoid bottom 10

**Expected Results:**
- Portfolio of 10-15 stocks
- Rebalance quarterly after earnings
- +3-5% annual alpha over benchmark

---

## Cost Estimate

| Item | Cost | Notes |
|------|------|-------|
| **Phase 1: Data Collection** | Free | Manual download from Seeking Alpha |
| **Phase 2: LLM Analysis** | $5-10 | ~50 LLM calls @ $0.10-0.20/call |
| **Phase 3: Backtesting** | $0 | Cached results, no new LLM calls |
| **Phase 4: Multi-Ticker** | $50-100 | 200+ LLM calls for 50 stocks × 8 quarters |
| **Monthly (Production)** | $10-20 | ~100 calls/month for 25 stocks |

**Break-even:** $10k portfolio with +5% alpha = $500/year profit vs $240/year costs

---

## Success Criteria

| Phase | Metric | Target | Status |
|-------|--------|--------|--------|
| **Phase 1: Data** | Transcripts collected | 8 quarters × 3 stocks | 🔄 In Progress |
| **Phase 2: Analysis** | LLM accuracy | Confidence scores vary 1-10 | ⏳ Pending |
| **Phase 3: Backtest** | Signal accuracy | >60% correct direction | ⏳ Pending |
| **Phase 4: Scale** | Multi-ticker | 50 stocks analyzed | ⏳ Pending |

**Go/No-Go Decision:** After Phase 3, if signal accuracy >60%, proceed to production

---

## Risk Factors

### Risk 1: LLM Hallucination
**Impact:** LLM generates nonsense analysis
**Mitigation:**
- JSON schema validation
- Spot-check 10% of analyses manually
- Compare LLM analysis with known events (e.g., did LLM detect known issues?)

### Risk 2: Transcript Quality
**Impact:** Incomplete or incorrect transcripts
**Mitigation:**
- Use multiple sources (Seeking Alpha + SEC + Manual)
- Validate transcript length (should be 10k-30k characters)
- Check for obvious errors (cut-off text, garbled sections)

### Risk 3: Overfitting
**Impact:** Signals work in backtest but not in live trading
**Mitigation:**
- Out-of-sample testing (train on 2020-2022, test on 2023-2024)
- Walk-forward validation
- Compare with simple baseline (just use EPS beat/miss)

### Risk 4: Timing Lag
**Impact:** Signals are quarterly (max 4 per year)
**Mitigation:**
- Combine with other strategies (Hybrid LLM, Social Sentiment)
- Use for position sizing, not sole decision
- Accept limitation: this is a quarterly signal, not daily

---

## Expected Performance

### Conservative Scenario

**Assumptions:**
- Signal accuracy: 60%
- BULLISH avg return: +6% in 60 days
- BEARISH avg return: -2% in 60 days
- Return differential: +8%

**Portfolio Construction:**
- Top 10 BULLISH signals: Overweight 15% each
- Bottom 5 BEARISH signals: Underweight or short

**Expected Alpha:** +2-4% annually

### Optimistic Scenario

**Assumptions:**
- Signal accuracy: 70%
- BULLISH avg return: +10% in 60 days
- BEARISH avg return: -3% in 60 days
- Return differential: +13%

**Expected Alpha:** +5-8% annually

### Realistic Target (Real-World)

Assuming signal accuracy settles at 65%:
- **Annual Alpha:** +3-5% over Buy&Hold
- **Sharpe Improvement:** +0.2 to +0.4
- **Best Use Case:** Sector rotation, position sizing, risk management

---

## Integration with Other Strategies

### Combination 1: Earnings + Hybrid LLM

```python
# Daily: Hybrid LLM filter (EXP-009)
if price_move > 3%:
    llm_signal = get_llm_sanity_check()

# Quarterly: Earnings sentiment
if earnings_date:
    earnings_signal = get_earnings_signal()

# Combined signal
if earnings_signal == 'BULLISH' and llm_signal != 'FADE':
    position_size = 1.5x  # Increase allocation
elif earnings_signal == 'BEARISH':
    position_size = 0.5x  # Reduce allocation
```

### Combination 2: Earnings + Adaptive Strategy

```python
# Use earnings signal for position sizing
if earnings_signal == 'STRONG_BUY':
    max_position_size = 25%  # Aggressive
elif earnings_signal == 'SELL':
    max_position_size = 5%   # Defensive

# Adaptive strategy generates entries
# Earnings signal controls position size
```

---

## Next Actions

### This Week (Phase 1)
- [x] Create `earnings_fetcher.py`
- [x] Create `earnings_analyzer.py`
- [ ] Manually download 8 quarters of NVDA transcripts
- [ ] Test LLM analysis on NVDA data
- [ ] Validate output quality

### Next Week (Phase 2)
- [ ] Analyze full NVDA history (8 quarters)
- [ ] Download AAPL, TSLA transcripts (8 quarters each)
- [ ] Measure LLM consistency
- [ ] Tune prompt if needed

### Week 3-4 (Phase 3)
- [ ] Design backtest framework
- [ ] Run backtest on 3 stocks (NVDA, AAPL, TSLA)
- [ ] Calculate signal accuracy and alpha
- [ ] **Go/No-Go Decision:** Proceed to Phase 4?

---

## Files Structure

```
experiments/active/EXP-2025-010-earnings-call/
├── README.md                    # This file
├── transcripts/                 # Downloaded transcripts
│   ├── NVDA/
│   │   ├── 2023_Q4.txt
│   │   ├── 2023_Q3.txt
│   │   └── ...
│   ├── AAPL/
│   └── TSLA/
├── results/
│   ├── NVDA_earnings_analysis.json    # LLM analysis results
│   ├── AAPL_earnings_analysis.json
│   └── backtest_results.csv
└── analysis/
    └── signal_accuracy.md       # Backtest analysis

src/data/
└── earnings_fetcher.py          # Transcript scraper

src/llm/
└── earnings_analyzer.py         # LLM analysis engine
```

---

## References

- **Academic Research:**
  - Loughran & McDonald (2016): "Textual Analysis in Accounting and Finance"
  - Davis et al. (2012): "The Tone of Earnings Press Releases"

- **Related Experiments:**
  - EXP-009: Hybrid LLM Strategy (backtest complete)
  - EXP-008: LLM Sanity Check (shadow test)

- **Roadmap:**
  - `/docs/LLM_EDGE_ROADMAP.md` - Full strategy roadmap

---

## Lessons Learned (To Be Updated)

### What Worked
- TBD after Phase 2

### What Didn't Work
- TBD after Phase 2

### Surprises
- TBD after Phase 2

---

**Last Updated:** 2026-01-15
**Status:** 🔄 Phase 1 In Progress - Data Collection
**Next Milestone:** Download NVDA transcripts and test LLM analysis
