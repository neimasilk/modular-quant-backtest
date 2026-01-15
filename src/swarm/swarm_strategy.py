from backtesting import Strategy
from typing import Dict
import pandas as pd
import numpy as np

# Import agents lazily inside init to avoid circular imports if any, 
# but standard imports are fine here.
from src.agents.vix_agent import VIXAgent
from src.agents.trend_agent import TrendAgent
from src.agents.volume_agent import VolumeAgent
from src.agents.momentum_agent import MomentumAgent
from src.agents.seasonal_agent import SeasonalAgent
from src.agents.support_resistance_agent import SupportResistanceAgent
from src.agents.sentiment_agent import SentimentAgent
from src.swarm.aggregator import SwarmAggregator

class SwarmStrategy(Strategy):
    """
    Multi-agent swarm trading strategy for backtesting.
    """
    
    # Strategy parameters
    buy_threshold = 0.25
    sell_threshold = -0.25
    position_size = 0.95
    
    # Risk management
    stop_loss_pct = 0.20
    trailing_stop_pct = 0.05
    
    def init(self):
        """Initialize agents and aggregator."""
        
        self.agents = {
            'vix': VIXAgent(),
            'trend': TrendAgent(),
            'volume': VolumeAgent(),
            'momentum': MomentumAgent(),
            'seasonal': SeasonalAgent(),
            'support_resistance': SupportResistanceAgent(),
            'sentiment': SentimentAgent(),
        }
        
        self.aggregator = SwarmAggregator()
        self.entry_price = None
        self.highest_since_entry = None
    
    def collect_votes(self) -> Dict:
        """Collect votes from all agents for the current step."""
        
        # In backtesting.py, self.data contains the data up to the current point
        # when accessed within next(). We can convert to pandas Series.
        
        # idx = len(self.data.Close) - 1
        
        # Function to safely get data up to current point as a Series
        def get_series(data_array):
            return pd.Series(data_array)
            
        closes = get_series(self.data.Close)
        highs = get_series(self.data.High)
        lows = get_series(self.data.Low)
        volumes = get_series(self.data.Volume)
        
        votes = {}
        
        # VIX Agent
        # self.data.VIX might be an array
        current_vix = self.data.VIX[-1] if hasattr(self.data, 'VIX') else 20.0
        votes['vix'] = self.agents['vix'].analyze(current_vix)
        
        # Trend Agent
        votes['trend'] = self.agents['trend'].analyze(closes)
        
        # Volume Agent
        votes['volume'] = self.agents['volume'].analyze(closes, volumes)
        
        # Momentum Agent
        votes['momentum'] = self.agents['momentum'].analyze(closes)
        
        # Seasonal Agent
        # Use the last index of the available data
        current_date = self.data.index[-1]
        votes['seasonal'] = self.agents['seasonal'].analyze(current_date)
        
        # S/R Agent
        votes['support_resistance'] = self.agents['support_resistance'].analyze(highs, lows, closes)
        
        # Sentiment Agent
        if hasattr(self.data, 'AI_Stock_Sentiment'):
            sentiment_series = pd.Series(self.data.AI_Stock_Sentiment)
            votes['sentiment'] = self.agents['sentiment'].analyze(sentiment_series)
        else:
            votes['sentiment'] = (0, 0.3)
        
        return votes

    def check_stop_loss(self) -> bool:
        """Check stop-loss conditions."""
        if not self.position:
            self.entry_price = None
            self.highest_since_entry = None
            return False
        
        current_price = self.data.Close[-1]
        
        if self.entry_price is None:
            self.entry_price = current_price
            self.highest_since_entry = current_price
            return False
        
        if self.position.is_long:
            self.highest_since_entry = max(self.highest_since_entry, current_price)
            stop_price = self.entry_price * (1 - self.stop_loss_pct)
            trail_price = self.highest_since_entry * (1 - self.trailing_stop_pct)
            
            if current_price <= stop_price or current_price <= trail_price:
                return True
        
        return False
    
    def next(self):
        """Main strategy logic executed on every candle."""
        
        # 1. Risk Management Check
        if self.check_stop_loss():
            if self.position:
                self.position.close()
            return
        
        # 2. Minimum Data Requirement (Max lookback of agents is 50 for SMA50)
        if len(self.data.Close) < 60:
            return
        
        # 3. Collect Votes
        votes = self.collect_votes()
        
        # 4. Aggregate
        decision, score, breakdown = self.aggregator.aggregate(votes)
        
        # 5. Execute
        if decision == "BUY" and not self.position:
            self.buy(size=self.position_size)
            self.entry_price = self.data.Close[-1]
            self.highest_since_entry = self.entry_price
            
        elif decision == "SELL" and self.position and self.position.is_long:
            self.position.close()