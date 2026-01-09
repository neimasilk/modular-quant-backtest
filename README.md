# Modular Quantitative Backtesting Framework

Kerangka kerja backtesting yang modular dan terstruktur untuk strategi trading berbasis AI Signals.

## Struktur Project

```
modular/
├── main.py                     # Entry point utama
├── requirements.txt            # Dependencies
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   └── data_generator.py   # Layer 1: Data Generation dengan AI Signals
│   ├── strategies/
│   │   ├── __init__.py
│   │   └── adaptive_strategy.py # Layer 2: Strategy Logic (Quantifiable Rules)
│   └── engines/
│       ├── __init__.py
│       └── backtest_engine.py  # Layer 3: Backtest Engine & Reporting
└── output/                     # Hasil plot dan laporan
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Run Default Backtest

```bash
python main.py
```

### Compare Strategies

```bash
python main.py --compare
```

### Custom Parameters

```bash
python main.py --days 500        # Generate 500 days of data
python main.py --no-plot         # Skip plot generation
python main.py --quiet           # Minimal output
```

### Parameter Optimization

```bash
python main.py --optimize
```

## Layer Overview

### Layer 1: Data Generation (`src/data/data_generator.py`)

Menghasilkan mock OHLCV data dengan AI Signals:

```python
from src.data.data_generator import prepare_data

df = prepare_data(n_days=252)
# Columns: Open, High, Low, Close, Volume, AI_Regime_Score, AI_Stock_Sentiment
```

**AI Signals:**
- `AI_Regime_Score`: Float (-1.0 to 1.0) - Hasil analisis makro dari LLM
- `AI_Stock_Sentiment`: Float (-1.0 to 1.0) - Hasil analisis berita harian

### Layer 2: Strategy Logic (`src/strategies/adaptive_strategy.py`)

Transformasi AI Signals menjadi keputusan Buy/Sell yang MATHEMATICAL:

```
┌─────────────────┬─────────────────────────────────────────────────────┐
│ Regime Condition │ Strategy Mode & Entry Logic                        │
├─────────────────┼─────────────────────────────────────────────────────┤
│ > 0.5 (Bullish) │ AGGRESSIVE: Buy if Sentiment > 0.2                 │
│ < -0.5 (Bearish) │ DEFENSIVE: Cash/Short if Sentiment < -0.8         │
│ -0.5 to 0.5     │ MEAN REVERSION: Buy at support, Sell at resistance │
└─────────────────┴─────────────────────────────────────────────────────┘
```

### Layer 3: Backtest Engine (`src/engines/backtest_engine.py`)

Menjalankan backtest dan menghasilkan laporan:

```python
from src.engines.backtest_engine import BacktestEngine
from src.strategies.adaptive_strategy import AdaptiveStrategy

engine = BacktestEngine(data, AdaptiveStrategy, initial_cash=100_000)
engine.run()
engine.print_report()
```

## Metrics Output

- Total Return & Annual Return
- Sharpe Ratio & Sortino Ratio
- Maximum Drawdown & Duration
- Win Rate & Average Win/Loss
- Trade count by regime

## Key Features

1. **Modular Design**: Setiap layer terpisah, mudah di-extend
2. **Quantifiable Logic**: Tidak ada "feeling", semua rule berbasis angka
3. **AI-Ready**: Struktur siap untuk integrasi dengan LLM/API
4. **Comprehensive Metrics**: Semua metrik penting tersedia

## Extending the Framework

### Add New Strategy

```python
from backtesting import Strategy

class MyStrategy(Strategy):
    def init(self):
        # Setup indicators
        pass

    def next(self):
        # Trading logic
        pass
```

### Add Custom Metrics

```python
def my_custom_metric(equity_curve):
    # Your calculation
    return metric_value
```
