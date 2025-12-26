"""
Generate Content with Media - Complete Phase 3 Example

This example demonstrates the full Phase 3 workflow:
1. Generate blog post content
2. Create featured image
3. Generate video script
4. Create podcast script
5. Optimize and store all media
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.research_agent import ResearchAgent
from src.agents.content_agent import ContentGeneratorAgent
from src.agents.image_generator_agent import ImageGeneratorAgent
from src.agents.video_creator_agent import VideoCreatorAgent
from src.agents.audio_creator_agent import AudioCreatorAgent
from src.infrastructure.media_processor import MediaProcessor
from src.infrastructure.storage_manager import CloudStorageManager


def generate_content_with_media(topic: str, project_id: str = "demo_phase3"):
    """
    Complete content generation workflow with media
    
    Args:
        topic: Content topic
        project_id: Project identifier
    """
    print("\n" + "="*70)
    print(f"GENERATING CONTENT WITH MEDIA: {topic}")
    print("="*70)
    
    # Initialize agents
    research_agent = ResearchAgent()
    content_agent = ContentGeneratorAgent()
    image_agent = ImageGeneratorAgent()
    video_agent = VideoCreatorAgent()
    audio_agent = AudioCreatorAgent()
    media_processor = MediaProcessor()
    
    total_cost = 0.0
    
    # Step 1: Research
    print("\n📚 Step 1: Researching topic...")
    research_result = research_agent.execute(
        project_id=project_id,
        topic=topic
    )
    print(f"   ✓ Research completed")
    print(f"   ✓ Key points: {len(research_result.get('key_points', []))}")
    print(f"   ✓ Cost: ${research_result.get('cost', 0):.4f}")
    total_cost += research_result.get('cost', 0)
    
    # Step 2: Generate blog post
    print("\n✍️  Step 2: Generating blog post...")
    content_result = content_agent.execute(
        project_id=project_id,
        topic=topic,
        research_findings=research_result,
        target_word_count=1200
    )
    
    title = content_result.get('title', topic)
    body = content_result.get('body', '')
    
    print(f"   ✓ Blog post created")
    print(f"   ✓ Title: {title}")
    print(f"   ✓ Word count: ~{len(body.split())}")
    print(f"   ✓ Cost: ${content_result.get('cost', 0):.4f}")
    total_cost += content_result.get('cost', 0)
    
    # Step 3: Generate images
    print("\n🎨 Step 3: Generating images...")
    
    # Get image suggestions from content
    image_prompts = image_agent.suggest_images_for_content(
        content=body,
        title=title,
        content_type="blog",
        num_suggestions=3
    )
    
    print(f"   ✓ Generated {len(image_prompts)} image prompt suggestions")
    
    # Generate hero image
    if image_prompts:
        hero_prompt = image_prompts[0]
        print(f"\n   Generating hero image...")
        print(f"   Prompt: {hero_prompt[:80]}...")
        
        image_result = image_agent.execute(
            project_id=project_id,
            prompts=[hero_prompt],
            number_of_images=1,
            aspect_ratio="16:9",
            content_type="blog"
        )
        
        print(f"   ✓ Hero image generated")
        print(f"   ✓ Cost: ${image_result.get('cost', 0):.4f}")
        total_cost += image_result.get('cost', 0)
        
        # Process and optimize images
        images = image_result.get('images', [])
        if images:
            print(f"\n   Optimizing images...")
            for idx, img_data in enumerate(images):
                img = img_data['image']
                
                # Optimize
                optimized = media_processor.optimize_image(
                    image=img,
                    quality=85,
                    max_width=1920
                )
                
                # Create thumbnail
                thumbnail = media_processor.create_thumbnail(
                    image=optimized,
                    size=(300, 300)
                )
                
                # Create responsive versions
                responsive = media_processor.create_responsive_set(optimized)
                
                print(f"   ✓ Image {idx+1} optimized")
                print(f"      - Main: {optimized.size}")
                print(f"      - Thumbnail: {thumbnail.size}")
                print(f"      - Responsive versions: {len(responsive)}")
    
    # Step 4: Generate video script
    print("\n🎥 Step 4: Creating video script...")
    video_result = video_agent.execute(
        project_id=project_id,
        topic=title,
        content=body[:1000],  # First 1000 chars as context
        duration=120,
        video_type="explainer",
        tone="professional",
        target_platform="youtube"
    )
    
    video_script = video_result.get('script', {})
    print(f"   ✓ Video script created")
    print(f"   ✓ Title: {video_script.get('title', 'N/A')}")
    print(f"   ✓ Scenes: {len(video_script.get('scenes', []))}")
    print(f"   ✓ Duration: {video_result.get('duration', 0)} seconds")
    print(f"   ✓ Cost: ${video_result.get('cost', 0):.4f}")
    total_cost += video_result.get('cost', 0)
    
    # Generate video metadata
    video_metadata = video_agent.generate_video_metadata(
        script=video_script,
        platform="youtube"
    )
    print(f"   ✓ Video metadata generated")
    
    # Step 5: Generate podcast script
    print("\n🎙️  Step 5: Creating podcast script...")
    audio_result = audio_agent.execute(
        project_id=project_id,
        topic=title,
        content=body[:1500],
        duration=15,
        audio_type="podcast",
        tone="conversational",
        num_speakers=1
    )
    
    audio_script = audio_result.get('script', {})
    print(f"   ✓ Podcast script created")
    print(f"   ✓ Title: {audio_script.get('title', 'N/A')}")
    print(f"   ✓ Segments: {len(audio_script.get('segments', []))}")
    print(f"   ✓ Duration: {audio_result.get('duration_minutes', 0)} minutes")
    print(f"   ✓ Cost: ${audio_result.get('cost', 0):.4f}")
    total_cost += audio_result.get('cost', 0)
    
    # Generate podcast metadata
    podcast_metadata = audio_agent.generate_podcast_metadata(
        script=audio_script
    )
    print(f"   ✓ Podcast metadata generated")
    
    # Summary
    print("\n" + "="*70)
    print("GENERATION COMPLETE")
    print("="*70)
    
    print(f"\n📝 Content:")
    print(f"   - Blog Post: {title}")
    print(f"   - Word Count: ~{len(body.split())}")
    
    print(f"\n🎨 Media Generated:")
    print(f"   - Hero Image: 1")
    print(f"   - Video Script: {len(video_script.get('scenes', []))} scenes")
    print(f"   - Podcast Script: {len(audio_script.get('segments', []))} segments")
    
    print(f"\n💰 Total Cost: ${total_cost:.4f}")
    
    # Return all results
    return {
        'research': research_result,
        'content': content_result,
        'images': image_result if 'image_result' in locals() else None,
        'video': video_result,
        'audio': audio_result,
        'total_cost': total_cost
    }


def main():
    """Run the complete example"""
    
    # Example topics
    topics = [
        "The Future of Remote Work",
        "Sustainable Living Tips for Beginners",
        "Introduction to Machine Learning"
    ]
    
    print("\n" + "="*70)
    print("PHASE 3 - CONTENT WITH MEDIA GENERATION EXAMPLE")
    print("="*70)
    
    print("\nAvailable topics:")
    for i, topic in enumerate(topics, 1):
        print(f"  {i}. {topic}")
    
    # Use first topic for demo
    selected_topic = topics[0]
    
    print(f"\n🚀 Generating content for: {selected_topic}")
    print("="*70)
    
    try:
        result = generate_content_with_media(
            topic=selected_topic,
            project_id="demo_phase3_001"
        )
        
        print("\n✅ Example completed successfully!")
        print("\nNext steps:")
        print("  1. Review generated content and media")
        print("  2. Upload media to Cloud Storage")
        print("  3. Publish content to CMS")
        print("  4. Track performance analytics")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
