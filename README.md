# Multi-Agent Content Generation System

**Phase 0: MVP Foundation**

A scalable multi-agent system for automated content generation using Google Cloud Platform.

## 🎯 Current Phase: Phase 0 (MVP)

**Goal:** Validate core concept with minimal viable system

**Features:**
- ✅ Research Agent - Gathers information on topics
- ✅ Content Generator Agent - Creates blog posts
- ✅ Basic Firestore schema
- ✅ Synchronous workflow
- ✅ Error logging
- ✅ Cost tracking

**Success Criteria:** Generate 1 quality blog post end-to-end

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.9+
- Google Cloud Project
- GCP Authentication configured

### 2. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your GCP project details
```

### 3. Run

```bash
# Generate a blog post
python main.py --topic "Getting Started with Google Cloud AI"

# Or use the example script
python examples/generate_blog_post.py
```

---

## 📁 Project Structure

```
multi_agent_content_generation/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py       # Base agent class
│   │   ├── research_agent.py   # Research agent
│   │   └── content_agent.py    # Content generator
│   ├── orchestration/
│   │   ├── __init__.py
│   │   └── workflow.py         # Synchronous workflow
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── firestore.py        # Database operations
│   │   └── cost_tracker.py     # Cost tracking
│   └── monitoring/
│       ├── __init__.py
│       └── logger.py           # Structured logging
├── config/
│   ├── agent_config.yaml       # Agent configurations
│   └── prompts.yaml            # AI prompts
├── examples/
│   └── generate_blog_post.py   # Example usage
├── tests/
│   └── test_agents.py          # Unit tests
├── main.py                     # Main entry point
├── requirements.txt
└── README.md
```

---

## 🔧 Configuration

### Environment Variables (.env)

```env
GOOGLE_CLOUD_PROJECT=your-project-id
GCS_BUCKET_NAME=your-bucket-name
FIRESTORE_COLLECTION=content_projects
```

### Agent Configuration (config/agent_config.yaml)

Configure agent behavior, model selection, and parameters.

---

## 📊 Data Schema

### Project Document (Firestore)

```json
{
  "projectId": "uuid",
  "topic": "Blog post topic",
  "status": "pending|research|generating|completed|failed",
  "research": {
    "keyPoints": [],
    "sources": [],
    "completedAt": "timestamp"
  },
  "content": {
    "title": "Generated title",
    "body": "Generated content",
    "wordCount": 1500,
    "completedAt": "timestamp"
  },
  "costs": {
    "research": 0.05,
    "generation": 0.10,
    "total": 0.15
  },
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_agents.py
```

---

## 💰 Cost Tracking

Estimated costs per blog post generation:
- Research: $0.03 - $0.05
- Content Generation: $0.08 - $0.12
- **Total: ~$0.15 per post**

---

## 🗺️ Roadmap

- [x] **Phase 0** (Current): MVP with Research + Content agents
- [ ] **Phase 1**: Pub/Sub messaging, Editor + SEO agents
- [ ] **Phase 2**: Quality assurance, caching, rate limiting
- [ ] **Phase 3**: Media generation (images, video)
- [ ] **Phase 4**: Multi-platform publishing

---

## 📚 Documentation

- [Architecture](./ARCHITECTURE.md)
- [Architecture Review](./ARCHITECTURE_REVIEW_SUMMARY.md)

---

## 📝 License

MIT License
