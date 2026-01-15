from typing import Tuple, List
import pandas as pd
from .base_agent import BaseAgent

class SupportResistanceAgent(BaseAgent):
    """
    Identifies support/resistance levels and price position.
    
    Logic:
    - Price near support + bouncing = Bullish
    - Price near resistance + rejecting = Bearish
    - Breakout above resistance = Bullish
    - Breakdown below support = Bearish
    """
    
    def __init__(self):
        self.lookback = 20
        self.threshold = 0.02  # 2% buffer zone
    
    def get_name(self) -> str:
        return "support_resistance"
    
    def get_required_data(self) -> List[str]:
        return ['highs', 'lows', 'closes']
    
    def analyze(self, highs: pd.Series, lows: pd.Series, closes: pd.Series) -> Tuple[int, float]:
        if len(closes) < self.lookback + 1:
            return (0, 0.0)
        
        # Calculate support/resistance from recent history
        support = lows.iloc[-self.lookback-1:-1].min()
        resistance = highs.iloc[-self.lookback-1:-1].max()
        price = closes.iloc[-1]
        prev_price = closes.iloc[-2]
        
        # Distance to levels
        dist_to_support = (price - support) / support if support > 0 else 1
        dist_to_resistance = (resistance - price) / resistance if resistance > 0 else 1
        
        if price > resistance:
            # Breakout
            return (+1, 0.8)
        elif price < support:
            # Breakdown
            return (-1, 0.8)
        elif dist_to_support < self.threshold:
            # Near support
            if price > prev_price:  # Bouncing up
                return (+1, 0.7)
            else:
                return (0, 0.4) # Still falling towards support
        elif dist_to_resistance < self.threshold:
            # Near resistance
            if price < prev_price:  # Rejecting down
                return (-1, 0.7)
            else:
                return (0, 0.4) # Still pushing towards resistance
        else:
            # In the middle of the range
            return (0, 0.2)
