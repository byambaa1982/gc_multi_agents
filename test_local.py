"""
Test local FastAPI server
"""
import requests
import json

# Local server URL
BASE_URL = "http://localhost:8000"

def test_local_generation():
    """Test content generation on local server"""
    
    print("Testing local content generation...")
    print("=" * 60)
    
    # Test payload
    payload = {
        "topic": "cute puppy playing in park",
        "media_types": ["image"],
        "target_word_count": 800,
        "tone": "friendly"
    }
    
    print(f"\nPayload:")
    print(json.dumps(payload, indent=2))
    
    try:
        # Send request
        print(f"\nSending request to {BASE_URL}/generate/sync...")
        response = requests.post(
            f"{BASE_URL}/generate/sync",
            json=payload,
            timeout=300  # 5 minutes
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "=" * 60)
            print("SUCCESS!")
            print("=" * 60)
            print(f"Status: {result.get('status')}")
            print(f"Message: {result.get('message')}")
            print(f"Project ID: {result.get('project_id')}")
            
            if result.get('content'):
                content_preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                print(f"\nContent Preview:\n{content_preview}")
            
            if result.get('media_urls'):
                print(f"\nMedia URLs: {result['media_urls']}")
            else:
                print("\nNo media generated")
                
        else:
            print(f"\nERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\nException occurred: {str(e)}")

if __name__ == "__main__":
    test_local_generation()
