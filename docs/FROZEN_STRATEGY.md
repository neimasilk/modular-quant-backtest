# Frozen Strategy: Adaptive Regime-Based Strategy

**Status:** FROZEN - Production Ready
**Frozen Date:** 2025-01-11
**Version:** 1.0

---

## Strategy Identity

This is a **defensive/capital preservation strategy** designed to:
- Protect capital in bear markets
- Participate in sideways/volatile markets
- Accept underperformance in mega-bull markets

**Trade-off:** Lower absolute returns for significantly better drawdown protection.

---

## Performance Summary

| Market Type | Period | Strategy Return | B&H Return | Outperformance |
|-------------|--------|-----------------|------------|----------------|
| Bear (2022) | Full year | **+13.1%** | -30.8% | **+43.9%** |
| Bull (2023) | Full year | +46.7% | +101.7% | -55.0% |
| Multi-year | 2020-2024 | TBD | TBD | TBD |

**Key Metrics (NVDA 2022):**
- Return: +18.68% vs -47.94% B&H
- Max DD: -9.95% vs -58.09% B&H
- Sharpe: 0.84 vs -1.46 B&H

---

## Strategy Components

### 1. Regime Detection (VIX-Based)

```python
AI_Regime_Score = f(VIX_realized):
    VIX < 15%  → 0.8  (Very Bullish)
    VIX < 25%  → 0.3  (Mildly Bullish)
    VIX < 35%  → 0.0  (Neutral)
    VIX < 50%  → -0.3 (Mildly Bearish)
    VIX >= 50% → -0.8 (Very Bearish)
```

### 2. Three Trading Modes

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Aggressive** | AI_Regime_Score > 0.5 | Long bias, sentiment-based entries |
| **Defensive** | AI_Regime_Score < -0.5 | Short bias, protective stops |
| **Mean Reversion** | -0.5 <= Score <= 0.5 | Buy support, sell resistance |

### 3. Risk Management

- **Hard Stop-Loss:** 20% from entry
- **Position Sizing:** 95% (aggressive), 50% (defensive), 50% (mean reversion)
- **Support/Resistance:** Dynamic lookback-based

### 4. Signal Generation

```python
# Heuristic sentiment (LAGGED to avoid look-ahead bias)
AI_Stock_Sentiment = shift(pct_change(Close, 5) * 2, 1)
# Clipped to [-1, 1], lagged by 1 day
```

---

## Entry/Exit Rules

### Aggressive Mode (Bullish)
```
ENTRY:  sentiment > 0.0
EXIT:   sentiment < -0.5
SIZE:   95% of equity
STOP:   20% hard stop
```

### Defensive Mode (Bearish)
```
ENTRY:  sentiment < -0.3 (short)
EXIT:   sentiment > 0.0 (cover)
SIZE:   50% of equity
STOP:   20% hard stop
```

### Mean Reversion Mode (Sideways)
```
BUY:  Price <= Support * 1.03
SELL: Price >= Resistance * 0.97
SIZE: 50% of equity
STOP: 20% hard stop
TARGET: Opposite band
```

---

## Parameters

```python
# Regime Thresholds
BULLISH_MIN = 0.5
BEARISH_MAX = -0.5

# Aggressive Mode
SENTIMENT_ENTRY = 0.0
SENTIMENT_EXIT = -0.5
POSITION_SIZE = 0.95

# Defensive Mode
SENTIMENT_SHORT = -0.3
SENTIMENT_COVER = 0.0
POSITION_SIZE = 0.50

# Mean Reversion Mode
LOOKBACK_PERIOD = 20
SUPPORT_THRESHOLD = 0.03
RESISTANCE_THRESHOLD = 0.03
POSITION_SIZE = 0.50

# Risk Management
STOP_LOSS_PCT = 0.20
```

---

## Files

```
src/strategies/
├── adaptive_strategy.py    # Main strategy (FROZEN)
├── regime_threshold.py      # Parameters (FROZEN)
├── aggressive_mode.py       # Bullish logic (FROZEN)
├── defensive_mode.py        # Bearish logic (FROZEN)
└── mean_reversion_mode.py   # Sideways logic (FROZEN)
```

---

## What Was Tried and Failed

| Attempt | Result | Verdict |
|---------|--------|---------|
| LLM News Sentiment (EXP-005) | Underperformed | Dead end |
| ADX + Trailing Stop (EXP-006) | Made performance worse | DO NOT revisit |

---

## Usage

```python
from backtesting import Backtest
from src.strategies.adaptive_strategy import AdaptiveStrategy

bt = Backtest(
    data,           # Must have: OHLCV, AI_Regime_Score, AI_Stock_Sentiment
    AdaptiveStrategy,
    cash=100_000,
    commission=0.001,
    exclusive_orders=True
)

stats = bt.run()
print(stats)
```

---

## Limitations (Accepted)

1. **Underperforms in Strong Bull Markets**
   - By design: prioritizes capital preservation over max returns
   - 2023 NVDA: +94% vs +229% B&H
   - This is acceptable

2. **Heuristic Sentiment**
   - Derived from price, not fundamental news
   - Has look-ahead bias (mitigated with lag)
   - Works despite simplicity

3. **No Fundamental Analysis**
   - Purely technical
   - May miss value opportunities

---

## Next Steps (For This Strategy)

1. ✅ Document as frozen
2. ✅ Archive failed experiments
3. ⏸️ No further modifications planned
4. Future: Full cycle validation (2020-2024)

---

## Notes for Future Reference

**If unfreezing this strategy, first consider:**
- What problem are we solving?
- Is this within the strategy's design scope?
- Did we try something similar before? (Check failed experiments)

**This strategy is NOT designed to:**
- Beat Buy&Hold in mega-bull markets
- Capture 100% of upside moves
- Replace fundamental analysis

**This strategy IS designed to:**
- Protect capital in bear markets
- Generate consistent risk-adjusted returns
- Handle all market regimes gracefully
