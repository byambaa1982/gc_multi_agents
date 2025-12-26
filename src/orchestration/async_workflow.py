"""
Enhanced async workflow orchestrator with Pub/Sub messaging
Orchestrates multi-agent content generation with event-driven architecture
"""

import json
import time
from typing import Dict, Any, Optional, List
from enum import Enum

from src.agents import ResearchAgent, ContentGeneratorAgent
from src.agents.editor_agent import EditorAgent
from src.agents.seo_optimizer_agent import SEOOptimizerAgent
from src.infrastructure import FirestoreManager, CostTracker
from src.infrastructure.pubsub_manager import PubSubManager
from src.monitoring import StructuredLogger


class WorkflowStage(Enum):
    """Workflow stages"""
    CREATED = "created"
    RESEARCH = "research"
    GENERATING = "generating"
    EDITING = "editing"
    SEO_OPTIMIZATION = "seo_optimization"
    COMPLETED = "completed"
    FAILED = "failed"


class AsyncContentWorkflow:
    """
    Event-driven async workflow orchestrator for content generation
    Uses Pub/Sub for inter-agent communication
    """
    
    def __init__(self):
        """Initialize async workflow components"""
        self.logger = StructuredLogger(name='async_workflow')
        self.db = FirestoreManager()
        self.cost_tracker = CostTracker()
        self.pubsub = PubSubManager()
        
        # Initialize agents
        self.research_agent = ResearchAgent()
        self.content_agent = ContentGeneratorAgent()
        self.editor_agent = EditorAgent()
        self.seo_agent = SEOOptimizerAgent()
        
        self.logger.info("Async workflow orchestrator initialized")
    
    def start_workflow(
        self,
        topic: str,
        tone: str = 'professional and conversational',
        target_word_count: int = 1200,
        primary_keyword: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Start async content generation workflow
        
        Args:
            topic: Topic for content
            tone: Writing tone
            target_word_count: Target word count
            primary_keyword: Primary SEO keyword
            **kwargs: Additional parameters
            
        Returns:
            Project ID
        """
        try:
            # Create project in Firestore
            project_id = self.db.create_project(
                topic=topic,
                tone=tone,
                target_word_count=target_word_count,
                metadata={
                    'primary_keyword': primary_keyword,
                    'workflow_type': 'async',
                    **kwargs
                }
            )
            
            self.logger.info(
                "Starting async content workflow",
                project_id=project_id,
                topic=topic
            )
            
            # Start research phase
            self._execute_research_phase(project_id, topic)
            
            return project_id
            
        except Exception as e:
            self.logger.error(
                "Failed to start workflow",
                error=str(e),
                topic=topic
            )
            raise
    
    def _execute_research_phase(self, project_id: str, topic: str):
        """
        Execute research phase and publish completion event
        
        Args:
            project_id: Project ID
            topic: Research topic
        """
        try:
            self.db.update_status(project_id, WorkflowStage.RESEARCH.value)
            
            # Execute research
            research_result = self.research_agent.execute(
                project_id=project_id,
                topic=topic
            )
            
            # Save research
            self.db.save_research(project_id, research_result)
            self.db.update_costs(
                project_id,
                'research',
                research_result.get('cost', 0.0)
            )
            
            self.logger.info(
                "Research phase completed",
                project_id=project_id
            )
            
            # Publish event for content generation
            self.pubsub.publish_message(
                'research-complete',
                {
                    'project_id': project_id,
                    'topic': topic,
                    'research_findings': research_result,
                    'next_stage': WorkflowStage.GENERATING.value
                }
            )
            
        except Exception as e:
            self._handle_stage_failure(project_id, WorkflowStage.RESEARCH.value, str(e))
    
    def handle_research_complete(self, message_data: Dict[str, Any]):
        """
        Handle research-complete event and start content generation
        
        Args:
            message_data: Message payload
        """
        project_id = message_data.get('project_id')
        
        try:
            # Get project details
            project = self.db.get_project(project_id)
            
            self.db.update_status(project_id, WorkflowStage.GENERATING.value)
            
            # Execute content generation
            content_result = self.content_agent.execute(
                project_id=project_id,
                topic=project['topic'],
                research_findings=message_data['research_findings'],
                tone=project.get('tone', 'professional'),
                target_word_count=project.get('target_word_count', 1200)
            )
            
            # Save content
            self.db.save_content(project_id, content_result)
            self.db.update_costs(
                project_id,
                'generation',
                content_result.get('cost', 0.0)
            )
            
            self.logger.info(
                "Content generation completed",
                project_id=project_id
            )
            
            # Publish event for editing
            self.pubsub.publish_message(
                'content-generated',
                {
                    'project_id': project_id,
                    'content': content_result,
                    'tone': project.get('tone'),
                    'next_stage': WorkflowStage.EDITING.value
                }
            )
            
        except Exception as e:
            self._handle_stage_failure(project_id, WorkflowStage.GENERATING.value, str(e))
    
    def handle_content_generated(self, message_data: Dict[str, Any]):
        """
        Handle content-generated event and start editing
        
        Args:
            message_data: Message payload
        """
        project_id = message_data.get('project_id')
        
        try:
            self.db.update_status(project_id, WorkflowStage.EDITING.value)
            
            # Execute editing
            edited_result = self.editor_agent.execute(
                project_id=project_id,
                content=message_data['content'],
                tone=message_data.get('tone', 'professional')
            )
            
            # Validate quality
            quality_validation = self.editor_agent.validate_quality(edited_result)
            
            # Save edited content
            self.db.save_edited_content(project_id, edited_result, quality_validation)
            self.db.update_costs(
                project_id,
                'editing',
                edited_result.get('cost', 0.0)
            )
            
            self.logger.info(
                "Editing completed",
                project_id=project_id,
                quality_passed=quality_validation.get('overall_passed')
            )
            
            # Publish event for SEO optimization
            self.pubsub.publish_message(
                'editing-complete',
                {
                    'project_id': project_id,
                    'edited_content': {
                        'title': edited_result.get('edited_title'),
                        'body': edited_result.get('edited_body')
                    },
                    'quality_validation': quality_validation,
                    'next_stage': WorkflowStage.SEO_OPTIMIZATION.value
                }
            )
            
        except Exception as e:
            self._handle_stage_failure(project_id, WorkflowStage.EDITING.value, str(e))
    
    def handle_editing_complete(self, message_data: Dict[str, Any]):
        """
        Handle editing-complete event and start SEO optimization
        
        Args:
            message_data: Message payload
        """
        project_id = message_data.get('project_id')
        
        try:
            # Get project to retrieve primary keyword
            project = self.db.get_project(project_id)
            primary_keyword = project.get('metadata', {}).get('primary_keyword')
            
            self.db.update_status(project_id, WorkflowStage.SEO_OPTIMIZATION.value)
            
            # Execute SEO optimization
            seo_result = self.seo_agent.execute(
                project_id=project_id,
                content=message_data['edited_content'],
                primary_keyword=primary_keyword
            )
            
            # Validate SEO
            seo_validation = self.seo_agent.validate_seo(seo_result)
            
            # Save SEO data
            self.db.save_seo_data(project_id, seo_result, seo_validation)
            self.db.update_costs(
                project_id,
                'seo_optimization',
                seo_result.get('cost', 0.0)
            )
            
            self.logger.info(
                "SEO optimization completed",
                project_id=project_id,
                seo_score=seo_result.get('seo_score')
            )
            
            # Mark workflow complete
            self.db.update_status(project_id, WorkflowStage.COMPLETED.value)
            
            # Publish completion event
            self.pubsub.publish_message(
                'seo-optimized',
                {
                    'project_id': project_id,
                    'seo_validation': seo_validation,
                    'workflow_status': WorkflowStage.COMPLETED.value
                }
            )
            
        except Exception as e:
            self._handle_stage_failure(project_id, WorkflowStage.SEO_OPTIMIZATION.value, str(e))
    
    def _handle_stage_failure(self, project_id: str, stage: str, error: str):
        """
        Handle workflow stage failure
        
        Args:
            project_id: Project ID
            stage: Failed stage
            error: Error message
        """
        self.logger.error(
            f"Workflow stage {stage} failed",
            project_id=project_id,
            stage=stage,
            error=error
        )
        
        # Update project status
        self.db.update_status(project_id, WorkflowStage.FAILED.value)
        
        # Save error info
        self.db.add_error(project_id, stage, error)
        
        # Publish failure event
        self.pubsub.publish_message(
            'task-failed',
            {
                'project_id': project_id,
                'failed_stage': stage,
                'error': error,
                'timestamp': time.time()
            }
        )
    
    def get_workflow_status(self, project_id: str) -> Dict[str, Any]:
        """
        Get current workflow status
        
        Args:
            project_id: Project ID
            
        Returns:
            Workflow status and progress
        """
        project = self.db.get_project(project_id)
        
        return {
            'project_id': project_id,
            'status': project['status'],
            'topic': project['topic'],
            'created_at': project.get('createdAt', project.get('created_at')),
            'updated_at': project.get('updatedAt', project.get('updated_at')),
            'costs': project.get('costs', {}),
            'completed_stages': self._get_completed_stages(project),
            'current_stage': project['status'],
            'errors': project.get('errors', [])
        }
    
    def _get_completed_stages(self, project: Dict[str, Any]) -> List[str]:
        """
        Determine which stages have been completed
        
        Args:
            project: Project data
            
        Returns:
            List of completed stages
        """
        completed = []
        
        if project.get('research'):
            completed.append(WorkflowStage.RESEARCH.value)
        
        if project.get('content'):
            completed.append(WorkflowStage.GENERATING.value)
        
        if project.get('edited_content'):
            completed.append(WorkflowStage.EDITING.value)
        
        if project.get('seo_data'):
            completed.append(WorkflowStage.SEO_OPTIMIZATION.value)
        
        return completed
    
    def setup_event_handlers(self):
        """
        Set up Pub/Sub event handlers for workflow stages
        """
        self.logger.info("Setting up workflow event handlers")
        
        # Handler for research-complete
        def research_handler(message):
            data = json.loads(message.data.decode('utf-8'))
            self.handle_research_complete(data)
        
        # Handler for content-generated
        def content_handler(message):
            data = json.loads(message.data.decode('utf-8'))
            self.handle_content_generated(data)
        
        # Handler for editing-complete
        def editing_handler(message):
            data = json.loads(message.data.decode('utf-8'))
            self.handle_editing_complete(data)
        
        # Subscribe to events
        self.research_future = self.pubsub.subscribe(
            'research-complete-sub',
            research_handler
        )
        
        self.content_future = self.pubsub.subscribe(
            'content-generated-sub',
            content_handler
        )
        
        self.editing_future = self.pubsub.subscribe(
            'editing-complete-sub',
            editing_handler
        )
        
        self.logger.info("Workflow event handlers configured")
    
    def run_event_loop(self):
        """
        Run the event loop to process workflow events
        This is a blocking operation
        """
        self.logger.info("Starting workflow event loop")
        
        try:
            # Wait on futures
            self.research_future.result()
        except KeyboardInterrupt:
            self.logger.info("Shutting down workflow event loop")
            self.research_future.cancel()
            self.content_future.cancel()
            self.editing_future.cancel()
        except Exception as e:
            self.logger.error(f"Event loop error: {e}")
            raise
