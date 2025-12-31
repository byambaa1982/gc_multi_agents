# Setup Secrets in Google Secret Manager
# Run this BEFORE deploying to Cloud Run

$ErrorActionPreference = "Stop"

# Check if PROJECT_ID is set
if (-not $env:PROJECT_ID) {
    $env:PROJECT_ID = "datalogichub-461612"
}

$PROJECT_ID = $env:PROJECT_ID
$SERVICE_ACCOUNT = "content-generator@${PROJECT_ID}.iam.gserviceaccount.com"

Write-Host "========================================" -ForegroundColor Green
Write-Host "Setting up Secrets in Secret Manager" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Project: $PROJECT_ID" -ForegroundColor Yellow
Write-Host ""

# Enable Secret Manager API
Write-Host "Enabling Secret Manager API..." -ForegroundColor Yellow
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID

# Read secrets from .env file
Write-Host "`nReading credentials from .env file..." -ForegroundColor Yellow

# Function to create or update secret
function Set-GCPSecret {
    param(
        [string]$SecretName,
        [string]$SecretValue
    )
    
    if (-not $SecretValue) {
        Write-Host "  ⚠️  Skipping $SecretName (empty value)" -ForegroundColor Yellow
        return
    }
    
    # Check if secret exists
    $exists = gcloud secrets describe $SecretName --project=$PROJECT_ID 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        # Update existing secret
        Write-Host "  ↻ Updating $SecretName..." -ForegroundColor Cyan
        echo $SecretValue | gcloud secrets versions add $SecretName --data-file=- --project=$PROJECT_ID
    } else {
        # Create new secret
        Write-Host "  + Creating $SecretName..." -ForegroundColor Green
        echo $SecretValue | gcloud secrets create $SecretName --data-file=- --project=$PROJECT_ID
    }
    
    # Grant service account access
    gcloud secrets add-iam-policy-binding $SecretName `
        --member="serviceAccount:$SERVICE_ACCOUNT" `
        --role="roles/secretmanager.secretAccessor" `
        --project=$PROJECT_ID 2>$null | Out-Null
}

# Parse .env file and create secrets for sensitive values
Write-Host "`nCreating secrets..." -ForegroundColor Yellow

# Twitter credentials
$envContent = Get-Content .env -Raw
if ($envContent -match 'TWITTER_API_KEY=(.+)') {
    Set-GCPSecret -SecretName "twitter-api-key" -SecretValue $matches[1].Trim()
}
if ($envContent -match 'TWITTER_API_SECRET=(.+)') {
    Set-GCPSecret -SecretName "twitter-api-secret" -SecretValue $matches[1].Trim()
}
if ($envContent -match 'TWITTER_ACCESS_TOKEN=(.+)') {
    Set-GCPSecret -SecretName "twitter-access-token" -SecretValue $matches[1].Trim()
}
if ($envContent -match 'TWITTER_ACCESS_TOKEN_SECRET=(.+)') {
    Set-GCPSecret -SecretName "twitter-access-token-secret" -SecretValue $matches[1].Trim()
}

# Facebook credentials (if exists)
if ($envContent -match 'FACEBOOK_ACCESS_TOKEN=(.+)') {
    Set-GCPSecret -SecretName "facebook-access-token" -SecretValue $matches[1].Trim()
}
if ($envContent -match 'FACEBOOK_PAGE_ID=(.+)') {
    Set-GCPSecret -SecretName "facebook-page-id" -SecretValue $matches[1].Trim()
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✓ Secrets configured in Secret Manager" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "List all secrets:" -ForegroundColor Yellow
gcloud secrets list --project=$PROJECT_ID

Write-Host "`n⚠️  IMPORTANT SECURITY STEPS:" -ForegroundColor Red
Write-Host "1. Add .env to .gitignore (if not already)" -ForegroundColor Yellow
Write-Host "2. Never commit .env or creds.json files" -ForegroundColor Yellow
Write-Host "3. Delete local .env after deployment (optional)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next step: Run deployment" -ForegroundColor Green
Write-Host "  .\deploy.ps1" -ForegroundColor Cyan
Write-Host ""
