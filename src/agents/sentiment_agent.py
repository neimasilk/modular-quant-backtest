from typing import Tuple, List
import pandas as pd
from .base_agent import BaseAgent

class SentimentAgent(BaseAgent):
    """
    Uses AI-generated sentiment from news/analysis.
    Wraps existing sentiment scores into the voting system.
    """
    
    def __init__(self):
        self.lookback = 5  # Check for consistency over 5 days
    
    def get_name(self) -> str:
        return "sentiment"
    
    def get_required_data(self) -> List[str]:
        return ['sentiment_series']
    
    def analyze(self, sentiment_series: pd.Series) -> Tuple[int, float]:
        if len(sentiment_series) < self.lookback:
            # Not enough data
            return (0, 0.3)
        
        current_sentiment = sentiment_series.iloc[-1]
        
        # Check sentiment consistency (std dev of recent sentiment)
        recent_sentiments = sentiment_series.iloc[-self.lookback:]
        consistency = recent_sentiments.std()
        
        # Convert sentiment to vote (-1 to 1 scale assumed)
        if current_sentiment > 0.3:
            vote = +1
        elif current_sentiment < -0.3:
            vote = -1
        else:
            vote = 0
        
        # Higher confidence if sentiment is consistent (low volatility)
        if pd.isna(consistency):
             confidence = 0.5
        elif consistency < 0.2:
            confidence = 0.7
        elif consistency < 0.4:
            confidence = 0.5
        else:
            confidence = 0.3 # Volatile sentiment, less trustworthy
        
        # Boost confidence for extreme sentiment signals
        if abs(current_sentiment) > 0.6:
            confidence = min(0.9, confidence + 0.2)
        
        return (vote, confidence)
