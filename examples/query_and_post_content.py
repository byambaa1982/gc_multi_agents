"""
Query Generated Content from Firestore and Prepare for Social Media Posting

This script demonstrates how to:
1. Query content from Firestore
2. Filter by status, tags, or date
3. Display ready-to-post social media content
4. Mark content as posted
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.firestore import FirestoreManager
from src.monitoring.logger import StructuredLogger


def display_content(content: dict, logger: StructuredLogger):
    """Display content details in a readable format"""
    logger.info("\n" + "="*70)
    logger.info(f"📄 Content: {content['content_id']}")
    logger.info("="*70)
    
    # Basic info
    logger.info(f"\n📊 Basic Information:")
    logger.info(f"  Type: {content['content_type']}")
    logger.info(f"  Category: {content['category']}")
    logger.info(f"  Status: {content['status']}")
    logger.info(f"  Created: {content['created_at']}")
    
    # Generation details
    gen = content['generation']
    logger.info(f"\n🎨 Generation Details:")
    logger.info(f"  Prompt: {gen['prompt'][:80]}...")
    logger.info(f"  Model: {gen['model']}")
    logger.info(f"  Cost: ${gen['cost_usd']:.4f}")
    
    # Image URLs
    storage = content['storage']
    logger.info(f"\n🖼️  Image URLs:")
    logger.info(f"  Main: {storage['main_image']['url']}")
    logger.info(f"  Thumbnail: {storage['thumbnail']['url']}")
    logger.info(f"  Size: {storage['main_image']['size_bytes']:,} bytes")
    logger.info(f"  Dimensions: {content['image_properties']['dimensions']}")
    
    # Social media content
    social = content['social_media']
    logger.info(f"\n📱 Social Media Content:")
    logger.info(f"\n  Caption:")
    logger.info(f"  {social['caption']}")
    logger.info(f"\n  Full Post Text:")
    logger.info(f"  {social['post_text']}")
    logger.info(f"\n  Hashtags:")
    logger.info(f"  {' '.join(social['hashtags'])}")
    
    # Posting status
    status = content['posting_status']
    logger.info(f"\n📮 Posting Status:")
    logger.info(f"  Facebook: {status['facebook']}")
    logger.info(f"  Instagram: {status['instagram']}")
    logger.info(f"  Twitter: {status['twitter']}")
    logger.info(f"  LinkedIn: {status['linkedin']}")


def main():
    """Query and display content from Firestore"""
    load_dotenv()
    
    logger = StructuredLogger("ContentQuery")
    
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        logger.error("GOOGLE_CLOUD_PROJECT not set")
        return 1
    
    logger.info("="*70)
    logger.info("Content Query & Social Media Preparation")
    logger.info("="*70)
    logger.info(f"Project: {project_id}")
    
    # Initialize Firestore
    firestore_manager = FirestoreManager()
    
    # Query all ready-to-post content
    logger.info("\n🔍 Querying content ready to post...")
    
    # Get all documents (you can add filters here)
    collection = firestore_manager.db.collection(firestore_manager.collection_name)
    
    # Filter for image content that's ready to post
    docs = collection.where('content_type', '==', 'image').stream()
    
    contents = []
    for doc in docs:
        data = doc.to_dict()
        data['doc_id'] = doc.id
        if 'status' in data and data['status'] == 'ready_to_post':
            contents.append(data)
    
    if not contents:
        logger.info("No content found ready to post")
        logger.info("\nTip: Run generate_and_store_cartoon.py to create content first!")
        return 0
    
    logger.info(f"✓ Found {len(contents)} content item(s) ready to post")
    
    # Display each content item
    for idx, content in enumerate(contents, 1):
        display_content(content, logger)
        
        if idx < len(contents):
            logger.info("\n" + "-"*70)
    
    # Example: Mark as posted to Facebook
    logger.info("\n" + "="*70)
    logger.info("📤 Example: Mark as Posted")
    logger.info("="*70)
    
    if contents:
        example_content = contents[0]
        doc_id = example_content['doc_id']
        
        logger.info(f"\nTo mark content as posted to Facebook:")
        logger.info(f"  Document ID: {doc_id}")
        logger.info(f"  Content ID: {example_content['content_id']}")
        
        # Update posting status
        update_data = {
            'posting_status.facebook': 'posted',
            'posting_status.facebook_posted_at': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        # Uncomment to actually update:
        # firestore_manager.collection.document(doc_id).update(update_data)
        # logger.info("✓ Updated posting status")
        
        logger.info("\n💡 To actually post, integrate with social media APIs:")
        logger.info("  - Facebook Graph API")
        logger.info("  - Instagram Graph API")
        logger.info("  - Twitter API v2")
        logger.info("  - LinkedIn API")
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("✓ Query Complete")
    logger.info("="*70)
    logger.info(f"Total content items: {len(contents)}")
    logger.info(f"Ready to post: {len([c for c in contents if c.get('status') == 'ready_to_post'])}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
