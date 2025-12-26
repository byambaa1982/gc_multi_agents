"""
Video Creator Agent - Generates video scripts and manages video content creation
"""

import json
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent


class VideoCreatorAgent(BaseAgent):
    """Agent that creates video scripts and manages video content generation"""
    
    def __init__(self):
        """Initialize Video Creator Agent"""
        super().__init__(agent_name='video_creator')
        
    def _execute_internal(self, **kwargs) -> Dict[str, Any]:
        """
        Create video content including scripts, scenes, and metadata
        
        Args:
            topic: Video topic
            content: Related content (optional, e.g., blog post to convert)
            duration: Target duration in seconds (default: 60-180)
            video_type: Type (explainer, tutorial, promo, review, story)
            tone: Video tone (professional, casual, energetic, calm)
            include_voiceover: Whether to generate voiceover script
            include_visuals: Whether to suggest visual elements
            target_platform: Platform (youtube, tiktok, instagram, linkedin)
            
        Returns:
            Video creation package with script, scenes, and metadata
        """
        topic = kwargs.get('topic')
        content = kwargs.get('content', '')
        duration = kwargs.get('duration', 120)
        video_type = kwargs.get('video_type', 'explainer')
        tone = kwargs.get('tone', 'professional')
        include_voiceover = kwargs.get('include_voiceover', True)
        include_visuals = kwargs.get('include_visuals', True)
        target_platform = kwargs.get('target_platform', 'youtube')
        
        if not topic:
            raise ValueError("Topic is required for video creation")
        
        # Validate duration
        if duration < 15:
            duration = 15
        elif duration > 600:  # 10 minutes max
            duration = 600
        
        self.logger.info(
            "Starting video creation",
            agent=self.agent_name,
            topic=topic,
            video_type=video_type,
            duration=duration
        )
        
        # Generate video script
        script = self._generate_video_script(
            topic=topic,
            content=content,
            duration=duration,
            video_type=video_type,
            tone=tone,
            target_platform=target_platform
        )
        
        # Calculate cost
        cost = self._calculate_cost("", script.get('raw_response', ''))
        self.logger.cost_tracking(
            project_id=kwargs.get('project_id', 'unknown'),
            operation='video_script_generation',
            cost=cost,
            model=self.model_name
        )
        
        result = {
            'topic': topic,
            'video_type': video_type,
            'duration': duration,
            'target_platform': target_platform,
            'script': script,
            'cost': cost,
            'metadata': {
                'tone': tone,
                'has_voiceover': include_voiceover,
                'has_visual_suggestions': include_visuals
            }
        }
        
        # Generate voiceover script if requested
        if include_voiceover:
            voiceover = self._generate_voiceover_script(script['scenes'])
            result['voiceover'] = voiceover
        
        # Generate visual suggestions if requested
        if include_visuals:
            visuals = self._suggest_visual_elements(script['scenes'], video_type)
            result['visual_suggestions'] = visuals
        
        return result
    
    def _generate_video_script(
        self,
        topic: str,
        content: str,
        duration: int,
        video_type: str,
        tone: str,
        target_platform: str
    ) -> Dict[str, Any]:
        """Generate video script with scenes and timing"""
        
        platform_specs = {
            'youtube': {'optimal_duration': '8-12 min', 'hook_time': '0-15s'},
            'tiktok': {'optimal_duration': '15-60s', 'hook_time': '0-3s'},
            'instagram': {'optimal_duration': '30-90s', 'hook_time': '0-3s'},
            'linkedin': {'optimal_duration': '30-120s', 'hook_time': '0-5s'}
        }
        
        specs = platform_specs.get(target_platform, platform_specs['youtube'])
        
        # Build content context
        content_context = f"Related Content:\n{content[:1000]}" if content else ""
        
        prompt = f"""Create a detailed video script for {video_type} video.

Topic: {topic}
Duration: {duration} seconds
Tone: {tone}
Platform: {target_platform} (Optimal: {specs['optimal_duration']}, Hook: {specs['hook_time']})

{content_context}

Create a comprehensive video script including:
1. Hook (first few seconds to grab attention)
2. Introduction
3. Main content (broken into scenes)
4. Call-to-action
5. Outro

Return as JSON:
{{
    "title": "Video title",
    "description": "Brief description",
    "hook": {{
        "duration": seconds,
        "script": "Hook text",
        "visual_notes": "What to show"
    }},
    "scenes": [
        {{
            "scene_number": 1,
            "duration": seconds,
            "script": "Scene narration",
            "visual_notes": "Visual description",
            "key_points": ["point1", "point2"]
        }}
    ],
    "call_to_action": "CTA text",
    "total_duration": {duration},
    "tags": ["tag1", "tag2"],
    "thumbnail_suggestion": "Thumbnail idea"
}}"""

        response = self._call_model(prompt)
        
        try:
            script_data = json.loads(response)
            script_data['raw_response'] = response
            return script_data
        except json.JSONDecodeError as e:
            self.logger.warning(
                f"Failed to parse JSON response: {e}",
                agent=self.agent_name
            )
            # Return basic structure
            return {
                'title': topic,
                'description': topic,
                'hook': {'duration': 5, 'script': '', 'visual_notes': ''},
                'scenes': [],
                'call_to_action': '',
                'total_duration': duration,
                'tags': [],
                'thumbnail_suggestion': '',
                'raw_response': response
            }
    
    def _generate_voiceover_script(self, scenes: List[Dict]) -> Dict[str, Any]:
        """Generate formatted voiceover script from scenes"""
        
        voiceover_lines = []
        total_duration = 0
        
        for scene in scenes:
            scene_script = scene.get('script', '')
            scene_duration = scene.get('duration', 10)
            
            voiceover_lines.append({
                'scene': scene.get('scene_number', 0),
                'text': scene_script,
                'duration': scene_duration,
                'start_time': total_duration,
                'end_time': total_duration + scene_duration
            })
            
            total_duration += scene_duration
        
        return {
            'lines': voiceover_lines,
            'total_duration': total_duration,
            'word_count': sum(len(line['text'].split()) for line in voiceover_lines),
            'estimated_speaking_rate': 'moderate'  # Can be customized
        }
    
    def _suggest_visual_elements(
        self,
        scenes: List[Dict],
        video_type: str
    ) -> List[Dict[str, Any]]:
        """Suggest visual elements for each scene"""
        
        prompt = f"""Suggest specific visual elements for this {video_type} video.

Scenes:
{json.dumps(scenes, indent=2)}

For each scene, suggest:
1. B-roll footage ideas
2. Graphics/text overlays
3. Transitions
4. Color scheme
5. Camera angles/movements

Return as JSON array:
[
    {{
        "scene_number": 1,
        "b_roll": ["suggestion1", "suggestion2"],
        "graphics": ["text overlay idea"],
        "transition": "fade/cut/wipe",
        "color_palette": ["#color1", "#color2"],
        "camera": "close-up/wide/pan"
    }}
]"""

        response = self._call_model(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Return basic suggestions
            return [
                {
                    'scene_number': scene.get('scene_number', i),
                    'b_roll': ['Stock footage'],
                    'graphics': ['Title overlay'],
                    'transition': 'fade',
                    'color_palette': ['#000000', '#FFFFFF'],
                    'camera': 'medium'
                }
                for i, scene in enumerate(scenes, 1)
            ]
    
    def generate_video_metadata(
        self,
        script: Dict[str, Any],
        platform: str = 'youtube'
    ) -> Dict[str, Any]:
        """Generate platform-specific metadata for video"""
        
        prompt = f"""Create optimized metadata for {platform} video.

Title: {script.get('title', '')}
Description: {script.get('description', '')}
Tags: {', '.join(script.get('tags', []))}

Generate:
1. SEO-optimized title (platform-specific character limits)
2. Compelling description with keywords
3. Relevant tags/hashtags
4. Category suggestion
5. Thumbnail text suggestion

Return as JSON:
{{
    "optimized_title": "...",
    "description": "...",
    "tags": ["tag1", "tag2"],
    "category": "...",
    "thumbnail_text": "...",
    "hashtags": ["#hash1", "#hash2"]
}}"""

        response = self._call_model(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                'optimized_title': script.get('title', ''),
                'description': script.get('description', ''),
                'tags': script.get('tags', []),
                'category': 'Education',
                'thumbnail_text': '',
                'hashtags': []
            }
    
    def create_storyboard_description(
        self,
        scenes: List[Dict[str, Any]]
    ) -> List[str]:
        """Create image generation prompts for storyboard frames"""
        
        storyboard_prompts = []
        
        for scene in scenes:
            visual_notes = scene.get('visual_notes', '')
            scene_script = scene.get('script', '')
            
            # Create detailed prompt for image generation
            prompt = f"""Professional video storyboard frame: {visual_notes}. 
Context: {scene_script[:100]}. 
Cinematic composition, clear visual storytelling, professional lighting."""
            
            storyboard_prompts.append(prompt)
        
        return storyboard_prompts
