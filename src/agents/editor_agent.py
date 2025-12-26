"""
Editor Agent - Refines and polishes content
"""

import json
from typing import Dict, Any
from src.agents.base_agent import BaseAgent


class EditorAgent(BaseAgent):
    """Agent that reviews, edits, and polishes content"""
    
    def __init__(self):
        """Initialize Editor Agent"""
        super().__init__(agent_name='editor')
    
    def _execute_internal(self, **kwargs) -> Dict[str, Any]:
        """
        Edit and refine content
        
        Args:
            content: Content to edit (dict with title, body, etc.)
            editing_focus: Areas to focus on (default: all)
            tone: Desired tone
            
        Returns:
            Edited content with changes tracked
        """
        content = kwargs.get('content')
        editing_focus = kwargs.get('editing_focus', 'grammar, style, clarity, structure')
        tone = kwargs.get('tone', 'professional and conversational')
        
        if not content:
            raise ValueError("Content is required for editing")
        
        # Extract content text
        title = content.get('title', '')
        body = content.get('body', '')
        
        if not body:
            raise ValueError("Content body is required for editing")
        
        # Build prompt from template
        prompt = self.user_prompt_template.format(
            title=title,
            body=body,
            editing_focus=editing_focus,
            tone=tone
        )
        
        # Call AI model
        self.logger.info(
            "Starting content editing",
            agent=self.agent_name,
            title=title,
            original_length=len(body)
        )
        
        response = self._call_model(prompt)
        
        # Calculate cost
        cost = self._calculate_cost(prompt, response)
        self.logger.cost_tracking(
            project_id=kwargs.get('project_id', 'unknown'),
            operation='editing',
            cost=cost,
            model=self.model_name
        )
        
        # Parse JSON response
        try:
            edited_data = self._parse_editor_response(response)
        except Exception as e:
            self.logger.warning(
                f"Failed to parse JSON response, using raw text: {e}",
                agent=self.agent_name
            )
            edited_data = {
                'edited_title': title,
                'edited_body': response,
                'changes_made': ['Unable to parse structured changes'],
                'improvements': []
            }
        
        # Add metadata
        edited_data['cost'] = cost
        edited_data['model_used'] = self.model_name
        edited_data['original_title'] = title
        edited_data['original_body'] = body
        edited_data['word_count_change'] = self._count_words(
            edited_data.get('edited_body', '')
        ) - self._count_words(body)
        
        # Calculate quality scores
        edited_data['quality_metrics'] = self._calculate_quality_metrics(
            edited_data.get('edited_body', '')
        )
        
        return edited_data
    
    def _parse_editor_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON editor response
        
        Args:
            response: Model response
            
        Returns:
            Parsed editor data
        """
        # Try to find JSON in response
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response[start_idx:end_idx]
            return json.loads(json_str)
        
        # If no JSON found, try parsing entire response
        return json.loads(response)
    
    def _count_words(self, text: str) -> int:
        """
        Count words in text
        
        Args:
            text: Text to count
            
        Returns:
            Word count
        """
        return len(text.split())
    
    def _calculate_quality_metrics(self, text: str) -> Dict[str, Any]:
        """
        Calculate basic quality metrics for edited text
        
        Args:
            text: Edited text
            
        Returns:
            Quality metrics
        """
        words = text.split()
        sentences = text.split('.')
        
        # Basic readability metrics
        avg_sentence_length = len(words) / max(len(sentences), 1)
        
        # Estimate reading time (average 200 words per minute)
        reading_time_minutes = len(words) / 200
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'average_sentence_length': round(avg_sentence_length, 1),
            'reading_time_minutes': round(reading_time_minutes, 1),
            'character_count': len(text)
        }
    
    def validate_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate content quality against thresholds
        
        Args:
            content_data: Edited content data
            
        Returns:
            Validation results
        """
        quality_metrics = content_data.get('quality_metrics', {})
        word_count = quality_metrics.get('word_count', 0)
        
        # Define quality thresholds
        validations = {
            'min_word_count': {
                'passed': word_count >= 800,
                'threshold': 800,
                'actual': word_count,
                'message': 'Content meets minimum word count'
            },
            'max_word_count': {
                'passed': word_count <= 2000,
                'threshold': 2000,
                'actual': word_count,
                'message': 'Content within maximum word count'
            },
            'sentence_length': {
                'passed': quality_metrics.get('average_sentence_length', 0) <= 25,
                'threshold': 25,
                'actual': quality_metrics.get('average_sentence_length', 0),
                'message': 'Sentences are concise'
            }
        }
        
        all_passed = all(v['passed'] for v in validations.values())
        
        return {
            'overall_passed': all_passed,
            'validations': validations,
            'quality_score': sum(1 for v in validations.values() if v['passed']) / len(validations)
        }
