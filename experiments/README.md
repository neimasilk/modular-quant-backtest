# Experiments Directory

This directory contains all experimental work for the modular quant backtest project.

## Directory Structure

```
experiments/
├── README.md              # This file
├── EXPERIMENT_INDEX.md    # Master index of all experiments
├── LESSONS_LEARNED.md     # Key insights across all experiments
│
├── templates/             # Experiment templates
│   └── experiment.md      # Standard experiment template
│
├── active/                # Currently running/partial experiments
│   ├── EXP-2025-003-multi-ticker-test/
│   ├── EXP-2025-004-bear-market-2022/
│   └── EXP-2025-005-real-news-sentiment/
│
├── completed/             # Recently finished experiments
│   ├── EXP-2025-001-fix-look-ahead-bias/
│   └── EXP-2025-002-critical-fixes/
│
└── archived/              # Old experiments (organized by outcome)
    ├── failed/            # Strategies that didn't work
    │   └── EXP-2025-006-bull-market-optimization/
    ├── successful/        # Strategies that worked
    └── partial/           # Partial successes, may revisit
```

## Quick Start

### Starting a New Experiment

```bash
# 1. Create experiment folder with today's date and title
mkdir experiments/active/EXP-2025-001-fix-look-ahead-bias

# 2. Copy the template
cp experiments/templates/experiment.md experiments/active/EXP-2025-001-fix-look-ahead-bias/README.md

# 3. Fill in the hypothesis and parameters

# 4. Run your experiment

# 5. Move outputs to experiment folder
```

### Experiment Naming Convention

```
EXP-YYYY-NNN-short-title
```

- **YYYY:** Current year (2025)
- **NNN:** Sequential experiment number (001, 002, ...)
- **short-title:** kebab-case descriptive title

Examples:
- `EXP-2025-001-rsi-mean-reversion`
- `EXP-2025-002-vix-regime-detection`
- `EXP-2025-003-sentiment-analysis-fix`

## Workflow

1. **Create** - New experiment from template in `experiments/active/`
2. **Execute** - Run backtest with documented parameters
3. **Analyze** - Review results against success criteria
4. **Decide** - Promote, iterate, or archive
5. **Archive** - Move to appropriate folder in `experiments/archived/`
6. **Update** - Add entry to `EXPERIMENT_INDEX.md`

See `EXPERIMENT_WORKFLOW.md` (in project root) for detailed workflow guide.

## Monthly Maintenance

Once per month:
1. Review all experiments in `active/` and `completed/`
2. Move finished experiments to `archived/`
3. Update `EXPERIMENT_INDEX.md`
4. Add key learnings to `LESSONS_LEARNED.md`
5. Compress/delete old raw data files (keep configs and results)

## Important Notes

- **Never delete failed experiments** - They prevent repeated mistakes
- **Always document before coding** - Write hypothesis first
- **Update index after each experiment** - Keeps everything searchable
- **Use version control** - Each experiment can be a git branch

## Related Documentation

- `../EXPERIMENT_WORKFLOW.md` - Detailed workflow guide
- `../ROADMAP.md` - Project roadmap
- `../README.md` - Main project documentation
