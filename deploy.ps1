# Cloud Run Deployment Script (PowerShell)
# Multi-Agent Content Generation System

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Green
Write-Host "Cloud Run Deployment Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Check if PROJECT_ID is set
if (-not $env:PROJECT_ID) {
    Write-Host "Error: PROJECT_ID environment variable is not set" -ForegroundColor Red
    Write-Host "Usage: `$env:PROJECT_ID='your-project-id'; .\deploy.ps1"
    exit 1
}

# Configuration
$PROJECT_ID = $env:PROJECT_ID
$REGION = if ($env:REGION) { $env:REGION } else { "us-central1" }
$SERVICE_NAME = if ($env:SERVICE_NAME) { $env:SERVICE_NAME } else { "content-generator" }
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"
$SERVICE_ACCOUNT = "$SERVICE_NAME@$PROJECT_ID.iam.gserviceaccount.com"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Project ID: $PROJECT_ID"
Write-Host "  Region: $REGION"
Write-Host "  Service Name: $SERVICE_NAME"
Write-Host "  Image: $IMAGE_NAME"
Write-Host ""

# Step 1: Enable required APIs
Write-Host "Step 1: Enabling required APIs..." -ForegroundColor Yellow
$apis = @(
    "aiplatform.googleapis.com",
    "firestore.googleapis.com",
    "storage.googleapis.com",
    "pubsub.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "vision.googleapis.com",
    "translate.googleapis.com",
    "secretmanager.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com"
)

foreach ($api in $apis) {
    gcloud services enable $api --project=$PROJECT_ID
}

Write-Host "✓ APIs enabled" -ForegroundColor Green

# Step 2: Create service account (if not exists)
Write-Host "Step 2: Setting up service account..." -ForegroundColor Yellow
$saExists = gcloud iam service-accounts describe $SERVICE_ACCOUNT --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -ne 0) {
    gcloud iam service-accounts create $SERVICE_NAME `
        --display-name="Content Generator Service Account" `
        --project=$PROJECT_ID
    Write-Host "✓ Service account created" -ForegroundColor Green
} else {
    Write-Host "Service account already exists"
}

# Grant IAM roles
Write-Host "Granting IAM roles..." -ForegroundColor Yellow
$roles = @(
    "roles/aiplatform.user",
    "roles/datastore.user",
    "roles/storage.admin",
    "roles/pubsub.admin",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter",
    "roles/secretmanager.secretAccessor"
)

foreach ($role in $roles) {
    gcloud projects add-iam-policy-binding $PROJECT_ID `
        --member="serviceAccount:$SERVICE_ACCOUNT" `
        --role="$role" `
        --condition=None 2>$null | Out-Null
}

Write-Host "✓ IAM roles granted" -ForegroundColor Green

# Step 3: Create GCS bucket (if not exists)
Write-Host "Step 3: Setting up Cloud Storage bucket..." -ForegroundColor Yellow
$BUCKET_NAME = "$PROJECT_ID-content-storage"
$bucketExists = gsutil ls -b gs://$BUCKET_NAME 2>$null
if ($LASTEXITCODE -ne 0) {
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME
    Write-Host "✓ Storage bucket created" -ForegroundColor Green
} else {
    Write-Host "Bucket already exists"
}

# Step 4: Initialize Firestore (if not exists)
Write-Host "Step 4: Setting up Firestore..." -ForegroundColor Yellow
$dbExists = gcloud firestore databases describe --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -ne 0) {
    gcloud firestore databases create --region=$REGION --project=$PROJECT_ID
    Write-Host "✓ Firestore database created" -ForegroundColor Green
} else {
    Write-Host "Firestore database already exists"
}

# Step 5: Build container image
Write-Host "Step 5: Building container image..." -ForegroundColor Yellow
gcloud builds submit --tag $IMAGE_NAME --project=$PROJECT_ID

Write-Host "✓ Container image built" -ForegroundColor Green

# Step 6: Deploy to Cloud Run
Write-Host "Step 6: Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
  --image $IMAGE_NAME `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --memory 2Gi `
  --cpu 2 `
  --timeout 3600 `
  --max-instances 10 `
  --min-instances 0 `
  --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GCS_BUCKET_NAME=${PROJECT_ID}-content-storage,VERTEX_AI_LOCATION=us-central1,FIRESTORE_COLLECTION=content_projects" `
  --set-secrets "TWITTER_API_KEY=twitter-api-key:latest,TWITTER_API_SECRET=twitter-api-secret:latest,TWITTER_ACCESS_TOKEN=twitter-access-token:latest,TWITTER_ACCESS_TOKEN_SECRET=twitter-access-token-secret:latest" `
  --service-account $SERVICE_ACCOUNT `
  --project=$PROJECT_ID

Write-Host "✓ Deployed to Cloud Run" -ForegroundColor Green

# Step 7: Get service URL
$SERVICE_URL = gcloud run services describe $SERVICE_NAME `
  --platform managed `
  --region $REGION `
  --format 'value(status.url)' `
  --project=$PROJECT_ID

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment Successful! 🎉" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Service URL: $SERVICE_URL" -ForegroundColor Yellow
Write-Host ""
Write-Host "Test your deployment:"
Write-Host "  curl $SERVICE_URL/health" -ForegroundColor Yellow
Write-Host ""
Write-Host "Generate content:"
Write-Host "  curl -X POST $SERVICE_URL/generate ``" -ForegroundColor Yellow
Write-Host "    -H 'Content-Type: application/json' ``" -ForegroundColor Yellow
Write-Host "    -d '{\"topic\": \"AI trends in 2024\", \"include_image\": true}'" -ForegroundColor Yellow
Write-Host ""
Write-Host "View logs:"
Write-Host "  gcloud logging read 'resource.type=cloud_run_revision' --limit 50 --project=$PROJECT_ID" -ForegroundColor Yellow
Write-Host ""
Write-Host "API Documentation:"
Write-Host "  $SERVICE_URL/docs" -ForegroundColor Yellow
Write-Host ""
