from typing import Tuple, List
import pandas as pd
import numpy as np
from .base_agent import BaseAgent

class VolumeAgent(BaseAgent):
    """
    Measures accumulation/distribution through volume analysis.
    
    Concepts:
    - Price up + High volume = Strong buying (accumulation)
    - Price down + High volume = Strong selling (distribution)
    - Price up + Low volume = Weak rally (suspect)
    - Price down + Low volume = Weak decline (less concerning)
    """
    
    def __init__(self):
        self.lookback = 20
    
    def get_name(self) -> str:
        return "volume"
    
    def get_required_data(self) -> List[str]:
        return ['closes', 'volumes']
    
    def analyze(self, closes: pd.Series, volumes: pd.Series) -> Tuple[int, float]:
        if len(closes) < self.lookback:
            return (0, 0.0)
        
        # Calculate OBV (On-Balance Volume)
        price_diff = closes.diff()
        obv = (np.sign(price_diff) * volumes).fillna(0).cumsum()
        
        # OBV trend (is OBV making higher highs?)
        obv_sma = obv.rolling(self.lookback).mean()
        obv_trend_up = obv.iloc[-1] > obv_sma.iloc[-1]
        
        # Today's price action
        price_change = closes.pct_change().iloc[-1]
        
        # Volume relative to average
        vol_avg = volumes.rolling(self.lookback).mean().iloc[-1]
        vol_ratio = volumes.iloc[-1] / vol_avg if vol_avg > 0 else 1
        
        # High volume threshold = > 1.5x average
        high_volume = vol_ratio > 1.5
        
        if price_change > 0 and high_volume and obv_trend_up:
            # Strong accumulation
            return (+1, 0.8)
        elif price_change < 0 and high_volume and not obv_trend_up:
            # Strong distribution
            return (-1, 0.8)
        elif abs(price_change) > 0.02 and not high_volume:
            # Price move without volume support - signal 0 with low confidence
            return (0, 0.4)
        else:
            # Neutral/Normal
            return (0, 0.3)
