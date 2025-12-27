"""
Publisher Agent - Multi-platform content distribution

This agent handles publishing content to various platforms including:
- WordPress
- Medium
- Social Media (Twitter/X, LinkedIn, Facebook, Instagram)
- Email newsletters
- Custom webhooks
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from .base_agent import BaseAgent


class PublisherAgent(BaseAgent):
    """Agent responsible for publishing content across multiple platforms"""
    
    SUPPORTED_PLATFORMS = [
        'wordpress',
        'medium',
        'twitter',
        'linkedin',
        'facebook',
        'instagram',
        'email',
        'webhook'
    ]
    
    PLATFORM_LIMITS = {
        'twitter': {'max_length': 280, 'image_count': 4},
        'linkedin': {'max_length': 3000, 'image_count': 20},
        'facebook': {'max_length': 63206, 'image_count': 10},
        'instagram': {'max_length': 2200, 'image_count': 10},
        'medium': {'max_length': None, 'image_count': None},
        'wordpress': {'max_length': None, 'image_count': None}
    }
    
    def __init__(self):
        """Initialize publisher agent"""
        super().__init__(
            agent_name='publisher'
        )
    
    def _execute_internal(self, **kwargs) -> Dict[str, Any]:
        """Internal execution - required by BaseAgent"""
        # Extract parameters without duplicating them in **kwargs
        platforms = kwargs.pop('platforms', [])
        content = kwargs.pop('content', {})
        schedule = kwargs.pop('schedule', None)
        project_id = kwargs.pop('project_id', 'default_project')
        
        return self.publish(
            project_id=project_id,
            platforms=platforms,
            content=content,
            schedule=schedule,
            **kwargs
        )
    
    def publish(
        self,
        project_id: str,
        platforms: List[str],
        content: Dict[str, Any],
        schedule: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Publish content to specified platforms
        
        Args:
            project_id: Project identifier
            platforms: List of platforms to publish to
            content: Content to publish including title, body, images, etc.
            schedule: Optional scheduling information
            **kwargs: Additional platform-specific parameters
            
        Returns:
            Publishing results with status for each platform
        """
        self.logger.info(
            "Starting content publishing",
            project_id=project_id,
            platforms=platforms
        )
        
        # Validate platforms
        invalid_platforms = [p for p in platforms if p not in self.SUPPORTED_PLATFORMS]
        if invalid_platforms:
            raise ValueError(f"Unsupported platforms: {invalid_platforms}")
        
        # Prepare content for each platform
        platform_content = self._prepare_content_for_platforms(
            content=content,
            platforms=platforms,
            project_id=project_id
        )
        
        # Generate publishing plan
        publishing_plan = self._generate_publishing_plan(
            platforms=platforms,
            schedule=schedule,
            content=content
        )
        
        # Execute publishing (simulation for now - actual API calls would go here)
        results = {}
        for platform in platforms:
            results[platform] = self._publish_to_platform(
                platform=platform,
                content=platform_content[platform],
                plan=publishing_plan[platform],
                project_id=project_id
            )
        
        return {
            'project_id': project_id,
            'timestamp': datetime.utcnow().isoformat(),
            'platforms': platforms,
            'results': results,
            'publishing_plan': publishing_plan,
            'status': 'completed' if all(r['success'] for r in results.values()) else 'partial',
            'cost': sum(r.get('cost', 0) for r in results.values())
        }
    
    def _prepare_content_for_platforms(
        self,
        content: Dict[str, Any],
        platforms: List[str],
        project_id: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Prepare content for each platform with platform-specific formatting
        
        Args:
            content: Original content
            platforms: Target platforms
            project_id: Project ID for tracking
            
        Returns:
            Platform-specific content dictionary
        """
        platform_content = {}
        
        for platform in platforms:
            if platform == 'twitter':
                platform_content[platform] = self._format_for_twitter(content)
            elif platform == 'linkedin':
                platform_content[platform] = self._format_for_linkedin(content)
            elif platform == 'facebook':
                platform_content[platform] = self._format_for_facebook(content)
            elif platform == 'instagram':
                platform_content[platform] = self._format_for_instagram(content)
            elif platform == 'medium':
                platform_content[platform] = self._format_for_medium(content)
            elif platform == 'wordpress':
                platform_content[platform] = self._format_for_wordpress(content)
            elif platform == 'email':
                platform_content[platform] = self._format_for_email(content)
            else:
                platform_content[platform] = content
        
        return platform_content
    
    def _format_for_twitter(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for Twitter/X"""
        title = content.get('title', '')
        body = content.get('body', '').strip()
        excerpt = content.get('excerpt', '')
        
        # Create concise tweet (template-based for demo)
        max_length = 280
        
        # Use excerpt or first sentence of body
        text = excerpt if excerpt else body.split('.')[0] + '.'
        
        # Add hashtags from tags if available
        tags = content.get('tags', [])
        hashtags = ' '.join([f'#{tag.replace(" ", "")}' for tag in tags[:3]])
        
        # Create tweet text
        tweet_text = f"{text} {hashtags}".strip()
        
        # Ensure within limit
        if len(tweet_text) > max_length:
            tweet_text = tweet_text[:max_length-3] + "..."
        
        return {
            'text': tweet_text,
            'images': content.get('images', [])[:4],  # Max 4 images
            'metadata': {
                'hashtags': tags[:3],
                'length': len(tweet_text)
            }
        }
    
    def _format_for_linkedin(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for LinkedIn"""
        title = content.get('title', '')
        body = content.get('body', '')
        
    def _format_for_linkedin(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for LinkedIn"""
        title = content.get('title', '')
        body = content.get('body', '').strip()
        excerpt = content.get('excerpt', '')
        tags = content.get('tags', [])
        
        # Create professional LinkedIn post (template-based)
        post_text = f"{title}\n\n{excerpt}\n\n"
        
        # Add first paragraph of body
        paragraphs = body.split('\n\n')
        if paragraphs:
            post_text += paragraphs[0][:500] + "...\n\n"
        
        # Add hashtags
        hashtags = ' '.join([f'#{tag.replace(" ", "")}' for tag in tags[:5]])
        post_text += f"\n{hashtags}"
        
        # Ensure within limit (3000 chars)
        if len(post_text) > 3000:
            post_text = post_text[:2997] + "..."
        
        return {
            'text': post_text,
            'images': content.get('images', []),
            'metadata': {
                'hashtags': tags[:5],
                'length': len(post_text)
            }
        }
    
    def _format_for_facebook(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for Facebook"""
        title = content.get('title', '')
        body = content.get('body', '').strip()
        excerpt = content.get('excerpt', '')
        tags = content.get('tags', [])
        
        # Create engaging Facebook post (template-based)
        post_text = f"{title}\n\n{excerpt}\n\n"
        
        # Add snippet from body
        if body:
            first_para = body.split('\n')[0][:300]
            post_text += first_para + "...\n\n"
        
        # Add hashtags
        hashtags = ' '.join([f'#{tag.replace(" ", "")}' for tag in tags[:3]])
        post_text += hashtags
        
        return {
            'text': post_text,
            'images': content.get('images', [])[:10],
            'metadata': {
                'hashtags': tags[:3],
                'length': len(post_text)
            }
        }
    
    def _format_for_instagram(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for Instagram"""
        title = content.get('title', '')
        body = content.get('body', '').strip()
        excerpt = content.get('excerpt', '')
        tags = content.get('tags', [])
        
        # Create Instagram caption (template-based, visual-first)
        caption = f"✨ {title}\n\n{excerpt}\n\n"
        
        # Add hashtags (Instagram loves them)
        hashtags = '\n'.join([f'#{tag.replace(" ", "")}' for tag in tags[:10]])
        caption += f"\n{hashtags}"
        
        # Ensure within limit (2200 chars)
        if len(caption) > 2200:
            caption = caption[:2197] + "..."
        
        return {
            'caption': caption,
            'images': content.get('images', [])[:10],
            'metadata': {
                'hashtags': tags[:10],
                'length': len(caption)
            }
        }
    
    def _format_for_medium(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for Medium"""
        return {
            'title': content.get('title', ''),
            'body': content.get('body', ''),
            'subtitle': content.get('excerpt', ''),
            'tags': content.get('tags', [])[:5],  # Medium allows max 5 tags
            'canonical_url': content.get('canonical_url'),
            'images': content.get('images', [])
        }
    
    def _format_for_wordpress(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for WordPress"""
        return {
            'title': content.get('title', ''),
            'content': content.get('body', ''),
            'excerpt': content.get('excerpt', ''),
            'categories': content.get('categories', []),
            'tags': content.get('tags', []),
            'featured_image': content.get('images', [None])[0],
            'seo': content.get('seo', {}),
            'status': 'draft'  # Default to draft for safety
        }
    
    def _format_for_email(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for email newsletter"""
        title = content.get('title', '')
        body = content.get('body', '')
    def _format_for_email(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for email newsletter"""
        title = content.get('title', '')
        body = content.get('body', '').strip()
        excerpt = content.get('excerpt', '')
        
        # Create email-friendly version (template-based)
        return {
            'subject': title,
            'preview_text': excerpt[:90] if excerpt else body[:90],
            'body_html': f"<h1>{title}</h1>\n<p>{excerpt}</p>\n<div>{body[:500]}...</div>",
            'from_name': content.get('author', 'Content Team'),
            'images': content.get('images', [])
        }
    
    def _generate_publishing_plan(
        self,
        platforms: List[str],
        schedule: Optional[Dict[str, Any]],
        content: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate optimal publishing schedule for each platform
        
        Args:
            platforms: Target platforms
            schedule: User-provided schedule preferences
            content: Content being published
            
        Returns:
            Publishing plan for each platform
        """
        now = datetime.utcnow()
        
        # Default best times for each platform (UTC)
        best_times = {
            'twitter': {'hour': 13, 'minute': 0},  # 1 PM UTC
            'linkedin': {'hour': 10, 'minute': 0},  # 10 AM UTC (business hours)
            'facebook': {'hour': 15, 'minute': 0},  # 3 PM UTC
            'instagram': {'hour': 18, 'minute': 0},  # 6 PM UTC (evening engagement)
            'medium': {'hour': 8, 'minute': 0},   # 8 AM UTC (morning reads)
            'wordpress': {'hour': 9, 'minute': 0}, # 9 AM UTC
            'email': {'hour': 14, 'minute': 0}     # 2 PM UTC
        }
        
        plan = {}
        for platform in platforms:
            if schedule and platform in schedule:
                # Use user-provided schedule
                scheduled_time = schedule[platform]
            else:
                # Use optimal time
                optimal = best_times.get(platform, {'hour': 12, 'minute': 0})
                scheduled_time = now.replace(
                    hour=optimal['hour'],
                    minute=optimal['minute'],
                    second=0,
                    microsecond=0
                )
                
                # If time has passed, schedule for next day
                if scheduled_time < now:
                    scheduled_time += timedelta(days=1)
            
            plan[platform] = {
                'scheduled_time': scheduled_time.isoformat() if isinstance(scheduled_time, datetime) else scheduled_time,
                'status': 'scheduled',
                'retry_policy': {
                    'max_retries': 3,
                    'backoff': 'exponential'
                }
            }
        
        return plan
    
    def _publish_to_platform(
        self,
        platform: str,
        content: Dict[str, Any],
        plan: Dict[str, Any],
        project_id: str
    ) -> Dict[str, Any]:
        """
        Publish content to a specific platform
        
        Note: This is a simulation. In production, this would integrate with
        actual platform APIs (WordPress REST API, Twitter API, etc.)
        
        Args:
            platform: Target platform
            content: Formatted content
            plan: Publishing plan
            project_id: Project ID
            
        Returns:
            Publishing result
        """
        self.logger.info(
            f"Publishing to {platform}",
            project_id=project_id,
            platform=platform
        )
        
        # Simulate API call
        result = {
            'success': True,
            'platform': platform,
            'published_at': datetime.utcnow().isoformat(),
            'content_id': f"{project_id}_{platform}",
            'url': f"https://{platform}.example.com/{project_id}",
            'status': 'published',
            'cost': 0.0,  # No direct cost for publishing
            'metadata': {
                'scheduled_time': plan.get('scheduled_time'),
                'platform_response': 'simulated_success'
            }
        }
        
        return result
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        hashtags = re.findall(r'#\w+', text)
        return hashtags
    
    def schedule_content(
        self,
        project_id: str,
        platforms: List[str],
        content: Dict[str, Any],
        publish_times: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Schedule content for future publishing
        
        Args:
            project_id: Project ID
            platforms: Target platforms
            content: Content to publish
            publish_times: Dictionary mapping platform to publish time
            
        Returns:
            Scheduling confirmation
        """
        schedule_info = {}
        
        for platform in platforms:
            publish_time = publish_times.get(platform)
            if not publish_time:
                continue
            
            schedule_info[platform] = {
                'scheduled_for': publish_time,
                'status': 'scheduled',
                'project_id': project_id
            }
        
        return {
            'project_id': project_id,
            'schedules': schedule_info,
            'total_scheduled': len(schedule_info)
        }
    
    def get_platform_analytics(
        self,
        project_id: str,
        platform: str,
        content_id: str
    ) -> Dict[str, Any]:
        """
        Get analytics for published content on a specific platform
        
        Args:
            project_id: Project ID
            platform: Platform name
            content_id: Content ID on the platform
            
        Returns:
            Analytics data
        """
        # Simulated analytics - in production, would call platform APIs
        return {
            'project_id': project_id,
            'platform': platform,
            'content_id': content_id,
            'metrics': {
                'views': 1523,
                'likes': 87,
                'shares': 34,
                'comments': 12,
                'clicks': 245,
                'engagement_rate': 0.089
            },
            'timestamp': datetime.utcnow().isoformat()
        }
