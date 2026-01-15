import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.vix_agent import VIXAgent
from src.agents.trend_agent import TrendAgent
from src.agents.volume_agent import VolumeAgent
from src.agents.momentum_agent import MomentumAgent
from src.agents.support_resistance_agent import SupportResistanceAgent

class TestAgents(unittest.TestCase):
    
    def test_vix_agent(self):
        agent = VIXAgent()
        # Test Extreme Greed (<15) -> Neutral/Cautious
        vote, conf = agent.analyze(14.0)
        self.assertEqual(vote, 0)
        
        # Test Low Fear (15-20) -> Bullish
        vote, conf = agent.analyze(18.0)
        self.assertEqual(vote, 1)

    def test_trend_agent(self):
        agent = TrendAgent()
        # Strong Uptrend
        prices = [100 + i for i in range(100)]
        closes = pd.Series(prices)
        vote, conf = agent.analyze(closes)
        self.assertEqual(vote, 1)

    def test_volume_agent(self):
        agent = VolumeAgent()
        # Setup data: Price up + High volume
        prices = [100 + i for i in range(21)]
        volumes = [1000] * 20 + [5000] # spike in last volume
        vote, conf = agent.analyze(pd.Series(prices), pd.Series(volumes))
        self.assertEqual(vote, 1)
        self.assertGreaterEqual(conf, 0.7)

    def test_momentum_agent(self):
        agent = MomentumAgent()
        # RSI high (>70) but momentum stalling (ROC < 10%)
        # Steady gain for 50 days, then very slow gain for last 5 days
        prices = [100 + i for i in range(50)] + [150.1, 150.2, 150.3, 150.4, 150.5]
        vote, conf = agent.analyze(pd.Series(prices))
        self.assertEqual(vote, -1) # Overbought reversal signal

    def test_sr_agent(self):
        agent = SupportResistanceAgent()
        # Setup: Range 100-110, then price at 112 (Breakout)
        highs = pd.Series([110] * 20 + [112])
        lows = pd.Series([100] * 20 + [111])
        closes = pd.Series([105] * 20 + [112])
        vote, conf = agent.analyze(highs, lows, closes)
        self.assertEqual(vote, 1) # Breakout signal


if __name__ == '__main__':
    unittest.main()
