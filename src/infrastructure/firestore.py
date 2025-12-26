"""
Firestore database manager for content projects
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
from google.cloud import firestore
from google.cloud.firestore_v1 import FieldFilter


class FirestoreManager:
    """Manages Firestore operations for content generation projects"""
    
    def __init__(self):
        """Initialize Firestore client"""
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        self.collection_name = os.getenv('FIRESTORE_COLLECTION', 'content_projects')
        
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
        
        self.db = firestore.Client(project=self.project_id)
        self.collection = self.db.collection(self.collection_name)
    
    def create_project(self, topic: str, **kwargs) -> str:
        """
        Create a new content project
        
        Args:
            topic: The topic for content generation
            **kwargs: Additional project metadata
            
        Returns:
            Project ID
        """
        project_data = {
            'topic': topic,
            'status': 'pending',
            'research': None,
            'content': None,
            'costs': {
                'research': 0.0,
                'generation': 0.0,
                'total': 0.0
            },
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP,
            **kwargs
        }
        
        # Create document with auto-generated ID
        doc_ref = self.collection.document()
        doc_ref.set(project_data)
        
        return doc_ref.id
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project by ID
        
        Args:
            project_id: Project document ID
            
        Returns:
            Project data or None if not found
        """
        doc = self.collection.document(project_id).get()
        
        if doc.exists:
            data = doc.to_dict()
            data['projectId'] = doc.id
            return data
        
        return None
    
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> None:
        """
        Update project data
        
        Args:
            project_id: Project document ID
            updates: Dictionary of fields to update
        """
        updates['updatedAt'] = firestore.SERVER_TIMESTAMP
        self.collection.document(project_id).update(updates)
    
    def update_status(self, project_id: str, status: str) -> None:
        """
        Update project status
        
        Args:
            project_id: Project document ID
            status: New status (pending, research, generating, completed, failed)
        """
        self.update_project(project_id, {'status': status})
    
    def save_research(self, project_id: str, research_data: Dict[str, Any]) -> None:
        """
        Save research results
        
        Args:
            project_id: Project document ID
            research_data: Research findings
        """
        research_with_timestamp = {
            **research_data,
            'completedAt': datetime.utcnow().isoformat()
        }
        
        self.update_project(project_id, {
            'research': research_with_timestamp,
            'status': 'research_completed'
        })
    
    def save_content(self, project_id: str, content_data: Dict[str, Any]) -> None:
        """
        Save generated content
        
        Args:
            project_id: Project document ID
            content_data: Generated content
        """
        content_with_timestamp = {
            **content_data,
            'completedAt': datetime.utcnow().isoformat()
        }
        
        self.update_project(project_id, {
            'content': content_with_timestamp,
            'status': 'completed'
        })
    
    def update_costs(self, project_id: str, cost_type: str, amount: float) -> None:
        """
        Update cost tracking
        
        Args:
            project_id: Project document ID
            cost_type: Type of cost (research, generation, etc.)
            amount: Cost amount in USD
        """
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        costs = project.get('costs', {})
        costs[cost_type] = costs.get(cost_type, 0.0) + amount
        costs['total'] = sum(v for k, v in costs.items() if k != 'total')
        
        self.update_project(project_id, {'costs': costs})
    
    def list_projects(
        self, 
        status: Optional[str] = None, 
        limit: int = 10
    ) -> list:
        """
        List projects with optional filtering
        
        Args:
            status: Filter by status
            limit: Maximum number of results
            
        Returns:
            List of projects
        """
        query = self.collection.order_by(
            'createdAt', 
            direction=firestore.Query.DESCENDING
        ).limit(limit)
        
        if status:
            query = query.where(filter=FieldFilter('status', '==', status))
        
        projects = []
        for doc in query.stream():
            data = doc.to_dict()
            data['projectId'] = doc.id
            projects.append(data)
        
        return projects
    
    def mark_failed(self, project_id: str, error_message: str) -> None:
        """
        Mark project as failed
        
        Args:
            project_id: Project document ID
            error_message: Error description
        """
        self.update_project(project_id, {
            'status': 'failed',
            'error': error_message,
            'failedAt': datetime.utcnow().isoformat()
        })
    
    def save_edited_content(self, project_id: str, edited_data: Dict[str, Any], quality_validation: Dict[str, Any] = None) -> None:
        """
        Save edited content
        
        Args:
            project_id: Project document ID
            edited_data: Edited content data
            quality_validation: Quality validation results (optional)
        """
        update_data = {
            'edited_content': edited_data,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        if quality_validation:
            update_data['quality_validation'] = quality_validation
        self.update_project(project_id, update_data)
    
    def save_seo_data(self, project_id: str, seo_data: Dict[str, Any], seo_validation: Dict[str, Any] = None) -> None:
        """
        Save SEO-optimized content
        
        Args:
            project_id: Project document ID
            seo_data: SEO content data
            seo_validation: SEO validation results (optional)
        """
        update_data = {
            'seo_content': seo_data,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        if seo_validation:
            update_data['seo_validation'] = seo_validation
        self.update_project(project_id, update_data)
    
    def add_error(self, project_id: str, stage: str, error: str) -> None:
        """
        Add an error to the project errors array
        
        Args:
            project_id: Project document ID
            stage: The workflow stage where the error occurred
            error: Error message
        """
        project = self.get_project(project_id)
        errors = project.get('errors', [])
        errors.append({
            'stage': stage,
            'message': error,
            'timestamp': datetime.utcnow().isoformat()
        })
        self.update_project(project_id, {
            'errors': errors,
            'updatedAt': firestore.SERVER_TIMESTAMP
        })

