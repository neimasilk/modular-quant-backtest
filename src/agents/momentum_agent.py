from typing import Tuple, List
import pandas as pd
from .base_agent import BaseAgent

class MomentumAgent(BaseAgent):
    """
    Measures momentum using RSI and rate of change.
    
    RSI Interpretation:
    - > 70: Overbought (potential reversal down)
    - 50-70: Bullish momentum
    - 30-50: Bearish momentum
    - < 30: Oversold (potential reversal up)
    """
    
    def __init__(self):
        self.rsi_period = 14
        self.roc_period = 10
    
    def get_name(self) -> str:
        return "momentum"
    
    def get_required_data(self) -> List[str]:
        return ['closes']
    
    def calculate_rsi(self, closes: pd.Series) -> float:
        delta = closes.diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.rsi_period).mean()
        
        # Avoid division by zero
        rs = gain / loss.replace(0, 1e-9)
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def analyze(self, closes: pd.Series) -> Tuple[int, float]:
        if len(closes) < self.rsi_period + 1:
            return (0, 0.0)
        
        rsi = self.calculate_rsi(closes)
        
        # Calculate ROC
        if len(closes) >= self.roc_period + 1:
            roc = (closes.iloc[-1] - closes.iloc[-self.roc_period - 1]) / closes.iloc[-self.roc_period - 1]
        else:
            roc = 0
        
        if rsi > 70:
            # Overbought - potential reversal down unless momentum is extremely strong
            if roc > 0.10: # Momentum very strong, don't fight it
                return (0, 0.4)
            else:
                return (-1, 0.7)
        elif rsi < 30:
            # Oversold - potential bounce
            if roc < -0.10: # Strong downward momentum
                return (0, 0.4)
            else:
                return (+1, 0.7)
        elif rsi > 50:
            # Bullish momentum
            return (+1, 0.5)
        else:
            # Bearish momentum
            return (-1, 0.5)
