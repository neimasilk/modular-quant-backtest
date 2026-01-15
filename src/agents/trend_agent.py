from typing import Tuple, List
import pandas as pd
from .base_agent import BaseAgent

class TrendAgent(BaseAgent):
    """
    Measures trend using multiple moving averages.
    
    Signals:
    - Price > SMA20 > SMA50: Strong uptrend
    - Price > SMA20, SMA20 < SMA50: Potential reversal up
    - Price < SMA20 < SMA50: Strong downtrend
    - Price < SMA20, SMA20 > SMA50: Potential reversal down
    """
    
    def __init__(self):
        self.sma_short = 20
        self.sma_long = 50
    
    def get_name(self) -> str:
        return "trend"
    
    def get_required_data(self) -> List[str]:
        return ['closes']
    
    def analyze(self, closes: pd.Series) -> Tuple[int, float]:
        if len(closes) < self.sma_long:
            return (0, 0.0)  # Not enough data
            
        # Calculate indicators on the fly (or assume pre-calc if optimized later)
        # For agent simplicity, we calc here.
        sma20 = closes.rolling(self.sma_short).mean().iloc[-1]
        sma50 = closes.rolling(self.sma_long).mean().iloc[-1]
        price = closes.iloc[-1]
        
        # Avoid division by zero
        if sma50 == 0:
            return (0, 0.0)

        # Calculate trend strength
        trend_strength = (price - sma50) / sma50  # % above/below SMA50
        
        if price > sma20 > sma50:
            # Strong uptrend
            confidence = min(0.9, 0.5 + abs(trend_strength))
            return (+1, confidence)
        elif price > sma20 and sma20 < sma50:
            # Potential reversal up
            return (+1, 0.5)
        elif price < sma20 < sma50:
            # Strong downtrend
            confidence = min(0.9, 0.5 + abs(trend_strength))
            return (-1, confidence)
        elif price < sma20 and sma20 > sma50:
            # Potential reversal down
            return (-1, 0.5)
        else:
            return (0, 0.3)
