"""
Direct test of workflow with image generation
"""
import os
from dotenv import load_dotenv
from src.orchestration import ContentGenerationWorkflow

# Load environment variables
load_dotenv()

def test_workflow():
    """Test workflow directly with image generation"""
    
    print("Testing workflow with image generation...")
    print("=" * 60)
    
    # Initialize workflow
    workflow = ContentGenerationWorkflow()
    
    # Generate content with images
    result = workflow.generate_content(
        topic="cute puppy playing in park",
        tone="friendly",
        target_word_count=800,
        generate_images=True
    )
    
    print("\n" + "=" * 60)
    print("RESULT:")
    print("=" * 60)
    print(f"Success: {result.get('success')}")
    print(f"Project ID: {result.get('project_id')}")
    
    if result.get('content'):
        print(f"Word Count: {result['content'].get('word_count')}")
        
    if result.get('media_urls'):
        print(f"\nMedia URLs:")
        print(f"  Images: {result['media_urls'].get('image', [])}")
        print(f"  Videos: {result['media_urls'].get('video', [])}")
        
    if result.get('project'):
        costs = result['project'].get('costs', {})
        print(f"\nTotal Cost: ${costs.get('total', 0):.4f}")
        
        if 'media' in result['project']:
            print(f"\nStored Media:")
            media = result['project']['media']
            print(f"  Main Image: {media.get('main_image', 'None')}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_workflow()
