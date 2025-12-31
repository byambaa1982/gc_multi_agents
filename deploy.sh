#!/bin/bash

# Cloud Run Deployment Script
# Multi-Agent Content Generation System

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cloud Run Deployment Script${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: PROJECT_ID environment variable is not set${NC}"
    echo "Usage: export PROJECT_ID=your-project-id && ./deploy.sh"
    exit 1
fi

# Configuration
REGION=${REGION:-"us-central1"}
SERVICE_NAME=${SERVICE_NAME:-"content-generator"}
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
SERVICE_ACCOUNT="${SERVICE_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Service Name: $SERVICE_NAME"
echo "  Image: $IMAGE_NAME"
echo ""

# Step 1: Enable required APIs
echo -e "${YELLOW}Step 1: Enabling required APIs...${NC}"
gcloud services enable \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  pubsub.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  vision.googleapis.com \
  translate.googleapis.com \
  secretmanager.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  --project=$PROJECT_ID

echo -e "${GREEN}✓ APIs enabled${NC}"

# Step 2: Create service account (if not exists)
echo -e "${YELLOW}Step 2: Setting up service account...${NC}"
if gcloud iam service-accounts describe $SERVICE_ACCOUNT --project=$PROJECT_ID 2>/dev/null; then
    echo "Service account already exists"
else
    gcloud iam service-accounts create $SERVICE_NAME \
        --display-name="Content Generator Service Account" \
        --project=$PROJECT_ID
    echo -e "${GREEN}✓ Service account created${NC}"
fi

# Grant IAM roles
echo -e "${YELLOW}Granting IAM roles...${NC}"
ROLES=(
    "roles/aiplatform.user"
    "roles/datastore.user"
    "roles/storage.admin"
    "roles/pubsub.admin"
    "roles/monitoring.metricWriter"
    "roles/logging.logWriter"
    "roles/secretmanager.secretAccessor"
)

for role in "${ROLES[@]}"; do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SERVICE_ACCOUNT}" \
        --role="$role" \
        --condition=None \
        > /dev/null 2>&1
done

echo -e "${GREEN}✓ IAM roles granted${NC}"

# Step 3: Create GCS bucket (if not exists)
echo -e "${YELLOW}Step 3: Setting up Cloud Storage bucket...${NC}"
BUCKET_NAME="${PROJECT_ID}-content-storage"
if gsutil ls -b gs://$BUCKET_NAME 2>/dev/null; then
    echo "Bucket already exists"
else
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME
    echo -e "${GREEN}✓ Storage bucket created${NC}"
fi

# Step 4: Initialize Firestore (if not exists)
echo -e "${YELLOW}Step 4: Setting up Firestore...${NC}"
if gcloud firestore databases describe --project=$PROJECT_ID 2>/dev/null; then
    echo "Firestore database already exists"
else
    gcloud firestore databases create --region=$REGION --project=$PROJECT_ID
    echo -e "${GREEN}✓ Firestore database created${NC}"
fi

# Step 5: Build container image
echo -e "${YELLOW}Step 5: Building container image...${NC}"
gcloud builds submit --tag $IMAGE_NAME --project=$PROJECT_ID

echo -e "${GREEN}✓ Container image built${NC}"

# Step 6: Deploy to Cloud Run
echo -e "${YELLOW}Step 6: Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
  --service-account $SERVICE_ACCOUNT \
  --project=$PROJECT_ID

echo -e "${GREEN}✓ Deployed to Cloud Run${NC}"

# Step 7: Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)' \
  --project=$PROJECT_ID)

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Successful! 🎉${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Service URL: ${YELLOW}${SERVICE_URL}${NC}"
echo ""
echo "Test your deployment:"
echo -e "  ${YELLOW}curl ${SERVICE_URL}/health${NC}"
echo ""
echo "Generate content:"
echo -e "  ${YELLOW}curl -X POST ${SERVICE_URL}/generate \\${NC}"
echo -e "    ${YELLOW}-H 'Content-Type: application/json' \\${NC}"
echo -e "    ${YELLOW}-d '{\"topic\": \"AI trends in 2024\", \"include_image\": true}'${NC}"
echo ""
echo "View logs:"
echo -e "  ${YELLOW}gcloud logging read \"resource.type=cloud_run_revision\" --limit 50 --project=$PROJECT_ID${NC}"
echo ""
echo "API Documentation:"
echo -e "  ${YELLOW}${SERVICE_URL}/docs${NC}"
echo ""
