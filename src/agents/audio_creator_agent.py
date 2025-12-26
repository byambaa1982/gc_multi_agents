"""
Audio Creator Agent - Generates podcast scripts and manages audio content creation
"""

import json
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent


class AudioCreatorAgent(BaseAgent):
    """Agent that creates audio content including podcast scripts and narration"""
    
    def __init__(self):
        """Initialize Audio Creator Agent"""
        super().__init__(agent_name='audio_creator')
        
    def _execute_internal(self, **kwargs) -> Dict[str, Any]:
        """
        Create audio content including scripts and metadata
        
        Args:
            topic: Audio content topic
            content: Related content to convert to audio (optional)
            duration: Target duration in minutes (default: 10-30)
            audio_type: Type (podcast, narration, audiobook, meditation, interview)
            tone: Audio tone (conversational, professional, energetic, calm)
            num_speakers: Number of speakers (1-4, default: 1)
            include_music_cues: Whether to include background music suggestions
            include_sound_effects: Whether to suggest sound effects
            target_audience: Target audience description
            
        Returns:
            Audio creation package with script, timing, and production notes
        """
        topic = kwargs.get('topic')
        content = kwargs.get('content', '')
        duration = kwargs.get('duration', 15)  # minutes
        audio_type = kwargs.get('audio_type', 'podcast')
        tone = kwargs.get('tone', 'conversational')
        num_speakers = kwargs.get('num_speakers', 1)
        include_music_cues = kwargs.get('include_music_cues', True)
        include_sound_effects = kwargs.get('include_sound_effects', False)
        target_audience = kwargs.get('target_audience', 'general')
        
        if not topic:
            raise ValueError("Topic is required for audio creation")
        
        # Validate inputs
        if num_speakers < 1 or num_speakers > 4:
            raise ValueError("num_speakers must be between 1 and 4")
        
        if duration < 1:
            duration = 1
        elif duration > 120:  # 2 hours max
            duration = 120
        
        self.logger.info(
            "Starting audio creation",
            agent=self.agent_name,
            topic=topic,
            audio_type=audio_type,
            duration=duration
        )
        
        # Generate audio script
        script = self._generate_audio_script(
            topic=topic,
            content=content,
            duration=duration,
            audio_type=audio_type,
            tone=tone,
            num_speakers=num_speakers,
            target_audience=target_audience
        )
        
        # Calculate cost
        cost = self._calculate_cost("", script.get('raw_response', ''))
        self.logger.cost_tracking(
            project_id=kwargs.get('project_id', 'unknown'),
            operation='audio_script_generation',
            cost=cost,
            model=self.model_name
        )
        
        result = {
            'topic': topic,
            'audio_type': audio_type,
            'duration_minutes': duration,
            'num_speakers': num_speakers,
            'script': script,
            'cost': cost,
            'metadata': {
                'tone': tone,
                'target_audience': target_audience,
                'has_music_cues': include_music_cues,
                'has_sound_effects': include_sound_effects
            }
        }
        
        # Add production elements if requested
        if include_music_cues:
            music_cues = self._generate_music_cues(script['segments'], tone)
            result['music_cues'] = music_cues
        
        if include_sound_effects:
            sound_effects = self._suggest_sound_effects(script['segments'], audio_type)
            result['sound_effects'] = sound_effects
        
        # Generate voice characteristics for TTS
        voice_config = self._generate_voice_configuration(num_speakers, tone, audio_type)
        result['voice_configuration'] = voice_config
        
        return result
    
    def _generate_audio_script(
        self,
        topic: str,
        content: str,
        duration: int,
        audio_type: str,
        tone: str,
        num_speakers: int,
        target_audience: str
    ) -> Dict[str, Any]:
        """Generate audio script with timing and speaker assignments"""
        
        # Calculate approximate word count (average speaking rate: 150 words/minute)
        target_word_count = duration * 150
        
        speaker_setup = ""
        if num_speakers == 1:
            speaker_setup = "Single narrator/host"
        elif num_speakers == 2:
            speaker_setup = "Host and guest, or co-hosts"
        else:
            speaker_setup = f"{num_speakers} speakers (host + guests/panel)"
        
        # Build content context
        content_context = f"Source Content:\n{content[:1500]}" if content else ""
        
        prompt = f"""Create a detailed {audio_type} script for audio content.

Topic: {topic}
Duration: {duration} minutes
Target Word Count: ~{target_word_count} words
Tone: {tone}
Speakers: {speaker_setup}
Target Audience: {target_audience}

{content_context}

Create a comprehensive audio script including:
1. Opening (hook and introduction)
2. Main content (broken into segments with timing)
3. Transitions between segments
4. Closing (recap and call-to-action)

Return as JSON:
{{
    "title": "Episode/Audio title",
    "description": "Brief description",
    "speakers": [
        {{
            "id": "speaker1",
            "name": "Host/Speaker Name",
            "role": "host/guest/narrator"
        }}
    ],
    "opening": {{
        "duration_minutes": 1.0,
        "speaker": "speaker1",
        "script": "Opening text",
        "notes": "Delivery notes"
    }},
    "segments": [
        {{
            "segment_number": 1,
            "title": "Segment title",
            "duration_minutes": 3.0,
            "content": [
                {{
                    "speaker": "speaker1",
                    "text": "What the speaker says",
                    "notes": "Tone/delivery notes"
                }}
            ]
        }}
    ],
    "closing": {{
        "duration_minutes": 1.0,
        "speaker": "speaker1",
        "script": "Closing text",
        "notes": "Delivery notes"
    }},
    "total_duration_minutes": {duration},
    "word_count": {target_word_count},
    "show_notes": "Episode notes/description",
    "keywords": ["keyword1", "keyword2"]
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
                'speakers': [{'id': 'speaker1', 'name': 'Host', 'role': 'host'}],
                'opening': {'duration_minutes': 1, 'speaker': 'speaker1', 'script': '', 'notes': ''},
                'segments': [],
                'closing': {'duration_minutes': 1, 'speaker': 'speaker1', 'script': '', 'notes': ''},
                'total_duration_minutes': duration,
                'word_count': target_word_count,
                'show_notes': '',
                'keywords': [],
                'raw_response': response
            }
    
    def _generate_music_cues(
        self,
        segments: List[Dict],
        tone: str
    ) -> List[Dict[str, Any]]:
        """Generate background music and transition cues"""
        
        music_cues = []
        
        # Opening music
        music_cues.append({
            'position': 'opening',
            'type': 'intro_music',
            'duration_seconds': 10,
            'style': f'{tone} intro theme',
            'volume': 'full then fade under voice',
            'notes': 'Energetic opening, establishes mood'
        })
        
        # Segment transitions
        for i, segment in enumerate(segments):
            if i > 0:  # Not first segment
                music_cues.append({
                    'position': f'transition_to_segment_{i+1}',
                    'type': 'transition',
                    'duration_seconds': 3,
                    'style': 'brief musical sting',
                    'volume': 'medium',
                    'notes': 'Smooth transition between topics'
                })
        
        # Background music during segments (optional)
        music_cues.append({
            'position': 'background',
            'type': 'ambient_background',
            'duration_seconds': -1,  # Continuous
            'style': f'subtle {tone} ambient',
            'volume': 'very low (10-15%)',
            'notes': 'Optional light background during speech'
        })
        
        # Closing music
        music_cues.append({
            'position': 'closing',
            'type': 'outro_music',
            'duration_seconds': 15,
            'style': f'{tone} outro theme',
            'volume': 'fade in under voice, full after speech ends',
            'notes': 'Matches intro theme, provides closure'
        })
        
        return music_cues
    
    def _suggest_sound_effects(
        self,
        segments: List[Dict],
        audio_type: str
    ) -> List[Dict[str, Any]]:
        """Suggest sound effects based on content"""
        
        # For now, return generic suggestions
        # In production, this could use AI to analyze script content
        
        sound_effects = []
        
        if audio_type == 'podcast':
            sound_effects.extend([
                {
                    'trigger': 'key_point',
                    'effect': 'subtle notification sound',
                    'usage': 'Emphasize important points',
                    'volume': 'low'
                },
                {
                    'trigger': 'transition',
                    'effect': 'whoosh or swoosh',
                    'usage': 'Topic transitions',
                    'volume': 'medium-low'
                }
            ])
        elif audio_type == 'narration' or audio_type == 'audiobook':
            sound_effects.extend([
                {
                    'trigger': 'chapter_break',
                    'effect': 'gentle chime',
                    'usage': 'Chapter or section breaks',
                    'volume': 'medium'
                }
            ])
        
        return sound_effects
    
    def _generate_voice_configuration(
        self,
        num_speakers: int,
        tone: str,
        audio_type: str
    ) -> List[Dict[str, Any]]:
        """Generate voice characteristics for text-to-speech"""
        
        # Google Cloud TTS voices configuration
        voice_configs = []
        
        # Map tone to speaking rate and pitch
        tone_mapping = {
            'conversational': {'rate': 1.0, 'pitch': 0.0},
            'professional': {'rate': 0.95, 'pitch': -1.0},
            'energetic': {'rate': 1.1, 'pitch': 2.0},
            'calm': {'rate': 0.85, 'pitch': -2.0}
        }
        
        settings = tone_mapping.get(tone, tone_mapping['conversational'])
        
        # Voice options for different speakers
        voice_options = [
            {'name': 'en-US-Neural2-J', 'gender': 'MALE', 'description': 'Natural male voice'},
            {'name': 'en-US-Neural2-F', 'gender': 'FEMALE', 'description': 'Natural female voice'},
            {'name': 'en-US-Neural2-A', 'gender': 'MALE', 'description': 'Deep male voice'},
            {'name': 'en-US-Neural2-C', 'gender': 'FEMALE', 'description': 'Warm female voice'}
        ]
        
        for i in range(num_speakers):
            voice = voice_options[i % len(voice_options)]
            voice_configs.append({
                'speaker_id': f'speaker{i+1}',
                'voice_name': voice['name'],
                'language_code': 'en-US',
                'ssml_gender': voice['gender'],
                'speaking_rate': settings['rate'],
                'pitch': settings['pitch'],
                'volume_gain_db': 0.0,
                'description': voice['description']
            })
        
        return voice_configs
    
    def generate_podcast_metadata(
        self,
        script: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate podcast metadata and show notes"""
        
        prompt = f"""Create comprehensive podcast metadata and show notes.

Title: {script.get('title', '')}
Description: {script.get('description', '')}
Keywords: {', '.join(script.get('keywords', []))}

Generate:
1. SEO-optimized podcast title
2. Compelling episode description
3. Detailed show notes with timestamps
4. Episode tags/categories
5. Social media post suggestions

Return as JSON:
{{
    "title": "...",
    "description": "...",
    "show_notes": "Formatted show notes with timestamps",
    "tags": ["tag1", "tag2"],
    "category": "...",
    "social_posts": {{
        "twitter": "...",
        "linkedin": "..."
    }}
}}"""

        response = self._call_model(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                'title': script.get('title', ''),
                'description': script.get('description', ''),
                'show_notes': script.get('show_notes', ''),
                'tags': script.get('keywords', []),
                'category': 'Education',
                'social_posts': {}
            }
    
    def create_narration_from_text(
        self,
        text: str,
        tone: str = 'professional',
        max_duration_minutes: int = 30
    ) -> Dict[str, Any]:
        """Convert written content into narration script"""
        
        # Estimate reading time (150 words per minute)
        word_count = len(text.split())
        estimated_duration = word_count / 150
        
        if estimated_duration > max_duration_minutes:
            # Need to summarize
            prompt = f"""Convert this text into a {max_duration_minutes}-minute narration script.
Maintain key points but make it concise and engaging for audio.

Original text ({word_count} words):
{text[:3000]}

Create a narration-friendly version with:
1. Natural speech patterns
2. Clear transitions
3. Appropriate pacing
4. Emphasis markers for important points

Target: ~{max_duration_minutes * 150} words"""
            
            narration_text = self._call_model(prompt)
        else:
            narration_text = text
        
        return {
            'narration_text': narration_text,
            'original_word_count': word_count,
            'narration_word_count': len(narration_text.split()),
            'estimated_duration_minutes': len(narration_text.split()) / 150,
            'tone': tone
        }
