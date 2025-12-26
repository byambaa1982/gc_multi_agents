"""
Base agent class for all AI agents
"""

import os
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import yaml
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from tenacity import retry, stop_after_attempt, wait_exponential

from src.infrastructure.cost_tracker import CostTracker
from src.monitoring.logger import StructuredLogger


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(
        self, 
        agent_name: str,
        config_path: str = 'config/agent_config.yaml',
        prompts_path: str = 'config/prompts.yaml'
    ):
        """
        Initialize base agent
        
        Args:
            agent_name: Name of the agent
            config_path: Path to agent configuration
            prompts_path: Path to prompts configuration
        """
        self.agent_name = agent_name
        self.config_path = config_path
        self.prompts_path = prompts_path
        
        # Initialize logger and cost tracker
        self.logger = StructuredLogger(name=f"agent.{agent_name}")
        self.cost_tracker = CostTracker(config_path=config_path)
        
        # Load configuration
        self._load_config()
        self._load_prompts()
        
        # Initialize Vertex AI
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
        
        if not project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
        
        vertexai.init(project=project_id, location=location)
        
        # Initialize model
        self.model = GenerativeModel(self.model_name)
        self.generation_config = GenerationConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens
        )
    
    def _load_config(self) -> None:
        """Load agent configuration from YAML"""
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        agent_config = config['agents'].get(self.agent_name, {})
        
        self.model_name = agent_config.get('model', 'gemini-1.5-flash')
        self.temperature = agent_config.get('temperature', 0.7)
        self.max_output_tokens = agent_config.get('max_output_tokens', 2048)
        self.description = agent_config.get('description', '')
    
    def _load_prompts(self) -> None:
        """Load prompts from YAML"""
        with open(self.prompts_path, 'r') as f:
            prompts = yaml.safe_load(f)
        
        agent_prompts = prompts.get(self.agent_name, {})
        
        self.system_prompt = agent_prompts.get('system_prompt', '')
        self.user_prompt_template = agent_prompts.get('user_prompt_template', '')
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _call_model(self, prompt: str) -> str:
        """
        Call the AI model with retry logic
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Model response text
        """
        full_prompt = f"{self.system_prompt}\n\n{prompt}"
        
        response = self.model.generate_content(
            full_prompt,
            generation_config=self.generation_config
        )
        
        return response.text
    
    def _calculate_cost(self, input_text: str, output_text: str) -> float:
        """
        Calculate cost for model usage
        
        Args:
            input_text: Input prompt
            output_text: Model output
            
        Returns:
            Cost in USD
        """
        input_chars = len(input_text)
        output_chars = len(output_text)
        
        cost = self.cost_tracker.calculate_cost(
            self.model_name,
            input_chars,
            output_chars
        )
        
        return cost
    
    def execute(
        self, 
        project_id: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute the agent
        
        Args:
            project_id: Project ID for tracking
            **kwargs: Agent-specific parameters
            
        Returns:
            Agent execution result
        """
        start_time = time.time()
        
        self.logger.agent_start(
            agent_name=self.agent_name,
            project_id=project_id,
            **kwargs
        )
        
        try:
            # Execute agent-specific logic
            result = self._execute_internal(**kwargs)
            
            duration = time.time() - start_time
            
            self.logger.agent_complete(
                agent_name=self.agent_name,
                project_id=project_id,
                duration_seconds=duration
            )
            
            return result
            
        except Exception as e:
            self.logger.agent_error(
                agent_name=self.agent_name,
                project_id=project_id,
                error=e
            )
            raise
    
    @abstractmethod
    def _execute_internal(self, **kwargs) -> Dict[str, Any]:
        """
        Internal execution logic (to be implemented by subclasses)
        
        Args:
            **kwargs: Agent-specific parameters
            
        Returns:
            Execution result
        """
        pass
