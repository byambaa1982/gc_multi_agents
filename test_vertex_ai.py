"""
Quick test to diagnose Vertex AI access
"""

import os
import traceback
from dotenv import load_dotenv

# Load environment
load_dotenv()

project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')

print(f"Project ID: {project_id}")
print(f"Location: {location}")
print()

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    
    print("✓ Imports successful")
    
    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)
    print("✓ Vertex AI initialized")
    
    # Try to create a model
    model = GenerativeModel('gemini-2.5-flash')
    print(f"✓ Model created: {model}")
    
    # Try to generate content
    print("\nTesting content generation...")
    response = model.generate_content("Say 'Hello, World!' in one sentence.")
    
    print(f"✓ Content generated successfully!")
    print(f"\nResponse: {response.text}")
    
except Exception as e:
    print(f"\n❌ Error occurred:")
    print(f"Type: {type(e).__name__}")
    print(f"Message: {str(e)}")
    print(f"\nFull traceback:")
    traceback.print_exc()
