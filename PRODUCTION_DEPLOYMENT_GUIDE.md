# Production Deployment Guide

## 🎯 System Status
✅ **Phase 5 Complete** - All tests passing (100% success rate)  
✅ **Production Ready** - All core features validated  
⏭️ **Next Step** - Deploy to production environment

---

## 📋 Pre-Deployment Checklist

### ✅ Phase Completion
- [x] Phase 1: Core Infrastructure (Firestore, Storage, Pub/Sub)
- [x] Phase 2: Agent Implementation (6 specialized agents)
- [x] Phase 3: Media Generation (Image, Video, Audio)
- [x] Phase 4: Content Publishing (Facebook, Twitter)
- [x] Phase 5: Optimization & Security

### ✅ Testing
- [x] Unit tests for Phase 1-5 components
- [x] Integration tests for complete workflow
- [x] Performance validation (latency, throughput, resource usage)
- [x] Security validation (input validation, rate limiting, encryption)
- [x] Budget tracking and cost prediction

### ⏹️ Production Requirements (To Do)
- [ ] GCP project configured with billing enabled
- [ ] Service account with proper IAM permissions
- [ ] Environment variables configured
- [ ] Secrets stored securely (Secret Manager)
- [ ] Monitoring dashboards set up
- [ ] Alerting policies configured
- [ ] CI/CD pipeline established
- [ ] Backup and disaster recovery plan

---

## 🚀 Deployment Options

### Option 1: Cloud Run (Recommended for MVP)
**Best for:** Serverless, auto-scaling, pay-per-use

**Pros:**
- Zero infrastructure management
- Auto-scales from 0 to N instances
- Pay only for actual usage
- Built-in HTTPS endpoints
- Easy rollbacks

**Cons:**
- 60-minute request timeout
- Cold start latency
- Limited persistent storage

**Cost Estimate:** $5-50/month (depends on usage)

**Deployment Steps:**
```bash
# 1. Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/content-generator

# 2. Deploy to Cloud Run
gcloud run deploy content-generator \
  --image gcr.io/YOUR_PROJECT_ID/content-generator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID" \
  --service-account YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

---

### Option 2: Google Kubernetes Engine (GKE)
**Best for:** High traffic, complex deployments, microservices

**Pros:**
- Full control over cluster
- No request timeouts
- Advanced networking and load balancing
- Can run background jobs

**Cons:**
- More complex setup
- Higher minimum cost
- Requires Kubernetes knowledge

**Cost Estimate:** $100-500/month (minimum cluster + workloads)

**Deployment Steps:**
```bash
# 1. Create GKE cluster
gcloud container clusters create content-generator-cluster \
  --region us-central1 \
  --num-nodes 2 \
  --machine-type e2-medium \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 5

# 2. Deploy application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

---

### Option 3: Compute Engine VM
**Best for:** Full control, custom configurations, persistent workloads

**Pros:**
- Complete control over OS and environment
- No request timeouts
- Persistent local storage
- Can run 24/7 background jobs

**Cons:**
- Manual scaling
- OS and security patch management
- Higher operational overhead

**Cost Estimate:** $50-200/month (depending on VM size)

**Deployment Steps:**
```bash
# 1. Create VM instance
gcloud compute instances create content-generator \
  --zone us-central1-a \
  --machine-type e2-medium \
  --image-family ubuntu-2204-lts \
  --image-project ubuntu-os-cloud \
  --boot-disk-size 50GB \
  --service-account YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com

# 2. SSH into VM and deploy
gcloud compute ssh content-generator --zone us-central1-a
# Then install dependencies, clone repo, run application
```

---

## 🔧 Configuration Steps

### 1. GCP Project Setup

```bash
# Set project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  pubsub.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  vision.googleapis.com \
  translate.googleapis.com \
  secretmanager.googleapis.com

# Verify APIs enabled
gcloud services list --enabled
```

### 2. Service Account Setup

```bash
# Create service account
gcloud iam service-accounts create content-generator \
  --display-name="Content Generator Service Account"

export SA_EMAIL="content-generator@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant required roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/pubsub.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/monitoring.metricWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

# Create and download key (for local development only)
gcloud iam service-accounts keys create ~/key.json \
  --iam-account=$SA_EMAIL
```

### 3. Environment Variables

Create `.env.production` file:
```bash
# GCP Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Budget Configuration
MONTHLY_BUDGET=250.00
WARNING_THRESHOLD=0.80
CRITICAL_THRESHOLD=0.95
AUTO_THROTTLE_ENABLED=true

# Performance Thresholds
LATENCY_THRESHOLD_MS=200
ERROR_RATE_THRESHOLD=0.05
CPU_THRESHOLD=0.80
MEMORY_THRESHOLD=0.85

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=100
BURST_LIMIT=20

# Social Media (store in Secret Manager, not in .env file!)
# FACEBOOK_ACCESS_TOKEN=your_token_here
# FACEBOOK_PAGE_ID=your_page_id
# TWITTER_API_KEY=your_key_here
# TWITTER_API_SECRET=your_secret_here
# TWITTER_ACCESS_TOKEN=your_token_here
# TWITTER_ACCESS_SECRET=your_secret_here

# Model Configuration
DEFAULT_MODEL=gemini-1.5-flash
TEMPERATURE=0.7
MAX_OUTPUT_TOKENS=2048

# Storage
GCS_BUCKET=your-project-id-content-storage
```

### 4. Secret Manager Setup

```bash
# Store sensitive credentials in Secret Manager
echo -n "YOUR_FACEBOOK_ACCESS_TOKEN" | \
  gcloud secrets create facebook-access-token --data-file=-

echo -n "YOUR_TWITTER_API_KEY" | \
  gcloud secrets create twitter-api-key --data-file=-

echo -n "YOUR_TWITTER_API_SECRET" | \
  gcloud secrets create twitter-api-secret --data-file=-

# Grant service account access to secrets
gcloud secrets add-iam-policy-binding facebook-access-token \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding twitter-api-key \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"
```

### 5. Firestore Setup

```bash
# Create Firestore database (if not exists)
gcloud firestore databases create --region=us-central1

# Create indexes (if needed)
gcloud firestore indexes composite create \
  --collection-group=content \
  --field-config field-path=status,order=ASCENDING \
  --field-config field-path=created_at,order=DESCENDING
```

### 6. Cloud Storage Setup

```bash
# Create storage bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 \
  gs://${PROJECT_ID}-content-storage

# Set lifecycle policy (delete old files after 90 days)
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 90}
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://${PROJECT_ID}-content-storage

# Set CORS policy (if serving files publicly)
cat > cors.json << EOF
[
  {
    "origin": ["*"],
    "method": ["GET"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
EOF

gsutil cors set cors.json gs://${PROJECT_ID}-content-storage
```

### 7. Monitoring Setup

```bash
# Create notification channel for alerts
gcloud alpha monitoring channels create \
  --display-name="Email Alerts" \
  --type=email \
  --channel-labels=email_address=your-email@example.com

# Create alert policies
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s

gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Latency" \
  --condition-display-name="Latency > 500ms" \
  --condition-threshold-value=500 \
  --condition-threshold-duration=300s

gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Budget Alert" \
  --condition-display-name="Budget usage > 80%" \
  --condition-threshold-value=0.80 \
  --condition-threshold-duration=600s
```

---

## 📦 Containerization (for Cloud Run / GKE)

### Create `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}

# Expose port (for Cloud Run)
EXPOSE 8080

# Run application
CMD ["python", "main.py"]
```

### Create `.dockerignore`:

```
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
.git/
.gitignore
.env
*.md
tests/
examples/test_*.py
.vscode/
*.log
creds.json
key.json
```

### Build and test locally:

```bash
# Build image
docker build -t content-generator:latest .

# Run locally
docker run -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=your-project-id \
  -v $HOME/.config/gcloud:/root/.config/gcloud \
  content-generator:latest
```

---

## 🔄 CI/CD Pipeline (Cloud Build)

### Create `cloudbuild.yaml`:

```yaml
steps:
  # Run tests
  - name: 'python:3.13-slim'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install -r requirements.txt
        python examples/test_phase5.py

  # Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/content-generator:$SHORT_SHA', '.']

  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/content-generator:$SHORT_SHA']

  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'content-generator'
      - '--image=gcr.io/$PROJECT_ID/content-generator:$SHORT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--memory=2Gi'
      - '--cpu=2'
      - '--max-instances=10'

images:
  - 'gcr.io/$PROJECT_ID/content-generator:$SHORT_SHA'

options:
  machineType: 'E2_HIGHCPU_8'
```

### Set up Cloud Build trigger:

```bash
# Connect GitHub repository
gcloud beta builds triggers create github \
  --repo-name=google_projects \
  --repo-owner=YOUR_GITHUB_USERNAME \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml

# Grant Cloud Build permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$(gcloud projects describe $PROJECT_ID \
  --format='value(projectNumber)')@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$(gcloud projects describe $PROJECT_ID \
  --format='value(projectNumber)')@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

---

## 📊 Monitoring Dashboards

### Create custom dashboard in Cloud Console:

1. Go to **Monitoring > Dashboards**
2. Click **Create Dashboard**
3. Add the following charts:

**Performance Metrics:**
- Latency (P50, P95, P99)
- Throughput (requests/second)
- Error rate (%)
- CPU usage (%)
- Memory usage (%)

**Budget Metrics:**
- Total spending
- Spending by category
- Budget remaining
- Predicted monthly cost

**Security Metrics:**
- Rate limit violations
- Input validation failures
- Security events by severity
- Blocked IPs/users

**Agent Metrics:**
- Content generation success rate
- Media generation latency
- Publishing success rate
- Queue depth

---

## 🧪 Post-Deployment Testing

### 1. Health Check
```bash
# Test endpoint
curl https://content-generator-XXXXX-uc.a.run.app/health

# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

### 2. Generate Content
```bash
# Trigger content generation
curl -X POST https://content-generator-XXXXX-uc.a.run.app/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI trends in 2026",
    "content_type": "blog_post",
    "include_image": true
  }'
```

### 3. Monitor Metrics
```bash
# Check Cloud Monitoring
gcloud monitoring time-series list \
  --filter='metric.type="custom.googleapis.com/content_generator/latency"' \
  --format=json

# Check logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit 50 \
  --format json
```

---

## 🔒 Security Best Practices

### 1. Least Privilege Access
- Use dedicated service accounts per environment
- Grant only necessary IAM roles
- Regularly review and audit permissions

### 2. Secret Management
- Store all credentials in Secret Manager
- Never commit secrets to Git
- Rotate secrets every 90 days
- Use secret versioning

### 3. Network Security
- Use VPC Service Controls for sensitive data
- Enable Cloud Armor for DDoS protection
- Use Cloud Load Balancing with SSL

### 4. Input Validation
- Always validate user inputs
- Use rate limiting to prevent abuse
- Monitor for suspicious patterns

### 5. Audit Logging
- Enable audit logs for all services
- Set up log sinks for long-term storage
- Create alerts for suspicious activity

---

## 💰 Cost Optimization

### Current Budget: $250/month

**Expected Costs:**
- AI API (Gemini): $100/month (40%)
- Storage: $30/month (12%)
- Compute: $40/month (16%)
- Database (Firestore): $40/month (16%)
- Network: $20/month (8%)
- Monitoring: $10/month (4%)
- Other: $10/month (4%)

**Optimization Strategies:**

1. **Model Selection**
   - Use Gemini Flash for most operations ($0.00001875/1K chars)
   - Reserve Gemini Pro for complex tasks only
   - Batch requests when possible

2. **Caching**
   - Cache frequently accessed content
   - Use CDN for media files
   - Implement response caching

3. **Storage**
   - Set lifecycle policies (delete old files after 90 days)
   - Use Nearline/Coldline for archival
   - Compress images and videos

4. **Compute**
   - Use Cloud Run for auto-scaling
   - Set min instances to 0 for dev/staging
   - Use sustained use discounts for VMs

5. **Monitoring**
   - Sample metrics instead of full collection
   - Use log-based metrics instead of custom metrics
   - Set data retention to 30 days

---

## 🆘 Troubleshooting

### Common Issues

**1. Authentication Errors**
```
ERROR: Could not authenticate with Google Cloud
```
**Solution:**
- Verify `GOOGLE_APPLICATION_CREDENTIALS` is set
- Check service account has required IAM roles
- Re-generate service account key

**2. Budget Exceeded**
```
WARNING: Category 'ai_api_calls' throttled
```
**Solution:**
- Check budget status: `python -c "from src.infrastructure.budget_controller import BudgetController; print(BudgetController().get_budget_status())"`
- Adjust budget allocations if needed
- Investigate cost spike causes

**3. Rate Limit Exceeded**
```
ERROR: Rate limit exceeded for user123
```
**Solution:**
- Check rate limit settings
- Adjust limits for production traffic
- Implement exponential backoff

**4. High Latency**
```
WARNING: Latency threshold exceeded (500ms)
```
**Solution:**
- Check Cloud Monitoring dashboards
- Review slow operations in logs
- Consider scaling up resources

**5. Firestore Quota Exceeded**
```
ERROR: Quota exceeded for Firestore writes
```
**Solution:**
- Check quota limits in console
- Batch write operations
- Request quota increase if needed

---

## 📝 Next Steps

### Immediate (This Week)
1. [ ] Choose deployment option (Cloud Run recommended)
2. [ ] Set up GCP project and enable APIs
3. [ ] Create service account with IAM roles
4. [ ] Store secrets in Secret Manager
5. [ ] Deploy to production environment

### Short-term (This Month)
6. [ ] Set up monitoring dashboards
7. [ ] Configure alerting policies
8. [ ] Implement CI/CD pipeline
9. [ ] Load testing and performance tuning
10. [ ] Documentation and runbooks

### Long-term (Next 3 Months)
11. [ ] Multi-region deployment
12. [ ] Disaster recovery testing
13. [ ] A/B testing for content quality
14. [ ] Advanced analytics and reporting
15. [ ] Auto-scaling optimization

---

## 📞 Support

**Documentation:**
- [Architecture Guide](ARCHITECTURE.md)
- [Implementation Status](IMPLEMENTATION_STATUS.md)
- [Quick Start](QUICK_START.md)
- [Test Results](PHASE_5_TEST_RESULTS.md)

**Monitoring:**
- Cloud Console: https://console.cloud.google.com
- Monitoring Dashboards: https://console.cloud.google.com/monitoring
- Logs Explorer: https://console.cloud.google.com/logs

**Emergency Response:**
1. Check monitoring dashboards for anomalies
2. Review recent logs for errors
3. Verify service health endpoints
4. Check budget and quota status
5. Roll back to previous version if needed

---

🎉 **Ready to deploy! Good luck!** 🚀
