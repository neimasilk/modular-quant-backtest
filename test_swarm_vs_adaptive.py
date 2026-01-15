import pandas as pd
import numpy as np
from backtesting import Backtest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.strategies.adaptive_strategy import AdaptiveStrategy
from src.swarm.swarm_strategy import SwarmStrategy

def prepare_data(file_path):
    """Load and prepare data for backtesting."""
    data = pd.read_csv(file_path, parse_dates=['Date'], index_col='Date')
    
    # Ensure columns are capitalized as required by backtesting.py
    data.columns = [col.capitalize() if col.lower() in ['open', 'high', 'low', 'close', 'volume'] else col for col in data.columns]
    
    # Add dummy VIX if not present (using 20 as neutral baseline)
    if 'VIX' not in data.columns:
        data['VIX'] = 20.0
        
    # Ensure AI_Stock_Sentiment exists (fallback to 0)
    if 'AI_Stock_Sentiment' not in data.columns:
        data['AI_Stock_Sentiment'] = 0.0
        
    return data

def run_comparison():
    """Compare Swarm vs Adaptive across multiple tickers and years."""
    results = []
    tickers = ['NVDA', 'AAPL', 'SPY']
    years = ['2022', '2023']
    
    # Output directory
    os.makedirs('experiments/active/EXP-2025-011-swarm-intelligence/results', exist_ok=True)
    
    print(f"{'Ticker':<6} | {'Year':<5} | {'Strategy':<10} | {'Return %':<10} | {'Sharpe':<8} | {'MaxDD %':<10} | {'Trades':<6}")
    print("-" * 75)
    
    for ticker in tickers:
        for year in years:
            file_path = f'data/{ticker}_{year}.csv'
            if not os.path.exists(file_path):
                continue
                
            data = prepare_data(file_path)
            
            # 1. Run Adaptive (Baseline)
            bt_adaptive = Backtest(data, AdaptiveStrategy, cash=10000, commission=.002)
            stats_adaptive = bt_adaptive.run()
            
            # 2. Run Swarm
            bt_swarm = Backtest(data, SwarmStrategy, cash=10000, commission=.002)
            stats_swarm = bt_swarm.run()
            
            # Log results
            for name, stats in [("Adaptive", stats_adaptive), ("Swarm", stats_swarm)]:
                results.append({
                    'Ticker': ticker,
                    'Year': year,
                    'Strategy': name,
                    'Return': stats['Return [%]'],
                    'Sharpe': stats['Sharpe Ratio'],
                    'MaxDD': stats['Max. Drawdown [%]'],
                    'Trades': stats['# Trades'],
                    'WinRate': stats['Win Rate [%]']
                })
                print(f"{ticker:<6} | {year:<5} | {name:<10} | {stats['Return [%]']:>9.2f}% | {stats['Sharpe Ratio']:>7.2f} | {stats['Max. Drawdown [%]']:>9.2f}% | {stats['# Trades']:<6}")
            print("-" * 75)
            
    # Save to CSV
    df_results = pd.DataFrame(results)
    output_path = 'experiments/active/EXP-2025-011-swarm-intelligence/results/comparison.csv'
    df_results.to_csv(output_path, index=False)
    print(f"\nResults saved to {output_path}")
    
    # Generate Summary
    summary = df_results.groupby('Strategy')[['Return', 'Sharpe', 'MaxDD']].mean()
    print("\nOVERALL SUMMARY (Average across all tests):")
    print(summary)

if __name__ == "__main__":
    run_comparison()
