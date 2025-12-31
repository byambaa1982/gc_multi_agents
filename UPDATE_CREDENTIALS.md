# Update Credentials Guide

Quick guide for updating API credentials in your deployed Cloud Run service.

## 🔄 Update Existing Credentials (e.g., Twitter Token Expired)

### Method 1: Using Command Line

```powershell
# Update a single secret
echo "NEW_TOKEN_VALUE" | gcloud secrets versions add twitter-access-token --data-file=-

# Cloud Run automatically picks up the new version!
# No redeployment needed
```

### Method 2: Using Cloud Console

1. Go to [Secret Manager](https://console.cloud.google.com/security/secret-manager?project=datalogichub-461612)
2. Click on the secret name (e.g., `twitter-access-token`)
3. Click **"NEW VERSION"**
4. Paste new value
5. Click **"ADD NEW VERSION"**
6. ✅ Cloud Run automatically uses the latest version

---

## ➕ Add New Credentials (e.g., Facebook Tokens)

### Step 1: Create Secrets

```powershell
# Facebook Access Token
echo "YOUR_FACEBOOK_ACCESS_TOKEN" | gcloud secrets create facebook-access-token --data-file=-

# Facebook Page ID
echo "YOUR_FACEBOOK_PAGE_ID" | gcloud secrets create facebook-page-id --data-file=-

# Grant service account access
gcloud secrets add-iam-policy-binding facebook-access-token `
  --member="serviceAccount:content-generator@datalogichub-461612.iam.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding facebook-page-id `
  --member="serviceAccount:content-generator@datalogichub-461612.iam.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor"
```

### Step 2: Update Cloud Run Service

```powershell
# Add new secrets to Cloud Run
gcloud run services update content-generator `
  --update-secrets="FACEBOOK_ACCESS_TOKEN=facebook-access-token:latest,FACEBOOK_PAGE_ID=facebook-page-id:latest" `
  --region us-central1
```

### Step 3: Verify

```powershell
# Check service configuration
gcloud run services describe content-generator --region us-central1

# Test the service
curl https://content-generator-279772560710.us-central1.run.app/health
```

---

## 📋 Quick Reference: All Credentials

### Current Secrets (Twitter)
```
twitter-api-key
twitter-api-secret
twitter-access-token
twitter-access-token-secret
```

### Add More Platforms

**Facebook:**
```powershell
echo "TOKEN" | gcloud secrets create facebook-access-token --data-file=-
echo "PAGE_ID" | gcloud secrets create facebook-page-id --data-file=-
```

**Instagram:**
```powershell
echo "TOKEN" | gcloud secrets create instagram-access-token --data-file=-
echo "ACCOUNT_ID" | gcloud secrets create instagram-account-id --data-file=-
```

**LinkedIn:**
```powershell
echo "TOKEN" | gcloud secrets create linkedin-access-token --data-file=-
echo "ORG_ID" | gcloud secrets create linkedin-org-id --data-file=-
```

After creating secrets, update Cloud Run:
```powershell
gcloud run services update content-generator `
  --update-secrets="FACEBOOK_ACCESS_TOKEN=facebook-access-token:latest,FACEBOOK_PAGE_ID=facebook-page-id:latest" `
  --region us-central1
```

---

## 🔍 Verify Secrets Configuration

### List All Secrets
```powershell
gcloud secrets list --project=datalogichub-461612
```

### View Secret Metadata (not the value)
```powershell
gcloud secrets describe twitter-access-token
```

### Check Cloud Run Secret Mounts
```powershell
gcloud run services describe content-generator --region us-central1 --format="yaml(spec.template.spec.containers[0].env)"
```

---

## 🚨 Troubleshooting

### Secret Not Working After Update

**Problem:** New secret version not being used

**Solution:**
```powershell
# Force Cloud Run to restart with new secrets
gcloud run services update content-generator `
  --region us-central1 `
  --update-env-vars "REFRESH=$(date +%s)"
```

### Permission Denied Error

**Problem:** Service account can't access secret

**Solution:**
```powershell
# Grant access to service account
gcloud secrets add-iam-policy-binding SECRET_NAME `
  --member="serviceAccount:content-generator@datalogichub-461612.iam.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor"
```

### Secret Not Found in Application

**Problem:** Environment variable not set in Cloud Run

**Solution:**
```powershell
# Add secret to Cloud Run configuration
gcloud run services update content-generator `
  --update-secrets="ENV_VAR_NAME=secret-name:latest" `
  --region us-central1
```

---

## 🔒 Security Best Practices

### ✅ DO:
- Use Secret Manager for all API keys and tokens
- Rotate credentials every 90 days
- Use `latest` version for auto-updates
- Grant minimal IAM permissions

### ❌ DON'T:
- Never commit credentials to Git
- Don't store secrets in environment variables (use Secret Manager)
- Don't share service account keys
- Don't use the same credentials across environments

---

## 📊 Cost

**Secret Manager Pricing:**
- $0.06 per secret per month
- $0.03 per 10,000 access operations
- Very affordable for production use!

**Example:** 10 secrets × $0.06 = **$0.60/month**

---

## 🔄 Complete Update Workflow

```powershell
# 1. Create or update secret
echo "NEW_VALUE" | gcloud secrets versions add secret-name --data-file=-

# 2. (If new secret) Grant access
gcloud secrets add-iam-policy-binding secret-name `
  --member="serviceAccount:content-generator@datalogichub-461612.iam.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor"

# 3. (If new secret) Add to Cloud Run
gcloud run services update content-generator `
  --update-secrets="ENV_VAR_NAME=secret-name:latest" `
  --region us-central1

# 4. Verify
curl https://content-generator-279772560710.us-central1.run.app/health
```

---

## 📞 Quick Commands

```powershell
# View all secrets
gcloud secrets list

# View secret versions
gcloud secrets versions list SECRET_NAME

# Delete a secret version (if compromised)
gcloud secrets versions destroy VERSION_ID --secret=SECRET_NAME

# Delete a secret entirely
gcloud secrets delete SECRET_NAME

# View Cloud Run configuration
gcloud run services describe content-generator --region us-central1
```

---

## 💡 Pro Tips

1. **Auto-rotation:** Update secrets, and Cloud Run picks up changes automatically (no redeploy!)
2. **Version pinning:** Use `:1`, `:2` instead of `:latest` for specific versions
3. **Audit logging:** All secret access is logged in Cloud Audit Logs
4. **Environment separation:** Use different secrets for dev/staging/production

---

**Need Help?**
- [Secret Manager Docs](https://cloud.google.com/secret-manager/docs)
- [Cloud Run Secrets](https://cloud.google.com/run/docs/configuring/secrets)
- Project: `datalogichub-461612`
- Service: `content-generator`
- Region: `us-central1`
