"""
Content Generator Agent - Creates blog posts from research
"""

import json
from typing import Dict, Any
from .base_agent import BaseAgent


class ContentGeneratorAgent(BaseAgent):
    """Agent that generates blog post content from research"""
    
    def __init__(self):
        """Initialize Content Generator Agent"""
        super().__init__(agent_name='content_generator')
    
    def _execute_internal(self, **kwargs) -> Dict[str, Any]:
        """
        Generate content from research
        
        Args:
            topic: Content topic
            research_findings: Research data from ResearchAgent
            tone: Content tone (default: professional)
            target_word_count: Target word count (default: 1200)
            
        Returns:
            Generated content
        """
        topic = kwargs.get('topic')
        research_findings = kwargs.get('research_findings')
        tone = kwargs.get('tone', 'professional and conversational')
        target_word_count = kwargs.get('target_word_count', 1200)
        
        if not topic:
            raise ValueError("Topic is required for content generation")
        
        if not research_findings:
            raise ValueError("Research findings are required for content generation")
        
        # Format research findings for prompt
        research_text = self._format_research(research_findings)
        
        # Build prompt from template
        prompt = self.user_prompt_template.format(
            topic=topic,
            research_findings=research_text,
            target_word_count=target_word_count,
            tone=tone
        )
        
        # Call AI model
        self.logger.info(
            "Starting content generation",
            agent=self.agent_name,
            topic=topic,
            target_word_count=target_word_count
        )
        
        response = self._call_model(prompt)
        
        # Calculate cost
        cost = self._calculate_cost(prompt, response)
        self.logger.cost_tracking(
            project_id=kwargs.get('project_id', 'unknown'),
            operation='content_generation',
            cost=cost,
            model=self.model_name
        )
        
        # Parse JSON response
        try:
            content_data = self._parse_content_response(response)
        except Exception as e:
            self.logger.warning(
                f"Failed to parse JSON response, using raw text: {e}",
                agent=self.agent_name
            )
            content_data = {
                'title': topic,
                'body': response,
                'sections': []
            }
        
        # Add metadata
        content_data['cost'] = cost
        content_data['model_used'] = self.model_name
        content_data['word_count'] = self._count_words(
            content_data.get('body', response)
        )
        
        return content_data
    
    def _format_research(self, research: Dict[str, Any]) -> str:
        """
        Format research findings into readable text
        
        Args:
            research: Research data
            
        Returns:
            Formatted research text
        """
        formatted = []
        
        if research.get('overview'):
            formatted.append(f"Overview:\n{research['overview']}")
        
        if research.get('key_points'):
            formatted.append("\nKey Points:")
            for i, point in enumerate(research['key_points'], 1):
                formatted.append(f"{i}. {point}")
        
        if research.get('trends'):
            formatted.append("\nCurrent Trends:")
            for trend in research['trends']:
                formatted.append(f"- {trend}")
        
        if research.get('common_questions'):
            formatted.append("\nCommon Questions:")
            for question in research['common_questions']:
                formatted.append(f"- {question}")
        
        return '\n'.join(formatted)
    
    def _parse_content_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON content response
        
        Args:
            response: Model response
            
        Returns:
            Parsed content data
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
            data = json.loads(json_str)
            
            # Build full body from sections
            if 'sections' in data and not data.get('body'):
                data['body'] = self._build_body_from_sections(data)
            
            return data
        
        # If no JSON found, try parsing entire response
        return json.loads(cleaned_response)
    
    def _build_body_from_sections(self, content_data: Dict[str, Any]) -> str:
        """
        Build full body text from sections
        
        Args:
            content_data: Parsed content with sections
            
        Returns:
            Full body text
        """
        parts = []
        
        # Add introduction
        if content_data.get('introduction'):
            parts.append(content_data['introduction'])
            parts.append('')  # Empty line
        
        # Add sections
        for section in content_data.get('sections', []):
            heading = section.get('heading', '')
            content = section.get('content', '')
            
            if heading:
                parts.append(f"## {heading}")
            if content:
                parts.append(content)
            parts.append('')  # Empty line
        
        # Add conclusion
        if content_data.get('conclusion'):
            parts.append("## Conclusion")
            parts.append(content_data['conclusion'])
        
        return '\n'.join(parts)
    
    def _count_words(self, text: str) -> int:
        """
        Count words in text
        
        Args:
            text: Text to count
            
        Returns:
            Word count
        """
        # Remove extra whitespace and split
        words = text.split()
        return len(words)
