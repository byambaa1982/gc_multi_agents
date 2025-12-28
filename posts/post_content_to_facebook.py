#!/usr/bin/env python3
"""
Post Agent-Generated Content to Facebook
Retrieves content from GCS storage and posts to Эхлэл Facebook page
"""

import json
import requests
import os
from google.cloud import firestore
from datetime import datetime

# Эхлэл page ID
EHLEL_PAGE_ID = "682084288324866"
GCP_PROJECT = "datalogichub-461612"
FIRESTORE_COLLECTION = "content_projects"

def load_page_credentials():
    """Load Facebook page credentials from system_users.json"""
    try:
        with open('system_users.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for page in data.get('facebook_pages', []):
            if page.get('id') == EHLEL_PAGE_ID:
                return page['access_token']
        
        print(f"❌ Эхлэл page not found in system_users.json")
        return None
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return None

def list_recent_content(limit=10):
    """List recent content from Firestore"""
    try:
        db = firestore.Client(project=GCP_PROJECT)
        
        # Query the content_projects collection
        content_ref = db.collection(FIRESTORE_COLLECTION)
        
        # Get documents without ordering (since timestamp might not exist on all docs)
        docs = content_ref.limit(limit).stream()
        
        content_list = []
        for doc in docs:
            try:
                data = doc.to_dict()
                
                # Extract title from various possible locations
                title = 'Untitled'
                if 'topic' in data:
                    title = data['topic']
                elif 'title' in data:
                    title = data['title']
                elif 'final_content' in data and isinstance(data['final_content'], dict):
                    title = data['final_content'].get('title', 'Untitled')
                elif 'edited_content' in data and isinstance(data['edited_content'], dict):
                    if 'edited_body' in data['edited_content']:
                        # Parse JSON if it's a string
                        edited = data['edited_content']['edited_body']
                        if isinstance(edited, str) and edited.startswith('```json'):
                            import json as js
                            edited = edited.replace('```json\n', '').replace('\n```', '')
                            try:
                                parsed = js.loads(edited)
                                title = parsed.get('edited_title', 'Untitled')
                            except:
                                pass
                
                # Get timestamp
                timestamp = data.get('timestamp', data.get('updatedAt', data.get('created_at', datetime.now())))
                
                content_list.append({
                    'id': doc.id,
                    'data': data,
                    'timestamp': timestamp,
                    'title': str(title)[:100]
                })
            except Exception as e:
                print(f"   ⚠️  Error processing document {doc.id}: {e}")
                continue
        
        print(f"   ℹ️  Retrieved {len(content_list)} content items")
        return content_list
    except Exception as e:
        print(f"❌ Error listing content from Firestore: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_content_by_id(doc_id):
    """Get specific content document from Firestore"""
    try:
        db = firestore.Client(project=GCP_PROJECT)
        doc_ref = db.collection(FIRESTORE_COLLECTION).document(doc_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        else:
            print(f"❌ Document {doc_id} not found")
            return None
    except Exception as e:
        print(f"❌ Error getting content: {e}")
        return None

def format_content_for_facebook(content_data):
    """
    Format agent-generated content for Facebook posting
    
    Args:
        content_data: Dictionary with content from agents
        
    Returns:
        str: Formatted message for Facebook
    """
    # Try to extract the best format for Facebook
    message = ""
    
    # Check for different content formats
    if 'facebook' in content_data:
        # Direct Facebook format from PublisherAgent
        fb_content = content_data['facebook']
        if isinstance(fb_content, dict):
            message = fb_content.get('content', '')
        else:
            message = str(fb_content)
    elif 'final_content' in content_data:
        # Final content from ContentAgent
        final = content_data['final_content']
        if isinstance(final, dict):
            title = final.get('title', '')
            body = final.get('body', '')
            tags = final.get('tags', [])
            
            message = f"{title}\n\n{body[:500]}"
            if len(body) > 500:
                message += "..."
            
            if tags:
                hashtags = ' '.join([f"#{tag.replace(' ', '')}" for tag in tags[:5]])
                message += f"\n\n{hashtags}"
        else:
            message = str(final)[:1000]
    elif 'content' in content_data:
        # Raw content
        content = content_data['content']
        if isinstance(content, dict):
            message = content.get('body', str(content))[:1000]
        else:
            message = str(content)[:1000]
    elif 'body' in content_data:
        # Body field
        message = content_data['body'][:1000]
    else:
        # Use entire content
        message = str(content_data)[:1000]
    
    return message.strip()

def post_to_facebook(page_id, access_token, message):
    """Post message to Facebook page"""
    url = f"https://graph.facebook.com/v23.0/{page_id}/feed"
    
    payload = {
        'message': message,
        'access_token': access_token
    }
    
    try:
        response = requests.post(url, data=payload, timeout=30)
        
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {
                'success': False,
                'error': response.json(),
                'status_code': response.status_code
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    """Main function"""
    print("=" * 80)
    print("POST AGENT-GENERATED CONTENT TO FACEBOOK")
    print("=" * 80)
    
    # Load credentials
    print("\n1. Loading Facebook credentials...")
    access_token = load_page_credentials()
    if not access_token:
        return
    print(f"   ✓ Credentials loaded")
    
    # List recent content
    print(f"\n2. Fetching recent content from Firestore ({FIRESTORE_COLLECTION})...")
    content_items = list_recent_content()
    
    if not content_items:
        print("   ⚠️  No content found")
        return
    
    print(f"   ✓ Found {len(content_items)} content item(s)")
    print("\n   Recent content:")
    for i, item in enumerate(content_items, 1):
        timestamp = item['timestamp']
        if isinstance(timestamp, datetime):
            time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        else:
            time_str = str(timestamp)
        title = item['title'][:60] + '...' if len(item['title']) > 60 else item['title']
        print(f"     [{i}] {title} ({time_str})")
    
    # Auto-select most recent content
    print("\n3. Selecting most recent content...")
    selected_item = content_items[0]
    print(f"   ✓ Selected: {selected_item['title']}")
    
    # Get content data
    print("\n4. Loading content...")
    content_data = selected_item['data']
    print(f"   ✓ Content loaded ({len(str(content_data))} bytes)")
    
    # Format for Facebook
    print("\n5. Formatting content for Facebook...")
    message = format_content_for_facebook(content_data)
    
    print("\n" + "-" * 80)
    print("PREVIEW:")
    print("-" * 80)
    print(message[:500] + "..." if len(message) > 500 else message)
    print("-" * 80)
    
    # Post to Facebook
    print("\n6. Posting to Facebook...")
    result = post_to_facebook(EHLEL_PAGE_ID, access_token, message)
    
    if result.get('success'):
        post_id = result['data'].get('id')
        print("\n" + "=" * 80)
        print("✅ SUCCESS!")
        print("=" * 80)
        print(f"Post ID: {post_id}")
        print(f"\nView your post at:")
        print(f"https://www.facebook.com/{post_id}")
        
        # Save posting record
        record = {
            'post_id': post_id,
            'content_id': selected_item['id'],
            'content_title': selected_item['title'],
            'posted_at': datetime.now().isoformat(),
            'message_length': len(message)
        }
        
        with open('posting_history.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + '\n')
        print("\n✓ Posting record saved to posting_history.json")
        
    else:
        print("\n" + "=" * 80)
        print("❌ FAILED")
        print("=" * 80)
        print(f"Status Code: {result.get('status_code', 'N/A')}")
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == '__main__':
    main()
