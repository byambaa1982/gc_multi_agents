"""
Test script to generate content with an image using the deployed Cloud Run service
"""
import requests
import json
import time

# Cloud Run service URL
SERVICE_URL = "https://content-generator-279772560710.us-central1.run.app"

def test_image_generation():
    """Test content generation with image"""
    
    print("🎨 Testing Image Generation\n")
    print(f"Service URL: {SERVICE_URL}\n")
    
    # Prepare the request
    payload = {
        "topic": "a cute robot learning to paint",
        "content_type": "social_media_post",
        "platform": "twitter",
        "media_types": ["image"],  # Request image generation
        "metadata": {
            "tone": "friendly",
            "length": "short",
            "hashtags": True
        }
    }
    
    print("📤 Sending request:")
    print(json.dumps(payload, indent=2))
    print("\n⏳ Generating content (this may take 30-60 seconds)...\n")
    
    try:
        # Make the request
        response = requests.post(
            f"{SERVICE_URL}/generate/sync",
            json=payload,
            timeout=120  # 2 minutes timeout
        )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Success!\n")
            print("=" * 60)
            print("GENERATED CONTENT:")
            print("=" * 60)
            print(f"\nStatus: {result.get('status', 'N/A')}")
            print(f"Message: {result.get('message', 'N/A')}")
            print(f"Project ID: {result.get('project_id', 'N/A')}")
            print(f"\nContent: {result.get('content_url', 'N/A')}")
            
            # Display media URLs
            media_urls = result.get('media_urls', {})
            image_urls = media_urls.get('image', [])
            video_urls = media_urls.get('video', [])
            
            if image_urls or video_urls:
                print(f"\n📸 Media Generated:")
                if image_urls:
                    print(f"\n  Images: {len(image_urls)} item(s)")
                    for idx, url in enumerate(image_urls, 1):
                        print(f"    {idx}. {url}")
                if video_urls:
                    print(f"\n  Videos: {len(video_urls)} item(s)")
                    for idx, url in enumerate(video_urls, 1):
                        print(f"    {idx}. {url}")
            else:
                print("\n⚠️  No media generated")
            
            # Display error if present
            if 'error' in result:
                print(f"\n⚠️  Error: {result.get('error')}")
            
            print("\n" + "=" * 60)
            
            # Save result to file
            with open('last_generated_content.json', 'w') as f:
                json.dump(result, f, indent=2)
            print("\n💾 Full result saved to: last_generated_content.json")
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The service might be cold starting or the generation is taking longer than expected.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_health():
    """Quick health check"""
    print("🏥 Health Check...")
    try:
        response = requests.get(f"{SERVICE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Service is healthy\n")
            return True
        else:
            print(f"⚠️  Service returned status {response.status_code}\n")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}\n")
        return False

if __name__ == "__main__":
    # First check health
    if test_health():
        # Then test image generation
        test_image_generation()
    else:
        print("⚠️  Service appears to be down. Skipping image generation test.")
