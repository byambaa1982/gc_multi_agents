"""
Synchronous workflow orchestrator for content generation
"""

from typing import Dict, Any, Optional, List
from src.agents import ResearchAgent, ContentGeneratorAgent
from src.agents.publisher_agent import PublisherAgent
from src.agents.quality_assurance_agent import QualityAssuranceAgent
from src.infrastructure import FirestoreManager, CostTracker
from src.infrastructure.platform_integrations import PlatformIntegrationManager
from src.monitoring import StructuredLogger
from src.monitoring.performance_monitor import performance_monitor


class ContentGenerationWorkflow:
    """Orchestrates the content generation process"""
    
    def __init__(self):
        """Initialize workflow components"""
        import os
        from src.infrastructure.quota_manager import QuotaManager
        import yaml
        
        self.logger = StructuredLogger(name='workflow')
        self.db = FirestoreManager()
        self.cost_tracker = CostTracker()
        
        # Get configuration
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
        
        # Load agent config
        try:
            with open('config/agent_config.yaml', 'r') as f:
                config = yaml.safe_load(f)
        except:
            # Default minimal config if file not found
            config = {
                'quality_assurance': {
                    'model': 'gemini-1.5-flash',
                    'thresholds': {
                        'min_quality_score': 0.7,
                        'min_readability_score': 0.6
                    }
                }
            }
        
        # Initialize quota manager
        quota_manager = QuotaManager()
        
        # Initialize agents
        self.research_agent = ResearchAgent()
        self.content_agent = ContentGeneratorAgent()
        self.publisher_agent = PublisherAgent()
        self.qa_agent = QualityAssuranceAgent(
            project_id=project_id,
            location=location,
            config=config.get('quality_assurance', {}),
            cost_tracker=self.cost_tracker,
            quota_manager=quota_manager
        )
        
        # Initialize platform integrations
        self.platform_manager = PlatformIntegrationManager()
    
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
    
    def publish_content(
        self,
        project_id: str,
        platforms: List[str],
        schedule: Optional[Dict[str, Any]] = None,
        run_qa: bool = True
    ) -> Dict[str, Any]:
        """
        Publish generated content to specified platforms
        
        Args:
            project_id: Project ID
            platforms: List of platforms to publish to
            schedule: Optional scheduling information
            run_qa: Whether to run quality assurance before publishing
            
        Returns:
            Publishing results
        """
        try:
            with performance_monitor.track_operation('workflow.publish'):
                self.logger.info(
                    "Starting content publishing",
                    project_id=project_id,
                    platforms=platforms
                )
                
                # Get project and content
                project = self.db.get_project(project_id)
                if not project:
                    raise ValueError(f"Project {project_id} not found")
                
                # Run QA if requested
                if run_qa:
                    self.db.update_status(project_id, 'qa_review')
                    qa_result = self.qa_agent.execute(
                        project_id=project_id,
                        content=project.get('content', {}),
                        title=project.get('topic', '')
                    )
                    
                    if not qa_result.get('passed', False):
                        self.logger.warning(
                            "Content failed QA, publishing aborted",
                            project_id=project_id,
                            quality_score=qa_result.get('overall_score')
                        )
                        return {
                            'success': False,
                            'project_id': project_id,
                            'error': 'Content failed quality assurance',
                            'qa_report': qa_result
                        }
                
                # Update status to publishing
                self.db.update_status(project_id, 'publishing')
                
                # Publish to platforms
                publish_result = self.publisher_agent.execute(
                    project_id=project_id,
                    platforms=platforms,
                    content=project.get('content', {}),
                    schedule=schedule
                )
                
                # Save publishing results
                self.db.update_costs(
                    project_id,
                    'publishing',
                    publish_result.get('cost', 0.0)
                )
                
                # Update project status
                if publish_result.get('status') == 'completed':
                    self.db.update_status(project_id, 'published')
                else:
                    self.db.update_status(project_id, 'publish_partial')
                
                self.logger.info(
                    "Content publishing completed",
                    project_id=project_id,
                    status=publish_result.get('status')
                )
                
                return {
                    'success': True,
                    'project_id': project_id,
                    'publishing_results': publish_result
                }
        
        except Exception as e:
            self.logger.error(
                f"Content publishing failed: {str(e)}",
                project_id=project_id,
                error=str(e)
            )
            
            return {
                'success': False,
                'project_id': project_id,
                'error': str(e)
            }
    
    def generate_and_publish(
        self,
        topic: str,
        platforms: List[str],
        tone: str = 'professional and conversational',
        target_word_count: int = 1200,
        schedule: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Complete workflow: Generate and publish content
        
        Args:
            topic: Content topic
            platforms: Platforms to publish to
            tone: Writing tone
            target_word_count: Target word count
            schedule: Publishing schedule
            **kwargs: Additional parameters
            
        Returns:
            Complete workflow result
        """
        try:
            # Step 1: Generate content
            generation_result = self.generate_content(
                topic=topic,
                tone=tone,
                target_word_count=target_word_count,
                **kwargs
            )
            
            if not generation_result.get('success'):
                return generation_result
            
            project_id = generation_result['project_id']
            
            # Step 2: Publish content
            publish_result = self.publish_content(
                project_id=project_id,
                platforms=platforms,
                schedule=schedule,
                run_qa=True
            )
            
            return {
                'success': publish_result.get('success'),
                'project_id': project_id,
                'generation': generation_result,
                'publishing': publish_result
            }
            
        except Exception as e:
            self.logger.error(
                f"Generate and publish workflow failed: {str(e)}",
                error=str(e)
            )
            
            return {
                'success': False,
                'error': str(e)
            }
