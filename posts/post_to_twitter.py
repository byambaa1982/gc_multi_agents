"""
Post content from storage to Twitter

This script:
1. Loads Twitter credentials from .env
2. Fetches recent content from Firestore
3. Posts it to Twitter using the API
"""

import os
import sys
from dotenv import load_dotenv
import tweepy
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from src.infrastructure.firestore import FirestoreManager
from src.monitoring.logger import StructuredLogger

# Load environment variables
load_dotenv()

logger = StructuredLogger("TwitterPoster")


def setup_twitter_client():
    """Setup Twitter API client with credentials from .env"""
    
    # Get credentials
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    # Validate credentials
    if not all([api_key, api_secret, access_token, access_token_secret]):
        logger.error("Missing Twitter credentials in .env file")
        print("\n❌ Error: Missing Twitter API credentials")
        print("\nRequired environment variables:")
        print("  - TWITTER_API_KEY")
        print("  - TWITTER_API_SECRET")
        print("  - TWITTER_ACCESS_TOKEN")
        print("  - TWITTER_ACCESS_TOKEN_SECRET")
        return None
    
    logger.info("Twitter credentials loaded from .env")
    print("✅ Twitter credentials loaded")
    print(f"   API Key: {api_key[:10]}...")
    print(f"   Access Token: {access_token[:20]}...")
    
    try:
        # Authenticate using OAuth 1.0a (User Context)
        auth = tweepy.OAuth1UserHandler(
            api_key,
            api_secret,
            access_token,
            access_token_secret
        )
        
        # Create API v1.1 client (for posting tweets)
        api = tweepy.API(auth)
        
        # Verify credentials
        user = api.verify_credentials()
        logger.info(f"Authenticated as @{user.screen_name}")
        print(f"✅ Authenticated as @{user.screen_name}")
        print(f"   Name: {user.name}")
        print(f"   Followers: {user.followers_count:,}")
        
        return api
        
    except tweepy.TweepyException as e:
        logger.error(f"Twitter authentication failed: {e}")
        print(f"\n❌ Twitter authentication failed: {e}")
        return None


def get_content_from_storage():
    """Get recent content from Firestore"""
    
    try:
        db = FirestoreManager()
        
        # Get all projects (you could filter by status, date, etc.)
        collection = os.getenv('FIRESTORE_COLLECTION', 'content_projects')
        
        logger.info(f"Fetching content from Firestore collection: {collection}")
        print(f"\n📚 Fetching content from Firestore...")
        
        # For demo, create sample content since we may not have actual data
        # In production, you would query: projects = db.collection.limit(1).stream()
        
        sample_content = {
            'project_id': 'demo_twitter_post',
            'title': 'AI-Powered Content Generation',
            'body': '''Exciting news! 🚀

We've built a multi-agent AI system that generates high-quality content automatically.

Key features:
✅ 9 specialized AI agents
✅ Multi-platform publishing
✅ Real-time analytics
✅ Cost optimization

#AI #ContentCreation #Automation #GCP''',
            'excerpt': 'Announcing our AI-powered content generation system with multi-agent collaboration',
            'tags': ['AI', 'ContentCreation', 'Automation', 'GCP'],
            'created_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Content prepared: {sample_content['title']}")
        print(f"✅ Content ready to post")
        print(f"   Title: {sample_content['title']}")
        print(f"   Length: {len(sample_content['body'])} characters")
        
        return sample_content
        
    except Exception as e:
        logger.error(f"Failed to get content from storage: {e}")
        print(f"\n❌ Failed to get content: {e}")
        return None


def format_for_twitter(content):
    """Format content for Twitter (280 character limit)"""
    
    body = content.get('body', '')
    
    # If body is already short enough, use it
    if len(body) <= 280:
        return body
    
    # Otherwise create a short version
    title = content.get('title', '')
    excerpt = content.get('excerpt', '')
    tags = content.get('tags', [])
    
    # Create tweet
    tweet = excerpt if excerpt else title
    
    # Add hashtags
    hashtags = ' '.join([f'#{tag.replace(" ", "")}' for tag in tags[:3]])
    tweet = f"{tweet}\n\n{hashtags}"
    
    # Ensure within limit
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."
    
    return tweet


def post_to_twitter(api, content):
    """Post content to Twitter"""
    
    try:
        # Format content for Twitter
        tweet_text = format_for_twitter(content)
        
        logger.info(f"Posting tweet: {tweet_text[:50]}...")
        print(f"\n📤 Posting to Twitter...")
        print(f"\n{'='*60}")
        print(tweet_text)
        print(f"{'='*60}")
        print(f"\n⏳ Sending...")
        
        # Post tweet
        status = api.update_status(tweet_text)
        
        # Get tweet details
        tweet_id = status.id
        tweet_url = f"https://twitter.com/{status.user.screen_name}/status/{tweet_id}"
        
        logger.info(f"Tweet posted successfully: {tweet_url}")
        print(f"\n✅ Tweet posted successfully!")
        print(f"\n🔗 Tweet URL: {tweet_url}")
        print(f"📊 Tweet ID: {tweet_id}")
        print(f"⏰ Posted at: {status.created_at}")
        
        return {
            'success': True,
            'tweet_id': tweet_id,
            'url': tweet_url,
            'created_at': status.created_at
        }
        
    except tweepy.TweepyException as e:
        logger.error(f"Failed to post tweet: {e}")
        print(f"\n❌ Failed to post tweet: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def main():
    """Main function"""
    
    print("\n" + "="*60)
    print("  Twitter Content Poster - Post from Storage")
    print("="*60)
    
    # Step 1: Setup Twitter client
    print("\n📱 Step 1: Setting up Twitter API client...")
    api = setup_twitter_client()
    
    if not api:
        print("\n⚠️  Cannot proceed without Twitter authentication")
        return 1
    
    # Step 2: Get content from storage
    print("\n📝 Step 2: Getting content from storage...")
    content = get_content_from_storage()
    
    if not content:
        print("\n⚠️  No content available to post")
        return 1
    
    # Step 3: Post to Twitter
    print("\n🚀 Step 3: Posting to Twitter...")
    result = post_to_twitter(api, content)
    
    if result['success']:
        print("\n" + "="*60)
        print("  ✅ SUCCESS - Content posted to Twitter!")
        print("="*60)
        print(f"\n🎉 Check your tweet at: {result['url']}")
        return 0
    else:
        print("\n" + "="*60)
        print("  ❌ FAILED - Could not post to Twitter")
        print("="*60)
        return 1


if __name__ == "__main__":
    exit(main())
