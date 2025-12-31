#!/usr/bin/env python3
"""
Simple test to check what's in Firestore from the workflow
"""

import os
from google.cloud import firestore

os.environ['GOOGLE_CLOUD_PROJECT'] = 'datalogichub-461612'

db = firestore.Client()

print("=" * 70)
print("FIRESTORE COLLECTIONS AND RECENT DATA")
print("=" * 70)

# Check projects collection
print("\n📦 PROJECTS COLLECTION:")
print("-" * 70)
try:
    projects = db.collection('projects').order_by('created_at', direction=firestore.Query.DESCENDING).limit(2).stream()
    
    for project in projects:
        data = project.to_dict()
        print(f"\n🆔 Project ID: {project.id}")
        print(f"📝 Topic: {data.get('topic')}")
        print(f"🔄 Status: {data.get('status')}")
        
        # Check for content field
        if 'content' in data:
            content = data['content']
            if isinstance(content, str):
                print(f"📄 Content (in project): {content[:200]}...")
            elif isinstance(content, dict):
                print(f"📄 Content (dict): {content.keys()}")
        
        print(f"\n🔑 All keys: {list(data.keys())}")
        
except Exception as e:
    print(f"❌ Error reading projects: {e}")

# Check content collection
print("\n\n📄 CONTENT COLLECTION:")
print("-" * 70)
try:
    contents = db.collection('content').limit(2).stream()
    
    found_any = False
    for content in contents:
        found_any = True
        data = content.to_dict()
        print(f"\n🆔 Content ID: {content.id}")
        print(f"🔑 Keys: {list(data.keys())}")
        
        # Check for body/content fields
        if 'body' in data:
            print(f"📝 Body: {data['body'][:300]}...")
        if 'content' in data:
            print(f"📝 Content: {data['content'][:300]}...")
        if 'title' in data:
            print(f"📌 Title: {data['title']}")
    
    if not found_any:
        print("⚠️  No documents in content collection")
        
except Exception as e:
    print(f"❌ Error reading content: {e}")

# Check content_projects collection (from the example)
print("\n\n🎨 CONTENT_PROJECTS COLLECTION:")
print("-" * 70)
try:
    content_projects = db.collection('content_projects').order_by('created_at', direction=firestore.Query.DESCENDING).limit(2).stream()
    
    for doc in content_projects:
        data = doc.to_dict()
        print(f"\n🆔 Doc ID: {doc.id}")
        print(f"📝 Content ID: {data.get('content_id')}")
        print(f"🎭 Type: {data.get('content_type')}/{data.get('category')}")
        
        if 'social_media' in data:
            social = data['social_media']
            print(f"📱 Caption: {social.get('caption', 'N/A')[:100]}...")
        
        if 'storage' in data:
            storage = data['storage']
            if 'main_image' in storage:
                print(f"🖼️  Image URL: {storage['main_image'].get('url')}")
                
except Exception as e:
    print(f"❌ Error reading content_projects: {e}")

print("\n" + "=" * 70)
