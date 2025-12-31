"""
Test the FastAPI application locally before deployment
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("✅ Health check passed")
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")


def test_root():
    """Test root endpoint"""
    print("\n🔍 Testing / endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        print("✅ Root endpoint passed")
    except Exception as e:
        print(f"❌ Root endpoint failed: {str(e)}")


def test_budget():
    """Test budget endpoint"""
    print("\n🔍 Testing /budget endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/budget")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        print("✅ Budget endpoint passed")
    except Exception as e:
        print(f"❌ Budget endpoint failed: {str(e)}")


def test_generate_async():
    """Test async content generation endpoint"""
    print("\n🔍 Testing /generate endpoint (async)...")
    try:
        payload = {
            "topic": "The Future of AI in 2026",
            "tone": "professional and engaging",
            "words": 500,
            "include_image": True,
            "include_video": False,
            "publish": False
        }
        
        response = requests.post(
            f"{BASE_URL}/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        assert response.json()["status"] == "processing"
        print("✅ Async generation endpoint passed")
    except Exception as e:
        print(f"❌ Async generation endpoint failed: {str(e)}")


def test_docs():
    """Test API documentation endpoint"""
    print("\n🔍 Testing /docs endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"Status Code: {response.status_code}")
        assert response.status_code == 200
        print("✅ Docs endpoint passed")
        print(f"📚 API docs available at: {BASE_URL}/docs")
    except Exception as e:
        print(f"❌ Docs endpoint failed: {str(e)}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing FastAPI Application")
    print("=" * 60)
    print(f"\nBase URL: {BASE_URL}")
    print("\nMake sure the server is running:")
    print("  python -m uvicorn app:app --host 0.0.0.0 --port 8080")
    print("\nOr using Docker:")
    print("  docker run -p 8080:8080 content-generator:latest")
    print("=" * 60)
    
    # Run tests
    test_root()
    test_health()
    test_budget()
    test_generate_async()
    test_docs()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Test sync generation (may take longer):")
    print(f"   curl -X POST {BASE_URL}/generate/sync \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"topic\": \"Test\", \"words\": 200}'")
    print("\n2. View API documentation:")
    print(f"   Open browser: {BASE_URL}/docs")
    print("\n3. Deploy to Cloud Run:")
    print("   $env:PROJECT_ID='your-project-id'; .\\deploy.ps1")
    print("=" * 60)


if __name__ == "__main__":
    main()
