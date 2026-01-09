"""
Data Layer Module
==================
Menghasilkan mock OHLCV data dengan AI Signals untuk backtesting.

Structure:
- prepare_data(): Generate base OHLCV DataFrame
- add_ai_signals(): Add AI Regime Score & Stock Sentiment
- create_correlated_signals(): Create realistic signal patterns
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple


def generate_ohlcv(
    n_days: int = 252,
    start_price: float = 100.0,
    volatility: float = 0.02,
    drift: float = 0.0005
) -> pd.DataFrame:
    """
    Generate base OHLCV data using Geometric Brownian Motion.

    Args:
        n_days: Number of trading days (default 252 = 1 year)
        start_price: Initial price
        volatility: Daily volatility (std of returns)
        drift: Daily drift (tendency)

    Returns:
        DataFrame with Date, Open, High, Low, Close, Volume
    """
    np.random.seed(42)  # For reproducibility

    # Generate returns with drift
    returns = np.random.normal(drift, volatility, n_days)

    # Generate price path
    prices = start_price * np.exp(np.cumsum(returns))
    prices = np.insert(prices, 0, start_price)  # Add starting price

    dates = pd.date_range(
        start=datetime.now() - timedelta(days=n_days),
        periods=n_days,
        freq='B'  # Business days
    )

    data = []
    for i in range(n_days):
        open_price = prices[i]
        close_price = prices[i + 1]

        # High/Low based on intraday volatility
        intraday_vol = volatility * 0.5
        high = max(open_price, close_price) * (1 + np.random.uniform(0, intraday_vol))
        low = min(open_price, close_price) * (1 - np.random.uniform(0, intraday_vol))

        # Volume (random with some autocorrelation)
        base_volume = 1_000_000
        volume_factor = np.random.lognormal(0, 0.3)
        volume = int(base_volume * volume_factor)

        data.append({
            'Date': dates[i],
            'Open': round(open_price, 2),
            'High': round(high, 2),
            'Low': round(low, 2),
            'Close': round(close_price, 2),
            'Volume': volume
        })

    df = pd.DataFrame(data)
    return df


def create_regime_signals(n_days: int) -> np.ndarray:
    """
    Create realistic Regime Score patterns with persistence.
    Regimes tend to persist for a while (market doesn't flip-flop daily).

    Args:
        n_days: Number of days

    Returns:
        Array of regime scores (-1.0 to 1.0)
    """
    np.random.seed(42)

    # Use Ornstein-Uhlenbeck process for mean-reverting regime scores
    # This creates realistic regime transitions

    regime_score = np.zeros(n_days)
    current_regime = 0.0
    mean_reversion_speed = 0.05  # How fast it reverts to 0
    regime_volatility = 0.15     # How much it fluctuates

    for i in range(n_days):
        # OU process: dX = theta * (mu - X) * dt + sigma * dW
        # theta = mean_reversion_speed, mu = 0, sigma = regime_volatility
        change = mean_reversion_speed * (0 - current_regime) + \
                 regime_volatility * np.random.randn()
        current_regime = np.clip(current_regime + change, -1.0, 1.0)
        regime_score[i] = current_regime

    return regime_score


def create_sentiment_signals(
    n_days: int,
    regime_scores: np.ndarray,
    correlation: float = 0.3
) -> np.ndarray:
    """
    Create sentiment signals with partial correlation to regime.

    Logic:
    - Sentiment correlates with Regime Score but has idiosyncratic noise
    - News-driven sentiment can be different from macro regime

    Args:
        n_days: Number of days
        regime_scores: Array of regime scores
        correlation: How much sentiment correlates with regime (0-1)

    Returns:
        Array of sentiment scores (-1.0 to 1.0)
    """
    np.random.seed(43)

    # Base sentiment from regime (correlated component)
    correlated_part = regime_scores * correlation

    # Idiosyncratic component (news-specific, stock-specific)
    idiosyncratic_part = np.random.randn(n_days) * 0.4

    # Combine and normalize
    sentiment = correlated_part + idiosyncratic_part
    sentiment = np.clip(sentiment, -1.0, 1.0)

    return sentiment


def add_price_impact_from_signals(
    df: pd.DataFrame,
    regime_scores: np.ndarray,
    sentiment_scores: np.ndarray,
    impact_strength: float = 0.3
) -> pd.DataFrame:
    """
    Add subtle price impact from AI signals to make backtest more realistic.
    High Regime Score -> slight upward bias
    Low Regime Score -> slight downward bias

    Args:
        df: Original OHLCV DataFrame
        regime_scores: Array of regime scores
        sentiment_scores: Array of sentiment scores
        impact_strength: How much signals affect price

    Returns:
        Modified DataFrame
    """
    df = df.copy()

    # Combined signal impact
    signal_impact = (regime_scores * 0.7 + sentiment_scores * 0.3) * impact_strength

    # Adjust close prices based on signals (very subtle)
    for i in range(len(df)):
        original_close = df.loc[i, 'Close']
        adjustment = 1 + signal_impact[i] * 0.001  # Very small daily impact
        df.loc[i, 'Close'] = round(original_close * adjustment, 2)

        # Ensure OHLC relationships are maintained
        if df.loc[i, 'Close'] > df.loc[i, 'High']:
            df.loc[i, 'High'] = df.loc[i, 'Close']
        if df.loc[i, 'Close'] < df.loc[i, 'Low']:
            df.loc[i, 'Low'] = df.loc[i, 'Close']

    return df


def prepare_data(
    n_days: int = 252,
    start_price: float = 100.0,
    volatility: float = 0.02,
    add_signal_impact: bool = True
) -> pd.DataFrame:
    """
    Main function: Generate complete dataset for backtesting.

    Args:
        n_days: Number of trading days
        start_price: Initial price
        volatility: Daily volatility
        add_signal_impact: Whether signals subtly affect prices

    Returns:
        DataFrame with columns:
        - Date, Open, High, Low, Close, Volume (OHLCV)
        - AI_Regime_Score (Macro regime from LLM analysis)
        - AI_Stock_Sentiment (Stock sentiment from news analysis)
    """
    # Step 1: Generate base OHLCV data
    df = generate_ohlcv(n_days, start_price, volatility)

    # Step 2: Generate AI Signals
    regime_scores = create_regime_signals(n_days)
    sentiment_scores = create_sentiment_signals(n_days, regime_scores)

    # Step 3: Add AI Signals to DataFrame
    df['AI_Regime_Score'] = regime_scores
    df['AI_Stock_Sentiment'] = sentiment_scores

    # Step 4: Optionally add price impact from signals
    if add_signal_impact:
        df = add_price_impact_from_signals(df, regime_scores, sentiment_scores)

    # Set Date as index for backtesting library
    df.set_index('Date', inplace=True)

    return df


def get_regime_distribution(df: pd.DataFrame) -> pd.Series:
    """
    Helper: Analyze regime distribution in the dataset.

    Args:
        df: DataFrame with AI_Regime_Score column

    Returns:
        Series with regime counts
    """
    regime = df['AI_Regime_Score']

    return pd.Series({
        'Bullish_Days': (regime > 0.5).sum(),
        'Bearish_Days': (regime < -0.5).sum(),
        'Sideways_Days': ((regime >= -0.5) & (regime <= 0.5)).sum(),
        'Avg_Regime': regime.mean(),
        'Avg_Sentiment': df['AI_Stock_Sentiment'].mean()
    })


# ============================================================================
# VALIDATION & UTILITIES
# ============================================================================

def validate_dataframe(df: pd.DataFrame) -> bool:
    """
    Validate that DataFrame meets all requirements.

    Args:
        df: DataFrame to validate

    Returns:
        True if valid, raises AssertionError if not
    """
    # Check required columns
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume',
                     'AI_Regime_Score', 'AI_Stock_Sentiment']
    missing_cols = set(required_cols) - set(df.columns)
    assert len(missing_cols) == 0, f"Missing columns: {missing_cols}"

    # Check OHLC relationships
    assert (df['High'] >= df['Open']).all(), "High must be >= Open"
    assert (df['High'] >= df['Close']).all(), "High must be >= Close"
    assert (df['Low'] <= df['Open']).all(), "Low must be <= Open"
    assert (df['Low'] <= df['Close']).all(), "Low must be <= Close"
    assert (df['Volume'] > 0).all(), "Volume must be positive"

    # Check AI signal ranges
    assert df['AI_Regime_Score'].between(-1, 1).all(), "Regime Score out of range"
    assert df['AI_Stock_Sentiment'].between(-1, 1).all(), "Sentiment out of range"

    # Check for NaN
    assert df.isna().sum().sum() == 0, "DataFrame contains NaN values"

    return True


if __name__ == "__main__":
    # Quick test of data generation
    print("=" * 60)
    print("DATA LAYER - MOCK DATA GENERATION TEST")
    print("=" * 60)

    df = prepare_data(n_days=252)
    validate_dataframe(df)

    print(f"\nGenerated {len(df)} rows of data")
    print(f"\nFirst 5 rows:\n{df.head()}")

    stats = get_regime_distribution(df)
    print(f"\nRegime Distribution:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")

    print("\n[OK] Data layer validation passed!")
