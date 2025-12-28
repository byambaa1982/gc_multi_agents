#!/usr/bin/env python3
"""
Simple Facebook Page Poster
Posts a message to Эхлэл (Ehlel) Facebook page
Based on: github.com/byambaa1982/facebook
"""

import json
import requests
import os

# Эхлэл page ID from your system_user.json
EHLEL_PAGE_ID = "682084288324866"

def load_page_token():
    """
    Load page access token for Эхлэл from system_user.json
    
    Returns:
        tuple: (page_id, page_token, page_name)
    """
    # Check if we have the token file locally
    local_paths = [
        'system_users.json',
        'system_user.json',
        'routes/system_user.json',
        os.path.expanduser('~/.facebook/system_user.json')
    ]
    
    for file_path in local_paths:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Look for Эхлэл page in facebook_pages array
                for page in data.get('facebook_pages', []):
                    if page.get('id') == EHLEL_PAGE_ID:
                        return (
                            page['id'],
                            page['access_token'],
                            page.get('name', 'Эхлэл')
                        )
                
                print(f"⚠️  Эхлэл page not found in {file_path}")
            except Exception as e:
                print(f"⚠️  Error reading {file_path}: {e}")
    
    return None, None, None

def post_to_facebook_page(page_id, access_token, message):
    """
    Post a message to a Facebook page
    
    Args:
        page_id: Facebook page ID
        access_token: Page access token
        message: Message to post
        
    Returns:
        dict: Response from Facebook API
    """
    url = f"https://graph.facebook.com/v23.0/{page_id}/feed"
    
    payload = {
        'message': message,
        'access_token': access_token
    }
    
    try:
        response = requests.post(url, data=payload, timeout=30)
        
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {
                'success': False,
                'error': response.json(),
                'status_code': response.status_code
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    """Main function to post to Эхлэл page"""
    print("=" * 70)
    print("FACEBOOK PAGE POSTER - Эхлэл")
    print("=" * 70)
    
    # Load page token
    print("\n1. Loading page credentials...")
    page_id, page_token, page_name = load_page_token()
    
    if not page_token:
        print("❌ Could not find Эхлэл page credentials!")
        print("\nPlease ensure:")
        print("  - routes/system_user.json exists")
        print("  - It contains facebook_pages array")
        print(f"  - Эхлэл page (ID: {EHLEL_PAGE_ID}) is in the array")
        print("\nOr provide credentials manually:")
        page_id = input("\nEnter Page ID (or press Enter to exit): ").strip()
        if not page_id:
            return
        page_token = input("Enter Page Access Token: ").strip()
        if not page_token:
            return
        page_name = "Эхлэл"
    
    print(f"   ✓ Loaded credentials for: {page_name}")
    print(f"   Page ID: {page_id}")
    print(f"   Token: {page_token[:30]}...")
    
    # Verify token works
    print("\n2. Verifying token...")
    verify_url = "https://graph.facebook.com/v23.0/me"
    verify_response = requests.get(verify_url, params={'access_token': page_token})
    
    if verify_response.status_code == 200:
        page_info = verify_response.json()
        print(f"   ✓ Token is valid for: {page_info.get('name', 'Unknown')}")
    else:
        print(f"   ❌ Token verification failed: {verify_response.json()}")
        return
    
    # Post message
    message = "Hi"
    print(f"\n3. Posting message to {page_name}...")
    print(f"   Message: \"{message}\"")
    
    result = post_to_facebook_page(page_id, page_token, message)
    
    if result.get('success'):
        post_id = result['data'].get('id')
        print("\n" + "=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"Post ID: {post_id}")
        print(f"\nView your post at:")
        print(f"https://www.facebook.com/{post_id}")
    else:
        print("\n" + "=" * 70)
        print("❌ FAILED")
        print("=" * 70)
        print(f"Status Code: {result.get('status_code', 'N/A')}")
        print(f"Error: {result.get('error', 'Unknown error')}")
        
        # Provide helpful tips
        print("\n💡 Troubleshooting:")
        print("  1. Check if token has expired")
        print("  2. Verify you have pages_manage_posts permission")
        print("  3. Ensure page ID is correct")
        print("  4. Try regenerating token at facebook.com/developers")

if __name__ == '__main__':
    main()
