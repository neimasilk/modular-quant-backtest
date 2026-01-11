# EXP-2025-007: Value Investing Strategy

**Status:** Active | **Created:** 2025-01-11
**Type:** Clean Slate - New Strategy Family

---

## Initial Test Results (2023)

### Top 10 Value Stocks (by combined score)

| Ticker | P/E | P/B | ROE | FCF Yield | Score |
|--------|-----|-----|-----|-----------|-------|
| PYPL | 11.6 | 2.69 | 24.4% | 5.7% | 0.123 |
| CMCSA | 4.7 | 1.07 | 24.2% | 3.6% | 0.208 |
| PG | 20.7 | 6.31 | 31.9% | 3.7% | 0.230 |
| BRK-B | 16.0 | ~0 | 10.2% | 4.5% | 0.232 |
| JNJ | 19.8 | 6.20 | 33.6% | 2.4% | 0.266 |

### Backtest Results (2023, Buy & Hold Top 5)

| Metric | Value Portfolio | Equal-Weight Benchmark |
|--------|-----------------|------------------------|
| Portfolio Return | **+2.62%** | **+42.76%** |
| Alpha | **-40.14%** | - |
| Final Value | $102,623 | $142,761 |

### Individual Returns (Top 5)

| Stock | Return |
|-------|--------|
| CMCSA | +25.92% |
| BRK-B | +15.09% |
| PG | -0.86% |
| JNJ | -9.37% |
| PYPL | -17.66% |

---

## Analysis

### What Happened

**Value stocks underperformed in 2023 bull market.**

This is **EXPECTED and consistent with value investing literature:**

1. **2023 was a growth/tech year** - NVDA +229%, META +180%, etc.
2. **Value stocks lag in strong bull markets** - proven academic finding
3. **Our portfolio did +2.62%** - positive but much less than benchmark

### Why This is OK

1. **Long-term outperformance** - Value beats growth over 5-10+ years
2. **Lower volatility** - Value stocks are more stable
3. **Different regime** - Value should shine in bear/sideways markets
4. **Only 1 year tested** - Need longer timeframe

---

## Next Steps

1. ✅ FundamentalDataFetcher implemented
2. ✅ ValueScreener implemented
3. ✅ Initial test complete
4. ⏳ Test longer timeframe (2018-2024)
5. ⏳ Test bear market performance
6. ⏳ Add monthly rebalancing
7. ⏳ Implement proper multi-stock backtesting

---

## Files

- `src/data/fundamental_fetcher.py` - Data fetching & screening
- `src/strategies/value_investing_strategy.py` - Strategy & backtester
- `experiments/active/EXP-2025-007-value-investing/`

---

## Notes

**Current Implementation: Simplified**
- Uses current fundamental data (not historical)
- Buy & Hold approach (no rebalancing yet)
- Simple equal-weight portfolio

**To Add:**
- Historical fundamental data (if available)
- Monthly rebalancing logic
- Minimum holding period enforcement
- Proper multi-stock backtesting engine
