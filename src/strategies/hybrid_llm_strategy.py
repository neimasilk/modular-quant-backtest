"""
Hybrid LLM Strategy - EXP-2025-009
===================================
Combines Adaptive Strategy (proven bear market performance) with LLM Sanity Checker
to filter out emotional trading mistakes (FOMO/Panic).

Strategy Philosophy:
- Adaptive Strategy = Baseline signal generator (regime-based)
- LLM Sanity Checker = Veto power on extreme volatility events
- Goal: Reduce drawdown by 20-30% while maintaining upside capture

Key Innovation:
- LLM doesn't predict - it PREVENTS stupidity
- Only activates on >3% moves (cost-efficient)
- Overrides are rare but high-impact

Performance Target:
- Bear markets: Match or beat Adaptive Strategy (-4% DD → -3% DD)
- Bull markets: Improve on Adaptive Strategy (+94% → +110%+)
- Key metric: Sharpe ratio improvement 10-20%
"""

import numpy as np
from backtesting import Strategy
from typing import Optional, Dict
import pandas as pd

# Import base components
from src.strategies.adaptive_strategy import (
    AdaptiveStrategy,
    RegimeThreshold,
    AggressiveMode,
    DefensiveMode,
    MeanReversionMode,
    detect_regime
)

try:
    from src.llm.sanity_checker import NewsSanityChecker
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("[WARNING] LLM Sanity Checker not available - running in Adaptive-only mode")


class HybridLLMStrategy(AdaptiveStrategy):
    """
    Hybrid Strategy that combines:
    1. Adaptive Strategy (regime-based baseline)
    2. LLM Sanity Checker (veto power on volatile moves)

    Inheritance Structure:
    - Inherits all Adaptive Strategy logic
    - Adds LLM filter layer on top
    - Maintains same parameters for easy comparison
    """

    # LLM-specific parameters
    llm_enabled = True                    # Enable/disable LLM filter
    llm_volatility_threshold = 0.03       # Only call LLM on >3% moves
    llm_veto_enabled = True               # Allow LLM to veto signals
    llm_override_enabled = True           # Allow LLM to override (e.g., buy dip on panic)

    # Mock mode for backtesting (when no real news data)
    mock_llm_mode = False                 # Use simulated LLM responses
    mock_llm_accuracy = 0.70              # Simulated accuracy (70% correct calls)

    # Tracking metrics
    llm_calls_count = 0
    llm_vetoes_count = 0
    llm_overrides_count = 0

    def init(self):
        """
        Initialize strategy - calls parent AdaptiveStrategy.init()
        plus LLM-specific setup.
        """
        # Initialize parent (Adaptive Strategy indicators)
        super().init()

        # Initialize LLM checker (if available and enabled)
        self.llm_checker = None
        if self.llm_enabled and LLM_AVAILABLE and not self.mock_llm_mode:
            try:
                self.llm_checker = NewsSanityChecker()
                print("[HYBRID] LLM Sanity Checker initialized successfully")
            except Exception as e:
                print(f"[HYBRID] LLM initialization failed: {e}")
                print("[HYBRID] Falling back to Adaptive-only mode")
                self.llm_enabled = False

        # Tracking
        self.llm_decisions = []  # Store all LLM decisions for analysis

    def get_price_change_pct(self) -> float:
        """
        Calculate price change percentage from previous bar.
        Returns: Decimal (e.g., 0.05 for +5%)
        """
        if len(self.data.Close) < 2:
            return 0.0

        current_price = self.data.Close[-1]
        prev_price = self.data.Close[-2]

        if prev_price == 0:
            return 0.0

        return (current_price - prev_price) / prev_price

    def get_news_for_current_bar(self) -> str:
        """
        Get news text for current bar.

        In real implementation, this would:
        - Query news API for timestamp range
        - Filter by ticker
        - Return concatenated headlines

        For backtesting with mock mode:
        - Return simulated news based on price action
        """
        # Check if we have a News column in data
        if hasattr(self.data, 'News') and self.data.News is not None:
            return str(self.data.News[-1]) if self.data.News[-1] else ""

        # Mock mode: Generate fake news based on price action
        if self.mock_llm_mode:
            price_change = self.get_price_change_pct()

            if abs(price_change) < self.llm_volatility_threshold:
                return ""  # No significant move, no news

            # Generate contextual fake news
            ticker = getattr(self.data, 'ticker', 'STOCK')
            if price_change > 0.05:
                return f"{ticker} announces major partnership deal"
            elif price_change > 0.03:
                return f"{ticker} beats analyst expectations"
            elif price_change < -0.05:
                return f"{ticker} faces regulatory scrutiny"
            elif price_change < -0.03:
                return f"{ticker} misses revenue targets"
            else:
                return f"{ticker} reports quarterly results"

        return ""

    def mock_llm_decision(self, price_change_pct: float) -> Dict:
        """
        Simulate LLM decision for backtesting without real API calls.

        Uses probabilistic model based on:
        - Price change magnitude
        - Simulated "news substance" (correlated with price)
        - Random noise (to simulate 70% accuracy)

        Returns: Same format as NewsSanityChecker.check_signal()
        """
        # Simulate substance score (higher price change = higher variance in score)
        # Sometimes big moves are justified, sometimes they're noise
        np.random.seed(int(self.data.index[-1]))  # Deterministic randomness per bar

        # Generate substance score with realistic distribution
        if abs(price_change_pct) > 0.08:
            # Very large moves: 50/50 chance of high/low substance
            substance_score = np.random.choice([2, 3, 8, 9])
        elif abs(price_change_pct) > 0.05:
            # Medium moves: Mostly moderate substance
            substance_score = np.random.choice([3, 4, 5, 6, 7])
        else:
            # Small moves: Usually low substance
            substance_score = np.random.choice([2, 3, 4, 5])

        # Add accuracy noise (30% chance of wrong assessment)
        if np.random.random() > self.mock_llm_accuracy:
            # Invert the score (simulate wrong assessment)
            substance_score = 10 - substance_score

        # Translate to signal (same logic as real LLM checker)
        LOW_SUBSTANCE = 4
        HIGH_SUBSTANCE = 7

        if price_change_pct > 0:  # Price UP
            if substance_score < LOW_SUBSTANCE:
                signal = "SHORT_SCALP"  # Hype, fade it
                verdict = "FADE"
            elif substance_score > HIGH_SUBSTANCE:
                signal = "BUY_TREND"    # Real news, follow
                verdict = "FOLLOW"
            else:
                signal = "NEUTRAL"
                verdict = "IGNORE"
        else:  # Price DOWN
            if substance_score < LOW_SUBSTANCE:
                signal = "BUY_DIP"      # Overreaction, contrarian
                verdict = "FADE"
            elif substance_score > HIGH_SUBSTANCE:
                signal = "HARD_EXIT"    # Real trouble, get out
                verdict = "FOLLOW"
            else:
                signal = "NEUTRAL"
                verdict = "IGNORE"

        return {
            "signal": signal,
            "verdict": verdict,
            "substance_score": substance_score,
            "reasoning": f"Mock: {'High' if substance_score > 6 else 'Low'} substance",
            "should_trade": signal != "NEUTRAL"
        }

    def get_llm_signal(self, price_change_pct: float, news_text: str) -> Optional[Dict]:
        """
        Get LLM assessment of current price move + news.

        Returns: LLM signal dict or None if not applicable
        """
        # Skip if LLM disabled
        if not self.llm_enabled:
            return None

        # Skip if price change below threshold (save API costs)
        if abs(price_change_pct) < self.llm_volatility_threshold:
            return None

        # Mock mode (for backtesting without news data)
        if self.mock_llm_mode or self.llm_checker is None:
            self.llm_calls_count += 1
            return self.mock_llm_decision(price_change_pct)

        # Real LLM call
        try:
            self.llm_calls_count += 1

            result = self.llm_checker.check_signal(
                ticker=getattr(self.data, 'ticker', 'UNKNOWN'),
                price_change_pct=price_change_pct,
                news_text=news_text,
                verbose=False  # Suppress logs during backtest
            )

            return result

        except Exception as e:
            print(f"[HYBRID] LLM call failed: {e}")
            return None

    def apply_llm_filter(self, adaptive_signal: str, llm_signal: Dict) -> str:
        """
        Apply LLM veto/override logic to Adaptive Strategy signal.

        Decision Matrix:

        Adaptive Signal | LLM Signal      | Final Action  | Reasoning
        ----------------|-----------------|---------------|------------------
        BUY             | SHORT_SCALP     | HOLD (veto)   | Avoid FOMO trap
        BUY             | HARD_EXIT       | HOLD (veto)   | Real trouble, don't buy
        SELL            | BUY_DIP         | BUY (override)| Overreaction, contrarian
        SELL/HOLD       | BUY_TREND       | BUY (override)| Strong fundamentals
        ANY             | NEUTRAL/IGNORE  | Keep original | LLM inconclusive

        Args:
            adaptive_signal: One of 'BUY', 'SELL', 'HOLD', 'CLOSE'
            llm_signal: LLM signal dict

        Returns:
            Final signal after LLM filter
        """
        if not llm_signal or not llm_signal.get('should_trade', False):
            # LLM says IGNORE - keep adaptive signal
            return adaptive_signal

        llm_action = llm_signal['signal']

        # === VETO LOGIC ===
        if self.llm_veto_enabled:
            # Veto BUY if LLM says SHORT_SCALP (avoid buying hype)
            if adaptive_signal == 'BUY' and llm_action == 'SHORT_SCALP':
                self.llm_vetoes_count += 1
                self.llm_decisions.append({
                    'bar': len(self.data),
                    'type': 'VETO',
                    'adaptive': 'BUY',
                    'llm': 'SHORT_SCALP',
                    'final': 'HOLD',
                    'reasoning': 'Avoided FOMO - hype detected'
                })
                return 'HOLD'

            # Veto BUY if LLM says HARD_EXIT (real trouble)
            if adaptive_signal == 'BUY' and llm_action == 'HARD_EXIT':
                self.llm_vetoes_count += 1
                self.llm_decisions.append({
                    'bar': len(self.data),
                    'type': 'VETO',
                    'adaptive': 'BUY',
                    'llm': 'HARD_EXIT',
                    'final': 'HOLD',
                    'reasoning': 'Avoided buying trouble'
                })
                return 'HOLD'

        # === OVERRIDE LOGIC ===
        if self.llm_override_enabled:
            # Override SELL/HOLD with BUY if LLM says BUY_DIP (contrarian)
            if adaptive_signal in ['SELL', 'HOLD'] and llm_action == 'BUY_DIP':
                self.llm_overrides_count += 1
                self.llm_decisions.append({
                    'bar': len(self.data),
                    'type': 'OVERRIDE',
                    'adaptive': adaptive_signal,
                    'llm': 'BUY_DIP',
                    'final': 'BUY',
                    'reasoning': 'Contrarian dip buy on overreaction'
                })
                return 'BUY'

            # Override HOLD with BUY if LLM says BUY_TREND (strong news)
            if adaptive_signal == 'HOLD' and llm_action == 'BUY_TREND':
                self.llm_overrides_count += 1
                self.llm_decisions.append({
                    'bar': len(self.data),
                    'type': 'OVERRIDE',
                    'adaptive': 'HOLD',
                    'llm': 'BUY_TREND',
                    'final': 'BUY',
                    'reasoning': 'Strong fundamental news detected'
                })
                return 'BUY'

            # Force exit if LLM says HARD_EXIT (regardless of adaptive)
            if llm_action == 'HARD_EXIT' and self.position:
                self.llm_overrides_count += 1
                self.llm_decisions.append({
                    'bar': len(self.data),
                    'type': 'OVERRIDE',
                    'adaptive': adaptive_signal,
                    'llm': 'HARD_EXIT',
                    'final': 'CLOSE',
                    'reasoning': 'Emergency exit - serious trouble'
                })
                return 'CLOSE'

        # No veto or override - keep original
        return adaptive_signal

    def next(self):
        """
        Main strategy logic with LLM filter.

        Flow:
        1. Calculate price change from previous bar
        2. Get news (if available)
        3. Query LLM (if volatility threshold exceeded)
        4. Get Adaptive Strategy baseline signal
        5. Apply LLM veto/override filter
        6. Execute final signal
        """
        # Step 1: Detect regime and get baseline signal from Adaptive Strategy
        regime = self.get_regime()
        self.current_regime = regime

        # Store current position state before strategy logic
        had_position_before = self.position is not None

        # Determine what Adaptive Strategy WOULD do (without executing yet)
        # We need to simulate the logic without executing trades
        adaptive_signal = self._get_adaptive_signal()

        # Step 2: Check for LLM filter conditions
        price_change_pct = self.get_price_change_pct()

        # Step 3: Get LLM assessment (if applicable)
        llm_signal = None
        if abs(price_change_pct) > self.llm_volatility_threshold:
            news_text = self.get_news_for_current_bar()
            llm_signal = self.get_llm_signal(price_change_pct, news_text)

        # Step 4: Apply LLM filter to get final signal
        final_signal = self.apply_llm_filter(adaptive_signal, llm_signal) if llm_signal else adaptive_signal

        # Step 5: Execute final signal
        self._execute_signal(final_signal, regime)

    def _get_adaptive_signal(self) -> str:
        """
        Determine what signal Adaptive Strategy would generate.
        Returns: 'BUY', 'SELL', 'HOLD', 'CLOSE'

        This simulates Adaptive Strategy logic without executing trades.
        """
        regime = self.get_regime()

        # Get current sentiment
        if hasattr(self.data, 'AI_Stock_Sentiment'):
            current_sentiment = self.data.AI_Stock_Sentiment[-1]
        else:
            current_sentiment = 0.0

        # Check thresholds based on regime
        if regime == 'BULLISH':
            # Get dynamic thresholds if enabled
            if self.use_dynamic_thresholds:
                thresholds = self.get_dynamic_thresholds_for_current_bar()
                entry_threshold = thresholds.get('aggressive_entry', self.aggr_entry_thresh)
                exit_threshold = thresholds.get('aggressive_exit', self.aggr_exit_thresh)
            else:
                entry_threshold = self.aggr_entry_thresh
                exit_threshold = self.aggr_exit_thresh

            if current_sentiment > entry_threshold and not self.position:
                return 'BUY'
            elif current_sentiment < exit_threshold and self.position and self.position.is_long:
                return 'CLOSE'
            else:
                return 'HOLD'

        elif regime == 'BEARISH':
            if self.use_dynamic_thresholds:
                thresholds = self.get_dynamic_thresholds_for_current_bar()
                short_threshold = thresholds.get('defensive_short', self.def_short_thresh)
                cover_threshold = thresholds.get('defensive_cover', self.def_cover_thresh)
            else:
                short_threshold = self.def_short_thresh
                cover_threshold = self.def_cover_thresh

            if current_sentiment < short_threshold and not self.position:
                return 'SELL'  # Short
            elif current_sentiment > cover_threshold and self.position and self.position.is_short:
                return 'CLOSE'
            else:
                return 'HOLD'

        else:  # SIDEWAYS
            current_price = self.data.Close[-1]
            current_support = self.support[-1]
            current_resistance = self.resistance[-1]

            if current_price <= current_support * (1 + self.mr_support_thresh):
                if not self.position or self.position.is_short:
                    return 'BUY'
            elif current_price >= current_resistance * (1 - self.mr_resist_thresh):
                if not self.position or self.position.is_long:
                    return 'SELL'

            return 'HOLD'

    def _execute_signal(self, signal: str, regime: str):
        """
        Execute the final trading signal.

        Args:
            signal: One of 'BUY', 'SELL', 'HOLD', 'CLOSE'
            regime: Current market regime
        """
        if signal == 'HOLD':
            return  # Do nothing

        elif signal == 'CLOSE':
            if self.position:
                self.position.close()

        elif signal == 'BUY':
            # Use same logic as Adaptive Strategy
            if regime == 'BULLISH':
                self.execute_aggressive_mode()
            elif regime == 'SIDEWAYS':
                self.execute_mean_reversion_mode()
            else:
                # Contrarian buy in bearish regime (LLM override)
                if not self.position:
                    current_price = self.data.Close[-1]
                    sl_price = current_price * (1 - self.stop_loss_pct)
                    self.buy(size=0.5, sl=sl_price)

        elif signal == 'SELL':
            if regime == 'BEARISH':
                self.execute_defensive_mode()
            elif regime == 'SIDEWAYS':
                self.execute_mean_reversion_mode()
            else:
                # Contrarian short in bullish regime (LLM override)
                if self.position and self.position.is_long:
                    self.position.close()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_hybrid_strategy_info():
    """Print strategy information."""
    print("\n" + "=" * 70)
    print("HYBRID LLM STRATEGY - EXP-2025-009")
    print("=" * 70)
    print("\nCombines:")
    print("  1. Adaptive Strategy (regime-based baseline)")
    print("  2. LLM Sanity Checker (veto power on volatility)")
    print("\nKey Features:")
    print("  - LLM only activates on >3% price moves (cost-efficient)")
    print("  - Veto power: Prevents FOMO buying on hype")
    print("  - Override power: Enables contrarian dip buying")
    print("  - Mock mode: Can backtest without real news data")
    print("\nExpected Improvement:")
    print("  - Drawdown reduction: 20-30%")
    print("  - Sharpe ratio improvement: 10-20%")
    print("  - Win rate improvement: 5-10%")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    print_hybrid_strategy_info()
