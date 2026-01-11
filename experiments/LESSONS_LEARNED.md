# Lessons Learned

> **Purpose:** Distilled insights from all experiments to prevent repeated mistakes
> **Last Updated:** 2025-01-11

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
| Regime-based thresholds (VIX) | Good for regime classification | Low trade frequency (6/year) |
| Mean reversion in sideways | Works but needs more trades | Too selective |

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
| Adaptive Aggressive | 1 trade only | Too selective |

### Bear Markets (AI_Regime_Score < -0.5)
| Strategy | Performance | Notes |
|----------|-------------|-------|
| Adaptive Defensive | 0 trades | Strategy avoids shorts |

### Sideways (-0.5 <= AI_Regime_Score <= 0.5)
| Strategy | Performance | Notes |
|----------|-------------|-------|
| Mean Reversion | 5 trades | Most active mode |

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
| Bug | Impact | Fix |
|-----|--------|-----|
| Look-ahead bias in `add_ai_stock_sentiment()` | Invalid backtest results | Use `.shift(1)` on sentiment |
| Data file naming confusion | Analysis errors | Validate data contents |

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
| | | |

---

## Questions to Answer

### Open Questions
- [ ] How to increase trade frequency while maintaining risk-adjusted returns?
- [ ] Should we implement real news sentiment (NewsAPI, Alpha Vantage)?
- [ ] What's the optimal stop-loss level for this strategy?
- [ ] Should we add fundamental filters (PE, PBV)?

### Hypotheses to Test
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
