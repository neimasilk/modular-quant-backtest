# Modular Quantitative Backtesting Framework with AI-Driven Data Mining

Framework backtesting modular untuk strategi trading berbasis AI Signals. Menggabungkan **ETL Pipeline** (Data Mining dengan DeepSeek API) dan **Backtesting Engine** untuk menguji strategi dengan data pasar nyata.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [1. Data Mining Pipeline](#1-data-mining-pipeline)
  - [2. Backtesting](#2-backtesting)
- [Strategy Logic](#strategy-logic)
- [Results](#results)
- [Google Drive Sync](#google-drive-sync)
- [Troubleshooting](#troubleshooting)

---

## Overview

Framework ini menggabungkan tiga komponen utama:

```
┌─────────────────────────────────────────────────────────────┐
│  1. DATA MINING LAYER                                      │
│  - Fetch real market data (Yahoo Finance)                   │
│  - AI Annotation via DeepSeek API (weekly batch)           │
│  - Forward fill untuk daily data                           │
├─────────────────────────────────────────────────────────────┤
│  2. STRATEGY LAYER                                         │
│  - Adaptive Strategy (3 modes: Bullish/Bearish/Sideways)   │
│  - Quantifiable rules, NO discretion                        │
│  - Based on AI_Regime_Score & AI_Stock_Sentiment            │
├─────────────────────────────────────────────────────────────┤
│  3. BACKTEST ENGINE                                        │
│  - Performance metrics (Sharpe, Max DD, Win Rate, etc)      │
│  - Strategy comparison                                     │
│  - Visualization & reporting                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

- **Real Market Data**: Fetch dari Yahoo Finance (stocks, indices, crypto)
- **AI Annotation**: DeepSeek API untuk market regime classification
- **Modular Architecture**: Layer terpisah, mudah di-extend
- **Multi-Strategy Comparison**: Bandingkan beberapa strategi sekaligus
- **Cloud Storage**: Auto-upload ke Google Drive via rclone
- **Robust Prototype**: Error handling, retries, logging

---

## Project Structure

```
modular/
├── main.py                      # Backtesting entry point (mock data)
├── data_miner.py               # ETL Pipeline (real data + AI annotation)
├── requirements.txt             # Python dependencies
├── .env                        # API keys (NOT in git)
├── .env.example                # Template untuk .env
├── .gitignore                  # Exclude sensitive files
│
├── src/
│   ├── data/
│   │   └── data_generator.py   # Mock data generation
│   ├── strategies/
│   │   └── adaptive_strategy.py # Adaptive, Buy&Hold, Momentum
│   └── engines/
│       └── backtest_engine.py  # Backtest runner & metrics
│
├── data/                       # Generated data files
│   ├── NVDA_real_data_2023.csv
│   └── GSPC_real_data_2023.csv
│
└── output/                     # Backtest results
    ├── nvda_2023_equity_curve.csv
    └── *.html (plots)
```

---

## Installation

### Prerequisites

- Python 3.9+
- pip
- rclone (untuk Google Drive sync)

### Step 1: Clone Repository

```bash
git clone https://github.com/neimasilk/modular-quant-backtest.git
cd modular-quant-backtest
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Setup Environment Variables

Copy `.env.example` ke `.env` dan isi API keys:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env`:

```env
# DeepSeek API Configuration
DEEPSEEK_API_KEY=sk-your-api-key-here

# Rclone Configuration
RCLONE_REMOTE_NAME=gdrive
RCLONE_REMOTE_PATH=quant_backtest_data
```

### Step 4: Setup rclone (Google Drive)

Jika belum ada rclone remote:

```bash
rclone config create gdrive
# Select: Google Drive
# Follow authentication steps
```

---

## Configuration

### API Keys

| Variable | Description | Source |
|----------|-------------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API key untuk AI annotation | https://platform.deepseek.com/api_keys |

### Rclone Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `RCLONE_REMOTE_NAME` | Nama remote rclone | `gdrive` |
| `RCLONE_REMOTE_PATH` | Path di Google Drive | `quant_backtest_data` |

---

## Usage

### 1. Data Mining Pipeline

Generate market data dengan AI annotation:

```bash
# Default: NVDA 2023
python data_miner.py

# Custom ticker dan periode
python data_miner.py --ticker AAPL --start 2022-01-01 --end 2023-01-01

# S&P 500
python data_miner.py --ticker ^GSPC --start 2023-01-01 --end 2024-01-01

# NASDAQ
python data_miner.py --ticker ^IXIC --start 2023-01-01 --end 2024-01-01

# Skip upload ke Google Drive
python data_miner.py --no-upload

# Dry run (fetch data only, no AI API call)
python data_miner.py --dry-run
```

**Output**: `{TICKER}_real_data_{YEAR}.csv` di folder `data/`

**Columns**:
- `Date`, `Open`, `High`, `Low`, `Close`, `Volume` (OHLCV)
- `VIX` (Volatility Index)
- `AI_Regime_Score` (-1.0 to 1.0, dari DeepSeek)
- `AI_Stock_Sentiment` (-1.0 to 1.0, heuristic-based)

### 2. Backtesting

#### With Mock Data (Quick Test)

```bash
# Run default backtest
python main.py

# Compare strategies
python main.py --compare

# Custom parameters
python main.py --days 500 --no-plot
```

#### With Real Mined Data

```python
import pandas as pd
from src.engines.backtest_engine import BacktestEngine
from src.strategies.adaptive_strategy import AdaptiveStrategy

# Load mined data
df = pd.read_csv('data/NVDA_real_data_2023.csv')
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Remove VIX column (not needed for backtesting)
df_backtest = df.drop(columns=['VIX'])

# Run backtest
engine = BacktestEngine(
    data=df_backtest,
    strategy_class=AdaptiveStrategy,
    initial_cash=100_000,
    commission=0.001
)
engine.run()
engine.print_report()
```

---

## Strategy Logic

### Adaptive Strategy (AI-Driven)

Strategy mengubah mode berdasarkan `AI_Regime_Score`:

| Regime Score | Mode | Entry Logic | Position Size |
|--------------|------|-------------|---------------|
| > 0.5 | **AGGRESSIVE** | Buy if Sentiment > 0.2 | 95% |
| < -0.5 | **DEFENSIVE** | Short if Sentiment < -0.8 | 50% |
| -0.5 to 0.5 | **MEAN REVERSION** | Buy support, Sell resistance | 60% |

### Available Strategies

| Strategy | Description | Best For |
|----------|-------------|----------|
| `AdaptiveStrategy` | AI-driven, 3 modes | Volatile markets |
| `BuyAndHoldStrategy` | Simple buy & hold | Strong uptrend |
| `SimpleMomentumStrategy` | Price momentum | Trending markets |

---

## Results

### NVDA 2023 (Real Data)

| Strategy | Return | Sharpe | Max DD | Trades |
|----------|--------|-------|--------|--------|
| Buy & Hold | **+231%** | 1.42 | -18.0% | 1 |
| Adaptive (AI) | +174% | **1.79** | **-11.6%** | 6 |
| Momentum | +109% | 1.31 | -14.6% | 10 |

### S&P 500 2023 (Real Data)

| Strategy | Return | Sharpe | Max DD | Trades |
|----------|--------|-------|--------|--------|
| Buy & Hold | **+22%** | 1.52 | -9.6% | 1 |
| Momentum | +16% | **1.54** | -7.6% | 7 |
| Adaptive (AI) | +12% | 1.39 | **-6.4%** | 2 |

---

## Google Drive Sync

### Automatic Sync

Data files otomatis di-upload ke Google Drive saat pipeline selesai:

```
gdrive:quant_backtest_data/
├── NVDA_real_data_2023.csv
├── GSPC_real_data_2023.csv
└── {TICKER}_real_data_{YEAR}.csv
```

### Manual Sync

```bash
# Upload .env ke Google Drive (untuk backup)
rclone copy .env gdrive:quant_backtest_config/

# Download dari komputer lain
rclone copy gdrive:quant_backtest_config/.env .env

# Sync semua data
rclone sync data/ gdrive:quant_backtest_data/
```

### Persistency (Pindah Komputer)

Untuk setup di komputer baru:

```bash
# 1. Clone repository
git clone https://github.com/neimasilk/modular-quant-backtest.git
cd modular-quant-backtest

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download .env dari Google Drive
rclone copy gdrive:quant_backtest_config/.env .env

# 4. Install rclone dan setup remote (jika belum)
# 5. Download data files
rclone copy gdrive:quant_backtest_data/ data/
```

---

## Troubleshooting

### Issue: "DEEPSEEK_API_KEY not found"

**Solution**: Buat file `.env` dari `.env.example` dan isi API key.

### Issue: rclone not found

**Solution**: Install rclone dari https://rclone.org/downloads/

### Issue: "Some trades remain open at the end"

**Solution**: Sudah di-fix di code (`finalize_trades=True`)

### Issue: UnicodeEncodeError pada Windows

**Solution**: Gunakan terminal UTF-8 atau set environment variable:
```bash
set PYTHONIOENCODING=utf-8
```

---

## Command Reference

```bash
# Data Mining
python data_miner.py [--ticker TICKER] [--start DATE] [--end DATE] [--no-upload] [--dry-run]

# Backtesting (mock data)
python main.py [--days N] [--compare] [--optimize] [--no-plot] [--quiet]

# Git
git add .
git commit -m "message"
git push

# Rclone
rclone copy .env gdrive:quant_backtest_config/
rclone sync data/ gdrive:quant_backtest_data/
```

---

## License

MIT License

---

## Author

Built with Claude Code (Anthropic)
