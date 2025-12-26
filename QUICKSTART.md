# Quick Start - Multi-Agent Content Generation

## Phase 0 is now implemented! 🎉

### What's Included:

✅ **Research Agent** - Gathers information using Gemini AI
✅ **Content Generator Agent** - Creates blog posts from research
✅ **Firestore Database** - Stores projects and content
✅ **Cost Tracking** - Monitors API usage costs
✅ **Error Logging** - Cloud Logging integration
✅ **Synchronous Workflow** - Orchestrates the entire process

---

## Quick Start (3 Steps)

### 1. Install Dependencies

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

### 2. Enable GCP APIs

```powershell
# Authenticate
gcloud auth application-default login

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable logging.googleapis.com

# Create Firestore database (if not exists)
gcloud firestore databases create --location=us-central1
```

### 3. Generate Your First Blog Post

```powershell
# Run the example
python examples/generate_blog_post.py

# Or use the CLI
python main.py --topic "Getting Started with AI"
```

---

## Project Structure

```
multi_agent_content_generation/
├── src/
│   ├── agents/              # AI Agents
│   │   ├── base_agent.py       - Base class with retry logic
│   │   ├── research_agent.py   - Research gathering
│   │   └── content_agent.py    - Content generation
│   ├── infrastructure/      # Database & Cost Tracking
│   │   ├── firestore.py        - Firestore operations
│   │   └── cost_tracker.py     - API cost tracking
│   ├── orchestration/       # Workflow Management
│   │   └── workflow.py         - Synchronous orchestration
│   └── monitoring/          # Logging
│       └── logger.py           - Structured logging
├── config/
│   ├── agent_config.yaml    # Agent configurations
│   └── prompts.yaml         # AI prompts
├── examples/
│   └── generate_blog_post.py  # Example script
├── tests/
│   └── test_agents.py       # Unit tests
├── main.py                  # CLI entry point
└── requirements.txt         # Dependencies
```

---

## Usage Examples

### Basic Usage

```powershell
python main.py --topic "Introduction to Cloud Computing"
```

### Custom Parameters

```powershell
python main.py `
  --topic "Machine Learning Best Practices" `
  --tone "technical and detailed" `
  --words 1500
```

### Retrieve Existing Project

```powershell
python main.py --project-id "your-project-id"
```

---

## Expected Output

```
🚀 Generating content for topic: Getting Started with AI
📝 Target word count: 1200
🎨 Tone: professional and conversational

================================================================================
✅ CONTENT GENERATION COMPLETED
================================================================================

📌 Project ID: abc123xyz789
📊 Status: completed

💰 Costs:
   Research: $0.0342
   Generation: $0.0987
   Total: $0.1329

📝 Content:
   Title: Getting Started with AI: A Comprehensive Guide
   Word Count: 1247
   Model Used: gemini-1.5-pro

📄 Introduction Preview:
   Artificial Intelligence (AI) has transformed from science fiction...

================================================================================
💾 Full content saved to Firestore (Project ID: abc123xyz789)
================================================================================
```

---

## Testing

```powershell
# Run unit tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_agents.py -v
```

---

## View Results in GCP Console

### Firestore
1. Go to [Firestore Console](https://console.cloud.google.com/firestore)
2. Select database
3. Browse `content_projects` collection
4. View your generated content

### Logs
1. Go to [Cloud Logging](https://console.cloud.google.com/logs)
2. Filter by resource type: `global`
3. Search for: `agent.research` or `agent.content_generator`

### Costs
1. Go to [Billing](https://console.cloud.google.com/billing)
2. View current month costs
3. Estimated: $0.12-$0.18 per blog post

---

## Phase 0 Success Criteria

- [x] Generate 1 quality blog post end-to-end ✅
- [x] Research agent returns structured findings ✅
- [x] Content agent produces 800-2000 word posts ✅
- [x] Cost tracking is accurate ✅
- [x] Errors are logged properly ✅
- [x] Data is persisted in Firestore ✅

---

## What's Next?

### Phase 1 (Weeks 4-6):
- ✨ Pub/Sub messaging between agents
- ✨ Editor Agent for content refinement
- ✨ SEO Optimization Agent
- ✨ Enhanced error handling with DLQ
- ✨ Monitoring dashboards
- ✨ Quota manager service

### Phase 2 (Weeks 7-10):
- ✨ Quality Assurance Agent
- ✨ 3-tier caching layer
- ✨ Rate limiting
- ✨ Budget controls

---

## Troubleshooting

### "API not enabled"
```powershell
gcloud services enable aiplatform.googleapis.com
```

### "Permission denied"
```powershell
# Ensure you have these roles:
# - Vertex AI User
# - Firestore User
# - Logs Writer
```

### "GOOGLE_CLOUD_PROJECT not set"
- Check that `.env` file exists in project root
- Ensure `GOOGLE_CLOUD_PROJECT=datalogichub-461612` is set

---

## Support

- 📖 [Full Setup Guide](./SETUP.md)
- 🏗️ [Architecture Documentation](./ARCHITECTURE.md)
- 📊 [Architecture Review](./ARCHITECTURE_REVIEW_SUMMARY.md)

---

**Phase 0 Status:** ✅ COMPLETE
**Ready for:** Testing and validation
**Next Phase:** Phase 1 implementation
