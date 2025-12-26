"""
Multi-Agent Content Generation System - Main Entry Point

Phase 0: MVP Foundation
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from src.orchestration import ContentGenerationWorkflow
from src.monitoring import StructuredLogger

# Load environment variables
load_dotenv()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate blog content using AI agents'
    )
    parser.add_argument(
        '--topic',
        type=str,
        required=True,
        help='Topic for the blog post'
    )
    parser.add_argument(
        '--tone',
        type=str,
        default='professional and conversational',
        help='Writing tone (default: professional and conversational)'
    )
    parser.add_argument(
        '--words',
        type=int,
        default=1200,
        help='Target word count (default: 1200)'
    )
    parser.add_argument(
        '--project-id',
        type=str,
        help='Get existing project instead of generating new content'
    )
    
    args = parser.parse_args()
    
    # Initialize logger
    logger = StructuredLogger(name='main')
    
    # Check environment
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        logger.error("GOOGLE_CLOUD_PROJECT environment variable not set")
        print("❌ Error: GOOGLE_CLOUD_PROJECT not set in .env file")
        print("Please create a .env file with your GCP project configuration.")
        print("See .env.example for reference.")
        sys.exit(1)
    
    logger.info(
        "Starting multi-agent content generation",
        gcp_project=project_id,
        topic=args.topic
    )
    
    # Initialize workflow
    workflow = ContentGenerationWorkflow()
    
    # Get existing project or generate new content
    if args.project_id:
        print(f"\n📖 Fetching project: {args.project_id}")
        result = workflow.get_project(args.project_id)
        
        if result:
            print_project_details(result)
        else:
            print(f"❌ Project {args.project_id} not found")
            sys.exit(1)
    else:
        print(f"\n🚀 Generating content for topic: {args.topic}")
        print(f"📝 Target word count: {args.words}")
        print(f"🎨 Tone: {args.tone}\n")
        
        # Generate content
        result = workflow.generate_content(
            topic=args.topic,
            tone=args.tone,
            target_word_count=args.words
        )
        
        if result['success']:
            print_generation_result(result)
        else:
            print(f"\n❌ Content generation failed: {result.get('error')}")
            sys.exit(1)


def print_generation_result(result: dict):
    """Print generation results"""
    project = result['project']
    content = result['content']
    
    print("=" * 80)
    print("✅ CONTENT GENERATION COMPLETED")
    print("=" * 80)
    
    print(f"\n📌 Project ID: {result['project_id']}")
    print(f"📊 Status: {project['status']}")
    
    # Costs
    costs = project.get('costs', {})
    print(f"\n💰 Costs:")
    print(f"   Research: ${costs.get('research', 0):.4f}")
    print(f"   Generation: ${costs.get('generation', 0):.4f}")
    print(f"   Total: ${costs.get('total', 0):.4f}")
    
    # Content details
    print(f"\n📝 Content:")
    print(f"   Title: {content.get('title', 'N/A')}")
    print(f"   Word Count: {content.get('word_count', 0)}")
    print(f"   Model Used: {content.get('model_used', 'N/A')}")
    
    # Preview
    if content.get('introduction'):
        print(f"\n📄 Introduction Preview:")
        preview = content['introduction'][:200]
        print(f"   {preview}...")
    
    print("\n" + "=" * 80)
    print(f"💾 Full content saved to Firestore (Project ID: {result['project_id']})")
    print("=" * 80)


def print_project_details(project: dict):
    """Print project details"""
    print("=" * 80)
    print("📖 PROJECT DETAILS")
    print("=" * 80)
    
    print(f"\n📌 Project ID: {project.get('projectId')}")
    print(f"📊 Status: {project.get('status')}")
    print(f"📝 Topic: {project.get('topic')}")
    
    # Costs
    costs = project.get('costs', {})
    print(f"\n💰 Costs:")
    print(f"   Total: ${costs.get('total', 0):.4f}")
    
    # Content
    content = project.get('content')
    if content:
        print(f"\n📝 Content:")
        print(f"   Title: {content.get('title', 'N/A')}")
        print(f"   Word Count: {content.get('word_count', 0)}")
        
        if content.get('body'):
            preview = content['body'][:300]
            print(f"\n📄 Content Preview:")
            print(f"   {preview}...")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger = StructuredLogger(name='main')
        logger.error(f"Unexpected error: {str(e)}", error=str(e))
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
