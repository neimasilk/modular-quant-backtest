import unittest
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.swarm.aggregator import SwarmAggregator
from src.agents.vix_agent import VIXAgent
# Import other agents as mocks or real

class TestSwarmSystem(unittest.TestCase):
    
    def setUp(self):
        self.aggregator = SwarmAggregator()
        
    def test_aggregator_logic(self):
        # Create a mock scenario
        # VIX: Bullish (+1, 0.7)
        # Trend: Bullish (+1, 0.6)
        # Volume: Neutral (0, 0.3)
        # Momentum: Bearish (-1, 0.5)
        # Seasonal: Bullish (+1, 0.4)
        
        agent_outputs = {
            'vix': (1, 0.7),
            'trend': (1, 0.6),
            'volume': (0, 0.3),
            'momentum': (-1, 0.5),
            'seasonal': (1, 0.4)
        }
        
        # Expected calculation:
        # VIX: 1 * 0.7 * 1.2 = 0.84
        # Trend: 1 * 0.6 * 1.0 = 0.60
        # Volume: 0 * 0.3 * 0.8 = 0.00
        # Momentum: -1 * 0.5 * 1.0 = -0.50
        # Seasonal: 1 * 0.4 * 0.6 = 0.24
        
        # Sum = 0.84 + 0.60 + 0 - 0.50 + 0.24 = 1.18
        # Total Weight = (0.7*1.2) + (0.6*1.0) + (0.3*0.8) + (0.5*1.0) + (0.4*0.6)
        #              = 0.84 + 0.6 + 0.24 + 0.5 + 0.24 = 2.42
        
        # Final Score = 1.18 / 2.42 = 0.487...
        
        decision, score, breakdown = self.aggregator.aggregate(agent_outputs)
        
        self.assertEqual(decision, "BUY") # > 0.25
        self.assertAlmostEqual(score, 1.18/2.42, places=2)
        
    def test_strong_sell_scenario(self):
         agent_outputs = {
            'vix': (-1, 0.8),
            'trend': (-1, 0.9),
            'volume': (-1, 0.8),
        }
         decision, score, breakdown = self.aggregator.aggregate(agent_outputs)
         self.assertEqual(decision, "SELL")
         self.assertLess(score, -0.5)

if __name__ == '__main__':
    unittest.main()
