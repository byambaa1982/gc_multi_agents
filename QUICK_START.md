# Phase 1 Quick Start Guide

Get your multi-agent content generation system running in 5 minutes!

---

## Prerequisites Check

Before you begin, verify you have:

- [ ] GCP Account with billing enabled
- [ ] Python 3.11+ installed
- [ ] gcloud CLI installed

---

## Step 1: GCP Setup (2 minutes)

### 1.1 Create/Select Project
```powershell
# List existing projects
gcloud projects list

# Or create a new one
gcloud projects create YOUR-PROJECT-ID

# Set as default
gcloud config set project YOUR-PROJECT-ID
```

### 1.2 Enable Required APIs
```powershell
gcloud services enable \
  pubsub.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  logging.googleapis.com
```

### 1.3 Authenticate
```powershell
gcloud auth application-default login
```

---

## Step 2: Environment Setup (1 minute)

### 2.1 Set Environment Variables
```powershell
# Required
$env:GOOGLE_CLOUD_PROJECT = "your-project-id"

# Optional (recommended)
$env:VERTEX_AI_LOCATION = "us-central1"
$env:DAILY_BUDGET_LIMIT = "10.0"
$env:PROJECT_BUDGET_LIMIT = "1.0"
```

### 2.2 Install Dependencies
```powershell
cd multi_agent_content_generation
pip install -r requirements.txt
```

---

## Step 3: Infrastructure Setup (1 minute)

Run the automated setup:

```powershell
python setup_phase1.py
```

This creates:
- ✅ Pub/Sub topics and subscriptions
- ✅ Firestore database connection
- ✅ Quota manager initialization
- ✅ All agent configurations

---

## Step 4: Run Your First Workflow (1 minute)

### Option A: Run Test Suite
```powershell
python examples/test_phase1.py
```

### Option B: Custom Workflow
```python
from src.orchestration.async_workflow import AsyncContentWorkflow

# Initialize
workflow = AsyncContentWorkflow()

# Start workflow
project_id = workflow.start_workflow(
    topic="Your Topic Here",
    tone='professional',
    target_word_count=1200,
    primary_keyword='your keyword'
)

print(f"Started project: {project_id}")

# Check status
status = workflow.get_workflow_status(project_id)
print(f"Status: {status['status']}")
```

---

## Step 5: Monitor Results

### View in Firestore
1. Open [GCP Console](https://console.cloud.google.com)
2. Navigate to **Firestore**
3. Find collection: `content_projects`
4. Look for your project ID

### View Logs
1. Open [GCP Console](https://console.cloud.google.com)
2. Navigate to **Logging**
3. Filter by:
   - Resource: Any
   - Severity: INFO
   - Search: Your project ID

### Check Costs
```python
from src.infrastructure import QuotaManager

quota = QuotaManager()
report = quota.get_usage_report(hours=24)

print(f"Total cost: ${report['total_cost']:.4f}")
print(f"Total requests: {report['total_requests']}")
```

---

## What Happens in a Workflow?

```
1. Research Agent
   └─ Gathers information about your topic
   └─ Publishes to Pub/Sub: research-complete
   
2. Content Generator
   └─ Creates blog post from research
   └─ Publishes to Pub/Sub: content-generated
   
3. Editor Agent
   └─ Refines grammar, style, clarity
   └─ Publishes to Pub/Sub: editing-complete
   
4. SEO Optimizer
   └─ Optimizes for search engines
   └─ Publishes to Pub/Sub: seo-optimized
   
5. Complete!
   └─ Check Firestore for full results
```

---

## Troubleshooting

### "Permission Denied" Errors
```powershell
# Grant yourself necessary roles
gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
  --member="user:YOUR-EMAIL" \
  --role="roles/editor"
```

### "API Not Enabled" Errors
```powershell
# Enable the specific API mentioned in error
gcloud services enable API-NAME.googleapis.com
```

### "Quota Exceeded" Errors
- Wait a few minutes for quota to refill
- Check quota status in GCP Console
- Increase quotas if needed (Project Settings → Quotas)

### Import Errors
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## Next Steps

✅ **You're all set!** Your Phase 1 system is running.

### To Learn More:
- Read [PHASE_1_COMPLETE.md](PHASE_1_COMPLETE.md) for detailed documentation
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Check [ARCHITECTURE_REVIEW_SUMMARY.md](ARCHITECTURE_REVIEW_SUMMARY.md) for best practices

### To Customize:
- Edit `config/agent_config.yaml` to change models or settings
- Edit `config/prompts.yaml` to customize agent behavior
- Adjust budget limits in environment variables

### To Scale:
- Increase `max_concurrent_projects` in config
- Deploy to Cloud Run for production
- Add caching layer (Phase 2)
- Implement Quality Assurance Agent (Phase 2)

---

## Estimated Costs

For a 1200-word blog post:

| Component | Cost |
|-----------|------|
| Research | ~$0.05 |
| Content Generation | ~$0.10 |
| Editing | ~$0.08 |
| SEO Optimization | ~$0.03 |
| **Total** | **~$0.26** |

**Daily budget of $10 = ~38 blog posts/day**

---

## Support

Having issues?

1. Check logs in Cloud Logging
2. Review [PHASE_1_COMPLETE.md](PHASE_1_COMPLETE.md) troubleshooting section
3. Verify all environment variables are set
4. Ensure all APIs are enabled

---

## Success Indicators

You know it's working when:

✅ `setup_phase1.py` completes without errors  
✅ Test workflow creates a project in Firestore  
✅ All 4 stages complete successfully  
✅ Total cost is under $0.50 per content piece  
✅ Logs show successful agent executions  

---

**That's it! You're ready to generate content with AI agents! 🚀**
