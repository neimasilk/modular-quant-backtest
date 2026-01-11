# Value Investing Exploration - Clean Slate

**Start Date:** 2025-01-11
**Status:** Planning Phase

---

## Why Value Investing?

The frozen AdaptiveStrategy is purely technical. Value investing offers:
- **Fundamental-based signals** - Different data source than price
- **Uncorrelated returns** - Not dependent on technical patterns
- **Long-term focus** - Less sensitive to daily noise
- **Proven track record** - Graham, Buffett, Klarman style

---

## What is Value Investing?

**Core Principle:** Buy assets trading below intrinsic value.

**Key Metrics:**
- P/E Ratio (Price to Earnings)
- P/B Ratio (Price to Book)
- P/S Ratio (Price to Sales)
- EV/EBITDA (Enterprise Value to EBITDA)
- FCF Yield (Free Cash Flow / Market Cap)
- Dividend Yield

**Value Screen Criteria (Example):**
```
P/E < 15
P/B < 1.5
Debt/Equity < 0.5
ROE > 15%
FCF positive
```

---

## Action List

### Phase 1: Research & Design (Week 1)

- [ ] **1.1** Study value investing fundamentals
  - Read: "The Intelligent Investor" summary
  - Read: Quantitative value investing papers
  - Document key principles

- [ ] **1.2** Design strategy architecture
  - Input: Fundamental data (PE, PB, ROE, etc.)
  - Screening: Filter universe by value criteria
  - Ranking: Score stocks by value metrics
  - Portfolio: Hold top N stocks
  - Rebalancing: Monthly/quarterly

- [ ] **1.3** Data source investigation
  - Test yfinance fundamental data availability
  - Check data quality for required metrics
  - Document missing data issues

### Phase 2: Data Pipeline (Week 2)

- [ ] **2.1** Implement `FundamentalDataFetcher`
  ```python
  class FundamentalDataFetcher:
      def get_pe(ticker, date)
      def get_pb(ticker, date)
      def get_ps(ticker, date)
      def get_debt_to_equity(ticker, date)
      def get_roe(ticker, date)
      def get_fcf_yield(ticker, date)
  ```

- [ ] **2.2** Implement `ValueScorer`
  ```python
  class ValueScorer:
      def calculate_value_score(ticker, date)
      def rank_universe(tickers, date)
      def get_top_n(rankings, n=20)
  ```

- [ ] **2.3** Data validation
  - Handle missing data
  - Handle negative earnings (P/E undefined)
  - Historical data availability check

### Phase 3: Strategy Implementation (Week 3)

- [ ] **3.1** Implement `ValueInvestingStrategy`
  ```python
  class ValueInvestingStrategy(Strategy):
      # Screening criteria
      max_pe = 15
      max_pb = 1.5
      max_debt_to_equity = 0.5
      min_roe = 15

      # Portfolio
      max_positions = 20
      rebalance_frequency = 'monthly'
  ```

- [ ] **3.2** Implement backtest compatibility
  - Work with existing BacktestEngine
  - Or create new engine for fundamental strategies

- [ ] **3.3** Paper trading setup
  - Prepare for live testing

### Phase 4: Backtesting (Week 4)

- [ ] **4.1** Historical backtest
  - Period: 2015-2024 (10 years)
  - Universe: S&P 500 stocks
  - Rebalance: Monthly

- [ ] **4.2** Benchmark comparison
  - vs S&P 500 (SPY)
  - vs Buy&Hold individual stocks
  - vs frozen AdaptiveStrategy

- [ ] **4.3** Analysis
  - Annual returns
  - Sharpe ratio
  - Max drawdown
  - Turnover rate
  - Sector concentration

### Phase 5: Iteration (Week 5+)

- [ ] **5.1** Analyze results
- [ ] **5.2** Tune parameters
- [ ] **5.3** Add filters (quality, momentum)
- [ ] **5.4** Document findings

---

## Recommended Approach

### Option A: Pure Value (Start Simple)

```python
# Monthly rebalance
# Buy top 20 cheapest stocks by P/E
# Hold for 1 year minimum (Graham's suggestion)
```

**Pros:** Simple, proven
**Cons:** May miss quality companies

### Option B: Value + Quality (Buffett Style)

```python
# Value filter: P/E < 15, P/B < 1.5
# Quality filter: ROE > 15%, Debt/Equity < 0.5
# Hold top 20 by combined score
```

**Pros:** Better companies
**Cons**: More complex, fewer opportunities

### Option C: Value + Momentum (Quant Style)

```python
# Value filter: P/E < 15
# Momentum filter: 12-month return > 0
# Hold top 20 by value score
```

**Pros:** Combines factors
**Cons:** More complex

---

## Milestones

### Milestone 1: Research Complete (Day 7)
- [ ] Document value investing principles
- [ ] Design strategy architecture
- [ ] Confirm data availability

### Milestone 2: Data Pipeline Working (Day 14)
- [ ] FundamentalDataFetcher functional
- [ ] ValueScorer functional
- [ ] Data validated for 50+ stocks

### Milestone 3: Strategy Implemented (Day 21)
- [ ] ValueInvestingStrategy coded
- [ ] Backtest integration complete
- [ ] Smoke test passed

### Milestone 4: First Backtest Results (Day 28)
- [ ] 10-year backtest complete
- [ ] Comparison vs benchmarks
- [ ] Initial analysis

### Milestone 5: Ready for Paper Trading (Day 35+)
- [ ] Strategy validated
- [ ] Parameters tuned
- [ ] Documentation complete

---

## Risk Considerations

| Risk | Mitigation |
|------|------------|
| Value trap (cheap for reason) | Quality filters |
| Data errors | Validation, cross-checks |
| Look-ahead bias | Use lagged/fundamental data |
| Survivorship bias | Include delisted stocks |
| Overfitting | Out-of-sample testing |

---

## Success Criteria

| Metric | Target | Notes |
|--------|--------|-------|
| 10-Year CAGR | > 10% | Beat inflation |
| Sharpe Ratio | > 1.0 | Risk-adjusted return |
| Max Drawdown | < 30% | Reasonable protection |
| Win Rate | > 60% | More winners than losers |
| vs SPY | Positive alpha | Beat market |

---

## Files to Create

```
src/
├── data/
│   └── fundamental_fetcher.py    # yfinance fundamental data
├── strategies/
│   └── value_investing_strategy.py # New strategy
├── indicators/
│   └── value_indicators.py         # P/E, P/B, scoring, etc.
└── engines/
    └── fundamental_backtest.py    # Backtest for fundamental strategies

docs/
└── VALUE_INVESTING_RESEARCH.md    # Research notes

experiments/
└── active/
    └── EXP-2025-007-value-investing/  # New experiment
```

---

## Recommended Next Step

**Start with Option A (Pure Value) - Keep it simple.**

1. Create `FundamentalDataFetcher` this week
2. Test with 10-20 stocks first
3. Implement simple P/E screen
4. Run first backtest next week

**Question for you:**
Do you want to start with:
- **A) Pure P/E screen** (simplest, fastest to implement)
- **B) Value + Quality** (Buffett style, balanced)
- **C) Full research first** (study before coding)
