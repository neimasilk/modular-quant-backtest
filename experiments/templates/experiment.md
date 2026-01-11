# EXP-YYYY-NNN: [Experiment Title]

**Status:** Active | Planned | Completed | Archived
**Created:** YYYY-MM-DD
**Author:** [Your Name]
**Tags:** [strategy-type, ticker, etc.]

---

## Hypothesis

[Write a clear, testable hypothesis here]

**Example:** "RSI < 20 combined with VIX < 20 produces profitable mean reversion opportunities on NASDAQ stocks."

---

## Strategy Definition

### Type
- [ ] Momentum
- [ ] Mean Reversion
- [ ] Regime-Based
- [ ] Hybrid
- [ ] Other: ___________

### Entry Rules
[Describe exactly when to enter a position]

### Exit Rules
[Describe exactly when to exit a position]

### Position Sizing
[Describe how much capital to allocate]

### Risk Management
- [ ] Stop-loss: _____%
- [ ] Take-profit: _____%
- [ ] Max position size: _____%
- [ ] Other: ___________

---

## Parameters

```python
# Backtest Configuration
ticker = "NVDA"
start_date = "2023-01-01"
end_date = "2024-01-01"
initial_cash = 10000
commission = 0.001

# Strategy Parameters
# [List all strategy-specific parameters here]
param_1 = value_1
param_2 = value_2
```

---

## Data

| Source | Ticker(s) | Timeframe | Notes |
|--------|-----------|-----------|-------|
| Yahoo Finance | NVDA | Daily | Real market data |

---

## Success Criteria

| Metric | Target | Actual (fill later) |
|--------|--------|-------------------|
| Sharpe Ratio | > 1.0 | _____ |
| Sortino Ratio | > 1.5 | _____ |
| Max Drawdown | < 20% | _____ |
| CAGR | > 15% | _____ |
| Win Rate | > 50% | _____ |

**Benchmark:** Buy & Hold on same ticker

---

## Execution Command

```bash
python main.py --ticker NVDA --start 2023-01-01 --end 2024-01-01
```

**Git Commit:** [Hash or branch name]

---

## Results (Fill After Execution)

### Performance Metrics
```
Sharpe Ratio: _____
Sortino Ratio: _____
Max Drawdown: _____%
CAGR: _____%
Win Rate: _____%
Total Return: _____%
```

### Comparison vs Benchmark
| Metric | Strategy | Buy & Hold | Delta |
|--------|----------|------------|-------|
| Total Return | _____% | _____% | _____% |
| Max Drawdown | _____% | _____% | _____% |
| Sharpe Ratio | _____ | _____ | _____ |

### Output Files
- [ ] `equity_curve.csv`
- [ ] `trades.csv`
- [ ] `metrics.json`
- [ ] `equity_curve.png`
- [ ] `drawdown.png`

---

## Analysis

### What Worked
[Document what aspects of the strategy performed well]

### What Didn't Work
[Document what aspects failed or underperformed]

### Surprising Findings
[Any unexpected results or patterns]

### Potential Biases
- [ ] Look-ahead bias: [Check and confirm/deny]
- [ ] Survivorship bias: [Check and confirm/deny]
- [ ] Overfitting: [Check and confirm/deny]
- [ ] Other: ___________

---

## Decision

- [ ] **Promote** - Move to next testing phase (out-of-sample/paper trading)
- [ ] **Iterate** - Modify parameters and re-test (document what to change)
- [ ] **Archive as Successful** - Strategy is ready for production consideration
- [ ] **Archive as Failed** - Strategy does not work
- [ ] **Archive as Partial** - Some merit, but not enough to continue now

**Decision Date:** YYYY-MM-DD
**Reasoning:** [Explain why this decision was made]

---

## Next Steps

[Based on the decision above, what should happen next?]

---

## Lessons Learned

[What did this experiment teach you? What would you do differently?]

---

## References

- [Link to related research/ideas]
- [Previous experiments that informed this one]
- [Any other relevant context]
