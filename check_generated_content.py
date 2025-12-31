"""
Check the generated content from Firestore
"""
import os
from dotenv import load_dotenv
from src.infrastructure.firestore import FirestoreManager

# Load environment
load_dotenv()

def check_content(project_id=None):
    """Check generated content in Firestore"""
    
    firestore_manager = FirestoreManager()
    
    if project_id:
        # Get specific project
        print(f"📄 Fetching project: {project_id}\n")
        doc = firestore_manager.get_project(project_id)
        
        if doc:
            print("=" * 70)
            print(f"🆔 Doc ID: {project_id}")
            
            # Determine project type
            is_image_project = 'storage' in doc and 'main_image' in doc.get('storage', {})
            is_content_project = 'content' in doc and 'body' in doc.get('content', {})
            
            if is_image_project:
                # Image/Cartoon project
                print(f"📝 Content ID: {doc.get('content_id', 'N/A')}")
                print(f"🎭 Type: {doc.get('content_type', 'N/A')}/{doc.get('category', 'N/A')}")
                
                # Display caption
                social_media = doc.get('social_media', {})
                caption = social_media.get('caption', 'N/A')
                print(f"📱 Caption: {caption[:100]}...")
                
                # Display image URL
                storage = doc.get('storage', {})
                main_image = storage.get('main_image', {})
                image_url = main_image.get('url', 'N/A')
                print(f"🖼️  Image URL: {image_url}")
                
                # Display full social media content
                if social_media:
                    print(f"\n📱 Full Social Media Content:")
                    print(f"   Caption: {caption}")
                    print(f"   Description: {social_media.get('description', 'N/A')[:150]}...")
                    print(f"   Hashtags: {', '.join(social_media.get('hashtags', []))}")
                    print(f"   Post Text:\n{social_media.get('post_text', 'N/A')}")
            
            elif is_content_project:
                # Blog/Article content project
                content = doc.get('content', {})
                print(f"📝 Title: {content.get('title', 'N/A')}")
                print(f"🎭 Type: Blog/Article")
                print(f"📊 Status: {doc.get('status', 'N/A')}")
                print(f"📏 Word Count: {content.get('word_count', 'N/A')}")
                print(f"💰 Total Cost: ${doc.get('costs', {}).get('total', 0):.4f}")
                
                # Display introduction
                intro = content.get('introduction', '')
                if intro:
                    print(f"\n📖 Introduction:")
                    print(f"   {intro[:200]}...")
                
                # Display body preview
                body = content.get('body', '')
                if body:
                    print(f"\n📄 Body Preview:")
                    print(f"   {body[:300]}...")
                
                # Display metadata
                metadata = content.get('metadata', {})
                if metadata:
                    print(f"\n🏷️  Tags: {', '.join(metadata.get('tags', []))}")
                    print(f"📁 Category: {metadata.get('category', 'N/A')}")
                
                # Display research info
                research = doc.get('research', {})
                if research:
                    print(f"\n🔍 Research:")
                    print(f"   Model: {research.get('model_used', 'N/A')}")
                    print(f"   Cost: ${research.get('cost', 0):.4f}")
            
            else:
                # Unknown/incomplete project
                print(f"⚠️  Project type: Unknown/Incomplete")
                print(f"📊 Status: {doc.get('status', 'N/A')}")
                print(f"📝 Topic: {doc.get('topic', 'N/A')}")
                if 'createdAt' in doc:
                    print(f"🕐 Created: {doc.get('createdAt')}")
            
            print("=" * 70)
        else:
            print(f"❌ Document not found: {project_id}")
    else:
        # Get specific project from last_generated_content.json
        try:
            import json
            with open('last_generated_content.json', 'r') as f:
                data = json.load(f)
                last_project_id = data.get('project_id')
                if last_project_id and last_project_id != 'N/A':
                    print(f"📄 Fetching project from last generation: {last_project_id}\n")
                    check_content(last_project_id)
                else:
                    print("❌ No valid project ID found in last_generated_content.json")
        except Exception as e:
            print(f"❌ Could not load last_generated_content.json: {e}")

if __name__ == "__main__":
    import sys
    
    # Check if project ID provided as argument
    if len(sys.argv) > 1:
        project_id = sys.argv[1]
        check_content(project_id)
    else:
        # Check the last generated project
        check_content()
