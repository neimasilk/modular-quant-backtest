from typing import Dict, Tuple

class SwarmAggregator:
    """
    Aggregates votes from all agents using weighted voting.
    """
    
    def __init__(self):
        # Base weights for each agent (tuned based on hypothesis)
        self.base_weights = {
            'vix': 1.2,        # Market regime is critical context
            'trend': 1.0,      # "The trend is your friend"
            'volume': 0.8,     # Volume confirms price
            'momentum': 1.0,   # Good for entry timing
            'seasonal': 0.6,   # Weak effect, tie-breaker
            'support_resistance': 1.0, # Good for risk management
            'sentiment': 0.8,  # Can be noisy/lagging
        }
        
        # Performance tracking for adaptive weights (future feature)
        self.agent_accuracy = {name: 0.5 for name in self.base_weights}
        
    def aggregate(self, agent_outputs: Dict[str, Tuple[int, float]]) -> Tuple[str, float, Dict]:
        """
        Aggregate agent votes into final decision.
        
        Args:
            agent_outputs: Dict {agent_name: (vote, confidence)}
            
        Returns:
            decision: "BUY", "SELL", or "HOLD"
            score: Weighted score (-1.0 to +1.0)
            breakdown: Detailed contribution of each agent
        """
        weighted_sum = 0.0
        total_weight = 0.0
        breakdown = {}
        
        for agent_name, (vote, confidence) in agent_outputs.items():
            base_weight = self.base_weights.get(agent_name, 1.0)
            
            # Simple adaptive factor (placeholder for future learning)
            accuracy_factor = 1.0 
            
            # Final weight calculation
            final_weight = base_weight * confidence * accuracy_factor
            
            contribution = vote * final_weight
            weighted_sum += contribution
            total_weight += final_weight
            
            breakdown[agent_name] = {
                'vote': vote,
                'confidence': confidence,
                'weight': final_weight,
                'contribution': contribution
            }
        
        # Calculate final normalized score
        if total_weight > 0:
            final_score = weighted_sum / total_weight
        else:
            final_score = 0.0
        
        # Decision thresholds
        if final_score > 0.25:
            decision = "BUY"
        elif final_score < -0.25:
            decision = "SELL"
        else:
            decision = "HOLD"
        
        return decision, final_score, breakdown
