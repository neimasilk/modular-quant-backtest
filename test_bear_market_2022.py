"""
Bear Market 2022 Backtest Test
================================
Test strategy performance during the 2022 bear market.
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from backtesting import Backtest

sys.path.insert(0, str(Path(__file__).parent))
from src.strategies.adaptive_strategy import AdaptiveStrategy, BuyAndHoldStrategy


def prepare_data_with_signals(csv_path: str) -> pd.DataFrame:
    """Load CSV and add AI signals (VIX regime + sentiment)."""
    df = pd.read_csv(csv_path)

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Calculate returns
    df['Returns'] = df['Close'].pct_change()

    # Mock VIX based on volatility (2022 had elevated VIX)
    volatility = df['Returns'].rolling(20).std() * np.sqrt(252) * 100
    df['VIX'] = 22 + (volatility / volatility.max()) * 20  # Higher base VIX for 2022
    df['VIX'] = df['VIX'].fillna(25)

    # AI_Regime_Score based on VIX + trend
    weekly_trend = df['Close'].pct_change(5) * 100
    df['AI_Regime_Score'] = np.where(
        df['VIX'] < 25,
        np.clip(weekly_trend / 5, -1, 1),
        np.where(
            df['VIX'] > 35,
            -0.7,  # Very bearish in high VIX
            -0.2  # Slightly bearish in medium VIX
        )
    )
    df['AI_Regime_Score'] = df['AI_Regime_Score'].fillna(0)

    # AI_Stock_Sentiment based on returns (LAGGED)
    df['AI_Stock_Sentiment'] = np.where(
        df['Returns'].shift(1) > 0.01, 0.5,
        np.where(df['Returns'].shift(1) < -0.01, -0.5, 0)
    )
    df['AI_Stock_Sentiment'] = df['AI_Stock_Sentiment'].fillna(0)

    df = df.drop(columns=['Returns'])

    return df


def run_backtest(data, strategy_class, name, initial_cash=10000):
    bt = Backtest(data, strategy_class, cash=initial_cash, commission=0.001,
                  exclusive_orders=True, finalize_trades=True)
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
    print("BEAR MARKET 2022 BACKTEST".center(70))
    print("="*70)
    print("2022 was a brutal year: SPY -18.65%, AAPL -28%, NVDA -51%")
    print("="*70)

    tickers = ['NVDA', 'AAPL', 'SPY']
    results = []

    for ticker in tickers:
        csv_path = f"data/{ticker}_2022.csv"
        if not Path(csv_path).exists():
            print(f"\n[SKIP] {ticker}: Data file not found")
            continue

        print(f"\n{'='*70}")
        print(f"Testing: {ticker} (2022)")
        print('='*70)

        data = prepare_data_with_signals(csv_path)
        print(f"Data: {len(data)} bars")
        print(f"Price range: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
        print(f"Avg VIX: {data['VIX'].mean():.2f} (elevated = bear market)")

        # Calculate actual 2022 return
        actual_return = (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100
        print(f"Actual 2022 Return: {actual_return:.2f}%")

        adaptive_result = run_backtest(data, AdaptiveStrategy, ticker, 10000)
        results.append(adaptive_result)

        bh_result = run_backtest(data, BuyAndHoldStrategy, f"{ticker} (B&H)", 10000)
        results.append(bh_result)

        print(f"\nAdaptive: Return={adaptive_result['return']:.2f}%, Sharpe={adaptive_result['sharpe']:.2f}, "
              f"MaxDD={adaptive_result['max_dd']:.2f}%, Trades={adaptive_result['trades']}")
        print(f"Buy&Hold: Return={bh_result['return']:.2f}%, Sharpe={bh_result['sharpe']:.2f}, "
              f"MaxDD={bh_result['max_dd']:.2f}%")

        # Calculate improvement
        return_diff = adaptive_result['return'] - bh_result['return']
        dd_diff = adaptive_result['max_dd'] - bh_result['max_dd']
        print(f"  Return diff: {return_diff:+.2f}%")
        print(f"  Drawdown diff: {dd_diff:+.2f}% (negative is better)")

    # Summary table
    print("\n" + "="*70)
    print("SUMMARY TABLE - BEAR MARKET 2022")
    print("="*70)
    print(f"{'Strategy':<15} {'Return %':<12} {'Sharpe':<10} {'Max DD %':<12} {'Trades':<10}")
    print("-"*70)

    for r in results:
        print(f"{r['name']:<15} {r['return']:<12.2f} {r['sharpe']:<10.2f} {r['max_dd']:<12.2f} {r['trades']:<10}")

    print("="*70)

    # Bear market analysis
    print("\nBEAR MARKET ANALYSIS:")
    adaptive_results = [r for r in results if '(B&H)' not in r['name']]
    bh_results = [r for r in results if '(B&H)' in r['name']]

    avg_return_adaptive = sum(r['return'] for r in adaptive_results) / len(adaptive_results)
    avg_return_bh = sum(r['return'] for r in bh_results) / len(bh_results)
    avg_dd_adaptive = sum(r['max_dd'] for r in adaptive_results) / len(adaptive_results)
    avg_dd_bh = sum(r['max_dd'] for r in bh_results) / len(bh_results)

    print(f"  Average Return: Adaptive {avg_return_adaptive:.2f}% vs Buy&Hold {avg_return_bh:.2f}%")
    print(f"  Average Max DD: Adaptive {avg_dd_adaptive:.2f}% vs Buy&Hold {avg_dd_bh:.2f}%")

    if avg_return_adaptive > avg_return_bh:
        print(f"  [SUCCESS] Adaptive beat Buy&Hold by {avg_return_adaptive - avg_return_bh:.2f}%")
    else:
        print(f"  [INFO] Adaptive underperformed by {avg_return_bh - avg_return_adaptive:.2f}%")

    if avg_dd_adaptive < avg_dd_bh:
        print(f"  [GOOD] Adaptive had {avg_dd_bh - avg_dd_adaptive:.2f}% smaller drawdown")


if __name__ == "__main__":
    main()
