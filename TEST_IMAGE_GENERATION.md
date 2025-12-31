# Testing Image Generation on Cloud Run

This guide shows you how to test the deployed content generation service with image creation.

## Prerequisites

- Python 3.9+ installed
- `requests` library (`pip install requests`)
- Service deployed to Cloud Run

## Quick Test

### Method 1: Using the Python Test Script

Run the included test script:

```bash
python test_image_generation.py
```

This will:
1. Check service health
2. Generate content with an image about "a cute robot learning to paint"
3. Display the results
4. Save the full response to `last_generated_content.json`

### Method 2: Using cURL

```bash
curl -X POST "https://content-generator-279772560710.us-central1.run.app/generate/sync" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "a cute robot learning to paint",
    "content_type": "social_media_post",
    "platform": "twitter",
    "media_types": ["image"],
    "metadata": {
      "tone": "friendly",
      "length": "short",
      "hashtags": true
    }
  }'
```

### Method 3: Using Python Requests Directly

```python
import requests
import json

url = "https://content-generator-279772560710.us-central1.run.app/generate/sync"

payload = {
    "topic": "a cute robot learning to paint",
    "content_type": "social_media_post",
    "platform": "twitter",
    "media_types": ["image"],
    "metadata": {
        "tone": "friendly",
        "length": "short",
        "hashtags": True
    }
}

response = requests.post(url, json=payload, timeout=120)

if response.status_code == 200:
    result = response.json()
    print(json.dumps(result, indent=2))
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

## Request Parameters

### Required
- `topic`: The subject for content generation (string, min 3 characters)

### Optional
- `content_type`: Type of content to generate
  - Options: `blog_post`, `article`, `social_media_post`
  - Default: `blog_post`

- `platform`: Target platform
  - Options: `twitter`, `facebook`, `instagram`, `wordpress`, `medium`
  - Default: `wordpress`

- `media_types`: List of media to generate
  - Options: `["image"]`, `["video"]`, `["audio"]`, `["image", "video"]`
  - Default: `[]` (no media)

- `metadata`: Additional options (dict)
  - `tone`: Writing tone (e.g., "friendly", "professional")
  - `length`: Content length ("short", "medium", "long")
  - `hashtags`: Include hashtags (true/false)

## Example Requests

### Simple Text Post (No Image)

```json
{
  "topic": "benefits of morning exercise",
  "content_type": "social_media_post",
  "platform": "twitter"
}
```

### Social Post with Image

```json
{
  "topic": "sunset over mountains",
  "content_type": "social_media_post",
  "platform": "instagram",
  "media_types": ["image"],
  "metadata": {
    "tone": "inspirational",
    "hashtags": true
  }
}
```

### Blog Post with Image

```json
{
  "topic": "getting started with AI",
  "content_type": "blog_post",
  "platform": "wordpress",
  "media_types": ["image"],
  "metadata": {
    "tone": "educational",
    "length": "medium"
  }
}
```

### Multiple Media Types

```json
{
  "topic": "product demo",
  "content_type": "social_media_post",
  "platform": "facebook",
  "media_types": ["image", "video"],
  "metadata": {
    "tone": "engaging"
  }
}
```

## Expected Response

Successful response (HTTP 200):

```json
{
  "status": "completed",
  "message": "Content generated successfully",
  "project_id": "content_20231231_123456",
  "content_url": "gs://bucket/path/to/content.txt",
  "media_urls": {
    "image": [
      "gs://bucket/images/generated_image.png"
    ],
    "video": []
  }
}
```

## Response Fields

- `status`: Generation status (`processing`, `completed`, or `failed`)
- `message`: Human-readable message
- `project_id`: Unique content ID for tracking
- `content_url`: Google Cloud Storage URL for the generated text
- `media_urls`: Object containing arrays of generated media URLs by type

## Error Responses

### Budget Exceeded (HTTP 429)

```json
{
  "detail": "Budget exceeded. Used 95.2% of monthly budget."
}
```

### Invalid Request (HTTP 422)

```json
{
  "detail": [
    {
      "loc": ["body", "topic"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Server Error (HTTP 500)

```json
{
  "detail": "Internal server error: <error message>"
}
```

## Endpoints

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "budget_status": {
    "total_spent": 0.0,
    "total_budget": 100.0,
    "percentage_used": 0.0,
    "categories": {...}
  }
}
```

### `GET /budget`
Get current budget status

**Response:**
```json
{
  "total_spent": 2.45,
  "total_budget": 100.0,
  "percentage_used": 2.45,
  "categories": {
    "vertex_ai": { "spent": 1.20, "budget": 30.0, "percentage": 4.0 },
    "storage": { "spent": 0.05, "budget": 5.0, "percentage": 1.0 }
  },
  "is_throttled": false
}
```

### `POST /generate`
Generate content asynchronously (returns immediately)

**Use when:** You want to trigger generation and check results later

**Response:**
```json
{
  "status": "processing",
  "message": "Content generation started. Check logs for progress.",
  "project_id": null
}
```

### `POST /generate/sync`
Generate content synchronously (waits for completion)

**Use when:** You need the result immediately

**Timeout:** 5 minutes maximum

## Troubleshooting

### Request Times Out

- The first request after deployment may be slow (cold start)
- Image generation takes 20-40 seconds
- Video generation takes 1-2 minutes
- Use `/generate` (async) for long operations

### Service Returns 500 Error

1. Check Cloud Run logs:
   ```bash
   gcloud run logs read content-generator --region us-central1
   ```

2. Verify secrets are configured:
   ```bash
   gcloud secrets list
   ```

3. Check service account permissions:
   ```bash
   gcloud projects get-iam-policy datalogichub-461612 \
     --flatten="bindings[].members" \
     --filter="bindings.members:content-generator@datalogichub-461612.iam.gserviceaccount.com"
   ```

### Budget Exceeded

Update budget limits:

```bash
# Edit src/infrastructure/budget_controller.py
# Or set environment variable:
gcloud run services update content-generator \
  --region us-central1 \
  --set-env-vars MONTHLY_BUDGET=200
```

## Testing Different Scenarios

### Test 1: Simple Text Generation
```python
# No media, quick response
payload = {"topic": "hello world", "content_type": "social_media_post"}
```

### Test 2: Image Generation
```python
# Single image, ~30 seconds
payload = {
    "topic": "beautiful landscape",
    "media_types": ["image"]
}
```

### Test 3: Multiple Media
```python
# Image + video, ~90 seconds
payload = {
    "topic": "product demo",
    "media_types": ["image", "video"]
}
```

### Test 4: Different Platforms
```python
# Test Twitter formatting
payload = {"topic": "AI news", "platform": "twitter"}

# Test Instagram formatting
payload = {"topic": "travel photo", "platform": "instagram"}
```

## Monitoring

### View Real-Time Logs

```bash
gcloud run logs tail content-generator --region us-central1
```

### Check Resource Usage

```bash
gcloud run services describe content-generator --region us-central1
```

### View Metrics in Console

https://console.cloud.google.com/run/detail/us-central1/content-generator/metrics

## Next Steps

1. **Test different content types** - Try blog posts, articles, social media
2. **Test media generation** - Verify image, video, audio creation
3. **Monitor costs** - Check budget endpoint regularly
4. **Scale testing** - Send multiple requests to test auto-scaling
5. **Publishing** - Enable `publish: true` to test social media posting

## Support

- View documentation: `GET /docs` endpoint
- Check health: `GET /health` endpoint
- Review logs: Cloud Run console or `gcloud run logs`
