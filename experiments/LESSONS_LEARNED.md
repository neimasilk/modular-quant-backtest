# Lessons Learned

> **Purpose:** distilled insights from all experiments to prevent repeated mistakes
> **Last Updated:** 2025-01-11

---

## Critical Lessons (Must Read Before Any Experiment)

### 1. Look-Ahead Bias is the Silent Killer
**Source:** review.md (Initial Code Review)
**Lesson:** Never use future data to generate signals. The original code created `AI_Stock_Sentiment` from `Daily_Return` - this means the strategy "knew" the future.
**Rule:** Always verify that signal data comes from time T-1 or earlier for decisions at time T.

### 2. Backtest Sharpe > 3.0 is Suspicious
**Lesson:** Real strategies rarely achieve Sharpe > 3 without look-ahead bias or data errors.
**Rule:** If Sharpe > 3, immediately check for:
- Look-ahead bias
- Data errors
- Future information leakage
- Overfitting

### 3. Paper Trading Before Real Money
**Lesson:** Backtest success ≠ live trading success.
**Rule:** Every strategy must pass 3+ months of profitable paper trading before real money.

### 4. What You Claim vs What You Code
**Source:** review.md - "Value Investing" claim vs 100% technical code
**Lesson:** Be honest about what the strategy actually does. Technical trading is fine; claiming it's value investing when it's not is misleading to yourself.
**Rule:** Match strategy description to actual implementation.

---

## Data Pipeline Lessons

### Yahoo Finance Data Quality
| Issue | Learning | Status |
|-------|----------|--------|
| | | |

### AI Signal Generation
| Issue | Learning | Status |
|-------|----------|--------|
| Look-ahead bias in sentiment | Must use lagged signals or news-based sentiment | Known issue |
| | | |

---

## Strategy Design Lessons

### Entry Rules
| What We Tried | What Worked | What Didn't |
|---------------|-------------|-------------|
| | | |

### Exit Rules
| What We Tried | What Worked | What Didn't |
|---------------|-------------|-------------|
| | | |

### Risk Management
| What We Tried | What Worked | What Didn't |
|---------------|-------------|-------------|
| | | |

---

## Market Regime Lessons

### Bull Markets
| Strategy | Performance | Notes |
|----------|-------------|-------|
| | | |

### Bear Markets
| Strategy | Performance | Notes |
|----------|-------------|-------|
| | | |

### High Volatility (VIX > 30)
| Strategy | Performance | Notes |
|----------|-------------|-------|
| | | |

### Low Volatility (VIX < 15)
| Strategy | Performance | Notes |
|----------|-------------|-------|
| | | |

---

## Technical Implementation Lessons

### Code Quality
| Issue | Learning | Action |
|-------|----------|--------|
| | | |

### Performance
| Issue | Learning | Action |
|-------|----------|--------|
| | | |

### Bugs Found
| Bug | Impact | Fix |
|-----|--------|-----|
| | | |

---

## Mental Model Updates

### Things I Used to Believe (But Were Wrong)
| Wrong Belief | Evidence | Correct Belief |
|--------------|----------|----------------|
| | | |

### Things I Was Right About
| Belief | Evidence | Next Steps |
|--------|----------|------------|
| | | |

---

## Questions to Answer

### Open Questions
- [ ] [Question 1]
- [ ] [Question 2]

### Hypotheses to Test
- [ ] [Hypothesis 1]
- [ ] [Hypothesis 2]

---

## Resource Reference

### Books/Articles Found Useful
- [ ] *Advances in Financial Machine Learning* - Marcos Lopez de Prado
- [ ] [Add more]

### Tools/Libraries Found Useful
- [ ] [Tool 1]
- [ ] [Tool 2]

### External References
- [ ] [Link 1]
- [ ] [Link 2]
