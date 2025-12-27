# Phase 4 Quick Start Guide

**Publishing, Analytics, and User Management**

This guide will help you quickly get started with Phase 4 features including multi-platform publishing, analytics dashboards, performance monitoring, and user management.

---

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
cd multi_agent_content_generation
pip install -r requirements.txt
```

### 2. Set Up Environment Variables (Optional)

```bash
# Create .env file for platform API credentials
cat > .env << EOF
# WordPress
WORDPRESS_SITE_URL=https://yourblog.com
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=your_app_password

# Medium
MEDIUM_ACCESS_TOKEN=your_access_token

# Twitter/X
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# LinkedIn
LINKEDIN_ACCESS_TOKEN=your_access_token
EOF
```

---

## 📝 5-Minute Tutorial

### Example 1: Publish Content to Multiple Platforms

```python
from src.agents.publisher_agent import PublisherAgent

# Initialize publisher
publisher = PublisherAgent()

# Your content
content = {
    'title': 'Getting Started with AI Content Creation',
    'body': 'Full article content here...',
    'images': ['https://example.com/image.jpg'],
    'tags': ['AI', 'Content', 'Automation']
}

# Publish to multiple platforms
result = publisher.execute(
    project_id='my_first_project',
    platforms=['twitter', 'linkedin', 'medium'],
    content=content
)

# Check results
for platform, res in result['results'].items():
    if res['success']:
        print(f"✅ {platform}: {res['url']}")
    else:
        print(f"❌ {platform}: {res['error']}")
```

**Output:**
```
✅ twitter: https://twitter.com/user/status/123456
✅ linkedin: https://linkedin.com/feed/update/urn:li:share:789
✅ medium: https://medium.com/@user/getting-started-abc123
```

---

### Example 2: View Analytics Dashboard

```python
from src.infrastructure.analytics_dashboard import AnalyticsDashboard

# Initialize dashboard
dashboard = AnalyticsDashboard()

# Get complete dashboard summary
summary = dashboard.get_dashboard_summary()

# Display key metrics
print(f"📊 Dashboard Summary")
print(f"Total Projects: {summary['overview']['total_projects']}")
print(f"Content Generated: {summary['overview']['total_content_generated']}")
print(f"Total Cost: ${summary['costs']['total_spent']:.2f}")
print(f"Avg Quality: {summary['quality']['average_quality_score']:.1%}")
print(f"Total Views: {summary['engagement']['total_views']:,}")

# Compare platforms
comparison = dashboard.get_platform_comparison()
print(f"\n🏆 Best Platform: {comparison['best_platform'].upper()}")
```

**Output:**
```
📊 Dashboard Summary
Total Projects: 234
Content Generated: 512
Total Cost: $285.50
Avg Quality: 87.0%
Total Views: 523,456

🏆 Best Platform: INSTAGRAM
```

---

### Example 3: Monitor Performance

```python
from src.monitoring.performance_monitor import performance_monitor

# Track an operation
with performance_monitor.track_operation('my_task'):
    # Your code here
    result = do_something()

# Get performance metrics
metrics = performance_monitor.get_metrics('my_task')

print(f"⏱️  Performance Metrics")
print(f"Total Runs: {metrics['count']}")
print(f"Avg Time: {metrics['average_time']:.2f}s")
print(f"Success Rate: {metrics['success_rate']:.1%}")
print(f"P95 Time: {metrics['p95_time']:.2f}s")

# Check for alerts
alerts = performance_monitor.get_alerts()
if alerts:
    print(f"\n⚠️  {len(alerts)} Active Alerts")
    for alert in alerts:
        print(f"  - [{alert['severity']}] {alert['message']}")
```

**Output:**
```
⏱️  Performance Metrics
Total Runs: 150
Avg Time: 2.34s
Success Rate: 96.0%
P95 Time: 4.12s
```

---

### Example 4: Manage Users

```python
from src.infrastructure.user_management import UserManager, Role

# Initialize user manager
user_manager = UserManager()

# Create a user
user = user_manager.create_user(
    email='creator@example.com',
    password='secure_password',
    name='Content Creator',
    role=Role.CONTENT_CREATOR
)

print(f"✅ User created: {user['name']}")
print(f"   Role: {user['role']}")
print(f"   Permissions: {len(user['permissions'])}")

# Authenticate user
auth = user_manager.authenticate(
    email='creator@example.com',
    password='secure_password'
)

if auth:
    print(f"\n🔐 Authentication successful")
    print(f"   Session Token: {auth['session_token'][:20]}...")
    print(f"   Last Login: {auth['last_login']}")
```

**Output:**
```
✅ User created: Content Creator
   Role: content_creator
   Permissions: 12

🔐 Authentication successful
   Session Token: Ab3xY9mK2pQ8vN4w...
   Last Login: 2025-12-26T15:30:00Z
```

---

### Example 5: Complete Workflow (Generate + Publish)

```python
from src.orchestration.workflow import ContentGenerationWorkflow

# Initialize workflow
workflow = ContentGenerationWorkflow()

# Generate and publish in one go
result = workflow.generate_and_publish(
    topic='The Future of Cloud Computing',
    platforms=['linkedin', 'medium'],
    tone='professional',
    target_word_count=1500
)

if result['success']:
    print("✅ Complete workflow finished!")
    print(f"\n📝 Generation:")
    print(f"   Project ID: {result['project_id']}")
    print(f"   Word Count: {result['generation']['content']['word_count']}")
    
    print(f"\n📤 Publishing:")
    for platform in result['publishing']['publishing_results']['platforms']:
        print(f"   ✅ {platform.capitalize()}")
```

**Output:**
```
✅ Complete workflow finished!

📝 Generation:
   Project ID: proj_abc123
   Word Count: 1523

📤 Publishing:
   ✅ Linkedin
   ✅ Medium
```

---

## 🎯 Common Use Cases

### Use Case 1: Daily Content Publishing Routine

```python
# Morning routine: Generate and publish
workflow = ContentGenerationWorkflow()

topics = [
    'AI Trends Today',
    'Cloud Best Practices',
    'Developer Productivity Tips'
]

for topic in topics:
    result = workflow.generate_and_publish(
        topic=topic,
        platforms=['twitter', 'linkedin'],
        target_word_count=1000
    )
    print(f"✅ Published: {topic}")
```

---

### Use Case 2: Weekly Analytics Review

```python
dashboard = AnalyticsDashboard()

# Get weekly performance
weekly = dashboard.get_performance_last_7d()
print(f"📊 This Week: {weekly['projects_completed']} projects completed")

# Platform comparison
comparison = dashboard.get_platform_comparison(time_range_days=7)
for platform, metrics in comparison['platforms'].items():
    print(f"{platform}: {metrics['engagement_rate']:.1%} engagement")

# Cost analysis
costs = dashboard.get_cost_analysis(time_range_days=7)
print(f"💰 Weekly Cost: ${costs['total_cost']:.2f}")
```

---

### Use Case 3: Performance Optimization

```python
# Monitor all agents
dashboard = AnalyticsDashboard()
agent_perf = dashboard.get_agent_performance()

# Find bottlenecks
for agent, metrics in agent_perf['agents'].items():
    if metrics['average_execution_time'] > 60:
        print(f"⚠️  Slow agent: {agent} ({metrics['average_execution_time']:.1f}s)")
    
    if metrics['error_rate'] > 0.05:
        print(f"⚠️  High error rate: {agent} ({metrics['error_rate']:.1%})")
```

---

### Use Case 4: User Activity Tracking

```python
user_manager = UserManager()

# Get user activity
user_id = 'user_123'
activity = user_manager.get_user_activity(user_id, days=30)

print(f"👤 User Activity (30 days)")
print(f"Projects Created: {activity['projects_created']}")
print(f"Content Generated: {activity['content_generated']}")
print(f"Total Cost: ${activity['total_cost']:.2f}")
print(f"Login Count: {activity['login_count']}")
```

---

## 🧪 Run Examples

### Run All Phase 4 Examples

```bash
python examples/test_phase4.py
```

This will run 7 comprehensive examples:
1. Publishing Content to Multiple Platforms
2. Analytics Dashboard Overview
3. Platform Performance Comparison
4. Agent Performance Monitoring
5. User Management Operations
6. Real-time Performance Monitoring
7. Complete End-to-End Workflow

### Run Individual Examples

```python
# Publishing
python -c "from examples.test_phase4 import example_1_publish_content; example_1_publish_content()"

# Analytics
python -c "from examples.test_phase4 import example_2_analytics_dashboard; example_2_analytics_dashboard()"

# Performance
python -c "from examples.test_phase4 import example_6_performance_monitoring; example_6_performance_monitoring()"
```

---

## 📊 Key Metrics to Monitor

### Content Performance
- Views across all platforms
- Engagement rate (likes, shares, comments)
- Quality scores
- Cost per content piece

### Agent Performance
- Execution time
- Success rate
- Cost per operation
- Error rate

### Platform Performance
- Reach and impressions
- Engagement rate
- Best performing platform
- Optimal posting times

### System Health
- Response time
- Error rate
- Resource utilization
- Uptime percentage

---

## 🔧 Configuration

### Alert Thresholds

```python
from src.monitoring.performance_monitor import performance_monitor

# Customize alert thresholds
performance_monitor.alert_thresholds = {
    'response_time_ms': 500,  # Alert if >500ms
    'error_rate': 0.05,       # Alert if >5% errors
    'queue_size': 100         # Alert if >100 queued tasks
}
```

### Budget Limits

```python
from src.infrastructure.cost_tracker import CostTracker

cost_tracker = CostTracker()
cost_tracker.set_budget_limit(1000.0)  # $1000/month
cost_tracker.set_alert_threshold(0.8)  # Alert at 80%
```

---

## 🐛 Troubleshooting

### Issue: Platform Authentication Failed

```python
# Check credentials
from src.infrastructure.platform_integrations import PlatformIntegrationManager

manager = PlatformIntegrationManager()
platform = manager.get_platform('wordpress')

# Test authentication
success = platform.authenticate({
    'username': 'your_username',
    'application_password': 'your_password'
})

if not success:
    print("❌ Authentication failed - check credentials")
```

### Issue: Low Performance

```python
# Check system health
from src.infrastructure.analytics_dashboard import AnalyticsDashboard

dashboard = AnalyticsDashboard()
health = dashboard.get_system_health()

if health['overall_status'] != 'healthy':
    print(f"⚠️  System status: {health['overall_status']}")
    for component, status in health['components'].items():
        if status['status'] != 'healthy':
            print(f"  Issue with {component}: {status}")
```

---

## 📚 Next Steps

1. **Customize Platform Settings**
   - Configure API credentials
   - Set up webhook endpoints
   - Customize posting schedules

2. **Set Up Monitoring**
   - Configure alert thresholds
   - Set up budget limits
   - Enable real-time dashboards

3. **Create User Roles**
   - Define team structure
   - Assign permissions
   - Set up authentication

4. **Optimize Performance**
   - Review agent metrics
   - Identify bottlenecks
   - Tune configurations

---

## 🎓 Best Practices

1. **Always run QA before publishing**
   ```python
   workflow.publish_content(project_id, platforms, run_qa=True)
   ```

2. **Monitor costs regularly**
   ```python
   costs = dashboard.get_cost_analysis()
   if costs['budget_utilization'] > 80:
       print("⚠️  Approaching budget limit")
   ```

3. **Check alerts daily**
   ```python
   alerts = performance_monitor.get_alerts()
   for alert in alerts:
       handle_alert(alert)
   ```

4. **Review analytics weekly**
   ```python
   summary = dashboard.get_dashboard_summary()
   # Make data-driven decisions
   ```

---

## 🆘 Support

For issues or questions:
1. Check [PHASE_4_COMPLETE.md](PHASE_4_COMPLETE.md) for detailed documentation
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Run examples in `examples/test_phase4.py`

---

**🎉 You're ready to use Phase 4!**

Start publishing, monitoring, and analyzing your content across multiple platforms!

---

*Last Updated: December 26, 2025*
