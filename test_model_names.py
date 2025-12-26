"""
Test different Gemini model names to find the correct one
"""

import os
from dotenv import load_dotenv

load_dotenv()

import vertexai
from vertexai.generative_models import GenerativeModel

project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')

vertexai.init(project=project_id, location=location)

# Try different model names
model_names = [
    'gemini-1.5-flash-001',
    'gemini-1.5-flash-002',
    'gemini-1.5-pro-001',
    'gemini-1.5-pro-002',
    'gemini-pro',
    'gemini-1.0-pro',
    'gemini-1.0-pro-001',
]

print("Testing model names...\n")

for model_name in model_names:
    try:
        print(f"Testing: {model_name}...", end=" ")
        model = GenerativeModel(model_name)
        response = model.generate_content("Say hello")
        print(f"✓ WORKS! Response: {response.text[:50]}")
        break  # Stop at first working model
    except Exception as e:
        error_type = type(e).__name__
        if 'not found' in str(e).lower():
            print(f"❌ Not found")
        elif 'permission' in str(e).lower() or 'access' in str(e).lower():
            print(f"❌ Permission denied")
        else:
            print(f"❌ Error: {error_type}")
