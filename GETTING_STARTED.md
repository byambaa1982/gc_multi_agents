# Getting Started - Phase 0

**Welcome to the Multi-Agent Content Generation System!**

This guide will walk you through setting up and running your first content generation.

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Install Dependencies (2 min)

```powershell
# Navigate to project directory
cd c:\Users\byamb\projects\google_projects\multi_agent_content_generation

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Enable GCP Services (2 min)

```powershell
# Authenticate with GCP
gcloud auth application-default login

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable logging.googleapis.com

# Create Firestore database (if it doesn't exist)
gcloud firestore databases create --location=us-central1
```

### Step 3: Validate Setup (1 min)

```powershell
# Run validation script
python validate.py
```

You should see all checks pass ✅

### Step 4: Generate Your First Blog Post! 🎉

```powershell
# Run the example
python examples/generate_blog_post.py
```

**That's it!** You should see content being generated in 1-2 minutes.

---

## 📖 What Happens During Generation?

```
🔄 Workflow Steps:
  1. Create project in Firestore
  2. Research Agent gathers information
  3. Save research results
  4. Content Generator creates blog post
  5. Save content and costs
  6. Display results

⏱️  Expected Time: 60-120 seconds
💰 Expected Cost: $0.12 - $0.18
```

---

## 🎯 Common Use Cases

### 1. Generate a Specific Topic

```powershell
python main.py --topic "Introduction to Machine Learning"
```

### 2. Customize Word Count

```powershell
python main.py --topic "Cloud Computing Best Practices" --words 1500
```

### 3. Change Writing Tone

```powershell
python main.py --topic "Getting Started with Python" --tone "casual and friendly"
```

### 4. Retrieve Existing Content

```powershell
# First generation returns a project ID
python main.py --topic "Test Topic"
# Output: Project ID: abc123xyz

# Retrieve it later
python main.py --project-id abc123xyz
```

---

## 📊 Understanding the Output

### Console Output

```
🚀 Generating content for topic: Introduction to AI
📝 Target word count: 1200
🎨 Tone: professional and conversational

================================================================================
✅ CONTENT GENERATION COMPLETED
================================================================================

📌 Project ID: xK2mN9pL4qR8sT6vY
📊 Status: completed

💰 Costs:
   Research: $0.0342
   Generation: $0.0987
   Total: $0.1329

📝 Content:
   Title: Introduction to AI: A Comprehensive Guide
   Word Count: 1247
   Model Used: gemini-1.5-pro
```

### Firestore Data

Your content is automatically saved to Firestore:

1. Go to [Firestore Console](https://console.cloud.google.com/firestore)
2. Select your project: `datalogichub-461612`
3. Browse collection: `content_projects`
4. View your generated content

---

## 🔍 Viewing Logs

### Cloud Logging Console

1. Go to [Cloud Logging](https://console.cloud.google.com/logs)
2. Select your project
3. Filter by:
   - `agent.research` - Research agent logs
   - `agent.content_generator` - Content generator logs
   - `workflow` - Workflow orchestration logs

### Local Logs

Logs are also printed to console in JSON format:

```json
{
  "message": "Agent research started",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "level": "INFO",
  "agent": "research",
  "project_id": "xK2mN9pL4qR8sT6vY"
}
```

---

## 💰 Cost Tracking

### Per Blog Post

- **Research**: $0.03 - $0.05
- **Content Generation**: $0.08 - $0.12
- **Storage (Firestore)**: < $0.01
- **Total**: ~$0.12 - $0.18

### View Costs in GCP

1. Go to [Billing Console](https://console.cloud.google.com/billing)
2. Select your project
3. View current month costs
4. Filter by service (Vertex AI, Firestore)

---

## 🧪 Running Tests

### Unit Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_agents.py -v

# Run specific test
pytest tests/test_agents.py::TestResearchAgent::test_research_agent_initialization -v
```

### Manual Testing Checklist

- [ ] Generate a blog post on a technical topic
- [ ] Generate a blog post on a non-technical topic
- [ ] Test with different word counts (800, 1200, 2000)
- [ ] Test with different tones (professional, casual, technical)
- [ ] Verify data appears in Firestore
- [ ] Check logs in Cloud Logging
- [ ] Validate cost tracking accuracy

---

## 🔧 Configuration

### Agent Configuration (`config/agent_config.yaml`)

```yaml
agents:
  research:
    model: "gemini-1.5-flash"      # Fast, cost-effective
    temperature: 0.3                # Focused, factual
    max_output_tokens: 2048
    
  content_generator:
    model: "gemini-1.5-pro"        # High quality
    temperature: 0.7                # Creative
    max_output_tokens: 4096
```

### Prompts (`config/prompts.yaml`)

You can customize the AI prompts to change:
- Writing style
- Output format
- Content structure
- Research depth

---

## 🐛 Troubleshooting

### Issue: "GOOGLE_CLOUD_PROJECT not set"

**Solution:**
```powershell
# Check .env file exists
cat .env

# Ensure it contains:
# GOOGLE_CLOUD_PROJECT=datalogichub-461612
```

### Issue: "API not enabled"

**Solution:**
```powershell
gcloud services enable aiplatform.googleapis.com
gcloud services enable firestore.googleapis.com
```

### Issue: "Permission denied"

**Solution:**
```powershell
# Re-authenticate
gcloud auth application-default login

# Ensure you're using the correct project
gcloud config set project datalogichub-461612
```

### Issue: "Firestore database not found"

**Solution:**
```powershell
# Create Firestore database
gcloud firestore databases create --location=us-central1
```

### Issue: Import errors

**Solution:**
```powershell
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Or install specific package
pip install google-cloud-aiplatform
```

---

## 📚 Next Steps

### Explore the Code

1. **Start with workflows**: `src/orchestration/workflow.py`
2. **Understand agents**: `src/agents/research_agent.py`
3. **Check infrastructure**: `src/infrastructure/firestore.py`

### Experiment

1. Modify prompts in `config/prompts.yaml`
2. Change agent parameters in `config/agent_config.yaml`
3. Try different topics and word counts
4. Review generated content quality

### Learn More

- [Architecture Documentation](./ARCHITECTURE.md)
- [Setup Guide](./SETUP.md)
- [Phase 0 Complete Summary](./PHASE_0_COMPLETE.md)
- [Architecture Review](./ARCHITECTURE_REVIEW_SUMMARY.md)

### Prepare for Phase 1

Once you're comfortable with Phase 0:
- Review Phase 1 requirements in [ARCHITECTURE_REVIEW_SUMMARY.md](./ARCHITECTURE_REVIEW_SUMMARY.md)
- Understand Pub/Sub messaging
- Learn about Cloud Workflows
- Plan Editor and SEO agents

---

## ✅ Success Checklist

Before moving to Phase 1, ensure:

- [ ] Successfully generated 5+ blog posts
- [ ] All validation checks pass (`python validate.py`)
- [ ] Data visible in Firestore Console
- [ ] Logs visible in Cloud Logging
- [ ] Cost tracking is accurate
- [ ] Understand the codebase structure
- [ ] Can modify prompts and see changes
- [ ] Can adjust agent parameters

---

## 🎉 You're Ready!

**Congratulations!** You now have a working multi-agent content generation system.

### What You've Built:

✅ AI-powered research agent  
✅ High-quality content generator  
✅ Cloud-native infrastructure  
✅ Cost tracking system  
✅ Production-ready logging  
✅ Scalable architecture  

### Generate Content Now:

```powershell
python main.py --topic "Your Amazing Topic Here"
```

**Happy content generating! 🚀**

---

**Need Help?**
- Check [SETUP.md](./SETUP.md) for detailed setup
- Review [PHASE_0_COMPLETE.md](./PHASE_0_COMPLETE.md) for implementation details
- Run `python validate.py` to check your setup
