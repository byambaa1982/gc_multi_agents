"""
Research Agent - Gathers information on topics
"""

import json
from typing import Dict, Any
from .base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    """Agent that researches topics and gathers key information"""
    
    def __init__(self):
        """Initialize Research Agent"""
        super().__init__(agent_name='research')
    
    def _execute_internal(self, **kwargs) -> Dict[str, Any]:
        """
        Execute research on a topic
        
        Args:
            topic: Topic to research
            
        Returns:
            Research findings
        """
        topic = kwargs.get('topic')
        if not topic:
            raise ValueError("Topic is required for research")
        
        # Build prompt from template
        prompt = self.user_prompt_template.format(topic=topic)
        
        # Call AI model
        self.logger.info(
            "Starting research",
            agent=self.agent_name,
            topic=topic
        )
        
        response = self._call_model(prompt)
        
        # Calculate cost
        cost = self._calculate_cost(prompt, response)
        self.logger.cost_tracking(
            project_id=kwargs.get('project_id', 'unknown'),
            operation='research',
            cost=cost,
            model=self.model_name
        )
        
        # Parse JSON response
        try:
            research_data = self._parse_research_response(response)
        except Exception as e:
            self.logger.warning(
                f"Failed to parse JSON response, using raw text: {e}",
                agent=self.agent_name
            )
            research_data = {
                'overview': response[:500],
                'key_points': self._extract_key_points(response),
                'raw_research': response
            }
        
        research_data['cost'] = cost
        research_data['model_used'] = self.model_name
        
        return research_data
    
    def _parse_research_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON research response with robust error handling
        
        Args:
            response: Model response
            
        Returns:
            Parsed research data
        """
        # Remove markdown code blocks if present
        cleaned_response = response.strip()
        
        # Remove ```json and ``` markers
        if cleaned_response.startswith('```'):
            # Find the first newline after ```json or ```
            first_newline = cleaned_response.find('\n')
            if first_newline > 0:
                cleaned_response = cleaned_response[first_newline + 1:]
            
            # Remove trailing ```
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
        
        cleaned_response = cleaned_response.strip()
        
        # Try to find JSON in response
        start_idx = cleaned_response.find('{')
        end_idx = cleaned_response.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = cleaned_response[start_idx:end_idx]
            
            # Try parsing as-is first
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                # Try to fix common JSON issues
                self.logger.warning(f"Initial JSON parse failed ({str(e)}), attempting to fix...")
                
                import re
                fixed_json = json_str
                
                # Fix 1: Remove trailing commas before closing braces/brackets
                fixed_json = re.sub(r',(\s*[}\]])', r'\1', fixed_json)
                
                # Fix 2: Fix missing commas between array string elements
                fixed_json = re.sub(r'"\s*\n\s*"', '",\n"', fixed_json)
                
                # Fix 3: Escape unescaped quotes in string values (heuristic)
                # This is tricky and may not work perfectly
                
                # Fix 4: Remove any incomplete trailing content after last }
                last_brace = fixed_json.rfind('}')
                if last_brace > 0:
                    fixed_json = fixed_json[:last_brace + 1]
                
                try:
                    return json.loads(fixed_json)
                except json.JSONDecodeError as e2:
                    # Still failed - log and use fallback
                    self.logger.warning(f"JSON repair failed ({str(e2)}), using text extraction fallback")
                    # Don't raise - let it fall through to raw text handling
        
        # Ultimate fallback - raise to trigger raw text extraction in calling code
        raise json.JSONDecodeError("Could not parse JSON", cleaned_response, 0)
    
    def _extract_key_points(self, text: str) -> list:
        """
        Extract key points from unstructured text
        
        Args:
            text: Research text
            
        Returns:
            List of key points
        """
        # Simple extraction: look for numbered lists or bullet points
        lines = text.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            # Match numbered items (1., 2., etc.) or bullet points (-, *, •)
            if (line and 
                (line[0].isdigit() or 
                 line.startswith(('-', '*', '•', '▪')))):
                # Clean up the line
                cleaned = line.lstrip('0123456789.-*•▪ ').strip()
                if cleaned:
                    key_points.append(cleaned)
        
        return key_points[:7]  # Return top 7 points
