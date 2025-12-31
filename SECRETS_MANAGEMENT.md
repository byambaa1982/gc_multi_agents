# Secure Credential Management Guide

## ✅ Your Current Setup (Correct!)

Your `.env` file contains:
- ✅ Project configuration (non-sensitive)
- ⚠️ Twitter API credentials (sensitive)

## 🔒 Security Approach for Cloud Run

### Step 1: Store Secrets in Secret Manager

Run this command to securely store your Twitter credentials:

```powershell
# This reads your .env file and creates secrets in Google Secret Manager
.\setup-secrets.ps1
```

This will:
- ✅ Create secrets: `twitter-api-key`, `twitter-api-secret`, etc.
- ✅ Grant Cloud Run service account access
- ✅ Keep credentials encrypted and secure

### Step 2: Deploy to Cloud Run

```powershell
$env:PROJECT_ID = "datalogichub-461612"
.\deploy.ps1
```

The deployment automatically:
- ✅ Sets non-sensitive env vars (project ID, bucket name, etc.)
- ✅ Mounts secrets from Secret Manager
- ✅ No credentials in container or logs!

## 📊 How Secrets are Used

```
┌─────────────────┐
│   Cloud Run     │
│  Service        │
└────────┬────────┘
         │
         │ References secrets by name
         │
         ▼
┌─────────────────┐
│ Secret Manager  │
│                 │
│ twitter-api-key │ ← Encrypted
│ twitter-secret  │ ← Versioned
│ access-token    │ ← IAM controlled
└─────────────────┘
```

## 🎯 What Goes Where

### ❌ NEVER Store in Cloud Storage:
- API keys
- Passwords
- Access tokens
- Service account keys

### ✅ Secret Manager (Sensitive):
- Twitter API credentials ← **Your case**
- Facebook tokens
- Database passwords
- API keys

### ✅ Cloud Run Environment Variables (Non-sensitive):
- Project ID: `datalogichub-461612`
- Bucket name: `datalogichub-learning-bucket-2025`
- Region: `us-central1`
- Feature flags

### ✅ Not Needed in Cloud Run:
- `creds.json` - Service account files
  - Cloud Run uses **Workload Identity**
  - Automatic authentication!

## 🔐 Your Credentials Security

### Current .env File:
```bash
# Non-sensitive (OK for env vars)
GOOGLE_CLOUD_PROJECT=datalogichub-461612
GCS_BUCKET_NAME=datalogichub-learning-bucket-2025
VERTEX_AI_LOCATION=us-central1

# Sensitive (MUST use Secret Manager)
TWITTER_API_KEY=***
TWITTER_API_SECRET=***
TWITTER_ACCESS_TOKEN=***
TWITTER_ACCESS_TOKEN_SECRET=***
```

### After Running setup-secrets.ps1:
- Secrets stored in **Secret Manager** (encrypted, versioned, audited)
- Cloud Run accesses via IAM (no credentials in code/container)
- Can rotate secrets without redeploying

## 📋 Deployment Steps (In Order)

```powershell
# 1. Set project ID
$env:PROJECT_ID = "datalogichub-461612"

# 2. Setup secrets (FIRST TIME ONLY)
.\setup-secrets.ps1

# 3. Deploy to Cloud Run
.\deploy.ps1
```

## 🔄 Updating Secrets

To update a credential (e.g., Twitter token expired):

```powershell
# Option 1: Re-run setup script
.\setup-secrets.ps1

# Option 2: Update manually
echo "NEW_TOKEN" | gcloud secrets versions add twitter-access-token --data-file=-

# Cloud Run automatically picks up new version!
```

## 🛡️ Security Checklist

- [x] `.env` in `.gitignore` ✅
- [ ] Run `.\setup-secrets.ps1` to create secrets
- [ ] Never commit credentials to Git
- [ ] Don't upload `creds.json` anywhere
- [ ] Use Secret Manager for sensitive data
- [ ] Rotate secrets every 90 days (best practice)

## 🆘 Common Questions

**Q: Can I delete .env after deployment?**
A: Yes! After secrets are in Secret Manager, you don't need .env in production. Keep it locally for development.

**Q: How much does Secret Manager cost?**
A: Very cheap! ~$0.06 per secret per month + $0.03 per 10K access operations.

**Q: What about creds.json?**
A: Not needed! Cloud Run uses service account identity automatically. No key files required.

**Q: Is Secret Manager safer than Cloud Storage?**
A: **Much safer!** Purpose-built for secrets with:
- Automatic encryption at rest
- IAM access control
- Audit logging
- Secret versioning
- Automatic rotation support

---

## 🚀 Quick Start

```powershell
# Setup secrets (first time)
.\setup-secrets.ps1

# Deploy
$env:PROJECT_ID = "datalogichub-461612"
.\deploy.ps1
```

Done! Your secrets are secure in Secret Manager, and Cloud Run accesses them safely via IAM. 🔒
