# Shadow Trading Setup Guide - EXP-2025-009

## Purpose

Validate REAL LLM accuracy before committing to paper trading with real capital.

## Prerequisites

### 1. DeepSeek API Key

You need a DeepSeek API key to run real LLM analysis.

**Get your API key:**
1. Visit https://platform.deepseek.com/
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-...`)

**Pricing:** ~$0.10-0.30 per call (very affordable)

### 2. Environment Setup

**Option A: Create .env file (recommended)**

```bash
# From project root
cp .env.example .env

# Edit .env and add your API key:
echo "DEEPSEEK_API_KEY=sk-your-actual-key-here" >> .env
```

**Option B: Set environment variable**

```bash
# Linux/Mac
export DEEPSEEK_API_KEY="sk-your-actual-key-here"

# Windows PowerShell
$env:DEEPSEEK_API_KEY="sk-your-actual-key-here"
```

### 3. Install Dependencies

```bash
# If not already installed
pip install yfinance openai python-dotenv pandas
```

## Running Shadow Trading

### Quick Test (1 ticker, 5 days)

```bash
cd experiments/active/EXP-2025-009-hybrid-llm

python shadow_trading.py --ticker NVDA --days 5
```

**Expected output:**
```
✅ LLM Sanity Checker initialized
📊 Fetching 5 days of data for NVDA...
   ✅ Fetched 5 bars from 2026-01-09 to 2026-01-14

🔍 Analyzing NVDA on 2026-01-10
   Price change: +3.5%
   News: NVIDIA announces new AI chip partnership...
   🤖 LLM: BUY_TREND (score: 8/10)
   💡 Reasoning: Strong partnership news, justified move

...

💾 Results saved to: shadow_logs/shadow_decisions_20260114_101530.json

SHADOW TRADING SUMMARY
========================
📊 Total LLM Calls: 3
Signal Distribution:
   BUY_TREND: 2
   SHORT_SCALP: 1

📈 Average Substance Score: 6.3/10
```

### Multi-Ticker Test

```bash
python shadow_trading.py --ticker NVDA,AAPL,TSLA --days 10
```

### Generate Accuracy Report (after waiting 1-3 days)

```bash
python shadow_trading.py --report
```

This will:
1. Load previous shadow trading decisions
2. Fetch actual price outcomes
3. Calculate LLM accuracy
4. Generate detailed report

## Success Criteria

| Metric | Target | Why |
|--------|--------|-----|
| **LLM Accuracy** | >65% | Below this, filter adds noise not signal |
| **Substance Scoring** | Avg 5-7/10 | Shows balanced skepticism |
| **FADE calls** | 30-40% | Healthy contrarian signal rate |
| **FOLLOW calls** | 30-40% | Balanced with FADE |
| **API Cost** | <$5/day | Economic viability |

## Interpreting Results

### Good Signs ✅

- LLM accuracy >65% on predicting outcomes
- Substance scores vary (1-10 range used fully)
- Mix of FADE and FOLLOW verdicts (not one-sided)
- Reasoning makes sense when reviewed manually

### Red Flags ⚠️

- LLM accuracy <60% (worse than coin flip)
- All substance scores 5-6 (not differentiating)
- 90%+ FADE or 90%+ FOLLOW (overfitting to one pattern)
- Reasoning is generic/repetitive

## Troubleshooting

### "DEEPSEEK_API_KEY not found in environment"

**Solution:**
```bash
# Check if key is set
echo $DEEPSEEK_API_KEY

# If empty, set it:
export DEEPSEEK_API_KEY="sk-your-key-here"

# Or create .env file (see step 2 above)
```

### "No data fetched for ticker"

**Solution:**
- Check ticker symbol is correct (use Yahoo Finance symbols)
- Try extending --days parameter
- Check internet connection

### "LLM call failed: 401 Unauthorized"

**Solution:**
- Verify API key is correct
- Check if API key has been activated
- Ensure DeepSeek account has credits

### "Rate limit exceeded"

**Solution:**
- Add delays between calls (modify script)
- Reduce number of tickers or days
- Wait and retry later

## Cost Estimation

### Per Session

| Setup | LLM Calls | Cost |
|-------|-----------|------|
| 1 ticker, 5 days | 0-5 calls | $0-1.50 |
| 3 tickers, 10 days | 0-30 calls | $0-9.00 |
| 5 tickers, 20 days | 0-100 calls | $0-30.00 |

**Note:** Only volatile moves (>3% change) trigger LLM calls, so actual cost is usually much lower than maximum.

### Monthly (if running daily)

- Daily scan (3 tickers): ~$10-30/month
- Daily scan (10 tickers): ~$30-100/month

**This is AFFORDABLE** for validation phase.

## Next Steps After Shadow Trading

### If LLM Accuracy >65%

1. ✅ **Proceed to Paper Trading**
   - Integrate with EXP-008 paper trading system
   - Run for 1-3 months
   - Track real P&L

2. ✅ **Fine-tune LLM Prompt**
   - Adjust system prompt based on errors
   - Test different substance score thresholds
   - Optimize for your risk tolerance

### If LLM Accuracy 55-65%

1. ⚠️ **Prompt Engineering**
   - Review wrong calls manually
   - Adjust prompt to fix common mistakes
   - Re-run shadow trading

2. ⚠️ **Threshold Tuning**
   - Maybe 3% threshold is too low
   - Test 5% threshold (only extreme moves)

### If LLM Accuracy <55%

1. ❌ **Pause and Reassess**
   - LLM may not add value in current form
   - Consider different LLM model (GPT-4, Claude, etc.)
   - Archive experiment, focus on other strategies

## Files Generated

```
experiments/active/EXP-2025-009-hybrid-llm/
└── shadow_logs/
    ├── shadow_decisions_20260114_101530.json    # Full decision log
    ├── shadow_decisions_20260114_101530.csv     # CSV for analysis
    ├── shadow_decisions_20260115_093022.json
    └── ...
```

## Manual Review

**After each session:**

1. Open JSON file in shadow_logs/
2. Review 5-10 decisions manually
3. Ask yourself:
   - Does the reasoning make sense?
   - Would I have made the same call?
   - Is substance score justified?

**This manual review is CRITICAL** - don't just trust accuracy numbers.

## Timeline

| Week | Activity | Goal |
|------|----------|------|
| **Week 1** | Daily shadow trading (3-5 tickers) | Collect 20-30 decisions |
| **Week 2** | Generate accuracy report | Measure >65% accuracy |
| **Week 3** | Prompt tuning (if needed) | Improve to >70% |
| **Week 4** | Final validation | Confirm stable accuracy |

**Total:** 3-4 weeks before paper trading decision.

## Questions?

Review:
- `shadow_trading.py` - Source code
- `analysis.md` - Backtest results
- `README.md` - Full experiment documentation

---

**Status:** Ready for shadow trading
**Next Action:** Run `python shadow_trading.py --ticker NVDA --days 5` to start
