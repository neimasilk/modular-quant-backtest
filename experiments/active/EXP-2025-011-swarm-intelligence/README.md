# EXP-2025-011: Multi-Agent Swarm Trading System

**Status:** Designed (Ready for Implementation)  
**Created:** 2025-01-15  
**Author:** Mukhlis Amien  
**Tags:** swarm-intelligence, multi-agent, ensemble, voting-system

---

## 1. EXECUTIVE SUMMARY

### Hypothesis

Sebuah sistem dengan 7 specialist agents yang masing-masing "bodoh" (hanya melihat 1 aspek) akan menghasilkan keputusan trading yang lebih baik daripada single adaptive strategy, karena:

1. **Diversifikasi sinyal** - Tidak bergantung pada 1 indikator
2. **Noise reduction** - Voting system filter out false signals
3. **Robustness** - Jika 1 agent salah, yang lain bisa kompensasi

### Success Criteria

| Metric | Current Adaptive | Target Swarm | Improvement |
|--------|------------------|--------------|-------------|
| Sharpe Ratio | 1.83 (NVDA 2023) | > 2.0 | +10% |
| Max Drawdown | -9.26% | < -8% | Better |
| Win Rate | ~55% | > 60% | +5% |
| Consistency | 2/3 tickers beat B&H | 3/3 tickers | More robust |

### Effort Estimate

| Phase | Time | Deliverable |
|-------|------|-------------|
| Design (this doc) | Done | Specification |
| Implementation | 2-3 days | Working code |
| Backtesting | 1 day | Results |
| Analysis | 1 day | Conclusions |
| **Total** | **4-5 days** | Complete experiment |

---

## 2. THEORETICAL FOUNDATION

### 2.1 Why Swarm Intelligence?

**Natural Examples:**
- Semut: Individually dumb, collectively find shortest path
- Lebah: Vote on new hive location through dancing
- Fish schools: No leader, but coordinated movement

**Trading Analogy:**
- Setiap agent = 1 "sensor" yang melihat aspek berbeda
- Agregasi = "collective wisdom" dari multiple perspectives
- Emergence = keputusan yang lebih baik dari sum of parts

### 2.2 Why NOT Full Swarm?

| Full Swarm | Our Approach |
|------------|--------------|
| 100+ identical agents | 7 specialist agents |
| Emergent behavior | Engineered ensemble |
| Black box | Interpretable |
| Unproven in markets | Proven in ML |

**Key Insight:** Market tidak seperti maze (static). Kita butuh "guided emergence" bukan "pure emergence".

### 2.3 Scientific Basis

**Ensemble Learning Theory:**
- Condorcet's Jury Theorem: Jika setiap voter > 50% akurat dan independent, majority vote → 100% akurat as N → ∞
- Wisdom of Crowds: Aggregated estimates beat individual experts

**Caveat:** Agents harus:
1. Better than random (> 50% accuracy)
2. Independent (tidak melihat hal yang sama)
3. Diverse (different perspectives)

---

## 3. SYSTEM ARCHITECTURE

### 3.1 Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        MARKET DATA                               │
│         (OHLCV, VIX, Volume, External Sentiment)                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SPECIALIST AGENTS                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │  VIX    │ │ TREND   │ │ VOLUME  │ │MOMENTUM │ │SEASONAL │   │
│  │ Agent   │ │ Agent   │ │ Agent   │ │ Agent   │ │ Agent   │   │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘   │
│       │           │           │           │           │         │
│  ┌────┴────┐ ┌────┴────┐                                        │
│  │SUPPORT/ │ │SENTIMENT│                                        │
│  │RESISTANCE│ │ Agent   │                                        │
│  └────┬────┘ └────┬────┘                                        │
└───────┼───────────┼─────────────────────────────────────────────┘
        │           │
        ▼           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AGGREGATION LAYER                             │
│                                                                  │
│   Votes: [+1, +1, 0, -1, +1, 0, +1]                             │
│   Confidences: [0.8, 0.6, 0.3, 0.7, 0.5, 0.4, 0.9]             │
│                                                                  │
│   Weighted Score = Σ(vote × confidence) / Σ(confidence)         │
│                  = (0.8 + 0.6 + 0 - 0.7 + 0.5 + 0 + 0.9) / 4.2 │
│                  = 2.1 / 4.2 = 0.50                             │
│                                                                  │
│   Decision: BUY (score > 0.3 threshold)                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RISK MANAGEMENT                               │
│         (Stop-loss, Position Sizing, Regime Override)           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXECUTION LAYER                               │
│              (Order Generation, IBKR Integration)               │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Agent Independence Matrix

Untuk Condorcet theorem bekerja, agents harus melihat hal BERBEDA:

| Agent | Primary Input | Secondary | Correlation Risk |
|-------|---------------|-----------|------------------|
| VIX Agent | VIX level | VIX change | Independent ✓ |
| Trend Agent | Price vs SMA | SMA slope | Low correlation with VIX |
| Volume Agent | Volume patterns | OBV | Independent ✓ |
| Momentum Agent | RSI, MACD | Rate of change | Some overlap with Trend |
| Seasonal Agent | Calendar | Historical patterns | Independent ✓ |
| S/R Agent | Support/Resistance | Breakout detection | Some overlap with Trend |
| Sentiment Agent | News/AI sentiment | Sentiment change | Independent ✓ |

**Mitigation untuk correlation:** Weighted voting akan menurunkan weight untuk highly correlated agents.

---

## 4. AGENT SPECIFICATIONS

### 4.1 VIX Agent (Fear/Greed Detector)

**Purpose:** Detect market-wide fear/greed regime

**Input:** VIX value (daily)

**Logic:**
```python
class VIXAgent(BaseAgent):
    """
    Measures market fear/greed through VIX.
    
    VIX Interpretation:
    - < 15: Extreme greed (complacency) → Cautious
    - 15-20: Low fear → Bullish
    - 20-25: Normal → Neutral
    - 25-35: Elevated fear → Cautious/Bearish
    - > 35: Extreme fear → Contrarian Bullish (blood in streets)
    """
    
    def get_name(self) -> str:
        return "vix"
    
    def get_required_data(self) -> list:
        return ['vix']
    
    def analyze(self, vix: float) -> Tuple[int, float]:
        """
        Returns:
            vote: -1 (bearish), 0 (neutral), +1 (bullish)
            confidence: 0.0 to 1.0
        """
        if vix < 15:
            # Extreme complacency - market may be topping
            return (0, 0.6)  # Neutral with medium confidence
        elif vix < 20:
            # Low fear - good for longs
            return (+1, 0.7)
        elif vix < 25:
            # Normal - no strong signal
            return (0, 0.3)  # Low confidence
        elif vix < 35:
            # Elevated fear - caution
            return (-1, 0.7)
        else:
            # Extreme fear - contrarian buy signal
            # "Be greedy when others are fearful"
            return (+1, 0.8)
```

**Expected Accuracy:** ~55-60% (VIX is a known predictor)

---

### 4.2 Trend Agent (Direction Detector)

**Purpose:** Identify primary trend direction

**Input:** Close prices (need 50+ days history)

**Logic:**
```python
class TrendAgent(BaseAgent):
    """
    Measures trend using multiple moving averages.
    
    Signals:
    - Price > SMA20 > SMA50: Strong uptrend
    - Price > SMA20, SMA20 < SMA50: Potential reversal up
    - Price < SMA20 < SMA50: Strong downtrend
    - Price < SMA20, SMA20 > SMA50: Potential reversal down
    """
    
    def __init__(self):
        self.sma_short = 20
        self.sma_long = 50
    
    def get_name(self) -> str:
        return "trend"
    
    def get_required_data(self) -> list:
        return ['closes']
    
    def analyze(self, closes: pd.Series) -> Tuple[int, float]:
        if len(closes) < self.sma_long:
            return (0, 0.0)  # Not enough data
            
        sma20 = closes.rolling(self.sma_short).mean().iloc[-1]
        sma50 = closes.rolling(self.sma_long).mean().iloc[-1]
        price = closes.iloc[-1]
        
        # Calculate trend strength
        trend_strength = (price - sma50) / sma50  # % above/below SMA50
        
        if price > sma20 > sma50:
            # Strong uptrend
            confidence = min(0.9, 0.5 + abs(trend_strength))
            return (+1, confidence)
        elif price > sma20 and sma20 < sma50:
            # Potential reversal up
            return (+1, 0.5)
        elif price < sma20 < sma50:
            # Strong downtrend
            confidence = min(0.9, 0.5 + abs(trend_strength))
            return (-1, confidence)
        elif price < sma20 and sma20 > sma50:
            # Potential reversal down
            return (-1, 0.5)
        else:
            return (0, 0.3)
```

**Expected Accuracy:** ~52-55% (trend following has slight edge)

---

### 4.3 Volume Agent (Accumulation/Distribution Detector)

**Purpose:** Detect smart money flow

**Input:** Price and Volume data

**Logic:**
```python
class VolumeAgent(BaseAgent):
    """
    Measures accumulation/distribution through volume analysis.
    
    Concepts:
    - Price up + High volume = Strong buying (accumulation)
    - Price down + High volume = Strong selling (distribution)
    - Price up + Low volume = Weak rally (suspect)
    - Price down + Low volume = Weak decline (less concerning)
    
    Uses On-Balance Volume (OBV) trend as confirmation.
    """
    
    def __init__(self):
        self.lookback = 20
    
    def get_name(self) -> str:
        return "volume"
    
    def get_required_data(self) -> list:
        return ['closes', 'volumes']
    
    def analyze(self, closes: pd.Series, volumes: pd.Series) -> Tuple[int, float]:
        if len(closes) < self.lookback:
            return (0, 0.0)
        
        # Calculate OBV
        obv = (np.sign(closes.diff()) * volumes).cumsum()
        
        # OBV trend (is OBV making higher highs?)
        obv_sma = obv.rolling(self.lookback).mean()
        obv_trend = obv.iloc[-1] > obv_sma.iloc[-1]
        
        # Today's price action
        price_change = closes.pct_change().iloc[-1]
        
        # Volume relative to average
        vol_avg = volumes.rolling(self.lookback).mean().iloc[-1]
        vol_ratio = volumes.iloc[-1] / vol_avg if vol_avg > 0 else 1
        
        # High volume = > 1.5x average
        high_volume = vol_ratio > 1.5
        
        if price_change > 0 and high_volume and obv_trend:
            # Strong accumulation
            return (+1, 0.8)
        elif price_change < 0 and high_volume and not obv_trend:
            # Strong distribution
            return (-1, 0.8)
        elif price_change > 0 and not high_volume:
            # Weak rally
            return (0, 0.4)
        elif price_change < 0 and not high_volume:
            # Weak decline - less bearish
            return (0, 0.4)
        else:
            return (0, 0.3)
```

**Expected Accuracy:** ~53-57% (volume is informative but noisy)

---

### 4.4 Momentum Agent (Overbought/Oversold Detector)

**Purpose:** Identify momentum extremes

**Input:** Close prices

**Logic:**
```python
class MomentumAgent(BaseAgent):
    """
    Measures momentum using RSI and rate of change.
    
    RSI Interpretation:
    - > 70: Overbought (potential reversal down)
    - 50-70: Bullish momentum
    - 30-50: Bearish momentum
    - < 30: Oversold (potential reversal up)
    
    Combines with Rate of Change for confirmation.
    """
    
    def __init__(self):
        self.rsi_period = 14
        self.roc_period = 10
    
    def get_name(self) -> str:
        return "momentum"
    
    def get_required_data(self) -> list:
        return ['closes']
    
    def calculate_rsi(self, closes: pd.Series) -> float:
        delta = closes.diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def analyze(self, closes: pd.Series) -> Tuple[int, float]:
        if len(closes) < self.rsi_period + 1:
            return (0, 0.0)
        
        rsi = self.calculate_rsi(closes)
        
        if len(closes) >= self.roc_period + 1:
            roc = (closes.iloc[-1] - closes.iloc[-self.roc_period - 1]) / closes.iloc[-self.roc_period - 1]
        else:
            roc = 0
        
        if rsi > 70:
            # Overbought - but could stay overbought
            if roc > 0.05:  # Strong momentum
                return (0, 0.4)  # Don't fight strong momentum
            else:
                return (-1, 0.6)  # Reversal likely
        elif rsi < 30:
            # Oversold - potential bounce
            if roc < -0.05:  # Strong downward momentum
                return (0, 0.4)  # Don't catch falling knife
            else:
                return (+1, 0.7)  # Reversal likely
        elif rsi > 50:
            # Bullish momentum
            return (+1, 0.5)
        else:
            # Bearish momentum
            return (-1, 0.5)
```

**Expected Accuracy:** ~50-55% (mean reversion has slight edge at extremes)

---

### 4.5 Seasonal Agent (Calendar Pattern Detector)

**Purpose:** Exploit known calendar anomalies

**Input:** Current date

**Logic:**
```python
class SeasonalAgent(BaseAgent):
    """
    Exploits known calendar effects:
    
    Monthly patterns (S&P 500 historical):
    - January: +1.2% avg (January Effect)
    - September: -0.5% avg (Worst month)
    - October: +0.8% avg (but volatile)
    - November-December: +1.5% avg (Santa Rally)
    """
    
    # Historical monthly returns (S&P 500 average)
    MONTHLY_BIAS = {
        1: 0.7,   # January: bullish
        2: 0.3,   # February: slightly bullish
        3: 0.4,   # March: slightly bullish
        4: 0.6,   # April: bullish
        5: 0.2,   # May: "Sell in May"
        6: 0.1,   # June: neutral
        7: 0.4,   # July: bullish
        8: 0.0,   # August: neutral
        9: -0.5,  # September: bearish
        10: 0.3,  # October: slightly bullish
        11: 0.6,  # November: bullish
        12: 0.7,  # December: bullish (Santa Rally)
    }
    
    def get_name(self) -> str:
        return "seasonal"
    
    def get_required_data(self) -> list:
        return ['date']
    
    def analyze(self, date) -> Tuple[int, float]:
        if hasattr(date, 'month'):
            month = date.month
            day_of_week = date.weekday() if hasattr(date, 'weekday') else 2
        else:
            return (0, 0.3)
        
        monthly_bias = self.MONTHLY_BIAS.get(month, 0)
        
        # Adjust for day of week
        if day_of_week == 0:  # Monday
            weekly_adjustment = -0.1
        elif day_of_week == 4:  # Friday
            weekly_adjustment = 0.1
        else:
            weekly_adjustment = 0
        
        combined_bias = monthly_bias + weekly_adjustment
        
        # Convert to vote
        if combined_bias > 0.3:
            return (+1, min(0.6, 0.3 + abs(combined_bias)))
        elif combined_bias < -0.3:
            return (-1, min(0.6, 0.3 + abs(combined_bias)))
        else:
            return (0, 0.3)
```

**Expected Accuracy:** ~52-54% (calendar effects are real but weak)

---

### 4.6 Support/Resistance Agent (Key Level Detector)

**Purpose:** Identify key price levels

**Input:** OHLC prices

**Logic:**
```python
class SupportResistanceAgent(BaseAgent):
    """
    Identifies support/resistance levels and price position.
    
    Logic:
    - Price near support + bouncing = Bullish
    - Price near resistance + rejecting = Bearish
    - Breakout above resistance = Bullish
    - Breakdown below support = Bearish
    """
    
    def __init__(self):
        self.lookback = 20
        self.threshold = 0.02  # 2% buffer
    
    def get_name(self) -> str:
        return "support_resistance"
    
    def get_required_data(self) -> list:
        return ['highs', 'lows', 'closes']
    
    def analyze(self, highs: pd.Series, lows: pd.Series, closes: pd.Series) -> Tuple[int, float]:
        if len(closes) < self.lookback + 1:
            return (0, 0.0)
        
        # Calculate support/resistance
        support = lows.rolling(self.lookback).min().iloc[-1]
        resistance = highs.rolling(self.lookback).max().iloc[-1]
        price = closes.iloc[-1]
        prev_price = closes.iloc[-2]
        
        # Distance to levels (as percentage)
        dist_to_support = (price - support) / support if support > 0 else 1
        dist_to_resistance = (resistance - price) / resistance if resistance > 0 else 1
        
        # Near support (within 2%)
        if dist_to_support < self.threshold:
            if price > prev_price:  # Bouncing
                return (+1, 0.7)
            else:  # Breaking down
                return (-1, 0.8)
        
        # Near resistance (within 2%)
        if dist_to_resistance < self.threshold:
            if price < prev_price:  # Rejecting
                return (-1, 0.7)
            else:  # Breaking out
                return (+1, 0.8)
        
        # In the middle - weak signal
        middle = (support + resistance) / 2
        if price > middle:
            return (+1, 0.4)
        else:
            return (-1, 0.4)
```

**Expected Accuracy:** ~54-58% (S/R levels are well-documented)

---

### 4.7 Sentiment Agent (AI/News Sentiment)

**Purpose:** Capture news and social sentiment

**Input:** AI-generated sentiment score (current system)

**Logic:**
```python
class SentimentAgent(BaseAgent):
    """
    Uses AI-generated sentiment from news/analysis.
    
    This is your existing AI_Stock_Sentiment with lag fix.
    """
    
    def __init__(self):
        self.lookback = 5  # 5-day sentiment consistency
    
    def get_name(self) -> str:
        return "sentiment"
    
    def get_required_data(self) -> list:
        return ['sentiment_series']
    
    def analyze(self, sentiment_series: pd.Series) -> Tuple[int, float]:
        if len(sentiment_series) < self.lookback:
            return (0, 0.3)
        
        current_sentiment = sentiment_series.iloc[-1]
        
        # Check sentiment consistency
        recent_sentiments = sentiment_series.iloc[-self.lookback:]
        consistency = recent_sentiments.std()
        
        # Convert sentiment to vote
        if current_sentiment > 0.3:
            vote = +1
        elif current_sentiment < -0.3:
            vote = -1
        else:
            vote = 0
        
        # Higher confidence if consistent
        if consistency < 0.2:
            confidence = 0.7
        elif consistency < 0.4:
            confidence = 0.5
        else:
            confidence = 0.3
        
        # Boost confidence for extreme sentiment
        if abs(current_sentiment) > 0.6:
            confidence = min(0.9, confidence + 0.2)
        
        return (vote, confidence)
```

**Expected Accuracy:** ~52-55% (current heuristic sentiment is weak)

---

## 5. AGGREGATION LAYER

### 5.1 Weighted Voting System

```python
class SwarmAggregator:
    """
    Aggregates votes from all agents using weighted voting.
    """
    
    def __init__(self):
        # Base weights for each agent (can be tuned)
        self.base_weights = {
            'vix': 1.2,        # Slightly higher - regime is important
            'trend': 1.0,
            'volume': 0.8,     # Volume can be noisy
            'momentum': 1.0,
            'seasonal': 0.6,   # Weak effect
            'support_resistance': 1.0,
            'sentiment': 0.8,  # Current sentiment is heuristic
        }
        
        # Performance tracking for adaptive weights
        self.agent_accuracy = {name: 0.5 for name in self.base_weights}
        
    def aggregate(self, agent_outputs: Dict[str, Tuple[int, float]]) -> Tuple[str, float, Dict]:
        """
        Aggregate agent votes into final decision.
        
        Returns:
            decision: "BUY", "SELL", or "HOLD"
            score: Weighted score (-1 to +1)
            breakdown: Individual agent contributions
        """
        weighted_sum = 0
        total_weight = 0
        breakdown = {}
        
        for agent_name, (vote, confidence) in agent_outputs.items():
            base_weight = self.base_weights.get(agent_name, 1.0)
            
            # Adjust weight by agent's historical accuracy
            accuracy_factor = self.agent_accuracy.get(agent_name, 0.5) / 0.5
            
            # Final weight
            final_weight = base_weight * confidence * accuracy_factor
            
            weighted_sum += vote * final_weight
            total_weight += final_weight
            
            breakdown[agent_name] = {
                'vote': vote,
                'confidence': confidence,
                'weight': final_weight,
                'contribution': vote * final_weight
            }
        
        # Calculate final score
        if total_weight > 0:
            final_score = weighted_sum / total_weight
        else:
            final_score = 0
        
        # Decision thresholds
        if final_score > 0.25:
            decision = "BUY"
        elif final_score < -0.25:
            decision = "SELL"
        else:
            decision = "HOLD"
        
        return decision, final_score, breakdown
    
    def update_accuracy(self, agent_name: str, was_correct: bool):
        """Update agent accuracy with exponential moving average."""
        alpha = 0.1
        current = self.agent_accuracy.get(agent_name, 0.5)
        new_value = 1.0 if was_correct else 0.0
        self.agent_accuracy[agent_name] = alpha * new_value + (1 - alpha) * current
```

### 5.2 Decision Thresholds

| Score Range | Decision | Confidence Level |
|-------------|----------|------------------|
| > 0.5 | Strong BUY | High |
| 0.25 to 0.5 | BUY | Medium |
| -0.25 to 0.25 | HOLD | Low/Uncertain |
| -0.5 to -0.25 | SELL | Medium |
| < -0.5 | Strong SELL | High |

---

## 6. FILE STRUCTURE

```
modular-quant-backtest/
├── src/
│   ├── agents/                    # NEW: Agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Abstract base class
│   │   ├── vix_agent.py
│   │   ├── trend_agent.py
│   │   ├── volume_agent.py
│   │   ├── momentum_agent.py
│   │   ├── seasonal_agent.py
│   │   ├── support_resistance_agent.py
│   │   └── sentiment_agent.py
│   │
│   ├── swarm/                     # NEW: Swarm system
│   │   ├── __init__.py
│   │   ├── aggregator.py          # Voting aggregation
│   │   └── swarm_strategy.py      # Backtesting strategy class
│   │
│   ├── strategies/
│   │   └── adaptive_strategy.py   # Existing (unchanged)
│   │
│   └── engines/
│       └── backtest_engine.py     # Existing (unchanged)
│
├── experiments/
│   └── active/
│       └── EXP-2025-011-swarm-intelligence/
│           ├── README.md          # This document
│           └── results/           # Backtest results
│
└── tests/
    └── test_agents.py             # NEW: Unit tests for agents
```

---

## 7. BASE AGENT CLASS

```python
# src/agents/base_agent.py

from abc import ABC, abstractmethod
from typing import Tuple, List, Any
import pandas as pd


class BaseAgent(ABC):
    """
    Abstract base class for all specialist agents.
    
    Each agent must implement:
    1. analyze() - Return vote and confidence
    2. get_name() - Return agent identifier
    3. get_required_data() - Specify data requirements
    """
    
    @abstractmethod
    def analyze(self, *args, **kwargs) -> Tuple[int, float]:
        """
        Analyze data and return trading signal.
        
        Returns:
            vote: -1 (bearish), 0 (neutral), +1 (bullish)
            confidence: 0.0 to 1.0
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return agent identifier."""
        pass
    
    @abstractmethod
    def get_required_data(self) -> List[str]:
        """Return list of required data fields."""
        pass
```

---

## 8. SWARM STRATEGY FOR BACKTESTING

```python
# src/swarm/swarm_strategy.py

from backtesting import Strategy
from typing import Dict
import pandas as pd
import numpy as np

class SwarmStrategy(Strategy):
    """
    Multi-agent swarm trading strategy for backtesting.
    """
    
    # Strategy parameters
    buy_threshold = 0.25
    sell_threshold = -0.25
    position_size = 0.95
    
    # Risk management
    stop_loss_pct = 0.20
    trailing_stop_pct = 0.05
    
    def init(self):
        """Initialize agents and aggregator."""
        from src.agents.vix_agent import VIXAgent
        from src.agents.trend_agent import TrendAgent
        from src.agents.volume_agent import VolumeAgent
        from src.agents.momentum_agent import MomentumAgent
        from src.agents.seasonal_agent import SeasonalAgent
        from src.agents.support_resistance_agent import SupportResistanceAgent
        from src.agents.sentiment_agent import SentimentAgent
        from src.swarm.aggregator import SwarmAggregator
        
        self.agents = {
            'vix': VIXAgent(),
            'trend': TrendAgent(),
            'volume': VolumeAgent(),
            'momentum': MomentumAgent(),
            'seasonal': SeasonalAgent(),
            'support_resistance': SupportResistanceAgent(),
            'sentiment': SentimentAgent(),
        }
        
        self.aggregator = SwarmAggregator()
        self.entry_price = None
        self.highest_since_entry = None
    
    def collect_votes(self) -> Dict:
        """Collect votes from all agents."""
        # Prepare data
        closes = pd.Series([self.data.Close[i] for i in range(len(self.data.Close))])
        highs = pd.Series([self.data.High[i] for i in range(len(self.data.High))])
        lows = pd.Series([self.data.Low[i] for i in range(len(self.data.Low))])
        volumes = pd.Series([self.data.Volume[i] for i in range(len(self.data.Volume))])
        
        votes = {}
        
        # VIX Agent
        vix = self.data.VIX[-1] if hasattr(self.data, 'VIX') else 20
        votes['vix'] = self.agents['vix'].analyze(vix)
        
        # Trend Agent
        votes['trend'] = self.agents['trend'].analyze(closes)
        
        # Volume Agent
        votes['volume'] = self.agents['volume'].analyze(closes, volumes)
        
        # Momentum Agent
        votes['momentum'] = self.agents['momentum'].analyze(closes)
        
        # Seasonal Agent
        votes['seasonal'] = self.agents['seasonal'].analyze(self.data.index[-1])
        
        # S/R Agent
        votes['support_resistance'] = self.agents['support_resistance'].analyze(highs, lows, closes)
        
        # Sentiment Agent
        if hasattr(self.data, 'AI_Stock_Sentiment'):
            sentiment_series = pd.Series([self.data.AI_Stock_Sentiment[i] for i in range(len(self.data.AI_Stock_Sentiment))])
            votes['sentiment'] = self.agents['sentiment'].analyze(sentiment_series)
        else:
            votes['sentiment'] = (0, 0.3)
        
        return votes
    
    def check_stop_loss(self) -> bool:
        """Check stop-loss conditions."""
        if not self.position:
            self.entry_price = None
            self.highest_since_entry = None
            return False
        
        current_price = self.data.Close[-1]
        
        if self.entry_price is None:
            self.entry_price = current_price
            self.highest_since_entry = current_price
            return False
        
        if self.position.is_long:
            self.highest_since_entry = max(self.highest_since_entry, current_price)
            stop_price = self.entry_price * (1 - self.stop_loss_pct)
            trail_price = self.highest_since_entry * (1 - self.trailing_stop_pct)
            
            if current_price <= stop_price or current_price <= trail_price:
                return True
        
        return False
    
    def next(self):
        """Main strategy logic."""
        # Check stop-loss first
        if self.check_stop_loss():
            if self.position:
                self.position.close()
            return
        
        # Need minimum data
        if len(self.data.Close) < 50:
            return
        
        # Collect votes
        votes = self.collect_votes()
        
        # Aggregate
        decision, score, breakdown = self.aggregator.aggregate(votes)
        
        # Execute
        if decision == "BUY" and not self.position:
            self.buy(size=self.position_size)
            self.entry_price = self.data.Close[-1]
            self.highest_since_entry = self.entry_price
            
        elif decision == "SELL" and self.position and self.position.is_long:
            self.position.close()
```

---

## 9. TESTING PROTOCOL

### 9.1 Comparison Test Script

```python
# test_swarm_vs_adaptive.py

import pandas as pd
from backtesting import Backtest
from src.strategies.adaptive_strategy import AdaptiveStrategy
from src.swarm.swarm_strategy import SwarmStrategy

def compare_strategies():
    """Compare swarm vs adaptive strategy."""
    results = []
    
    tickers = ['NVDA', 'AAPL', 'SPY']
    years = ['2022', '2023']
    
    for ticker in tickers:
        for year in years:
            try:
                # Load data
                data = pd.read_csv(f'data/{ticker}_{year}.csv')
                data = prepare_data(data)  # Add VIX, sentiment, etc.
                
                # Run Adaptive
                bt_adaptive = Backtest(data, AdaptiveStrategy, cash=10000)
                stats_adaptive = bt_adaptive.run()
                
                # Run Swarm
                bt_swarm = Backtest(data, SwarmStrategy, cash=10000)
                stats_swarm = bt_swarm.run()
                
                results.append({
                    'ticker': ticker,
                    'year': year,
                    'adaptive_sharpe': stats_adaptive['Sharpe Ratio'],
                    'swarm_sharpe': stats_swarm['Sharpe Ratio'],
                    'adaptive_return': stats_adaptive['Return [%]'],
                    'swarm_return': stats_swarm['Return [%]'],
                    'adaptive_dd': stats_adaptive['Max. Drawdown [%]'],
                    'swarm_dd': stats_swarm['Max. Drawdown [%]'],
                    'adaptive_trades': stats_adaptive['# Trades'],
                    'swarm_trades': stats_swarm['# Trades'],
                })
            except Exception as e:
                print(f"Error with {ticker} {year}: {e}")
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    results = compare_strategies()
    print(results.to_string())
    results.to_csv('experiments/active/EXP-2025-011-swarm-intelligence/results/comparison.csv')
```

---

## 10. EXPECTED RESULTS

### 10.1 Optimistic Scenario

| Metric | Adaptive | Swarm | Improvement |
|--------|----------|-------|-------------|
| Avg Sharpe | 1.82 | 2.2 | +21% |
| Avg Max DD | -9.70% | -7.5% | +23% |
| Win Rate | 55% | 62% | +7% |

### 10.2 Realistic Scenario

| Metric | Adaptive | Swarm | Change |
|--------|----------|-------|--------|
| Avg Sharpe | 1.82 | 1.90 | +4% |
| Avg Max DD | -9.70% | -9.0% | +7% |

### 10.3 Pessimistic Scenario

| Metric | Adaptive | Swarm | Change |
|--------|----------|-------|--------|
| Avg Sharpe | 1.82 | 1.70 | -7% |
| Note | - | Over-engineered | - |

---

## 11. DECISION CRITERIA

### Success (Proceed to Production)
- [ ] Swarm Sharpe > Adaptive by at least 5%
- [ ] Max Drawdown <= Adaptive
- [ ] Consistent across all 3 tickers
- [ ] At least 15+ trades per ticker per year

### Partial Success (Iterate)
- [ ] Swarm beats Adaptive in some conditions
- [ ] Clear pattern of when Swarm works better

### Failure (Abandon)
- [ ] Swarm consistently underperforms
- [ ] Higher drawdown
- [ ] Complexity not justified

---

## 12. IMPLEMENTATION CHECKLIST

### Day 1: Foundation
- [ ] Create `src/agents/` directory
- [ ] Implement `BaseAgent`
- [ ] Implement `VIXAgent`
- [ ] Implement `TrendAgent`
- [ ] Write unit tests

### Day 2: Core Agents
- [ ] Implement `VolumeAgent`
- [ ] Implement `MomentumAgent`
- [ ] Implement `SupportResistanceAgent`
- [ ] Write unit tests

### Day 3: Integration
- [ ] Implement `SeasonalAgent`
- [ ] Implement `SentimentAgent`
- [ ] Implement `SwarmAggregator`
- [ ] Implement `SwarmStrategy`
- [ ] Integration test

### Day 4: Testing
- [ ] Run on NVDA, AAPL, SPY × 2022, 2023
- [ ] Compare with Adaptive
- [ ] Generate report

### Day 5: Decision
- [ ] Analyze results
- [ ] Make go/no-go decision
- [ ] Document lessons learned

---

## 13. MY HONEST PREDICTION

**60% chance** - Marginal improvement (2-10% better Sharpe)
**30% chance** - Performs similarly to Adaptive
**10% chance** - Significantly underperforms

**But the learning value is 100%** - You'll understand multi-agent systems, ensemble methods, and have a more sophisticated framework.

---

**Good luck with the implementation!** 🚀

*Document created: January 2025*
*Ready for implementation*
