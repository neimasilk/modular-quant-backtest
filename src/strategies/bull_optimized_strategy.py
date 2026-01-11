"""
Bull Market Optimized Strategy for EXP-2025-006

Enhances AdaptiveStrategy with:
1. ADX trend strength filter
2. Trailing stop mechanism (5% from peak)
3. Trend-aware mode switching

Goal: Improve bull market capture while preserving bear market protection.
"""

import numpy as np
from backtesting import Strategy
from backtesting.lib import crossover

# Import parent strategy components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.adaptive_strategy import (
    calculate_volatility,
    calculate_support_resistance,
    detect_regime,
    RegimeThreshold,
    AggressiveMode,
    DefensiveMode,
    MeanReversionMode
)


# ============================================================================
# ADX INDICATOR
# ============================================================================

def calculate_adx(high, low, close, period=14):
    """
    Calculate Average Directional Index (ADX) - measures trend strength.

    ADX ranges from 0 to 100:
    - 0-20: Weak or no trend
    - 20-25: Emerging trend
    - 25-50: Strong trend
    - 50+: Very strong trend

    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: Lookback period (default 14)

    Returns:
        ADX values as numpy array
    """
    import pandas as pd

    # Convert to pandas Series if needed
    if not hasattr(high, 'rolling'):
        high = pd.Series(high)
        low = pd.Series(low)
        close = pd.Series(close)

    # Calculate True Range (TR)
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Calculate +DM and -DM
    plus_dm = high.diff()
    minus_dm = -low.diff()

    # Filter: only positive movements
    plus_dm = plus_dm.where((plus_dm > 0) & (plus_dm > minus_dm), 0.0)
    minus_dm = minus_dm.where((minus_dm > 0) & (minus_dm > plus_dm), 0.0)

    # Smooth TR, +DM, -DM
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

    # Calculate DX and ADX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()

    # Fill NaN with initial values
    adx = adx.fillna(20.0)  # Default to "weak trend"

    return adx.values


def is_strong_trend(adx_value: float, threshold: float = 25) -> bool:
    """Check if ADX indicates strong trend."""
    return adx_value >= threshold


# ============================================================================
# BULL OPTIMIZED STRATEGY
# ============================================================================

class BullOptimizedStrategy(Strategy):
    """
    Enhanced AdaptiveStrategy with bull market optimizations.

    Key Features:
    1. ADX trend filter - detects strong trends vs sideways
    2. Trailing stop (5%) - lets winners run in strong trends
    3. Mode-aware logic - different behavior per regime/trend combo
    """

    # Inherit base parameters
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

    # Risk Management
    stop_loss_pct = 0.20  # 20% hard stop (fallback)
    trailing_stop_pct = 0.05  # 5% trailing stop for strong trends

    # NEW: ADX Parameters
    adx_period = 14
    adx_trend_threshold = 25  # ADX >= 25 = strong trend
    use_trailing_stop = True  # Enable trailing stop feature

    # Track highest equity since position entry
    highest_equity_since_entry = None

    def init(self):
        """Initialize strategy indicators."""
        # Base indicators
        self.volatility = self.I(calculate_volatility, self.data.Close)
        self.support, self.resistance = self.I(
            calculate_support_resistance,
            self.data.Close,
            self.mr_lookback
        )

        # NEW: ADX indicator
        self.adx = self.I(
            calculate_adx,
            self.data.High,
            self.data.Low,
            self.data.Close,
            self.adx_period
        )

        # Track current regime
        self.current_regime = 'SIDEWAYS'

        # Track trade count by regime
        self.regime_trades = {
            'BULLISH': 0,
            'BEARISH': 0,
            'SIDEWAYS': 0
        }

        # Track entry price for trailing stop
        self.entry_price = None
        self.highest_since_entry = None

    def get_regime(self) -> str:
        """Get current regime based on AI_Regime_Score."""
        latest_regime = self.data.AI_Regime_Score[-1]
        return detect_regime(latest_regime)

    def is_strong_trend(self) -> bool:
        """Check if current ADX indicates strong trend."""
        current_adx = self.adx[-1]
        return is_strong_trend(current_adx, self.adx_trend_threshold)

    def get_trailing_stop_price(self) -> float:
        """
        Calculate trailing stop price based on highest equity since entry.

        Returns:
            Stop price level, or None if no position
        """
        if not self.position:
            return None

        # Track highest price since entry
        current_price = self.data.Close[-1]

        if self.highest_since_entry is None or current_price > self.highest_since_entry:
            self.highest_since_entry = current_price

        # Trailing stop is 5% below peak
        return self.highest_since_entry * (1 - self.trailing_stop_pct)

    def execute_aggressive_mode(self):
        """
        Execute Aggressive (Bullish) strategy with trend-aware logic.
        """
        strong_trend = self.is_strong_trend()

        # Get current sentiment
        if hasattr(self.data, 'AI_Stock_Sentiment'):
            current_sentiment = self.data.AI_Stock_Sentiment[-1]
        else:
            current_sentiment = 0.0

        # ENTRY LOGIC
        if current_sentiment > self.aggr_entry_thresh:
            if not self.position:
                size = self.aggr_size
                current_price = self.data.Close[-1]

                # In strong trend, use trailing stop. Otherwise, fixed stop.
                if strong_trend and self.use_trailing_stop:
                    # Entry with trailing stop logic handled in next()
                    self.buy(size=min(size, 0.95))
                    self.highest_since_entry = current_price
                else:
                    # Fixed 20% stop
                    sl_price = current_price * (1 - self.stop_loss_pct)
                    self.buy(size=min(size, 0.95), sl=sl_price)

                self.regime_trades['BULLISH'] += 1

        # EXIT LOGIC - Different for strong trend vs normal
        elif strong_trend and self.use_trailing_stop:
            # In strong trend: only exit on trailing stop breach
            if self.position and self.position.is_long:
                trailing_stop = self.get_trailing_stop_price()
                current_price = self.data.Close[-1]

                if trailing_stop and current_price < trailing_stop:
                    self.position.close()
                    self.highest_since_entry = None

        elif current_sentiment < self.aggr_exit_thresh:
            # Normal: exit on sentiment drop
            if self.position and self.position.is_long:
                self.position.close()
                self.highest_since_entry = None

    def execute_defensive_mode(self):
        """Execute Defensive (Bearish) strategy (unchanged from base)."""
        # Get current sentiment
        if hasattr(self.data, 'AI_Stock_Sentiment'):
            current_sentiment = self.data.AI_Stock_Sentiment[-1]
        else:
            current_sentiment = 0.0

        # SHORT ENTRY LOGIC
        if current_sentiment < self.def_short_thresh:
            if not self.position:
                size = self.def_size
                current_price = self.data.Close[-1]
                sl_price = current_price * (1 + self.stop_loss_pct)
                self.sell(size=size, sl=sl_price)
                self.regime_trades['BEARISH'] += 1

        # COVER LOGIC
        elif current_sentiment > self.def_cover_thresh:
            if self.position and self.position.is_short:
                self.position.close()

    def execute_mean_reversion_mode(self):
        """
        Execute Mean Reversion (Sideways) strategy.
        Modified to skip mean reversion in strong trends.
        """
        # NEW: Skip mean reversion if strong trend detected
        # In strong trends, we don't want to sell at "resistance"
        if self.is_strong_trend():
            # Let the aggressive mode handle it, or stay in cash
            return

        current_support = self.support[-1]
        current_resistance = self.resistance[-1]
        mid_point = (current_support + current_resistance) / 2
        current_price = self.data.Close[-1]

        # BUY ENTRY: Price near support
        if current_price <= current_support * (1 + 0.03):
            if not self.position or self.position.is_short:
                if self.position:
                    self.position.close()

                sl_price = current_price * (1 - self.stop_loss_pct)

                if mid_point <= current_price * 1.005:
                    target_price = current_resistance
                else:
                    target_price = mid_point

                if target_price <= current_price * 1.005:
                    target_price = current_price * 1.05

                self.buy(size=self.mr_size, sl=sl_price, tp=target_price)
                self.regime_trades['SIDEWAYS'] += 1

        # SELL ENTRY: Price near resistance
        elif current_price >= current_resistance * (1 - 0.03):
            if not self.position or self.position.is_long:
                if self.position:
                    self.position.close()

                sl_price = current_price * (1 + self.stop_loss_pct)

                if mid_point >= current_price * 0.995:
                    target_price = current_support
                else:
                    target_price = mid_point

                if target_price >= current_price * 0.995:
                    target_price = current_price * 0.95

                self.sell(size=self.mr_size, sl=sl_price, tp=target_price)
                self.regime_trades['SIDEWAYS'] += 1

    def next(self):
        """
        Main strategy logic - called on each candle.
        """
        # Update trailing stop tracking for open long positions
        if self.position and self.position.is_long:
            current_price = self.data.Close[-1]
            strong_trend = self.is_strong_trend()

            if strong_trend and self.use_trailing_stop:
                # Update highest since entry
                if self.highest_since_entry is None or current_price > self.highest_since_entry:
                    self.highest_since_entry = current_price

                # Check trailing stop
                if self.highest_since_entry:
                    trailing_stop = self.highest_since_entry * (1 - self.trailing_stop_pct)
                    if current_price < trailing_stop:
                        self.position.close()
                        self.highest_since_entry = None
                        return

        # Detect current regime
        regime = self.get_regime()
        self.current_regime = regime

        # Execute strategy based on regime
        if regime == 'BULLISH':
            self.execute_aggressive_mode()
        elif regime == 'BEARISH':
            self.execute_defensive_mode()
        else:
            self.execute_mean_reversion_mode()


# For comparison: Original AdaptiveStrategy (without bull optimizations)
from .adaptive_strategy import AdaptiveStrategy

__all__ = ['BullOptimizedStrategy', 'AdaptiveStrategy']
