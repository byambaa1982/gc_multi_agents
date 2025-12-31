"""
Simple test script to verify the deployed API
"""

import requests
import json
import time

# Service URL
SERVICE_URL = "https://content-generator-279772560710.us-central1.run.app"

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing /health endpoint...")
    response = requests.get(f"{SERVICE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_budget():
    """Test budget endpoint"""
    print("\n💰 Testing /budget endpoint...")
    response = requests.get(f"{SERVICE_URL}/budget")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_generate_simple():
    """Test simple content generation"""
    print("\n✍️ Testing content generation...")
    print("Topic: The Future of AI")
    print("Generating content with image...")
    
    payload = {
        "topic": "The Future of AI",
        "tone": "professional",
        "words": 300,
        "include_image": True,
        "include_video": False,
        "publish": False
    }
    
    response = requests.post(
        f"{SERVICE_URL}/generate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Request accepted!")
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        return True
    else:
        print(f"\n❌ Request failed")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Deployed Cloud Run Service")
    print("=" * 60)
    print(f"Service URL: {SERVICE_URL}")
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Budget Status", test_budget),
        ("Content Generation", test_generate_simple)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ {name} failed with error: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 60)
    print("\n📝 Note: Content generation runs in background.")
    print("Check Cloud Run logs to see the actual generation process:")
    print("  gcloud logging read 'resource.type=cloud_run_revision' --limit 20\n")
    print("Or view logs in Cloud Console:")
    print("  https://console.cloud.google.com/run/detail/us-central1/content-generator/logs\n")

if __name__ == "__main__":
    main()
