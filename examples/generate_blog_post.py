"""
Example: Generate a blog post using the multi-agent system

This script demonstrates the basic usage of the content generation workflow.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestration import ContentGenerationWorkflow


def main():
    """Generate a sample blog post"""
    
    # Load environment variables
    load_dotenv()
    
    print("=" * 80)
    print("Multi-Agent Content Generation - Example")
    print("=" * 80)
    
    # Initialize workflow
    print("\n🔧 Initializing workflow...")
    workflow = ContentGenerationWorkflow()
    
    # Define topic
    topic = "Getting Started with Google Cloud AI: A Beginner's Guide"
    
    print(f"\n📝 Topic: {topic}")
    print("⏳ Generating content (this may take 1-2 minutes)...\n")
    
    # Generate content
    result = workflow.generate_content(
        topic=topic,
        tone='friendly and educational',
        target_word_count=1000
    )
    
    if result['success']:
        print("\n✅ Content generated successfully!")
        
        project = result['project']
        content = result['content']
        
        # Display results
        print("\n" + "=" * 80)
        print("GENERATION SUMMARY")
        print("=" * 80)
        
        print(f"\n📌 Project ID: {result['project_id']}")
        
        # Costs
        costs = project.get('costs', {})
        print(f"\n💰 Costs:")
        print(f"   Research: ${costs.get('research', 0):.4f}")
        print(f"   Generation: ${costs.get('generation', 0):.4f}")
        print(f"   Total: ${costs.get('total', 0):.4f}")
        
        # Content details
        print(f"\n📝 Generated Content:")
        print(f"   Title: {content.get('title', 'N/A')}")
        print(f"   Word Count: {content.get('word_count', 0)}")
        
        # Full content
        if content.get('body'):
            print("\n" + "=" * 80)
            print("FULL CONTENT")
            print("=" * 80)
            print(f"\n{content['body']}\n")
        
        # Metadata
        if content.get('metadata'):
            print("=" * 80)
            print("METADATA")
            print("=" * 80)
            metadata = content['metadata']
            if metadata.get('tags'):
                print(f"\n🏷️  Tags: {', '.join(metadata['tags'])}")
            if metadata.get('category'):
                print(f"📂 Category: {metadata['category']}")
        
        print("\n" + "=" * 80)
        print(f"💾 Content saved to Firestore")
        print(f"Project ID: {result['project_id']}")
        print("=" * 80)
        
    else:
        print(f"\n❌ Content generation failed: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
