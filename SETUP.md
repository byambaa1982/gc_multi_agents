"""
Setup and Deployment Guide

This document provides instructions for setting up and deploying the
Multi-Agent Content Generation System on Google Cloud Platform.
"""

# Phase 0: Setup and Testing Guide

## Prerequisites

1. **Google Cloud Project**
   - Create a GCP project at [console.cloud.google.com](https://console.cloud.google.com)
   - Enable billing
   - Note your project ID

2. **Required APIs**
   ```bash
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable firestore.googleapis.com
   gcloud services enable logging.googleapis.com
   ```

3. **Authentication**
   ```bash
   # Authenticate with GCP
   gcloud auth login
   
   # Set application default credentials
   gcloud auth application-default login
   
   # Set project
   gcloud config set project YOUR_PROJECT_ID
   ```

## Local Setup

### 1. Clone and Install Dependencies

```bash
cd multi_agent_content_generation

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your project details
# Required variables:
# GOOGLE_CLOUD_PROJECT=your-project-id
# FIRESTORE_COLLECTION=content_projects
# VERTEX_AI_LOCATION=us-central1
```

### 3. Initialize Firestore

```bash
# Create Firestore database (if not exists)
gcloud firestore databases create --location=us-central1
```

## Testing the System

### 1. Run Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_agents.py -v
```

### 2. Test with Example Script

```bash
# Run the example
python examples/generate_blog_post.py
```

### 3. Test with Main CLI

```bash
# Generate content for a topic
python main.py --topic "Introduction to Machine Learning"

# Custom parameters
python main.py \
  --topic "Cloud Computing Best Practices" \
  --tone "professional and technical" \
  --words 1500

# Get existing project
python main.py --project-id PROJECT_ID
```

## Verifying the Setup

### 1. Check Firestore Data

```bash
# List all projects
gcloud firestore collections list

# Query documents
gcloud firestore documents list content_projects
```

### 2. Check Logs

```bash
# View logs in Cloud Console
gcloud logging read "resource.type=global" --limit 50 --format json
```

### 3. Monitor Costs

```bash
# Check current month costs
gcloud billing projects describe YOUR_PROJECT_ID
```

Or visit [Cloud Console Billing](https://console.cloud.google.com/billing)

## Troubleshooting

### Issue: "GOOGLE_CLOUD_PROJECT not set"

**Solution:**
```bash
# Ensure .env file exists and has correct values
cat .env

# Or set environment variable directly
export GOOGLE_CLOUD_PROJECT=your-project-id  # Mac/Linux
$env:GOOGLE_CLOUD_PROJECT="your-project-id"  # PowerShell
```

### Issue: "API not enabled"

**Solution:**
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable logging.googleapis.com
```

### Issue: "Permission denied"

**Solution:**
- Ensure your account has necessary roles:
  - Vertex AI User
  - Firestore User
  - Logs Writer

```bash
# Grant roles (as project owner)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member=user:YOUR_EMAIL \
  --role=roles/aiplatform.user

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member=user:YOUR_EMAIL \
  --role=roles/datastore.user
```

### Issue: "Firestore not initialized"

**Solution:**
```bash
# Create Firestore database
gcloud firestore databases create --location=us-central1
```

## Next Steps

Once Phase 0 is working:

1. **Test with different topics** to validate quality
2. **Monitor costs** to understand pricing
3. **Review generated content** for quality assurance
4. **Prepare for Phase 1** (Pub/Sub, Editor agent, SEO agent)

## Phase 0 Success Criteria

✅ System can generate 1 quality blog post end-to-end
✅ Research agent returns structured findings
✅ Content agent produces 800-2000 word posts
✅ Cost tracking is accurate
✅ Errors are logged properly
✅ Data is persisted in Firestore

## Cost Estimates (Phase 0)

Per blog post generation:
- Research: $0.03 - $0.05
- Content Generation: $0.08 - $0.12
- Firestore: < $0.01
- **Total: ~$0.12 - $0.18 per post**

Testing costs (10 posts): ~$1.50 - $2.00
