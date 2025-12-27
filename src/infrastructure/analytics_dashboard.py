"""
Analytics Dashboard - Centralized metrics and performance tracking

Provides comprehensive analytics for:
- Content performance across platforms
- Agent performance metrics
- Cost tracking and ROI
- System health and performance
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
from src.infrastructure import FirestoreManager, CostTracker
from src.monitoring import StructuredLogger


class AnalyticsDashboard:
    """Centralized analytics and metrics dashboard"""
    
    def __init__(self):
        """Initialize analytics dashboard"""
        self.logger = StructuredLogger(name='analytics_dashboard')
        self.db = FirestoreManager()
        self.cost_tracker = CostTracker()
    
    def get_content_performance(
        self,
        project_id: str,
        include_platforms: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics for a content project
        
        Args:
            project_id: Project ID
            include_platforms: Whether to include platform-specific metrics
            
        Returns:
            Performance metrics dictionary
        """
        try:
            # Get project data
            project = self.db.get_project(project_id)
            
            if not project:
                return {'error': 'Project not found'}
            
            # Calculate performance metrics
            metrics = {
                'project_id': project_id,
                'title': project.get('topic', 'Untitled'),
                'created_at': project.get('created_at'),
                'status': project.get('status'),
                'overall_score': self._calculate_overall_score(project),
                'costs': project.get('costs', {}),
                'timeline': self._get_timeline_metrics(project),
                'quality': self._get_quality_metrics(project),
                'engagement': self._get_engagement_metrics(project)
            }
            
            if include_platforms:
                metrics['platforms'] = self._get_platform_metrics(project_id)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get content performance: {e}", project_id=project_id)
            return {'error': str(e)}
    
    def get_agent_performance(
        self,
        agent_type: Optional[str] = None,
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get performance metrics for agents
        
        Args:
            agent_type: Optional specific agent type
            time_range_days: Number of days to analyze
            
        Returns:
            Agent performance metrics
        """
        try:
            # Get all projects from the time range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=time_range_days)
            
            # Simulated agent metrics (in production, query from Firestore)
            agent_types = [agent_type] if agent_type else [
                'research', 'content', 'editor', 'seo', 
                'image', 'video', 'audio', 'publisher', 'quality_assurance'
            ]
            
            metrics = {}
            
            for atype in agent_types:
                metrics[atype] = {
                    'agent_type': atype,
                    'tasks_completed': self._get_agent_task_count(atype, start_date, end_date),
                    'average_execution_time': self._get_average_execution_time(atype),
                    'success_rate': self._get_agent_success_rate(atype),
                    'average_cost': self._get_average_agent_cost(atype),
                    'total_cost': self._get_total_agent_cost(atype),
                    'quality_score': self._get_agent_quality_score(atype),
                    'error_rate': self._get_agent_error_rate(atype)
                }
            
            return {
                'time_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': time_range_days
                },
                'agents': metrics,
                'summary': self._get_agent_summary(metrics)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get agent performance: {e}")
            return {'error': str(e)}
    
    def get_cost_analysis(
        self,
        time_range_days: int = 30,
        group_by: str = 'agent'  # 'agent', 'project', 'day'
    ) -> Dict[str, Any]:
        """
        Get cost analysis and breakdown
        
        Args:
            time_range_days: Number of days to analyze
            group_by: How to group cost data
            
        Returns:
            Cost analysis data
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=time_range_days)
            
            # Get cost data from cost tracker
            cost_data = self.cost_tracker.get_cost_summary()
            
            analysis = {
                'time_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': time_range_days
                },
                'total_cost': cost_data.get('total_cost', 0.0),
                'average_cost_per_project': cost_data.get('average_cost_per_project', 0.0),
                'breakdown': self._get_cost_breakdown(group_by),
                'trends': self._get_cost_trends(time_range_days),
                'budget_status': self._get_budget_status()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to get cost analysis: {e}")
            return {'error': str(e)}
    
    def get_platform_comparison(
        self,
        platforms: Optional[List[str]] = None,
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """
        Compare performance across different publishing platforms
        
        Args:
            platforms: Optional list of platforms to compare
            time_range_days: Number of days to analyze
            
        Returns:
            Platform comparison metrics
        """
        try:
            if not platforms:
                platforms = ['wordpress', 'medium', 'twitter', 'linkedin', 'facebook', 'instagram']
            
            comparison = {}
            
            for platform in platforms:
                comparison[platform] = {
                    'platform': platform,
                    'total_publications': self._get_platform_publication_count(platform),
                    'average_views': self._get_platform_avg_views(platform),
                    'average_engagement': self._get_platform_avg_engagement(platform),
                    'total_reach': self._get_platform_total_reach(platform),
                    'engagement_rate': self._get_platform_engagement_rate(platform),
                    'top_performing_content': self._get_top_content_for_platform(platform, limit=5)
                }
            
            return {
                'time_range_days': time_range_days,
                'platforms': comparison,
                'best_platform': self._determine_best_platform(comparison),
                'recommendations': self._get_platform_recommendations(comparison)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get platform comparison: {e}")
            return {'error': str(e)}
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health metrics
        
        Returns:
            System health data
        """
        try:
            health = {
                'timestamp': datetime.utcnow().isoformat(),
                'overall_status': 'healthy',  # healthy, degraded, down
                'components': {
                    'agents': self._check_agent_health(),
                    'infrastructure': self._check_infrastructure_health(),
                    'api': self._check_api_health(),
                    'database': self._check_database_health()
                },
                'performance': {
                    'average_response_time': self._get_avg_response_time(),
                    'requests_per_minute': self._get_request_rate(),
                    'error_rate': self._get_system_error_rate(),
                    'uptime_percentage': 99.9
                },
                'resource_usage': {
                    'active_projects': self._get_active_project_count(),
                    'queued_tasks': self._get_queued_task_count(),
                    'storage_used_gb': self._get_storage_usage()
                }
            }
            
            # Determine overall status
            component_statuses = [c['status'] for c in health['components'].values()]
            if 'down' in component_statuses:
                health['overall_status'] = 'down'
            elif 'degraded' in component_statuses:
                health['overall_status'] = 'degraded'
            
            return health
            
        except Exception as e:
            self.logger.error(f"Failed to get system health: {e}")
            return {
                'overall_status': 'error',
                'error': str(e)
            }
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard summary
        
        Returns:
            Dashboard summary with key metrics
        """
        try:
            summary = {
                'timestamp': datetime.utcnow().isoformat(),
                'overview': {
                    'total_projects': self._get_total_project_count(),
                    'active_projects': self._get_active_project_count(),
                    'completed_projects': self._get_completed_project_count(),
                    'total_content_generated': self._get_total_content_count()
                },
                'recent_performance': {
                    'last_24h': self._get_performance_last_24h(),
                    'last_7d': self._get_performance_last_7d(),
                    'last_30d': self._get_performance_last_30d()
                },
                'costs': {
                    'total_spent': self.cost_tracker.get_total_cost(),
                    'this_month': self._get_month_cost(),
                    'average_per_project': self._get_avg_project_cost(),
                    'budget_utilization': self._get_budget_utilization()
                },
                'quality': {
                    'average_quality_score': self._get_avg_quality_score(),
                    'content_passing_qa': self._get_qa_pass_rate()
                },
                'engagement': {
                    'total_views': self._get_total_views(),
                    'total_engagement': self._get_total_engagement(),
                    'average_engagement_rate': self._get_avg_engagement_rate()
                },
                'top_performers': {
                    'best_content': self._get_top_content(limit=5),
                    'best_platform': self._get_best_platform(),
                    'best_agent': self._get_best_agent()
                },
                'alerts': self._get_active_alerts()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get dashboard summary: {e}")
            return {'error': str(e)}
    
    # Helper methods (simulated data - in production, query from Firestore/BigQuery)
    
    def _calculate_overall_score(self, project: Dict[str, Any]) -> float:
        """Calculate overall project score"""
        quality_score = project.get('quality_score', 0.85)
        return quality_score
    
    def _get_timeline_metrics(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Get timeline metrics for project"""
        created = project.get('created_at')
        updated = project.get('updated_at')
        
        return {
            'created_at': created,
            'updated_at': updated,
            'total_time_minutes': 45,
            'research_time': 10,
            'generation_time': 20,
            'editing_time': 10,
            'optimization_time': 5
        }
    
    def _get_quality_metrics(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Get quality metrics"""
        return {
            'overall_score': project.get('quality_score', 0.85),
            'plagiarism_score': 0.95,
            'grammar_score': 0.92,
            'readability_score': 0.88,
            'seo_score': 0.87,
            'brand_voice_score': 0.83
        }
    
    def _get_engagement_metrics(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Get engagement metrics"""
        return {
            'total_views': 5234,
            'total_likes': 456,
            'total_shares': 123,
            'total_comments': 78,
            'engagement_rate': 0.089
        }
    
    def _get_platform_metrics(self, project_id: str) -> Dict[str, Any]:
        """Get platform-specific metrics"""
        return {
            'wordpress': {'views': 1234, 'comments': 45},
            'medium': {'views': 2345, 'reads': 1890},
            'twitter': {'impressions': 5234, 'engagements': 456},
            'linkedin': {'impressions': 3456, 'engagements': 345}
        }
    
    def _get_agent_task_count(self, agent_type: str, start_date: datetime, end_date: datetime) -> int:
        """Get task count for agent"""
        return 150  # Simulated
    
    def _get_average_execution_time(self, agent_type: str) -> float:
        """Get average execution time for agent"""
        times = {
            'research': 45.2,
            'content': 62.3,
            'editor': 38.5,
            'seo': 28.7,
            'image': 52.1,
            'video': 89.3,
            'audio': 67.4,
            'publisher': 15.8,
            'quality_assurance': 42.6
        }
        return times.get(agent_type, 50.0)
    
    def _get_agent_success_rate(self, agent_type: str) -> float:
        """Get success rate for agent"""
        return 0.96
    
    def _get_average_agent_cost(self, agent_type: str) -> float:
        """Get average cost per task for agent"""
        costs = {
            'research': 0.05,
            'content': 0.08,
            'editor': 0.04,
            'seo': 0.03,
            'image': 0.12,
            'video': 0.15,
            'audio': 0.10,
            'publisher': 0.01,
            'quality_assurance': 0.06
        }
        return costs.get(agent_type, 0.05)
    
    def _get_total_agent_cost(self, agent_type: str) -> float:
        """Get total cost for agent"""
        return self._get_average_agent_cost(agent_type) * 150  # tasks * avg cost
    
    def _get_agent_quality_score(self, agent_type: str) -> float:
        """Get quality score for agent output"""
        return 0.88
    
    def _get_agent_error_rate(self, agent_type: str) -> float:
        """Get error rate for agent"""
        return 0.04
    
    def _get_agent_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary of agent metrics"""
        total_tasks = sum(m['tasks_completed'] for m in metrics.values())
        total_cost = sum(m['total_cost'] for m in metrics.values())
        
        return {
            'total_tasks': total_tasks,
            'total_cost': total_cost,
            'average_success_rate': 0.96,
            'most_used_agent': 'content',
            'most_expensive_agent': 'video'
        }
    
    def _get_cost_breakdown(self, group_by: str) -> Dict[str, Any]:
        """Get cost breakdown"""
        if group_by == 'agent':
            return {
                'research': 7.50,
                'content': 12.00,
                'editor': 6.00,
                'seo': 4.50,
                'image': 18.00,
                'video': 22.50,
                'audio': 15.00,
                'publisher': 1.50,
                'quality_assurance': 9.00
            }
        return {}
    
    def _get_cost_trends(self, days: int) -> List[Dict[str, Any]]:
        """Get cost trends over time"""
        return [
            {'date': '2025-12-20', 'cost': 28.50},
            {'date': '2025-12-21', 'cost': 32.10},
            {'date': '2025-12-22', 'cost': 29.80},
            {'date': '2025-12-23', 'cost': 31.20},
            {'date': '2025-12-24', 'cost': 27.90}
        ]
    
    def _get_budget_status(self) -> Dict[str, Any]:
        """Get budget status"""
        return {
            'monthly_budget': 1000.0,
            'spent': 285.50,
            'remaining': 714.50,
            'utilization_percentage': 28.55,
            'projected_end_of_month': 892.40,
            'status': 'on_track'
        }
    
    def _get_platform_publication_count(self, platform: str) -> int:
        """Get publication count for platform"""
        return 45
    
    def _get_platform_avg_views(self, platform: str) -> float:
        """Get average views for platform"""
        return 2345.6
    
    def _get_platform_avg_engagement(self, platform: str) -> float:
        """Get average engagement for platform"""
        return 234.5
    
    def _get_platform_total_reach(self, platform: str) -> int:
        """Get total reach for platform"""
        return 105552
    
    def _get_platform_engagement_rate(self, platform: str) -> float:
        """Get engagement rate for platform"""
        rates = {
            'twitter': 0.087,
            'linkedin': 0.102,
            'facebook': 0.065,
            'instagram': 0.134,
            'medium': 0.081,
            'wordpress': 0.056
        }
        return rates.get(platform, 0.08)
    
    def _get_top_content_for_platform(self, platform: str, limit: int) -> List[Dict[str, Any]]:
        """Get top performing content for platform"""
        return [
            {'title': 'AI Trends 2026', 'views': 5234, 'engagement': 456},
            {'title': 'Cloud Architecture Guide', 'views': 4123, 'engagement': 389}
        ][:limit]
    
    def _determine_best_platform(self, comparison: Dict[str, Any]) -> str:
        """Determine best performing platform"""
        return 'instagram'
    
    def _get_platform_recommendations(self, comparison: Dict[str, Any]) -> List[str]:
        """Get platform recommendations"""
        return [
            "Instagram shows highest engagement rate - prioritize visual content",
            "LinkedIn performs well for professional content - increase posting frequency",
            "Twitter engagement could be improved with more frequent updates"
        ]
    
    def _check_agent_health(self) -> Dict[str, Any]:
        """Check agent health"""
        return {'status': 'healthy', 'active_agents': 9, 'idle_agents': 0}
    
    def _check_infrastructure_health(self) -> Dict[str, Any]:
        """Check infrastructure health"""
        return {'status': 'healthy', 'firestore': 'ok', 'storage': 'ok', 'pubsub': 'ok'}
    
    def _check_api_health(self) -> Dict[str, Any]:
        """Check API health"""
        return {'status': 'healthy', 'response_time_ms': 156}
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        return {'status': 'healthy', 'latency_ms': 23}
    
    def _get_avg_response_time(self) -> float:
        """Get average response time"""
        return 156.3
    
    def _get_request_rate(self) -> float:
        """Get request rate"""
        return 45.2
    
    def _get_system_error_rate(self) -> float:
        """Get system error rate"""
        return 0.012
    
    def _get_active_project_count(self) -> int:
        """Get active project count"""
        return 12
    
    def _get_queued_task_count(self) -> int:
        """Get queued task count"""
        return 34
    
    def _get_storage_usage(self) -> float:
        """Get storage usage in GB"""
        return 45.7
    
    def _get_total_project_count(self) -> int:
        """Get total project count"""
        return 234
    
    def _get_completed_project_count(self) -> int:
        """Get completed project count"""
        return 198
    
    def _get_total_content_count(self) -> int:
        """Get total content count"""
        return 512
    
    def _get_performance_last_24h(self) -> Dict[str, Any]:
        """Get performance for last 24 hours"""
        return {'projects_completed': 5, 'average_time_minutes': 42}
    
    def _get_performance_last_7d(self) -> Dict[str, Any]:
        """Get performance for last 7 days"""
        return {'projects_completed': 28, 'average_time_minutes': 45}
    
    def _get_performance_last_30d(self) -> Dict[str, Any]:
        """Get performance for last 30 days"""
        return {'projects_completed': 102, 'average_time_minutes': 46}
    
    def _get_month_cost(self) -> float:
        """Get this month's cost"""
        return 285.50
    
    def _get_avg_project_cost(self) -> float:
        """Get average project cost"""
        return 0.28
    
    def _get_budget_utilization(self) -> float:
        """Get budget utilization percentage"""
        return 28.55
    
    def _get_avg_quality_score(self) -> float:
        """Get average quality score"""
        return 0.87
    
    def _get_qa_pass_rate(self) -> float:
        """Get QA pass rate"""
        return 0.92
    
    def _get_total_views(self) -> int:
        """Get total views across all content"""
        return 523456
    
    def _get_total_engagement(self) -> int:
        """Get total engagement"""
        return 45678
    
    def _get_avg_engagement_rate(self) -> float:
        """Get average engagement rate"""
        return 0.089
    
    def _get_top_content(self, limit: int) -> List[Dict[str, Any]]:
        """Get top performing content"""
        return [
            {'project_id': 'proj_001', 'title': 'AI Trends 2026', 'views': 12345, 'engagement_rate': 0.145},
            {'project_id': 'proj_002', 'title': 'Cloud Best Practices', 'views': 9876, 'engagement_rate': 0.132}
        ][:limit]
    
    def _get_best_platform(self) -> str:
        """Get best performing platform"""
        return 'instagram'
    
    def _get_best_agent(self) -> str:
        """Get best performing agent"""
        return 'content'
    
    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active system alerts"""
        return [
            {'severity': 'info', 'message': 'High traffic detected on LinkedIn integration'},
            {'severity': 'warning', 'message': 'Cost approaching 30% of monthly budget'}
        ]
