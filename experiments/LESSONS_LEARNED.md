# Lessons Learned

> **Purpose:** Distilled insights from all experiments to prevent repeated mistakes
> **Last Updated:** 2025-01-12

---

## Critical Lessons (Must Read Before Any Experiment)

### 1. Look-Ahead Bias is the Silent Killer
**Source:** review.md, EXP-2025-001
**Lesson:** Never use future data to generate signals. The original code created `AI_Stock_Sentiment` from `Daily_Return` - this means the strategy "knew" the future.
**Evidence:** Correlation of 0.78 between sentiment and same-day returns = definitive proof of look-ahead bias
**Rule:** Always verify that signal data comes from time T-1 or earlier for decisions at time T.
**Fix:** Use lagged signals (shift by 1 period) or ensure signals are generated from truly exogenous data.

### 2. Sharpe > 3.0 is Suspicious
**Lesson:** Real strategies rarely achieve Sharpe > 3 without look-ahead bias or data errors.
**Rule:** If Sharpe > 3, immediately check for:
- Look-ahead bias (correlation with returns)
- Data errors
- Future information leakage
- Overfitting

### 3. Paper Trading Before Real Money
**Lesson:** Backtest success ≠ live trading success.
**Rule:** Every strategy must pass 3+ months of profitable paper trading before real money.

### 4. What You Claim vs What You Code
**Source:** review.md
**Lesson:** Be honest about what the strategy actually does. Technical trading is fine; claiming it's "value investing" when it's 100% technical is misleading to yourself.
**Rule:** Match strategy description to actual implementation.

### 5. Small Sample Sizes Mislead
**Source:** EXP-2025-001
**Lesson:** 6 trades in a year is not statistically significant, even if Sharpe > 2.
**Rule:** Minimum 20-30 trades needed for meaningful statistics. Preferably 100+.

### 6. Always Use Stop-Loss
**Source:** review.md, EXP-2025-002
**Lesson:** No stop-loss = risking total account loss. Even "value investors" cut losses.
**Rule:** 20% hard stop-loss minimum for prototype strategies. 5-10% for more conservative.

---

## Data Pipeline Lessons

### Yahoo Finance Data Quality
| Issue | Learning | Status |
|-------|----------|--------|
| Filename mismatch | Files may be named differently than content (e.g., "nvda" contains S&P 500 data) | Known |
| Missing columns | Always validate column existence before use | Fixed |

### AI Signal Generation
| Issue | Learning | Status |
|-------|----------|--------|
| Look-ahead bias in sentiment | Must use lagged signals or news-based sentiment | Fixed in EXP-2025-001 |
| Correlation check | Always verify signal vs returns correlation | Now part of validation |

---

## Strategy Design Lessons

### Entry Rules
| What We Tried | What Worked | What Didn't |
|---------------|-------------|-------------|
| Tight thresholds (entry > 0.2) | Conservative, good Sharpe | Only 6 trades/year |
| **Lowered thresholds (entry > 0.0)** | **15 trades avg, better Sharpe** | Lower absolute return vs B&H |
| Mean reversion in sideways | Works in ranging markets | Less effective in strong trends |

### Exit Rules
| What We Tried | What Worked | What Didn't |
|---------------|-------------|-------------|
| Sentiment-based exits | Partially effective | Need clearer rules |
| | | No stop-loss implemented |

### Risk Management
| What We Tried | What Worked | What Didn't |
|---------------|-------------|-------------|
| Position sizing by volatility | Dynamic thresholds working | No hard stop-loss |
| | | No max drawdown limit |

---

## Market Regime Lessons

### Bull Markets (AI_Regime_Score > 0.5)
| Strategy | Performance | Notes |
|----------|-------------|-------|
| Adaptive Aggressive | 1 trade (old), 24 trades (new) | Too selective originally |
| NVDA 2023 | Sharpe 1.83, Return 94% | Missed 230% B&H due to early exits |

### Bear Markets (AI_Regime_Score < -0.5)
| Strategy | Performance | Notes |
|----------|-------------|-------|
| Adaptive Defensive | 0 trades | Strategy avoids shorts |

### Sideways (-0.5 <= AI_Regime_Score <= 0.5)
| Strategy | Performance | Notes |
|----------|-------------|-------|
| Mean Reversion | 5-24 trades depending on ticker | Most active mode |

---

## Multi-Ticker Findings (EXP-2025-003)

### Cross-Ticker Performance (2023)

| Ticker | Sharpe (Adaptive) | Sharpe (B&H) | Winner |
|--------|-------------------|--------------|--------|
| NVDA | 1.83 | 1.42 | Adaptive ✓ |
| AAPL | 2.10 | 1.75 | Adaptive ✓ |
| SPY | 1.52 | 1.63 | Buy&Hold ✓ |

**Key Insight:** Strategy consistently beats Buy&Hold on risk-adjusted basis (Sharpe) for volatile stocks (NVDA, AAPL), but may underperform on smooth indices (SPY).

### Trade Frequency by Ticker

| Ticker | Trades | Assessment |
|--------|--------|------------|
| NVDA | 24 | Good |
| AAPL | 14 | OK |
| SPY | 8 | Low - index less volatile |

---

## Technical Implementation Lessons

### Code Quality
| Issue | Learning | Action |
|-------|----------|--------|
| Hardcoded parameters | Difficult to tune | Moved to parameter classes |
| No bias validation | Look-ahead went undetected | Added correlation checks |

### Performance
| Issue | Learning | Action |
|-------|----------|--------|
| | | |

### Bugs Found
| Bug | Impact | Fix | Status |
|-----|--------|-----|--------|
| Look-ahead bias in `add_ai_stock_sentiment()` | Invalid backtest results | Use `.shift(1)` on sentiment | Fixed in EXP-2025-002 |
| No stop-loss mechanism | Risk of total loss | Added 20% hard stop + 5% trailing | Fixed in EXP-2025-002 |
| Data file naming confusion | Analysis errors | Added validate_data() function | Fixed in EXP-2025-002 |

---

## Mental Model Updates

### Things I Used to Believe (But Were Wrong)
| Wrong Belief | Evidence | Correct Belief |
|--------------|----------|----------------|
| Fake sentiment is good enough for testing | EXP-2025-001 showed bias | Real sentiment from news required |
| High Sharpe always means good strategy | Sharpe 2.03 with only 6 trades | Sample size matters more |
| Value investing with technical indicators | review.md showed mismatch | Be honest about strategy type |

### Things I Was Right About
| Belief | Evidence | Next Steps |
|--------|----------|------------|
| Regime-based approach has merit | Strategy worked in all regimes | Add more entry signals |
| VIX is useful for regime detection | Good regime classification | Add more indicators |
| **Defensive strategy wins in bear markets** | **2022: +13% vs -31% for B&H** | Consider more aggressive bull mode |

---

## Bear Market Findings (EXP-2025-004)

### 2022 Bear Market Performance

| Ticker | Adaptive Return | B&H Return | Outperformance |
|--------|-----------------|------------|---------------|
| NVDA | +18.68% | -47.94% | **+66.62%** |
| AAPL | +3.87% | -26.35% | **+30.22%** |
| SPY | +16.84% | -18.12% | **+34.96%** |

### Key Lessons from Bear Market Test

1. **Defensive mode works**: High VIX triggered appropriate caution
2. **Stop-loss validated**: Prevented catastrophic 50%+ NVDA losses
3. **Mean reversion profits**: Volatile swings = opportunities
4. **Drawdown protection**: 9.70% vs 36.28% average drawdown

### Strategy Character Confirmed

| Market Type | Strategy Behavior | Result |
|-------------|-------------------|--------|
| Bull Market | Conservative, early exits | Lower return, lower risk |
| Bear Market | Defensive, mean reversion | **Profitable**, protects capital |

**This is a defensive/conservative strategy, not a momentum chaser.**

---

## Bull Market Optimization Lessons (EXP-2025-006)

### What We Tried
- ADX trend strength filter to detect strong trends
- 5% trailing stop to "let winners run"
- Skipping mean reversion in strong trends

### What Happened
- NVDA 2023: -9.52% → -20.46% (WORSE!)
- Trades: 25 → 10 (60% reduction)
- Trailing stop caused whipsaw hell

### Key Learning
**Trailing stops are tricky in volatile markets.** 5% stop triggered too frequently, causing:
- Exit on pullback
- Miss continuation
- Re-entry too late

**This approach is DEAD.** Do not revisit.

---

## From EXP-2025-008 (LLM Sanity Check) - ACTIVE

### Key Difference from EXP-005

| Aspect | EXP-005 (Failed) | EXP-008 (Active) |
|--------|------------------|------------------|
| Trigger | LLM asks for sentiment | Price moves FIRST, then LLM validates |
| Role | Decision maker | Auditor/Filter |
| Output | Positive/Negative | FADE/FOLLOW/IGNORE + substance score |
| Goal | Predict direction | Prevent FOMO/Panic mistakes |

### Hypothesis
Using LLM to validate whether extreme price moves (>3%) are justified by actual news substance will:
1. Reduce drawdown by avoiding "pump and dump" rallies
2. Improve win rate by buying dips when news is overreaction

### Design Decisions
- **Only call LLM on volatility spikes** (>3% move) - saves API costs
- **Skeptical prompt** - Default to "this is bullshit" until proven otherwise
- **JSON output** - Strict format for programmatic trading decisions
- **Shadow testing first** - Cannot backtest historically (need precise news + timestamps)

### Decision Matrix

| Condition | LLM Analysis | Action |
|-----------|--------------|--------|
| Price UP + Low substance | Hype/Noise | SHORT_SCALP (sell the rip) |
| Price UP + High substance | Real news | BUY_TREND (follow) |
| Price DOWN + Low substance | Overreaction | BUY_DIP (contrarian) |
| Price DOWN + High substance | Real trouble | HARD_EXIT (don't catch knife) |

### TBD (Learning in Progress)
- [ ] LLM accuracy on real-time news validation
- [ ] API cost per month with trigger-based approach
- [ ] Optimal substance score thresholds (currently 4/7)
- [ ] Integration with frozen Adaptive Strategy

---

## Questions to Answer

### Open Questions
- [ ] How to increase trade frequency while maintaining risk-adjusted returns?
- [x] ~~Should we use trailing stop for bull markets?~~ NO - EXP-006 proved this hurts performance
- [ ] What's the optimal stop-loss level for this strategy?
- [ ] Should we add fundamental filters (PE, PBV)?

### Hypotheses to Test
- [x] ~~Trailing stop + ADX filter improves bull market~~ FAILED - made performance worse
- [ ] Real news sentiment will outperform heuristic sentiment
- [ ] Lowering entry thresholds will increase trade frequency
- [ ] Adding a 15% stop-loss will improve risk-adjusted returns
- [ ] Multi-ticker testing will reveal if strategy is robust

---

## From EXP-2025-001 (Look-Ahead Bias Fix)

### Key Findings
1. **Look-ahead bias confirmed**: 0.78 correlation between sentiment and same-day returns
2. **Fix works**: Lagged sentiment (shift) actually performed better (Sharpe 2.03 vs 1.88)
3. **Low trade frequency**: Only 6 trades in 250 days
4. **Doesn't beat Buy & Hold**: Return 17% vs 22% for B&H

### Action Items
1. [ ] Implement real news sentiment
2. [ ] Test on multiple tickers
3. [ ] Add stop-loss mechanism
4. [ ] Increase trade frequency

---

## Resource Reference

### Books/Articles Found Useful
- [ ] *Advances in Financial Machine Learning* - Marcos Lopez de Prado
- [ ] *Quantitative Trading* - Ernest Chan

### Tools/Libraries Found Useful
- [x] `backtesting` library - Easy backtesting framework
- [x] `yfinance` - Free market data
- [x] `pandas` - Data manipulation
- [ ] MLflow / Weights & Biases - Experiment tracking (future)

### External References
- [ ] Look-ahead bias: https://www.investopedia.com/terms/l/lookahead-bias.asp
- [ ] Backtesting best practices: https://quantopian.com/posts/the-balance-of-overfitting-and-underfitting
