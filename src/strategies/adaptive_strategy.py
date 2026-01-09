"""
Strategy Logic Module
======================
Quantifiable, rule-based adaptive strategy using AI signals.

Key Concept:
- Transform AI Signals (Regime Score, Sentiment) into EXACT Buy/Sell rules
- No discretion, no "feeling" - pure mathematical logic

Strategy Matrix:
+-----------------+-----------------------------------------------------+
| Regime Condition | Strategy Mode & Entry Logic                        |
+-----------------+-----------------------------------------------------+
| > 0.5 (Bullish) | AGGRESSIVE: Buy if Sentiment > 0.2                 |
| < -0.5 (Bearish)| DEFENSIVE: Cash/Short if Sentiment < -0.8         |
| -0.5 to 0.5     | MEAN REVERSION: Buy at support, Sell at resistance |
+-----------------+-----------------------------------------------------+
"""

import numpy as np
from backtesting import Strategy
from backtesting.lib import crossover


# ============================================================================
# STRATEGY CONSTANTS (Hyperparameters)
# ============================================================================

class RegimeThreshold:
    """Threshold values for regime classification."""
    BULLISH_MIN = 0.5      # Above this = Bullish regime
    BEARISH_MAX = -0.5     # Below this = Bearish regime
    SIDEWAYS_MIN = -0.5    # Sideways lower bound
    SIDEWAYS_MAX = 0.5     # Sideways upper bound


class AggressiveMode:
    """Parameters for Aggressive (Bullish) mode."""
    SENTIMENT_ENTRY = 0.2      # Min sentiment to enter long
    SENTIMENT_EXIT = -0.3      # Exit if sentiment drops below
    POSITION_SIZE = 0.95       # Aggressive sizing (near full portfolio)


class DefensiveMode:
    """Parameters for Defensive (Bearish) mode."""
    SENTIMENT_SHORT = -0.8     # Max sentiment to enter short
    SENTIMENT_COVER = 0.3      # Cover if sentiment rises above
    POSITION_SIZE = 0.5        # Conservative sizing


class MeanReversionMode:
    """Parameters for Mean Reversion (Sideways) mode."""
    LOOKBACK_PERIOD = 20       # Period for support/resistance
    SUPPORT_THRESHOLD = 0.02   # Buy when price within 2% of support
    RESISTANCE_THRESHOLD = 0.02  # Sell when price within 2% of resistance
    POSITION_SIZE = 0.6        # Moderate sizing


# ============================================================================
# INDICATOR HELPERS
# ============================================================================

def calculate_support_resistance(series, period: int = 20):
    """
    Calculate rolling support and resistance levels.

    Args:
        series: Price series (can be pandas Series or backtesting _Array)
        period: Lookback period

    Returns:
        Tuple of (support_level, resistance_level)
    """
    # Import pandas here for the helper function
    import pandas as pd

    # Convert to pandas Series if needed
    if not hasattr(series, 'rolling'):
        # It's a backtesting _Array, convert to list then to Series
        series_array = pd.Series([series[i] for i in range(len(series))])
    else:
        series_array = series

    rolling_min = series_array.rolling(window=period, min_periods=1).min()
    rolling_max = series_array.rolling(window=period, min_periods=1).max()

    # Add slight buffer (don't buy at exact bottom, don't sell at exact top)
    support = rolling_min * (1 + MeanReversionMode.SUPPORT_THRESHOLD)
    resistance = rolling_max * (1 - MeanReversionMode.RESISTANCE_THRESHOLD)

    # Convert back to array if needed
    if not hasattr(series, 'rolling'):
        return support.values, resistance.values
    return support, resistance


def detect_regime(regime_score: float) -> str:
    """
    Classify current regime based on AI_Regime_Score.

    Args:
        regime_score: Current regime score value

    Returns:
        One of: 'BULLISH', 'BEARISH', 'SIDEWAYS'
    """
    if regime_score > RegimeThreshold.BULLISH_MIN:
        return 'BULLISH'
    elif regime_score < RegimeThreshold.BEARISH_MAX:
        return 'BEARISH'
    else:
        return 'SIDEWAYS'


# ============================================================================
# MAIN STRATEGY CLASS
# ============================================================================

class AdaptiveStrategy(Strategy):
    """
    Adaptive Strategy that changes behavior based on AI Regime Score.

    Rules are STRICT and QUANTIFIABLE:
    - Entry conditions are precise numerical comparisons
    - Exit conditions are precise numerical comparisons
    - Position sizing is deterministic based on regime

    No room for interpretation - either condition is met or not.
    """

    # Strategy parameters (can be overridden during initialization)
    regime_bullish_threshold = RegimeThreshold.BULLISH_MIN
    regime_bearish_threshold = RegimeThreshold.BEARISH_MAX

    # Aggressive mode parameters
    aggressive_sentiment_entry = AggressiveMode.SENTIMENT_ENTRY
    aggressive_sentiment_exit = AggressiveMode.SENTIMENT_EXIT
    aggressive_size = AggressiveMode.POSITION_SIZE

    # Defensive mode parameters
    defensive_sentiment_short = DefensiveMode.SENTIMENT_SHORT
    defensive_sentiment_cover = DefensiveMode.SENTIMENT_COVER
    defensive_size = DefensiveMode.POSITION_SIZE

    # Mean reversion mode parameters
    mr_lookback = MeanReversionMode.LOOKBACK_PERIOD
    mr_size = MeanReversionMode.POSITION_SIZE

    def init(self):
        """
        Initialize strategy indicators.
        This is called once before backtest starts.
        """
        # Extract AI signals from data
        # The backtesting library provides access via self.data
        self.regime_score = self.data.AI_Regime_Score
        self.sentiment = self.data.AI_Stock_Sentiment

        # Calculate support/resistance for mean reversion mode
        self.support, self.resistance = calculate_support_resistance(
            self.data.Close,
            self.mr_lookback
        )

        # Track current regime for logging
        self.current_regime = 'SIDEWAYS'

        # Track trade count by regime
        self.regime_trades = {
            'BULLISH': 0,
            'BEARISH': 0,
            'SIDEWAYS': 0
        }

    def get_regime(self) -> str:
        """
        Get current regime based on latest AI_Regime_Score.

        Returns:
            One of: 'BULLISH', 'BEARISH', 'SIDEWAYS'
        """
        # Get the most recent regime score
        latest_regime = self.regime_score[-1]
        return detect_regime(latest_regime)

    def execute_aggressive_mode(self):
        """
        AGGRESSIVE MODE (Bullish Regime)
        ===============================
        Logic: Market is trending up, be aggressive with long positions.

        Entry:  AI_Stock_Sentiment > threshold (0.2)
        Exit:   AI_Stock_Sentiment < exit_threshold (-0.3)
        Size:   Large (95% of equity)

        This is a "momentum-within-trend" approach.
        """
        current_sentiment = self.sentiment[-1]

        # ENTRY LOGIC: Strict numerical comparison
        if current_sentiment > self.aggressive_sentiment_entry:
            if not self.position:
                self.buy(size=self.aggressive_size)
                self.regime_trades['BULLISH'] += 1

        # EXIT LOGIC: Strict numerical comparison
        elif current_sentiment < self.aggressive_sentiment_exit:
            if self.position and self.position.is_long:
                self.position.close()

    def execute_defensive_mode(self):
        """
        DEFENSIVE MODE (Bearish Regime)
        ===============================
        Logic: Market is trending down, protect capital or profit from decline.

        Short Entry: AI_Stock_Sentiment < threshold (-0.8)
        Cover:       AI_Stock_Sentiment > cover_threshold (0.3)
        Size:        Conservative (50% of equity)

        This is a "preserve capital" approach with selective shorting.
        """
        current_sentiment = self.sentiment[-1]

        # SHORT ENTRY LOGIC: Strict numerical comparison
        if current_sentiment < self.defensive_sentiment_short:
            if not self.position:
                self.sell(size=self.defensive_size)
                self.regime_trades['BEARISH'] += 1

        # COVER LOGIC: Strict numerical comparison
        elif current_sentiment > self.defensive_sentiment_cover:
            if self.position and self.position.is_short:
                self.position.close()

    def execute_mean_reversion_mode(self):
        """
        MEAN REVERSION MODE (Sideways Regime)
        ======================================
        Logic: Market is range-bound, buy low and sell high.

        Buy Entry:  Price near support (within threshold)
        Sell Entry: Price near resistance (within threshold)
        Exit Long:  Price reaches mid-range or resistance
        Exit Short: Price reaches mid-range or support
        Size:       Moderate (60% of equity)

        This is a "oscillation" approach for ranging markets.
        """
        current_price = self.data.Close[-1]
        current_support = self.support[-1]
        current_resistance = self.resistance[-1]

        # BUY ENTRY: Price near support
        if current_price <= current_support * 1.01:  # Within 1% of support
            if not self.position or self.position.is_short:
                if self.position:
                    self.position.close()  # Cover any existing short
                self.buy(size=self.mr_size)
                self.regime_trades['SIDEWAYS'] += 1

        # SELL ENTRY: Price near resistance
        elif current_price >= current_resistance * 0.99:  # Within 1% of resistance
            if not self.position or self.position.is_long:
                if self.position:
                    self.position.close()  # Exit any existing long
                self.sell(size=self.mr_size)
                self.regime_trades['SIDEWAYS'] += 1

        # EXIT LONG: Price back to middle of range
        if self.position and self.position.is_long:
            mid_point = (current_support + current_resistance) / 2
            if current_price >= mid_point:
                self.position.close()

        # EXIT SHORT: Price back to middle of range
        if self.position and self.position.is_short:
            mid_point = (current_support + current_resistance) / 2
            if current_price <= mid_point:
                self.position.close()

    def next(self):
        """
        Main strategy logic - called on each candle.
        This is where we decide what to do based on current conditions.
        """
        # Detect current regime
        regime = self.get_regime()
        self.current_regime = regime

        # Execute strategy based on regime
        # Each mode has STRICT mathematical entry/exit rules
        if regime == 'BULLISH':
            self.execute_aggressive_mode()
        elif regime == 'BEARISH':
            self.execute_defensive_mode()
        else:  # SIDEWAYS
            self.execute_mean_reversion_mode()


# ============================================================================
# STRATEGY VARIANTS (For comparison)
# ============================================================================

class BuyAndHoldStrategy(Strategy):
    """Simple Buy and Hold for benchmark comparison."""

    def init(self):
        self.bought = False

    def next(self):
        if not self.bought:
            # Buy with 95% of equity (close to full position)
            self.buy(size=0.95)
            self.bought = True


class SimpleMomentumStrategy(Strategy):
    """Simple momentum strategy (no AI signals) for comparison."""

    # Parameters
    momentum_period = 10
    entry_threshold = 0.02  # 2% positive momentum
    exit_threshold = -0.01  # -1% momentum triggers exit

    def init(self):
        # No indicators needed, calculated in next()
        pass

    def next(self):
        # Need at least momentum_period bars
        if len(self.data.Close) < self.momentum_period + 1:
            return

        # Calculate current momentum
        current = self.data.Close[-1]
        past = self.data.Close[-self.momentum_period - 1]
        current_momentum = (current - past) / past if past != 0 else 0.0

        if current_momentum > self.entry_threshold:
            if not self.position:
                self.buy(size=0.95)
        elif current_momentum < self.exit_threshold:
            if self.position:
                self.position.close()


# ============================================================================
# UTILITIES
# ============================================================================

def print_strategy_rules():
    """Print all strategy rules in a readable format."""
    print("\n" + "=" * 70)
    print("ADAPTIVE STRATEGY - TRADING RULES")
    print("=" * 70)

    print("\n+--- BULLISH REGIME (AI_Regime_Score > 0.5) ---------------------+")
    print(f"| Mode:     AGGRESSIVE                                         |")
    print(f"| Buy If:   AI_Stock_Sentiment > {AggressiveMode.SENTIMENT_ENTRY:.1f}                    |")
    print(f"| Sell If:  AI_Stock_Sentiment < {AggressiveMode.SENTIMENT_EXIT:.1f}                   |")
    print(f"| Size:     {int(AggressiveMode.POSITION_SIZE * 100)}% of equity                                      |")
    print("+----------------------------------------------------------------+")

    print("\n+--- BEARISH REGIME (AI_Regime_Score < -0.5) --------------------+")
    print(f"| Mode:     DEFENSIVE                                          |")
    print(f"| Short If: AI_Stock_Sentiment < {DefensiveMode.SENTIMENT_SHORT:.1f}                   |")
    print(f"| Cover If: AI_Stock_Sentiment > {DefensiveMode.SENTIMENT_COVER:.1f}                    |")
    print(f"| Size:     {int(DefensiveMode.POSITION_SIZE * 100)}% of equity                                      |")
    print("+----------------------------------------------------------------+")

    print("\n+--- SIDEWAYS REGIME (-0.5 <= AI_Regime_Score <= 0.5) ----------+")
    print(f"| Mode:     MEAN REVERSION                                     |")
    print(f"| Buy If:   Price near support ({int(MeanReversionMode.SUPPORT_THRESHOLD * 100)}% buffer)              |")
    print(f"| Sell If:  Price near resistance ({int(MeanReversionMode.RESISTANCE_THRESHOLD * 100)}% buffer)        |")
    print(f"| Lookback: {MeanReversionMode.LOOKBACK_PERIOD} periods                                          |")
    print(f"| Size:     {int(MeanReversionMode.POSITION_SIZE * 100)}% of equity                                      |")
    print("+----------------------------------------------------------------+")
    print()


if __name__ == "__main__":
    # Print strategy rules when run directly
    print_strategy_rules()
