# Quick Start Guide for Cloud Run Deployment

## Prerequisites

1. **Google Cloud Project with billing enabled**
2. **gcloud CLI installed and authenticated**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

## Deployment Steps

### Option 1: Using PowerShell (Windows)

```powershell
# Set your project ID
$env:PROJECT_ID = "your-project-id"

# Optional: Set region (default: us-central1)
$env:REGION = "us-central1"

# Run deployment script
.\deploy.ps1
```

### Option 2: Using Bash (Linux/Mac/WSL)

```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Optional: Set region (default: us-central1)
export REGION="us-central1"

# Make script executable
chmod +x deploy.sh

# Run deployment script
./deploy.sh
```

### Option 3: Manual Deployment

```bash
# 1. Set project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# 2. Build container
gcloud builds submit --tag gcr.io/$PROJECT_ID/content-generator

# 3. Deploy to Cloud Run
gcloud run deploy content-generator \
  --image gcr.io/$PROJECT_ID/content-generator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID"
```

## Testing Your Deployment

### 1. Health Check
```bash
curl https://YOUR_SERVICE_URL/health
```

### 2. Generate Content (Async)
```bash
curl -X POST https://YOUR_SERVICE_URL/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "The Future of AI",
    "tone": "professional and engaging",
    "words": 1200,
    "include_image": true,
    "include_video": false
  }'
```

### 3. Generate Content (Sync)
```bash
curl -X POST https://YOUR_SERVICE_URL/generate/sync \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Cloud Computing Trends",
    "tone": "technical",
    "words": 800,
    "include_image": true
  }'
```

### 4. Check Budget Status
```bash
curl https://YOUR_SERVICE_URL/budget
```

### 5. View API Documentation
Open in browser: `https://YOUR_SERVICE_URL/docs`

## Monitoring

### View Logs
```bash
gcloud logging read "resource.type=cloud_run_revision" \
  --limit 50 \
  --project=$PROJECT_ID
```

### View Metrics
```bash
# Go to Cloud Console > Cloud Run > YOUR_SERVICE > Metrics
```

### View Monitoring Dashboard
```bash
# Go to Cloud Console > Monitoring > Dashboards
```

## Configuration

### Environment Variables

Set these in Cloud Run:
```bash
gcloud run services update content-generator \
  --set-env-vars "MONTHLY_BUDGET=250,WARNING_THRESHOLD=0.80" \
  --region us-central1
```

### Secrets (Social Media Credentials)

Store sensitive data in Secret Manager:
```bash
# Create secrets
echo -n "YOUR_FACEBOOK_TOKEN" | gcloud secrets create facebook-access-token --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding facebook-access-token \
  --member="serviceAccount:content-generator@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Update Cloud Run to use secrets
gcloud run services update content-generator \
  --set-secrets="FACEBOOK_ACCESS_TOKEN=facebook-access-token:latest" \
  --region us-central1
```

## Troubleshooting

### Build Fails
```bash
# Check build logs
gcloud builds list --limit=5

# View specific build
gcloud builds log BUILD_ID
```

### Deployment Fails
```bash
# Check service status
gcloud run services describe content-generator \
  --region us-central1

# View deployment logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit 20
```

### Service Returns Errors
```bash
# Check recent errors
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit 20

# Check budget status
curl https://YOUR_SERVICE_URL/budget
```

## Cost Optimization

### Current Setup
- **Min instances**: 0 (scales to zero when idle)
- **Max instances**: 10
- **Memory**: 2Gi
- **CPU**: 2

### Reduce Costs
```bash
# Scale down for development
gcloud run services update content-generator \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 5 \
  --region us-central1
```

### Increase Performance
```bash
# Scale up for production
gcloud run services update content-generator \
  --memory 4Gi \
  --cpu 4 \
  --max-instances 20 \
  --min-instances 1 \
  --region us-central1
```

## Next Steps

1. **Set up monitoring alerts**
2. **Configure social media credentials**
3. **Set monthly budget limits**
4. **Create CI/CD pipeline**
5. **Load testing**

## Support

- [Architecture Guide](ARCHITECTURE.md)
- [Production Deployment Guide](PRODUCTION_DEPLOYMENT_GUIDE.md)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Console](https://console.cloud.google.com)
