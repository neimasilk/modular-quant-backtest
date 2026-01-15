from typing import Tuple, List, Any
import pandas as pd
from .base_agent import BaseAgent

class SeasonalAgent(BaseAgent):
    """
    Exploits known calendar effects:
    
    Monthly patterns (S&P 500 historical approximation):
    - January: +1.2% avg (January Effect)
    - September: -0.5% avg (Worst month)
    - October: +0.8% avg (but volatile)
    - November-December: +1.5% avg (Santa Rally)
    """
    
    # Historical monthly returns bias (simplified for demo)
    MONTHLY_BIAS = {
        1: 0.7,   # January: bullish
        2: 0.3,   # February: slightly bullish
        3: 0.4,   # March: slightly bullish
        4: 0.6,   # April: bullish
        5: 0.2,   # May: "Sell in May"
        6: 0.1,   # June: neutral
        7: 0.4,   # July: bullish
        8: 0.0,   # August: neutral
        9: -0.5,  # September: bearish
        10: 0.3,  # October: slightly bullish
        11: 0.6,  # November: bullish
        12: 0.7,  # December: bullish (Santa Rally)
    }
    
    def get_name(self) -> str:
        return "seasonal"
    
    def get_required_data(self) -> List[str]:
        return ['date']
    
    def analyze(self, date: Any) -> Tuple[int, float]:
        # Handle different date formats
        if hasattr(date, 'month'):
            month = date.month
            day_of_week = date.weekday() if hasattr(date, 'weekday') else 2
        elif isinstance(date, pd.Timestamp):
             month = date.month
             day_of_week = date.dayofweek
        else:
            # Fallback for unknown date format
            return (0, 0.3)
        
        monthly_bias = self.MONTHLY_BIAS.get(month, 0)
        
        # Adjust for day of week (Monday typically weaker, Friday stronger)
        if day_of_week == 0:  # Monday
            weekly_adjustment = -0.1
        elif day_of_week == 4:  # Friday
            weekly_adjustment = 0.1
        else:
            weekly_adjustment = 0
        
        combined_bias = monthly_bias + weekly_adjustment
        
        # Convert to vote
        if combined_bias > 0.3:
            return (+1, min(0.6, 0.3 + abs(combined_bias)))
        elif combined_bias < -0.3:
            return (-1, min(0.6, 0.3 + abs(combined_bias)))
        else:
            return (0, 0.3)
