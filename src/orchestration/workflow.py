"""
Synchronous workflow orchestrator for content generation
"""

from typing import Dict, Any, Optional
from src.agents import ResearchAgent, ContentGeneratorAgent
from src.infrastructure import FirestoreManager, CostTracker
from src.monitoring import StructuredLogger


class ContentGenerationWorkflow:
    """Orchestrates the content generation process"""
    
    def __init__(self):
        """Initialize workflow components"""
        self.logger = StructuredLogger(name='workflow')
        self.db = FirestoreManager()
        self.cost_tracker = CostTracker()
        
        # Initialize agents
        self.research_agent = ResearchAgent()
        self.content_agent = ContentGeneratorAgent()
    
    def generate_content(
        self,
        topic: str,
        tone: str = 'professional and conversational',
        target_word_count: int = 1200,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate blog post content end-to-end
        
        Args:
            topic: Topic for the blog post
            tone: Writing tone
            target_word_count: Target word count
            **kwargs: Additional parameters
            
        Returns:
            Complete generation result with project ID
        """
        project_id = None
        
        try:
            # Create project in Firestore
            project_id = self.db.create_project(
                topic=topic,
                tone=tone,
                target_word_count=target_word_count
            )
            
            self.logger.info(
                "Starting content generation workflow",
                project_id=project_id,
                topic=topic
            )
            
            # Step 1: Research
            self.db.update_status(project_id, 'research')
            
            research_result = self.research_agent.execute(
                project_id=project_id,
                topic=topic
            )
            
            # Save research and costs
            self.db.save_research(project_id, research_result)
            self.db.update_costs(
                project_id,
                'research',
                research_result.get('cost', 0.0)
            )
            
            # Step 2: Content Generation
            self.db.update_status(project_id, 'generating')
            
            content_result = self.content_agent.execute(
                project_id=project_id,
                topic=topic,
                research_findings=research_result,
                tone=tone,
                target_word_count=target_word_count
            )
            
            # Save content and costs
            self.db.save_content(project_id, content_result)
            self.db.update_costs(
                project_id,
                'generation',
                content_result.get('cost', 0.0)
            )
            
            # Get final project data
            final_project = self.db.get_project(project_id)
            
            self.logger.info(
                "Content generation completed",
                project_id=project_id,
                total_cost=final_project['costs']['total'],
                word_count=content_result.get('word_count', 0)
            )
            
            return {
                'success': True,
                'project_id': project_id,
                'project': final_project,
                'content': content_result,
                'research': research_result
            }
            
        except Exception as e:
            # Mark project as failed
            if project_id:
                self.db.mark_failed(project_id, str(e))
            
            self.logger.error(
                f"Content generation failed: {str(e)}",
                project_id=project_id,
                error=str(e)
            )
            
            return {
                'success': False,
                'project_id': project_id,
                'error': str(e)
            }
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project by ID
        
        Args:
            project_id: Project document ID
            
        Returns:
            Project data
        """
        return self.db.get_project(project_id)
    
    def list_projects(
        self,
        status: Optional[str] = None,
        limit: int = 10
    ) -> list:
        """
        List recent projects
        
        Args:
            status: Filter by status
            limit: Maximum results
            
        Returns:
            List of projects
        """
        return self.db.list_projects(status=status, limit=limit)
