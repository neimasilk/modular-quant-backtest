"""
Multi-Ticker Backtest Test
===========================
Test strategy on multiple tickers with locally generated AI signals.
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from backtesting import Backtest

sys.path.insert(0, str(Path(__file__).parent))
from src.strategies.adaptive_strategy import AdaptiveStrategy, BuyAndHoldStrategy


def prepare_data_with_signals(csv_path: str) -> pd.DataFrame:
    """
    Load CSV and add AI signals (VIX regime + sentiment).

    For testing, we generate:
    - VIX: Mock based on price volatility
    - AI_Regime_Score: Based on VIX + trend
    - AI_Stock_Sentiment: Based on returns (lagged to avoid bias)
    """
    df = pd.read_csv(csv_path)

    # Ensure Date is index
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')

    # Flatten MultiIndex if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Calculate returns
    df['Returns'] = df['Close'].pct_change()

    # Mock VIX based on volatility (20-day rolling std)
    volatility = df['Returns'].rolling(20).std() * np.sqrt(252) * 100
    # Map to VIX-like range (10-40)
    df['VIX'] = 15 + (volatility / volatility.max()) * 25
    df['VIX'] = df['VIX'].fillna(20)

    # AI_Regime_Score based on VIX + trend
    weekly_trend = df['Close'].pct_change(5) * 100  # 5-day trend
    df['AI_Regime_Score'] = np.where(
        df['VIX'] < 20,
        np.clip(weekly_trend / 5, -1, 1),  # Low VIX = more sensitive to trend
        np.where(
            df['VIX'] > 30,
            -0.5,  # High VIX = bearish
            0  # Medium VIX = neutral
        )
    )
    df['AI_Regime_Score'] = df['AI_Regime_Score'].fillna(0)

    # AI_Stock_Sentiment based on returns (LAGGED to avoid look-ahead bias)
    df['AI_Stock_Sentiment'] = np.where(
        df['Returns'].shift(1) > 0.01, 0.5,
        np.where(df['Returns'].shift(1) < -0.01, -0.5, 0)
    )
    df['AI_Stock_Sentiment'] = df['AI_Stock_Sentiment'].fillna(0)

    # Drop temporary columns
    df = df.drop(columns=['Returns'])

    # Ensure required columns exist
    required = ['Open', 'High', 'Low', 'Close', 'Volume', 'VIX', 'AI_Regime_Score', 'AI_Stock_Sentiment']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    return df


def run_backtest(data: pd.DataFrame, strategy_class, name: str, initial_cash: float = 10000):
    """Run backtest and return results."""
    bt = Backtest(
        data,
        strategy_class,
        cash=initial_cash,
        commission=0.001,
        exclusive_orders=True,
        finalize_trades=True
    )

    stats = bt.run()

    return {
        'name': name,
        'return': stats['Return [%]'],
        'sharpe': stats['Sharpe Ratio'],
        'max_dd': stats['Max. Drawdown [%]'],
        'trades': stats['# Trades'],
        'win_rate': stats.get('Win Rate [%]', 0)
    }


def main():
    print("\n" + "="*70)
    print("MULTI-TICKER BACKTEST".center(70))
    print("="*70)

    # Tickers to test
    tickers = ['NVDA', 'AAPL', 'SPY']
    initial_cash = 10000

    results = []

    for ticker in tickers:
        csv_path = f"data/{ticker}_2023.csv"

        if not Path(csv_path).exists():
            print(f"\n[SKIP] {ticker}: Data file not found")
            continue

        print(f"\n{'='*70}")
        print(f"Testing: {ticker}")
        print('='*70)

        try:
            # Prepare data
            data = prepare_data_with_signals(csv_path)
            print(f"Data: {len(data)} bars")
            print(f"Price range: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
            print(f"Avg VIX: {data['VIX'].mean():.2f}")

            # Run Adaptive Strategy
            adaptive_result = run_backtest(data, AdaptiveStrategy, ticker, initial_cash)
            results.append(adaptive_result)

            # Run Buy & Hold for comparison
            bh_result = run_backtest(data, BuyAndHoldStrategy, f"{ticker} (B&H)", initial_cash)
            results.append(bh_result)

            print(f"\nAdaptive: Return={adaptive_result['return']:.2f}%, Sharpe={adaptive_result['sharpe']:.2f}, Trades={adaptive_result['trades']}")
            print(f"Buy&Hold: Return={bh_result['return']:.2f}%, Sharpe={bh_result['sharpe']:.2f}")

        except Exception as e:
            print(f"[ERROR] {ticker}: {e}")

    # Summary table
    print("\n" + "="*70)
    print("SUMMARY TABLE")
    print("="*70)
    print(f"{'Strategy':<15} {'Return %':<12} {'Sharpe':<10} {'Max DD %':<12} {'Trades':<10}")
    print("-"*70)

    for r in results:
        print(f"{r['name']:<15} {r['return']:<12.2f} {r['sharpe']:<10.2f} {r['max_dd']:<12.2f} {r['trades']:<10}")

    print("="*70)

    # Analysis
    print("\nANALYSIS:")
    adaptive_results = [r for r in results if '(B&H)' not in r['name']]
    avg_trades = sum(r['trades'] for r in adaptive_results) / len(adaptive_results)
    avg_sharpe = sum(r['sharpe'] for r in adaptive_results) / len(adaptive_results)

    print(f"  Average trades per ticker: {avg_trades:.1f}")
    print(f"  Average Sharpe ratio: {avg_sharpe:.2f}")

    if avg_trades < 10:
        print("  [WARNING] Trade frequency still low - consider lowering thresholds further")
    else:
        print("  [OK] Trade frequency improved")


if __name__ == "__main__":
    main()
