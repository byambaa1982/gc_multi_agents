#!/usr/bin/env python3
"""
Local test to verify what's actually saved in Firestore
"""

import os
import sys
from google.cloud import firestore
from datetime import datetime

# Set project
os.environ['GOOGLE_CLOUD_PROJECT'] = 'datalogichub-461612'

def test_firestore_content():
    """Check what's actually stored in Firestore"""
    
    # Initialize Firestore with the default database
    db = firestore.Client()
    
    print("=" * 70)
    print("TESTING FIRESTORE CONTENT STORAGE")
    print("=" * 70)
    
    # Get the most recent project
    try:
        projects = db.collection('projects').order_by('created_at', direction=firestore.Query.DESCENDING).limit(3).stream()
        
        print("\n📦 Recent Projects:")
        print("-" * 70)
        
        for project in projects:
            project_data = project.to_dict()
            project_id = project.id
            
            print(f"\n🆔 Project ID: {project_id}")
            print(f"📝 Topic: {project_data.get('topic', 'N/A')}")
            print(f"📅 Created: {project_data.get('created_at', 'N/A')}")
            print(f"🔄 Status: {project_data.get('status', 'N/A')}")
            print(f"💰 Total Cost: ${project_data.get('costs', {}).get('total', 0):.4f}")
            
            # Check what keys are in the project
            print(f"\n🔑 Available Keys in Project:")
            for key in sorted(project_data.keys()):
                value = project_data[key]
                if isinstance(value, str) and len(value) > 100:
                    print(f"  - {key}: {value[:100]}... ({len(value)} chars)")
                elif isinstance(value, dict):
                    print(f"  - {key}: {{{', '.join(value.keys())}}}")
                elif isinstance(value, list):
                    print(f"  - {key}: [{len(value)} items]")
                else:
                    print(f"  - {key}: {value}")
            
            # Now check the content collection for this project
            print(f"\n📄 Checking content collection for {project_id}...")
            content_ref = db.collection('content').document(project_id)
            content_doc = content_ref.get()
            
            if content_doc.exists:
                content_data = content_doc.to_dict()
                print(f"\n✅ Content Document Found!")
                print(f"🔑 Available Keys in Content:")
                
                for key in sorted(content_data.keys()):
                    value = content_data[key]
                    if key == 'body' and isinstance(value, str):
                        print(f"  - {key}: {value[:200]}... ({len(value)} chars)")
                        print(f"\n📝 ACTUAL CONTENT PREVIEW:")
                        print("-" * 70)
                        print(value[:500])
                        print("-" * 70)
                    elif isinstance(value, str) and len(value) > 100:
                        print(f"  - {key}: {value[:100]}... ({len(value)} chars)")
                    elif isinstance(value, dict):
                        print(f"  - {key}: {{{', '.join(value.keys())}}}")
                    elif isinstance(value, list):
                        print(f"  - {key}: [{len(value)} items]")
                    else:
                        print(f"  - {key}: {value}")
            else:
                print(f"❌ No content document found for {project_id}")
            
            print("\n" + "=" * 70)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_firestore_content()
