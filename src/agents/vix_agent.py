from typing import Tuple, List
from .base_agent import BaseAgent

class VIXAgent(BaseAgent):
    """
    Measures market fear/greed through VIX.
    
    VIX Interpretation:
    - < 15: Extreme greed (complacency) → Cautious (Neutral/Bearish bias)
    - 15-20: Low fear → Bullish
    - 20-25: Normal → Neutral
    - 25-35: Elevated fear → Cautious/Bearish
    - > 35: Extreme fear → Contrarian Bullish (blood in streets)
    """
    
    def get_name(self) -> str:
        return "vix"
    
    def get_required_data(self) -> List[str]:
        return ['vix']
    
    def analyze(self, vix: float) -> Tuple[int, float]:
        """
        Returns:
            vote: -1 (bearish), 0 (neutral), +1 (bullish)
            confidence: 0.0 to 1.0
        """
        # Handle potential Series/Input issues
        try:
            val = float(vix)
        except (ValueError, TypeError):
            return (0, 0.0)

        if val < 15:
            # Extreme complacency - market may be topping
            return (0, 0.6)  # Neutral with medium confidence
        elif val < 20:
            # Low fear - good for longs
            return (+1, 0.7)
        elif val < 25:
            # Normal - no strong signal
            return (0, 0.3)  # Low confidence
        elif val < 35:
            # Elevated fear - caution
            return (-1, 0.7)
        else:
            # Extreme fear - contrarian buy signal
            # "Be greedy when others are fearful"
            return (+1, 0.8)
