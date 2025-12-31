#!/usr/bin/env python3
"""Quick script to check Firestore content."""

import os
from google.cloud import firestore

# Set project
os.environ['GOOGLE_CLOUD_PROJECT'] = 'datalogichub-461612'

# Initialize Firestore
db = firestore.Client(database='firestore-us-central1')

# Get the project we just created
project_id = 'DGBXbO6dklGCr6oI4LiS'

try:
    # Get the project document
    project_ref = db.collection('projects').document(project_id)
    project = project_ref.get()
    
    if project.exists:
        print(f"✅ Project found in Firestore!")
        print(f"\nProject ID: {project_id}")
        print(f"\nProject Data:")
        data = project.to_dict()
        for key, value in data.items():
            if key == 'content':
                print(f"  {key}: {value[:100]}..." if value and len(str(value)) > 100 else f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
        
        # Check content document
        print(f"\n" + "="*60)
        content_ref = db.collection('content').document(project_id)
        content = content_ref.get()
        
        if content.exists:
            print(f"✅ Content found in Firestore!")
            content_data = content.to_dict()
            print(f"\nContent Data:")
            for key, value in content_data.items():
                if isinstance(value, str) and len(value) > 200:
                    print(f"  {key}: {value[:200]}...")
                else:
                    print(f"  {key}: {value}")
        else:
            print(f"⚠️  No content document found")
            
    else:
        print(f"❌ Project {project_id} not found in Firestore")
        
except Exception as e:
    print(f"❌ Error checking Firestore: {e}")
    import traceback
    traceback.print_exc()
