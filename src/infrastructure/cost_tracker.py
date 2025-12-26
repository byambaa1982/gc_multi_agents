"""
Cost tracking for AI API usage
"""

import os
from typing import Dict, Optional
import yaml


class CostTracker:
    """Tracks costs for AI model usage"""
    
    def __init__(self, config_path: str = 'config/agent_config.yaml'):
        """
        Initialize cost tracker
        
        Args:
            config_path: Path to configuration file with pricing
        """
        self.config_path = config_path
        self.costs = {}
        self._load_pricing()
    
    def _load_pricing(self) -> None:
        """Load pricing configuration from YAML"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.model_costs = config.get('models', {})
        else:
            # Default pricing if config not found
            self.model_costs = {
                'gemini-1.5-flash': {'cost_per_1k_chars': 0.00002},
                'gemini-1.5-pro': {'cost_per_1k_chars': 0.00005}
            }
    
    def calculate_cost(
        self, 
        model_name: str, 
        input_chars: int, 
        output_chars: int
    ) -> float:
        """
        Calculate cost for model usage
        
        Args:
            model_name: Name of the model used
            input_chars: Number of input characters
            output_chars: Number of output characters
            
        Returns:
            Cost in USD
        """
        model_pricing = self.model_costs.get(model_name, {})
        cost_per_1k = model_pricing.get('cost_per_1k_chars', 0.00005)
        
        total_chars = input_chars + output_chars
        cost = (total_chars / 1000) * cost_per_1k
        
        return round(cost, 6)
    
    def track_operation(
        self, 
        operation_name: str, 
        model_name: str, 
        input_chars: int, 
        output_chars: int
    ) -> float:
        """
        Track cost for an operation
        
        Args:
            operation_name: Name of the operation (research, generation, etc.)
            model_name: Model used
            input_chars: Input character count
            output_chars: Output character count
            
        Returns:
            Cost for this operation
        """
        cost = self.calculate_cost(model_name, input_chars, output_chars)
        
        if operation_name not in self.costs:
            self.costs[operation_name] = 0.0
        
        self.costs[operation_name] += cost
        
        return cost
    
    def get_total_cost(self) -> float:
        """
        Get total tracked costs
        
        Returns:
            Total cost in USD
        """
        return sum(self.costs.values())
    
    def get_operation_cost(self, operation_name: str) -> float:
        """
        Get cost for specific operation
        
        Args:
            operation_name: Operation name
            
        Returns:
            Cost for operation
        """
        return self.costs.get(operation_name, 0.0)
    
    def get_cost_breakdown(self) -> Dict[str, float]:
        """
        Get breakdown of all costs
        
        Returns:
            Dictionary of operation names and costs
        """
        breakdown = dict(self.costs)
        breakdown['total'] = self.get_total_cost()
        return breakdown
    
    def reset(self) -> None:
        """Reset all tracked costs"""
        self.costs = {}
