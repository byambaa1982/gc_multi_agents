"""
Simple Twitter Poster - Post content directly to Twitter
No dependencies on infrastructure modules
"""

import os
from dotenv import load_dotenv
import tweepy
from datetime import datetime

# Load environment variables
load_dotenv()


def post_to_twitter():
    """Post content to Twitter using API credentials"""
    
    print("\n" + "="*70)
    print("  📱 Twitter Content Poster")
    print("="*70)
    
    # Get credentials from .env
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    # Validate credentials
    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("\n❌ Error: Missing Twitter credentials in .env file")
        print("\nPlease ensure these variables are set:")
        print("  - TWITTER_API_KEY")
        print("  - TWITTER_API_SECRET")
        print("  - TWITTER_ACCESS_TOKEN")
        print("  - TWITTER_ACCESS_TOKEN_SECRET")
        return
    
    print("\n✅ Step 1: Credentials loaded from .env")
    print(f"   API Key: {api_key[:10]}...")
    print(f"   Access Token: {access_token[:20]}...")
    
    try:
        # Authenticate
        print("\n🔐 Step 2: Authenticating with Twitter...")
        auth = tweepy.OAuth1UserHandler(
            api_key,
            api_secret,
            access_token,
            access_token_secret
        )
        
        api = tweepy.API(auth)
        
        # Verify credentials
        user = api.verify_credentials()
        print(f"✅ Authenticated as @{user.screen_name}")
        print(f"   Name: {user.name}")
        print(f"   Followers: {user.followers_count:,}")
        
        # Create tweet content
        print("\n📝 Step 3: Preparing content...")
        
        tweet_text = """🚀 Exciting Progress Update!

Just completed Phase 4 of our multi-agent content generation system:

✅ Publisher Agent - Multi-platform publishing
✅ Analytics Dashboard - 50+ metrics tracked  
✅ User Management - RBAC with 5 roles
✅ Performance Monitoring - Real-time tracking

Building the future of AI-powered content! 🤖

#AI #ContentGeneration #Automation #MachineLearning"""
        
        print(f"   Tweet length: {len(tweet_text)} characters")
        print("\n" + "─"*70)
        print(tweet_text)
        print("─"*70)
        
        # Post tweet
        print("\n📤 Step 4: Posting to Twitter...")
        status = api.update_status(tweet_text)
        
        # Get tweet details
        tweet_id = status.id
        tweet_url = f"https://twitter.com/{status.user.screen_name}/status/{tweet_id}"
        
        print(f"\n✅ SUCCESS! Tweet posted!")
        print(f"\n🔗 Tweet URL: {tweet_url}")
        print(f"📊 Tweet ID: {tweet_id}")
        print(f"⏰ Posted at: {status.created_at}")
        print(f"💬 Text: {status.text[:50]}...")
        
        print("\n" + "="*70)
        print("  ✨ Check your tweet on Twitter!")
        print("="*70)
        
    except tweepy.TweepyException as e:
        print(f"\n❌ Twitter Error: {e}")
        
        if "401" in str(e):
            print("\n💡 Tip: Error 401 means authentication failed.")
            print("   Please check your Twitter API credentials in .env")
        elif "403" in str(e):
            print("\n💡 Tip: Error 403 means forbidden.")
            print("   Your app might not have write permissions.")
        elif "duplicate" in str(e).lower():
            print("\n💡 Tip: This tweet was already posted.")
            print("   Try posting different content!")
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")


if __name__ == "__main__":
    post_to_twitter()
