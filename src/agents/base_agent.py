from abc import ABC, abstractmethod
from typing import Tuple, List, Any
import pandas as pd

class BaseAgent(ABC):
    """
    Abstract base class for all specialist agents.
    
    Each agent must implement:
    1. analyze() - Return vote and confidence
    2. get_name() - Return agent identifier
    3. get_required_data() - Specify data requirements
    """
    
    @abstractmethod
    def analyze(self, *args, **kwargs) -> Tuple[int, float]:
        """
        Analyze data and return trading signal.
        
        Returns:
            vote: -1 (bearish), 0 (neutral), +1 (bullish)
            confidence: 0.0 to 1.0
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return agent identifier."""
        pass
    
    @abstractmethod
    def get_required_data(self) -> List[str]:
        """Return list of required data fields."""
        pass
