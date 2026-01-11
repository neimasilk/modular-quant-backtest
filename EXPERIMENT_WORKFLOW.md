# Experiment Workflow Guide

> **Purpose:** Ensure every experiment is documented, reproducible, and learnings are preserved
> **Audience:** Anyone working on the quant backtest project

---

## The Experiment Lifecycle

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   1. IDEATE     │ -> │   2. PLAN       │ -> │   3. EXECUTE    │
│  "What if..."   │    │  Define params  │    │  Run backtest  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       v
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   6. ARCHIVE    │ <- │   5. DECIDE     │ <- │   4. ANALYZE    │
│  Store results  │    │  Continue/Stop  │    │  Review metrics │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## Phase 1: IDEATE - Define Your Hypothesis

### What makes a good hypothesis?
- **Specific:** Not "make money" but "momentum strategy works better in low VIX"
- **Testable:** Can be proven wrong with data
- **Grounded:** Based on some market insight or research

### Example Hypotheses

| Good Hypothesis | Bad Hypothesis |
|-----------------|----------------|
| "RSI < 20 + VIX < 20 produces mean reversion opportunities" | "Make the bot smarter" |
| "News sentiment leads price by 1-2 days" | "Use more AI" |
| "Stop-loss at -15% improves risk-adjusted returns" | "Fix the strategy" |

### Output
Create a new experiment file: `experiments/active/EXP-YYYY-MMDD-title.md`

---

## Phase 2: PLAN - Define Parameters

### Experiment Template (copy this for each experiment)

```markdown
# EXP-2025-001: [Title]

**Status:** Active | Planned | Completed | Archived
**Created:** 2025-01-11
**Author:** [Your Name]

## Hypothesis
[Your specific hypothesis here]

## Strategy
- Type: [Momentum / Mean Reversion / Regime-Based / Hybrid]
- Entry: [Clear entry rules]
- Exit: [Clear exit rules]
- Position Sizing: [How much to buy/sell]

## Parameters
```python
# Backtest Config
start_date = "2023-01-01"
end_date = "2024-01-01"
initial_cash = 10000
commission = 0.001

# Strategy Config
# [List all strategy parameters]
```

## Data
- Ticker(s): [NVDA, SPY, etc.]
- Timeframe: [Daily, Hourly]
- Data Source: [Yahoo Finance, etc.]

## Success Criteria
- Primary: [e.g., Sharpe Ratio > 1.0]
- Secondary: [e.g., Max Drawdown < 20%]
- Benchmark: [Buy & Hold performance]

## Execution Command
```bash
python main.py --ticker NVDA --start 2023-01-01 --end 2024-01-01
```

## Results
[Fill after execution]

## Analysis
[What worked, what didn't, what's surprising]

## Decision
- [ ] Promote to next testing phase
- [ ] Iterate with modifications
- [ ] Archive as failed experiment
- [ ] Archive as successful (document for production)

## Next Steps
[What to do next based on results]
```

---

## Phase 3: EXECUTE - Run the Experiment

### Before Running
1. [ ] Check no look-ahead bias in data
2. [ ] Verify parameters are saved
3. [ ] Ensure output directory is clean
4. [ ] Note the commit hash (for reproducibility)

### During Execution
- Monitor for errors or anomalies
- Check if execution time is reasonable

### After Execution
1. [ ] Copy all output files to experiment folder
2. [ ] Save the exact command used
3. [ ] Note any deviations from plan

### Files to Save
```
experiments/active/EXP-2025-001/
├── README.md              # Experiment template (filled)
├── config.json            # Exact parameters used
├── results/
│   ├── equity_curve.csv
│   ├── trades.csv
│   └── metrics.json
├── plots/
│   ├── equity_curve.png
│   └── drawdown.png
└── notes.md               # Additional observations
```

---

## Phase 4: ANALYZE - Review Results

### Key Metrics to Check

| Metric | Good | Warning | Bad |
|--------|------|---------|-----|
| Sharpe Ratio | > 1.5 | 0.5 - 1.5 | < 0.5 |
| Max Drawdown | < 15% | 15-25% | > 25% |
| Win Rate | > 55% | 45-55% | < 45% |
| CAGR | > 20% | 10-20% | < 10% |

### Red Flags (Immediate Investigation Needed)
- Sharpe Ratio > 3.0 (too good to be true = likely bug or bias)
- Perfect equity curve (straight line up = look-ahead bias)
- Negative correlation with benchmark (data error?)
- 100% win rate (impossible in real trading)

### Questions to Answer
1. Did it beat buy-and-hold?
2. Was the risk acceptable?
3. Did it perform differently in different market regimes?
4. Are there any suspicious patterns?

---

## Phase 5: DECIDE - What's Next?

### Decision Tree

```
                    ┌─────────────────────────────────┐
                    │   Did it meet success criteria? │
                    └─────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │ NO                          │ YES
                    ▼                             ▼
            ┌───────────────┐           ┌───────────────┐
            │ Any merit?    │           │ Out-of-sample │
            └───────────────┘           │ test needed?  │
                    │                   └───────────────┘
            ┌───────┴───────┐                   │
            │ NO           │ YES        ┌──────┴──────┐
            ▼              ▼            │ NO         │ YES
    ┌───────────┐  ┌────────────┐       ▼            ▼
    │ ARCHIVE   │  │ ITERATE   │  ┌─────────┐  ┌──────────┐
    │ (Failed)  │  │ Modify &  │  │ PAPER   │  │ PROMOTE  │
    └───────────┘  │ Re-test   │  │ TRADE   │  │ (Cand.)  │
                   └────────────┘  └─────────┘  └──────────┘
```

### Possible Actions

| Action | When | Why |
|--------|------|-----|
| **Archive Failed** | Metrics bad, no redeeming value | Failed experiments are still valuable |
| **Iterate** | Partial success, clear improvement path | Small modification might work |
| **Paper Trade** | Good backtest, needs real-world test | Simulated trading with IBKR paper account |
| **Promote** | Excellent results across tests | Ready for production consideration |

---

## Phase 6: ARCHIVE - Preserve Knowledge

### Folder Structure After Completion

```
experiments/
├── active/           # Currently running experiments
├── completed/        # Recently finished (review monthly)
└── archived/         # Organized by outcome
    ├── successful/   # Strategies that worked
    ├── failed/       # Strategies that didn't work
    └── partial/      # Partial successes, may revisit
```

### Archive Checklist
- [ ] Move experiment folder to appropriate archive subfolder
- [ ] Update EXPERIMENT_INDEX.md with summary
- [ ] Add any key learnings to LESSONS_LEARNED.md
- [ ] Delete or compress large raw data files (keep config/results)

### Experiment Index Template

Append to `experiments/EXPERIMENT_INDEX.md`:

```markdown
## EXP-2025-001: [Title]

- **Date:** 2025-01-11
- **Hypothesis:** [One-line summary]
- **Result:** [Sharpe: X, CAGR: Y%, MaxDD: Z%]
- **Outcome:** [Success/Failed/Partial]
- **Key Learning:** [One sentence]
- **Link:** [./archived/.../EXP-2025-001/](./archived/.../EXP-2025-001/)
```

---

## Daily Experiment Workflow (Quick Reference)

### Starting a New Experiment
```bash
# 1. Create new experiment folder
mkdir experiments/active/EXP-2025-001

# 2. Copy template
cp experiments/templates/experiment.md experiments/active/EXP-2025-001/README.md

# 3. Fill in the hypothesis and parameters

# 4. Run the experiment
python main.py [your params]

# 5. Move outputs to experiment folder
mv output/* experiments/active/EXP-2025-001/results/

# 6. Document results and decision
```

### Weekly Review (15 minutes)
1. Check all experiments in `active/` - move to `completed/` if done
2. Update `EXPERIMENT_INDEX.md`
3. Archive old completed experiments
4. Review `LESSONS_LEARNED.md` for patterns

---

## Anti-Patterns (Things to Avoid)

| Don't Do | Why | Alternative |
|----------|-----|-------------|
| Run experiments without documentation | You'll forget what you tested | Always use template |
| Delete "failed" experiments | Failed experiments prevent repeated mistakes | Archive with clear notes |
| Change parameters mid-experiment | Results become unreproducible | Create new experiment ID |
| Only document successes | Failures contain valuable data | Document everything |
| Overwrite previous results | Lose ability to compare | Create new experiment folder |

---

## Experiment Tracking Template Files

The following templates will be created:
- `experiments/templates/experiment.md` - Main experiment template
- `experiments/EXPERIMENT_INDEX.md` - Master index of all experiments
- `experiments/LESSONS_LEARNED.md` - Key insights across all experiments

---

## Git Integration

### Commit Strategy
```bash
# Each experiment gets its own branch
git checkout -b exp/2025-001-rsi-mean-reversion

# Document experiment in commit
git commit -m "EXP-2025-001: Test RSI mean reversion

- Hypothesis: RSI < 20 in low VIX produces mean reversion
- Result: Sharpe 0.8, MaxDD 18%
- Decision: Iterate with different RSI threshold"

# Merge to main only if promoting strategy
```

---

## Next Steps

1. [ ] Create the directory structure
2. [ ] Copy the experiment template
3. [ ] Set up EXPERIMENT_INDEX.md
4. [ ] Start your first documented experiment: fixing the look-ahead bias
