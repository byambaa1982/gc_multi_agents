"""
Media Processor - Optimizes and processes media files
"""

import io
import os
from typing import Dict, Any, Optional, Tuple
from PIL import Image as PILImage, ImageEnhance, ImageFilter
from pathlib import Path

from src.monitoring.logger import StructuredLogger


class MediaProcessor:
    """Handles media optimization and processing"""
    
    def __init__(self):
        """Initialize Media Processor"""
        self.logger = StructuredLogger(name="infrastructure.media_processor")
    
    # ==================== IMAGE PROCESSING ====================
    
    def optimize_image(
        self,
        image: PILImage.Image,
        target_format: str = 'JPEG',
        quality: int = 85,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        max_file_size_kb: Optional[int] = None
    ) -> PILImage.Image:
        """
        Optimize image for web delivery
        
        Args:
            image: PIL Image object
            target_format: Output format (JPEG, PNG, WEBP)
            quality: Compression quality (1-100)
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels
            max_file_size_kb: Maximum file size in KB
            
        Returns:
            Optimized PIL Image
        """
        original_size = image.size
        
        # Resize if dimensions specified
        if max_width or max_height:
            image = self._resize_image(image, max_width, max_height)
        
        # Convert color mode if needed
        if target_format == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
            # Convert to RGB for JPEG
            background = PILImage.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        elif target_format == 'PNG' and image.mode not in ('RGBA', 'RGB'):
            image = image.convert('RGBA')
        
        # Iteratively compress to meet file size requirement
        if max_file_size_kb:
            image = self._compress_to_size(image, target_format, max_file_size_kb * 1024, quality)
        
        self.logger.info(
            "Optimized image",
            original_size=original_size,
            new_size=image.size,
            format=target_format,
            quality=quality
        )
        
        return image
    
    def _resize_image(
        self,
        image: PILImage.Image,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        maintain_aspect: bool = True
    ) -> PILImage.Image:
        """Resize image maintaining aspect ratio"""
        width, height = image.size
        
        if not maintain_aspect:
            new_size = (max_width or width, max_height or height)
        else:
            # Calculate new size maintaining aspect ratio
            if max_width and max_height:
                ratio = min(max_width / width, max_height / height)
            elif max_width:
                ratio = max_width / width
            elif max_height:
                ratio = max_height / height
            else:
                return image
            
            new_size = (int(width * ratio), int(height * ratio))
        
        return image.resize(new_size, PILImage.Resampling.LANCZOS)
    
    def _compress_to_size(
        self,
        image: PILImage.Image,
        format: str,
        max_bytes: int,
        initial_quality: int = 95
    ) -> PILImage.Image:
        """Compress image to meet file size requirement"""
        quality = initial_quality
        
        while quality > 20:
            buffer = io.BytesIO()
            save_kwargs = {'format': format, 'quality': quality, 'optimize': True}
            
            if format == 'PNG':
                save_kwargs = {'format': format, 'optimize': True}
            
            image.save(buffer, **save_kwargs)
            size = buffer.tell()
            
            if size <= max_bytes:
                break
            
            quality -= 5
        
        return image
    
    def create_thumbnail(
        self,
        image: PILImage.Image,
        size: Tuple[int, int] = (300, 300),
        crop_to_fit: bool = False
    ) -> PILImage.Image:
        """
        Create thumbnail from image
        
        Args:
            image: Source image
            size: Thumbnail size (width, height)
            crop_to_fit: Whether to crop or fit with aspect ratio
            
        Returns:
            Thumbnail image
        """
        if crop_to_fit:
            # Crop to exact size
            img_ratio = image.width / image.height
            thumb_ratio = size[0] / size[1]
            
            if img_ratio > thumb_ratio:
                # Image is wider, crop width
                new_width = int(image.height * thumb_ratio)
                offset = (image.width - new_width) // 2
                crop_box = (offset, 0, offset + new_width, image.height)
            else:
                # Image is taller, crop height
                new_height = int(image.width / thumb_ratio)
                offset = (image.height - new_height) // 2
                crop_box = (0, offset, image.width, offset + new_height)
            
            thumbnail = image.crop(crop_box)
            thumbnail = thumbnail.resize(size, PILImage.Resampling.LANCZOS)
        else:
            # Fit within size maintaining aspect ratio
            thumbnail = image.copy()
            thumbnail.thumbnail(size, PILImage.Resampling.LANCZOS)
        
        return thumbnail
    
    def enhance_image(
        self,
        image: PILImage.Image,
        brightness: float = 1.0,
        contrast: float = 1.0,
        sharpness: float = 1.0,
        saturation: float = 1.0
    ) -> PILImage.Image:
        """
        Enhance image with adjustments
        
        Args:
            image: Source image
            brightness: Brightness factor (1.0 = original)
            contrast: Contrast factor (1.0 = original)
            sharpness: Sharpness factor (1.0 = original)
            saturation: Color saturation factor (1.0 = original)
            
        Returns:
            Enhanced image
        """
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)
        
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(sharpness)
        
        if saturation != 1.0:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(saturation)
        
        return image
    
    def apply_filter(
        self,
        image: PILImage.Image,
        filter_type: str = 'none'
    ) -> PILImage.Image:
        """
        Apply filter to image
        
        Args:
            image: Source image
            filter_type: Filter (none, blur, sharpen, edge_enhance, smooth)
            
        Returns:
            Filtered image
        """
        filters = {
            'blur': ImageFilter.BLUR,
            'sharpen': ImageFilter.SHARPEN,
            'edge_enhance': ImageFilter.EDGE_ENHANCE,
            'smooth': ImageFilter.SMOOTH,
            'detail': ImageFilter.DETAIL
        }
        
        if filter_type in filters:
            return image.filter(filters[filter_type])
        
        return image
    
    def convert_format(
        self,
        image: PILImage.Image,
        target_format: str,
        quality: int = 95
    ) -> bytes:
        """
        Convert image to different format
        
        Args:
            image: Source image
            target_format: Target format (JPEG, PNG, WEBP, GIF)
            quality: Quality for lossy formats
            
        Returns:
            Image bytes in new format
        """
        buffer = io.BytesIO()
        
        # Handle format-specific requirements
        if target_format.upper() == 'JPEG':
            if image.mode in ('RGBA', 'LA', 'P'):
                background = PILImage.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                image = background
            image.save(buffer, format='JPEG', quality=quality, optimize=True)
        elif target_format.upper() == 'WEBP':
            image.save(buffer, format='WEBP', quality=quality, method=6)
        else:
            image.save(buffer, format=target_format.upper())
        
        buffer.seek(0)
        return buffer.getvalue()
    
    # ==================== IMAGE BATCH PROCESSING ====================
    
    def batch_optimize_images(
        self,
        images: list,
        **kwargs
    ) -> list:
        """Optimize multiple images with same settings"""
        optimized = []
        for img in images:
            try:
                optimized.append(self.optimize_image(img, **kwargs))
            except Exception as e:
                self.logger.error(
                    f"Failed to optimize image: {e}",
                    error=str(e)
                )
                optimized.append(img)  # Use original if optimization fails
        
        return optimized
    
    def create_responsive_set(
        self,
        image: PILImage.Image,
        sizes: list = None
    ) -> Dict[str, PILImage.Image]:
        """
        Create responsive image set
        
        Args:
            image: Source image
            sizes: List of (width, name) tuples
            
        Returns:
            Dictionary of images by size name
        """
        if sizes is None:
            sizes = [
                (320, 'mobile'),
                (768, 'tablet'),
                (1024, 'desktop'),
                (1920, 'large')
            ]
        
        responsive_set = {}
        
        for width, name in sizes:
            if image.width > width:
                resized = self._resize_image(image, max_width=width)
                responsive_set[name] = resized
            else:
                responsive_set[name] = image.copy()
        
        return responsive_set
    
    # ==================== METADATA & ANALYSIS ====================
    
    def get_image_info(self, image: PILImage.Image) -> Dict[str, Any]:
        """Get comprehensive image information"""
        return {
            'dimensions': {
                'width': image.width,
                'height': image.height,
                'aspect_ratio': round(image.width / image.height, 2)
            },
            'mode': image.mode,
            'format': image.format,
            'size_bytes': len(image.tobytes()),
            'has_transparency': image.mode in ('RGBA', 'LA', 'P')
        }
    
    def estimate_file_size(
        self,
        image: PILImage.Image,
        format: str = 'JPEG',
        quality: int = 85
    ) -> int:
        """Estimate file size for given settings"""
        buffer = io.BytesIO()
        save_kwargs = {'format': format, 'quality': quality, 'optimize': True}
        
        if format == 'PNG':
            save_kwargs = {'format': format, 'optimize': True}
        
        image.save(buffer, **save_kwargs)
        return buffer.tell()
    
    # ==================== UTILITY FUNCTIONS ====================
    
    def calculate_optimal_quality(
        self,
        image: PILImage.Image,
        target_size_kb: int,
        format: str = 'JPEG'
    ) -> int:
        """Calculate optimal quality to meet target file size"""
        low, high = 1, 100
        best_quality = 85
        
        while low <= high:
            mid = (low + high) // 2
            size = self.estimate_file_size(image, format, mid)
            
            if size <= target_size_kb * 1024:
                best_quality = mid
                low = mid + 1
            else:
                high = mid - 1
        
        return best_quality
    
    def get_dominant_colors(
        self,
        image: PILImage.Image,
        num_colors: int = 5
    ) -> list:
        """Extract dominant colors from image"""
        # Resize for faster processing
        small_image = image.copy()
        small_image.thumbnail((100, 100))
        
        # Convert to RGB if needed
        if small_image.mode != 'RGB':
            small_image = small_image.convert('RGB')
        
        # Get color palette
        try:
            from collections import Counter
            pixels = list(small_image.getdata())
            counter = Counter(pixels)
            most_common = counter.most_common(num_colors)
            
            return [
                {'rgb': color, 'hex': '#{:02x}{:02x}{:02x}'.format(*color)}
                for color, _ in most_common
            ]
        except Exception as e:
            self.logger.warning(f"Could not extract colors: {e}")
            return []
