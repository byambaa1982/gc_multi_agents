"""
Image Generator Agent - Creates visual content using Vertex AI Imagen
"""

import base64
import io
import os
from typing import Dict, Any, List, Optional
from PIL import Image as PILImage

import vertexai
from vertexai.preview.vision_models import ImageGenerationModel, ImageGenerationResponse

from .base_agent import BaseAgent


class ImageGeneratorAgent(BaseAgent):
    """Agent that generates images using Vertex AI Imagen"""
    
    def __init__(self):
        """Initialize Image Generator Agent"""
        super().__init__(agent_name='image_generator')
        
        # Initialize Imagen model
        self.imagen_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
        
    def _execute_internal(self, **kwargs) -> Dict[str, Any]:
        """
        Generate images from text descriptions
        
        Args:
            prompts: Single prompt string or list of prompts
            negative_prompt: What to avoid in the image (optional)
            number_of_images: Number of images to generate per prompt (1-4)
            aspect_ratio: Aspect ratio (1:1, 9:16, 16:9, 4:3, 3:4)
            safety_filter_level: Safety filter (block_most, block_some, block_few)
            person_generation: Allow person generation (allow_adult, allow_all, dont_allow)
            content_type: Type of content (blog, social, hero, thumbnail, infographic)
            
        Returns:
            Dictionary with generated images and metadata
        """
        prompts = kwargs.get('prompts')
        negative_prompt = kwargs.get('negative_prompt', '')
        number_of_images = kwargs.get('number_of_images', 1)
        aspect_ratio = kwargs.get('aspect_ratio', '1:1')
        safety_filter_level = kwargs.get('safety_filter_level', 'block_some')
        person_generation = kwargs.get('person_generation', 'allow_adult')
        content_type = kwargs.get('content_type', 'blog')
        
        # Validate inputs
        if not prompts:
            raise ValueError("At least one prompt is required")
        
        # Convert single prompt to list
        if isinstance(prompts, str):
            prompts = [prompts]
        
        # Validate parameters
        if number_of_images < 1 or number_of_images > 4:
            raise ValueError("number_of_images must be between 1 and 4")
        
        valid_aspect_ratios = ['1:1', '9:16', '16:9', '4:3', '3:4']
        if aspect_ratio not in valid_aspect_ratios:
            raise ValueError(f"aspect_ratio must be one of {valid_aspect_ratios}")
        
        self.logger.info(
            "Starting image generation",
            agent=self.agent_name,
            num_prompts=len(prompts),
            number_of_images=number_of_images,
            aspect_ratio=aspect_ratio
        )
        
        all_generated_images = []
        total_cost = 0.0
        
        # Generate images for each prompt
        for prompt_idx, prompt in enumerate(prompts):
            self.logger.info(
                f"Generating images for prompt {prompt_idx + 1}/{len(prompts)}",
                agent=self.agent_name,
                prompt=prompt[:100]  # Log first 100 chars
            )
            
            try:
                # Generate images
                images = self._generate_images(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    number_of_images=number_of_images,
                    aspect_ratio=aspect_ratio,
                    safety_filter_level=safety_filter_level,
                    person_generation=person_generation
                )
                
                # Calculate cost (approximate - $0.02 per image for Imagen 3)
                image_cost = 0.02 * number_of_images
                total_cost += image_cost
                
                # Process generated images
                for img_idx, image in enumerate(images):
                    image_data = {
                        'prompt_index': prompt_idx,
                        'image_index': img_idx,
                        'prompt': prompt,
                        'negative_prompt': negative_prompt,
                        'image': image,
                        'aspect_ratio': aspect_ratio,
                        'content_type': content_type,
                        'metadata': {
                            'model': 'imagen-3.0-generate-001',
                            'safety_filter': safety_filter_level,
                            'person_generation': person_generation
                        }
                    }
                    all_generated_images.append(image_data)
                
            except Exception as e:
                self.logger.error(
                    f"Failed to generate images for prompt {prompt_idx + 1}",
                    agent=self.agent_name,
                    error=str(e)
                )
                # Continue with other prompts
                continue
        
        # Log cost
        self.logger.cost_tracking(
            project_id=kwargs.get('project_id', 'unknown'),
            operation='image_generation',
            cost=total_cost,
            model='imagen-3.0-generate-001'
        )
        
        return {
            'images': all_generated_images,
            'total_images': len(all_generated_images),
            'prompts_processed': len(prompts),
            'cost': total_cost,
            'content_type': content_type,
            'metadata': {
                'aspect_ratio': aspect_ratio,
                'number_of_images_per_prompt': number_of_images,
                'safety_filter': safety_filter_level
            }
        }
    
    def _generate_images(
        self,
        prompt: str,
        negative_prompt: str = '',
        number_of_images: int = 1,
        aspect_ratio: str = '1:1',
        safety_filter_level: str = 'block_some',
        person_generation: str = 'allow_adult'
    ) -> List[PILImage.Image]:
        """
        Generate images using Imagen model
        
        Args:
            prompt: Image generation prompt
            negative_prompt: Negative prompt
            number_of_images: Number of images to generate
            aspect_ratio: Image aspect ratio
            safety_filter_level: Safety filter level
            person_generation: Person generation setting
            
        Returns:
            List of PIL Image objects
        """
        response = self.imagen_model.generate_images(
            prompt=prompt,
            negative_prompt=negative_prompt,
            number_of_images=number_of_images,
            aspect_ratio=aspect_ratio,
            safety_filter_level=safety_filter_level,
            person_generation=person_generation,
            add_watermark=False
        )
        
        images = []
        for image in response.images:
            # Convert to PIL Image
            pil_image = PILImage.open(io.BytesIO(image._image_bytes))
            images.append(pil_image)
        
        return images
    
    def enhance_prompt(self, basic_prompt: str, content_type: str = 'blog') -> str:
        """
        Enhance a basic image prompt using AI
        
        Args:
            basic_prompt: Basic image description
            content_type: Type of content (blog, social, hero, etc.)
            
        Returns:
            Enhanced prompt
        """
        enhancement_prompt = f"""You are an expert at writing prompts for image generation AI.
        
Given a basic image description, enhance it to create a detailed, high-quality prompt for Imagen AI.

Content Type: {content_type}

Basic Description: {basic_prompt}

Create an enhanced prompt that:
1. Adds specific visual details (lighting, composition, style)
2. Specifies artistic quality and technical aspects
3. Includes relevant context for the content type
4. Maintains clarity and coherence

Enhanced prompt (max 500 characters):"""

        enhanced = self._call_model(enhancement_prompt)
        return enhanced.strip()
    
    def suggest_images_for_content(
        self, 
        content: str, 
        title: str,
        content_type: str = 'blog',
        num_suggestions: int = 3
    ) -> List[str]:
        """
        Suggest image prompts based on content
        
        Args:
            content: The content text
            title: Content title
            content_type: Type of content
            num_suggestions: Number of image suggestions
            
        Returns:
            List of image prompts
        """
        suggestion_prompt = f"""Analyze this content and suggest {num_suggestions} image prompts for Imagen AI.

Title: {title}
Content Type: {content_type}

Content (first 2000 chars):
{content[:2000]}

Generate {num_suggestions} detailed image prompts that would complement this content.
Each prompt should be specific, visually descriptive, and suitable for professional use.

Return as JSON:
{{
    "suggestions": [
        {{"prompt": "...", "purpose": "hero image"}},
        {{"prompt": "...", "purpose": "supporting visual"}},
        ...
    ]
}}"""

        response = self._call_model(suggestion_prompt)
        
        try:
            import json
            suggestions_data = json.loads(response)
            return [s['prompt'] for s in suggestions_data.get('suggestions', [])]
        except:
            # Fallback: extract lines
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            return lines[:num_suggestions]
