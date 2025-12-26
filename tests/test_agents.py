"""
Unit tests for agents
"""

import pytest
from unittest.mock import Mock, patch
from src.agents import ResearchAgent, ContentGeneratorAgent


class TestResearchAgent:
    """Tests for ResearchAgent"""
    
    @patch('src.agents.base_agent.GenerativeModel')
    def test_research_agent_initialization(self, mock_model):
        """Test that ResearchAgent initializes correctly"""
        agent = ResearchAgent()
        
        assert agent.agent_name == 'research'
        assert agent.model_name is not None
        assert agent.temperature is not None
    
    @patch('src.agents.base_agent.GenerativeModel')
    def test_research_execution_requires_topic(self, mock_model):
        """Test that research execution requires a topic"""
        agent = ResearchAgent()
        
        with pytest.raises(ValueError, match="Topic is required"):
            agent._execute_internal()
    
    def test_key_points_extraction(self):
        """Test key points extraction from text"""
        agent = ResearchAgent()
        
        text = """
        Here are the main points:
        1. First important point
        2. Second important point
        - Third point
        - Fourth point
        """
        
        points = agent._extract_key_points(text)
        
        assert len(points) > 0
        assert isinstance(points, list)


class TestContentGeneratorAgent:
    """Tests for ContentGeneratorAgent"""
    
    @patch('src.agents.base_agent.GenerativeModel')
    def test_content_agent_initialization(self, mock_model):
        """Test that ContentGeneratorAgent initializes correctly"""
        agent = ContentGeneratorAgent()
        
        assert agent.agent_name == 'content_generator'
        assert agent.model_name is not None
    
    @patch('src.agents.base_agent.GenerativeModel')
    def test_content_execution_requires_topic(self, mock_model):
        """Test that content execution requires a topic"""
        agent = ContentGeneratorAgent()
        
        with pytest.raises(ValueError, match="Topic is required"):
            agent._execute_internal()
    
    @patch('src.agents.base_agent.GenerativeModel')
    def test_content_execution_requires_research(self, mock_model):
        """Test that content execution requires research findings"""
        agent = ContentGeneratorAgent()
        
        with pytest.raises(ValueError, match="Research findings are required"):
            agent._execute_internal(topic="Test Topic")
    
    def test_word_counting(self):
        """Test word counting"""
        agent = ContentGeneratorAgent()
        
        text = "This is a test sentence with ten words in it."
        count = agent._count_words(text)
        
        assert count == 10
    
    def test_research_formatting(self):
        """Test research formatting"""
        agent = ContentGeneratorAgent()
        
        research = {
            'overview': 'Test overview',
            'key_points': ['Point 1', 'Point 2'],
            'trends': ['Trend 1']
        }
        
        formatted = agent._format_research(research)
        
        assert 'Test overview' in formatted
        assert 'Point 1' in formatted
        assert 'Trend 1' in formatted


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
