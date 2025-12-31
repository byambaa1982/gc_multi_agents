"""
Test the deployed service to diagnose issues
"""
import requests
import json
import time

# Cloud Run service URL
SERVICE_URL = "https://content-generator-279772560710.us-central1.run.app"

def test_simple_generation():
    """Test a simple content generation"""
    
    print("🧪 Testing Simple Content Generation\n")
    print(f"Service URL: {SERVICE_URL}\n")
    
    # Very simple request
    payload = {
        "topic": "The Future of AI"
    }
    
    print("📤 Sending simple request:")
    print(json.dumps(payload, indent=2))
    print("\n⏳ Generating content...\n")
    
    try:
        # Make the request
        response = requests.post(
            f"{SERVICE_URL}/generate/sync",
            json=payload,
            timeout=180  # 3 minutes timeout
        )
        
        print(f"Response Status: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Response received:\n")
            print(json.dumps(result, indent=2))
            
            # Save result
            with open('test_result.json', 'w') as f:
                json.dump(result, f, indent=2)
            print("\n💾 Saved to: test_result.json")
            
            # Check if we got a project_id
            project_id = result.get('project_id')
            if project_id:
                print(f"\n📄 Project created: {project_id}")
                print(f"   You can check it with: python check_generated_content.py {project_id}")
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_with_logging():
    """Test and check Cloud Logging for errors"""
    print("\n" + "="*70)
    print("🔍 Testing with detailed logging")
    print("="*70)
    
    # Make a request
    test_simple_generation()
    
    print("\n💡 To check Cloud Logging:")
    print("   1. Go to: https://console.cloud.google.com/logs")
    print("   2. Filter by: resource.type='cloud_run_revision'")
    print("   3. Look for errors in the last few minutes")

if __name__ == "__main__":
    test_with_logging()
