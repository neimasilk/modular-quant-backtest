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
    SENTIMENT_ENTRY = 0.0      # Min sentiment to enter long (lowered from 0.2 for more trades)
    SENTIMENT_EXIT = -0.5      # Exit if sentiment drops below (widened from -0.3)
    POSITION_SIZE = 0.95       # Aggressive sizing (near full portfolio)


class DefensiveMode:
    """Parameters for Defensive (Bearish) mode."""
    SENTIMENT_SHORT = -0.3     # Max sentiment to enter short (raised from -0.8 for more trades)
    SENTIMENT_COVER = 0.0      # Cover if sentiment rises above (lowered from 0.3)
    POSITION_SIZE = 0.5        # Conservative sizing


class MeanReversionMode:
    """Parameters for Mean Reversion (Sideways) mode."""
    LOOKBACK_PERIOD = 20       # Period for support/resistance
    SUPPORT_THRESHOLD = 0.03   # Buy when price within 3% of support (widened from 2%)
    RESISTANCE_THRESHOLD = 0.03  # Sell when price within 3% of resistance (widened from 2%)
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


def calculate_volatility(closes, period: int = 20) -> float:
    """
    Calculate annualized volatility from close prices.

    Args:
        closes: Close price series (backtesting _Array)
        period: Lookback period for volatility calculation

    Returns:
        Annualized volatility as percentage (e.g., 0.30 for 30%)
    """
    # Convert to list if needed
    if len(closes) < period + 1:
        return 0.2  # Default volatility

    # Calculate returns for last 'period' bars
    returns = []
    for i in range(max(0, len(closes) - period), len(closes)):
        if i > 0:
            ret = (closes[i] - closes[i-1]) / closes[i-1]
            returns.append(ret)

    if len(returns) == 0:
        return 0.2

    # Calculate standard deviation
    import numpy as np
    vol_std = np.std(returns)

    # Annualize (252 trading days)
    vol_annual = vol_std * np.sqrt(252)

    return float(vol_annual)


def get_dynamic_thresholds(volatility: float):
    """
    Calculate dynamic entry/exit thresholds based on volatility.

    Logic:
    - Low volatility (< 20%): Standard thresholds (more selective)
    - Medium volatility (20-50%): Relaxed thresholds
    - High volatility (50-80%): Very relaxed thresholds
    - Extreme volatility (> 80%): Aggressive thresholds (for volatile stocks)

    Args:
        volatility: Annualized volatility (e.g., 0.30 for 30%)

    Returns:
        Dictionary with dynamic thresholds
    """
    if volatility < 0.20:
        # Low volatility - Standard thresholds
        return {
            'aggressive_entry': 0.2,
            'aggressive_exit': -0.3,
            'defensive_short': -0.8,
            'defensive_cover': 0.3,
            'position_multiplier': 1.0
        }
    elif volatility < 0.50:
        # Medium volatility - Relaxed thresholds
        return {
            'aggressive_entry': 0.1,
            'aggressive_exit': -0.2,
            'defensive_short': -0.6,
            'defensive_cover': 0.2,
            'position_multiplier': 0.9
        }
    elif volatility < 0.80:
        # High volatility - Very relaxed thresholds
        return {
            'aggressive_entry': 0.0,
            'aggressive_exit': -0.1,
            'defensive_short': -0.4,
            'defensive_cover': 0.1,
            'position_multiplier': 0.7
        }
    else:
        # Extreme volatility - Aggressive thresholds for small caps
        return {
            'aggressive_entry': -0.1,  # Allow buy even with slightly negative sentiment
            'aggressive_exit': -0.3,
            'defensive_short': -0.3,
            'defensive_cover': 0.1,
            'position_multiplier': 0.5  # Smaller position size for extreme vol
        }


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
    aggr_entry_thresh = AggressiveMode.SENTIMENT_ENTRY
    aggr_exit_thresh = AggressiveMode.SENTIMENT_EXIT
    aggr_size = AggressiveMode.POSITION_SIZE

    # Defensive mode parameters
    def_short_thresh = DefensiveMode.SENTIMENT_SHORT
    def_cover_thresh = DefensiveMode.SENTIMENT_COVER
    def_size = DefensiveMode.POSITION_SIZE

    # Mean reversion mode parameters
    mr_lookback = MeanReversionMode.LOOKBACK_PERIOD
    mr_size = MeanReversionMode.POSITION_SIZE
    mr_support_thresh = MeanReversionMode.SUPPORT_THRESHOLD
    mr_resist_thresh = MeanReversionMode.RESISTANCE_THRESHOLD

    # Dynamic threshold settings
    use_dynamic_thresholds = True  # Set to False to use fixed thresholds

    # Risk Management - CRITICAL: Hard stop-loss to prevent total loss
    stop_loss_pct = 0.20  # 20% hard stop-loss (can be overridden)
    trailing_stop_pct = 0.05  # 5% trailing stop for profit protection

    def init(self):
        """
        Initialize strategy indicators.
        This is called once before backtest starts.
        """
        # NOTE: We don't store AI signal arrays here.
        # The backtesting library slices arrays based on current bar index.
        # We access them directly through self.data in each method to get
        # the properly sliced version for the current bar.

        # Calculate market volatility
        self.volatility = calculate_volatility(self.data.Close)

        # Get dynamic thresholds based on volatility
        if self.use_dynamic_thresholds:
            self.dynamic_thresholds = get_dynamic_thresholds(self.volatility)
        else:
            # Use fixed thresholds (original behavior)
            self.dynamic_thresholds = {
                'aggressive_entry': AggressiveMode.SENTIMENT_ENTRY,
                'aggressive_exit': AggressiveMode.SENTIMENT_EXIT,
                'defensive_short': DefensiveMode.SENTIMENT_SHORT,
                'defensive_cover': DefensiveMode.SENTIMENT_COVER,
                'position_multiplier': 1.0
            }

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
        # Access directly through self.data to get properly sliced array
        latest_regime = self.data.AI_Regime_Score[-1]
        return detect_regime(latest_regime)

    def execute_aggressive_mode(self):
        """
        Execute Aggressive (Bullish) strategy.
        Focus: Buy dips, hold for trend.
        """
        # Use optimizable thresholds
        entry_threshold = self.dynamic_thresholds.get('aggressive_entry', self.aggr_entry_thresh)
        exit_threshold = self.dynamic_thresholds.get('aggressive_exit', self.aggr_exit_thresh)
        pos_multiplier = self.dynamic_thresholds.get('position_multiplier', 1.0)

        # Get current sentiment
        # We need to handle both pandas Series and numpy array
        if hasattr(self.data, 'AI_Stock_Sentiment'):
            current_sentiment = self.data.AI_Stock_Sentiment[-1]
        else:
            current_sentiment = 0.0

        # ENTRY LOGIC: Strict numerical comparison
        if current_sentiment > entry_threshold:
            if not self.position:
                size = self.aggr_size * pos_multiplier
                current_price = self.data.Close[-1]
                sl_price = current_price * (1 - self.stop_loss_pct)
                
                self.buy(size=min(size, 0.95), sl=sl_price)  # Cap at 95%
                self.regime_trades['BULLISH'] += 1

        # EXIT LOGIC: Strict numerical comparison
        elif current_sentiment < exit_threshold:
            if self.position and self.position.is_long:
                self.position.close()

    def execute_defensive_mode(self):
        """
        Execute Defensive (Bearish) strategy.
        Focus: Short rallies, cash preservation.
        """
        # Use optimizable thresholds
        short_threshold = self.dynamic_thresholds.get('defensive_short', self.def_short_thresh)
        cover_threshold = self.dynamic_thresholds.get('defensive_cover', self.def_cover_thresh)
        pos_multiplier = self.dynamic_thresholds.get('position_multiplier', 1.0)

        # Get current sentiment
        if hasattr(self.data, 'AI_Stock_Sentiment'):
            current_sentiment = self.data.AI_Stock_Sentiment[-1]
        else:
            current_sentiment = 0.0

        # SHORT ENTRY LOGIC: Strict numerical comparison
        if current_sentiment < short_threshold:
            if not self.position:
                size = self.def_size * pos_multiplier
                current_price = self.data.Close[-1]
                sl_price = current_price * (1 + self.stop_loss_pct)
                
                self.sell(size=size, sl=sl_price)
                self.regime_trades['BEARISH'] += 1

        # COVER LOGIC: Strict numerical comparison
        elif current_sentiment > cover_threshold:
            if self.position and self.position.is_short:
                self.position.close()

    def execute_mean_reversion_mode(self):
        """
        Execute Mean Reversion (Sideways) strategy.
        Focus: Buy support, Sell resistance.
        """
        # Get support/resistance levels
        # When using self.I, these are arrays synced with data
        current_support = self.support[-1]
        current_resistance = self.resistance[-1]
        mid_point = (current_support + current_resistance) / 2
        
        current_price = self.data.Close[-1]
        dynamic_size = self.mr_size

        # BUY ENTRY: Price near support
        # Use optimizable threshold
        if current_price <= current_support * (1 + self.mr_support_thresh):  # Within threshold of support
            if not self.position or self.position.is_short:
                if self.position:
                    self.position.close()  # Cover any existing short
                
                sl_price = current_price * (1 - self.stop_loss_pct)
                self.buy(size=dynamic_size, sl=sl_price, tp=mid_point)
                self.regime_trades['SIDEWAYS'] += 1

        # SELL ENTRY: Price near resistance
        elif current_price >= current_resistance * (1 - self.mr_resist_thresh):  # Within threshold of resistance
            if not self.position or self.position.is_long:
                if self.position:
                    self.position.close()  # Exit any existing long
                
                sl_price = current_price * (1 + self.stop_loss_pct)
                self.sell(size=dynamic_size, sl=sl_price, tp=mid_point)
                self.regime_trades['SIDEWAYS'] += 1

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
