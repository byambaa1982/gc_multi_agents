"""
Generate a Cartoon Image and Store It

This example demonstrates how to:
1. Generate a cartoon image using ImageGeneratorAgent
2. Optimize the image using MediaProcessor
3. Store it in Google Cloud Storage
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from io import BytesIO

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.image_generator_agent import ImageGeneratorAgent
from src.infrastructure.media_processor import MediaProcessor
from src.infrastructure.storage_manager import CloudStorageManager
from src.monitoring.logger import StructuredLogger


def main():
    """Generate and store a cartoon image"""
    # Load environment variables
    load_dotenv()
    
    logger = StructuredLogger("CartoonGenerator")
    
    # Get GCP project details
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    bucket_name = os.getenv('GCS_BUCKET_NAME')
    
    if not project_id:
        logger.error("GOOGLE_CLOUD_PROJECT not set in .env file")
        return 1
    
    if not bucket_name:
        logger.warning("GCS_BUCKET_NAME not set, will skip storage step")
    
    logger.info("="*70)
    logger.info("Cartoon Image Generator & Storage")
    logger.info("="*70)
    logger.info(f"Project: {project_id}")
    logger.info(f"Bucket: {bucket_name or 'Not configured'}")
    
    # Step 1: Generate cartoon image
    logger.info("\n" + "="*70)
    logger.info("Step 1: Generating Cartoon Image")
    logger.info("="*70)
    
    # Define your cartoon description
    cartoon_prompt = (
        "A cheerful cartoon character, friendly robot with big eyes, "
        "colorful design, cute and playful, digital art style, "
        "clean background, vibrant colors"
    )
    
    logger.info(f"Prompt: {cartoon_prompt}")
    
    # Initialize Image Generator Agent
    image_agent = ImageGeneratorAgent()
    
    # Generate the image
    result = image_agent.execute(
        project_id=project_id,
        prompts=[cartoon_prompt],
        number_of_images=1,
        aspect_ratio="1:1",  # Square format for cartoon
        content_type="social"
    )
    
    if not result or 'images' not in result or len(result['images']) == 0:
        logger.error("Failed to generate image")
        return 1
    
    # Get the generated image (it's already a PIL Image object)
    image_info = result['images'][0]
    image = image_info['image']  # PIL Image object
    
    logger.info(f"✓ Generated image: {image.size}, mode: {image.mode}")
    logger.info(f"  Prompt used: {image_info['prompt'][:50]}...")
    
    # Step 2: Optimize the image (optional)
    logger.info("\n" + "="*70)
    logger.info("Step 2: Optimizing Image")
    logger.info("="*70)
    
    processor = MediaProcessor()
    
    # Optimize for web use (PNG is better for cartoons)
    optimized_image = processor.optimize_image(
        image,
        target_format='PNG',
        max_width=1024,
        quality=85
    )
    
    # Convert to bytes for storage
    original_buffer = BytesIO()
    image.save(original_buffer, format='PNG')
    original_bytes = original_buffer.getvalue()
    
    optimized_buffer = BytesIO()
    optimized_image.save(optimized_buffer, format='PNG')
    optimized_data = optimized_buffer.getvalue()
    
    logger.info(f"✓ Optimized: {len(original_bytes)} → {len(optimized_data)} bytes")
    if len(optimized_data) < len(original_bytes):
        logger.info(f"  Reduction: {((len(original_bytes) - len(optimized_data)) / len(original_bytes) * 100):.1f}%")
    else:
        logger.info(f"  Size maintained for quality")
    
    # Create thumbnail
    thumbnail_image = processor.create_thumbnail(
        optimized_image,
        size=(300, 300)
    )
    
    # Convert thumbnail to bytes
    thumb_buffer = BytesIO()
    thumbnail_image.save(thumb_buffer, format='PNG')
    thumbnail_data = thumb_buffer.getvalue()
    logger.info(f"✓ Created thumbnail: {len(thumbnail_data)} bytes")
    
    # Step 3: Store in Google Cloud Storage
    if bucket_name:
        logger.info("\n" + "="*70)
        logger.info("Step 3: Storing in Google Cloud Storage")
        logger.info("="*70)
        
        storage_manager = CloudStorageManager(
            project_id=project_id,
            bucket_name=bucket_name
        )
        
        # Upload main image
        main_path = "cartoons/robot_character.png"
        upload_result = storage_manager.upload_file(
            file_obj=BytesIO(optimized_data),
            blob_path=main_path,
            content_type='image/png'
        )
        logger.info(f"✓ Uploaded main image: {main_path}")
        logger.info(f"  Public URL: {upload_result['public_url']}")
        if upload_result['signed_url']:
            logger.info(f"  Signed URL (7 days): {upload_result['signed_url'][:80]}...")
        
        # Upload thumbnail
        thumb_path = "cartoons/thumbnails/robot_character.png"
        thumb_result = storage_manager.upload_file(
            file_obj=BytesIO(thumbnail_data),
            blob_path=thumb_path,
            content_type='image/png'
        )
        logger.info(f"✓ Uploaded thumbnail: {thumb_path}")
        logger.info(f"  Public URL: {thumb_result['public_url']}")
        
        # List files in cartoons folder
        logger.info("\nFiles in 'cartoons/' folder:")
        files = storage_manager.list_files(prefix="cartoons/")
        for file in files:
            logger.info(f"  - {file}")
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("✓ Complete! Your cartoon has been generated and stored")
    logger.info("="*70)
    logger.info(f"Generation cost: ${result.get('cost', 0):.4f}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
