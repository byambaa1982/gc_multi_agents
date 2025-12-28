# Phase 5 Quick Start Guide 🚀

**Production Optimization, Cost Control, and Security**

---

## 📋 What's New in Phase 5

Phase 5 adds enterprise-grade optimization, monitoring, and security features:

1. **Performance Monitoring** - Real-time metrics and alerts
2. **Budget Control** - Cost tracking and automatic throttling
3. **Advanced Caching** - Enhanced 3-tier caching strategy
4. **Load Testing** - Comprehensive testing framework
5. **Security Hardening** - Input validation, rate limiting, encryption

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New Phase 5 dependencies:
- `psutil` - System resource monitoring
- `cryptography` - Secret encryption
- `google-cloud-monitoring` - Cloud Monitoring integration

### 2. Run the Integration Example

```bash
# Set your project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Run Phase 5 example
python examples/phase5_integration_example.py
```

---

## 💡 Basic Usage Examples

### Performance Monitoring

```python
from src.infrastructure.performance_monitor import (
    PerformanceMonitor,
    MetricType,
    PerformanceContext
)

# Initialize monitor
monitor = PerformanceMonitor(config={
    "project_id": "your-project",
    "latency_threshold_ms": 200
})

# Start background monitoring
monitor.start_system_monitoring(interval_seconds=60)

# Track operation performance
with PerformanceContext(monitor, "content_generation"):
    result = generate_content()

# Record custom metrics
monitor.record_metric(
    MetricType.LATENCY,
    150.5,
    labels={"operation": "image_generation"}
)

# Get performance report
report = monitor.get_performance_report(time_window_hours=24)
print(f"Average latency: {report['metrics']['latency']['mean']:.2f}ms")

# Check alerts
alerts = monitor.get_active_alerts(severity="CRITICAL", hours=1)
for alert in alerts:
    print(f"⚠️ {alert.message}: {alert.current_value}")
```

### Budget Control

```python
from src.infrastructure.budget_controller import (
    BudgetController,
    CostCategory
)

# Initialize controller
controller = BudgetController(config={
    "total_monthly_budget": 250.0,
    "ai_api_budget": 100.0,
    "auto_throttle": True
})

# Estimate cost before operation
estimated_cost = controller.calculate_ai_cost(
    model="gemini-1.5-flash",
    input_chars=2000,
    output_chars=5000
)
print(f"Estimated cost: ${estimated_cost:.4f}")

# Record actual cost
controller.record_cost(
    category=CostCategory.AI_API_CALLS,
    amount=0.15,
    description="Blog post generation",
    service="vertex-ai"
)

# Check budget status
status = controller.get_budget_status()
print(f"Spent: ${status['total']['spent']:.2f}")
print(f"Remaining: ${status['total']['remaining']:.2f}")

# Get cost predictions
predicted, will_exceed = controller.predict_monthly_cost()
if will_exceed:
    print(f"⚠️ Warning: Predicted ${predicted:.2f} exceeds budget")
```

### Security Hardening

```python
from src.infrastructure.security_hardening import SecurityHardening

# Initialize security
security = SecurityHardening(config={})

# Validate incoming request
valid, reason = security.validate_request(
    user_id="user123",
    ip_address="192.168.1.1",
    data={"topic": "AI trends", "content": "User input..."}
)

if not valid:
    print(f"❌ Request blocked: {reason}")
else:
    print("✅ Request validated")

# Sanitize user input
safe_text = security.validator.sanitize_text(
    "User <script>alert('xss')</script> input",
    max_length=1000
)

# Rotate API keys
new_key = security.secret_manager.rotate_api_key("google_cloud")
print(f"New API key: {new_key[:10]}...")

# Get security report
report = security.auditor.get_security_report(hours=24)
print(f"Security events: {report['total_events']}")
print(f"Critical: {report['events_by_severity']['CRITICAL']}")

# Add security headers to HTTP responses
headers = security.get_security_headers()
```

### Load Testing

```python
from src.infrastructure.load_testing import LoadTester

# Initialize tester
tester = LoadTester(config={
    "max_avg_response_time_ms": 200,
    "min_success_rate": 0.95
})

# Define test operation
def api_call(**kwargs):
    # Your API call here
    response = make_request()
    return response

# Run baseline test
report = tester.run_baseline_test(
    operation=api_call,
    operation_args={"param": "value"}
)

# Print results
tester.print_report(report)

# Run stress test
stress_report = tester.run_stress_test(operation=api_call)

# Export results
tester.export_report(stress_report, "stress_test_results.json")
```

---

## 📊 Monitoring Dashboard

### Key Metrics to Track

**Performance Metrics:**
- Average latency < 200ms
- P95 latency < 500ms
- Error rate < 5%
- CPU usage < 80%
- Memory usage < 85%
- Cache hit rate > 60%

**Cost Metrics:**
- Daily spending vs budget
- Cost per operation
- AI API call costs
- Storage costs
- Compute costs

**Security Metrics:**
- Failed authentication attempts
- Rate limit violations
- Blocked IPs/users
- Suspicious activity events

### Viewing Metrics

```python
# Performance metrics
perf_stats = monitor.get_metric_statistics(
    MetricType.LATENCY,
    time_window_minutes=5
)
print(f"Latency - Mean: {perf_stats['mean']:.2f}ms")
print(f"Latency - P95: {perf_stats['p95']:.2f}ms")

# Cost breakdown
cost_report = controller.get_cost_report(
    period_days=30,
    group_by="category"
)
print(f"Total cost: ${cost_report['total_cost']:.2f}")
for category, data in cost_report['breakdown'].items():
    print(f"  {category}: ${data['cost']:.2f}")

# Security events
security_report = security.auditor.get_security_report(hours=24)
print(f"Events by type: {security_report['events_by_type']}")
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Required
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Optional - Redis (for L2 cache)
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export REDIS_PASSWORD="your-redis-password"

# Optional - Performance thresholds
export LATENCY_THRESHOLD_MS="200"
export ERROR_RATE_THRESHOLD="0.05"

# Optional - Budget limits
export TOTAL_MONTHLY_BUDGET="250.0"
export AI_API_BUDGET="100.0"
```

### Configuration File

Create `config/phase5_config.yaml`:

```yaml
performance:
  latency_threshold_ms: 200
  error_rate_threshold: 0.05
  cpu_usage_threshold: 80
  memory_usage_threshold: 85
  monitoring_interval_seconds: 60

budget:
  total_monthly_budget: 250.0
  budgets:
    ai_api_calls: 100.0
    storage: 20.0
    compute: 50.0
    database: 30.0
  warning_threshold: 0.8
  critical_threshold: 0.95
  auto_throttle: true

caching:
  redis_enabled: false
  l1_ttl_seconds: 3600    # 1 hour
  l2_ttl_seconds: 86400   # 24 hours
  
security:
  rate_limits:
    - name: "api_general"
      max_requests: 100
      window_seconds: 60
    - name: "api_heavy"
      max_requests: 10
      window_seconds: 60

load_testing:
  baseline:
    duration_seconds: 60
    concurrent_users: 10
  stress:
    duration_seconds: 300
    concurrent_users: 100
```

---

## 🔍 Common Operations

### 1. Check System Health

```python
# Get comprehensive status
monitor = PerformanceMonitor()
controller = BudgetController()
security = SecurityHardening()

# Performance
alerts = monitor.get_active_alerts(severity="CRITICAL")
if alerts:
    print("⚠️ Performance issues detected!")
    for alert in alerts:
        print(f"  - {alert.message}")

# Budget
status = controller.get_budget_status()
if status['total']['percentage_used'] > 80:
    print("⚠️ Budget warning!")
    print(f"  Used: {status['total']['percentage_used']:.1f}%")

# Security
sec_report = security.auditor.get_security_report(hours=1)
if sec_report['events_by_severity']['CRITICAL'] > 0:
    print("🚨 Critical security events!")
```

### 2. Export Reports

```python
# Performance report
monitor.export_metrics("performance_metrics.json")

# Cost report
controller.export_cost_data("cost_data.json")

# Security audit log
security.auditor.export_audit_log("security_audit.json", hours=24)

# Load test results
tester.export_report(report, "load_test.json")
```

### 3. Optimize Performance

```python
# Get performance recommendations
report = monitor.get_performance_report(time_window_hours=24)
for recommendation in report['recommendations']:
    print(f"💡 {recommendation}")

# Get cost optimization recommendations
status = controller.get_budget_status()
for category, data in status['categories'].items():
    if data['percentage_used'] > 80:
        recommendations = controller._get_cost_optimization_recommendations(
            CostCategory[category.upper()]
        )
        print(f"\n{category} optimization:")
        for rec in recommendations:
            print(f"  - {rec}")
```

---

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/test_performance_monitor.py
pytest tests/test_budget_controller.py
pytest tests/test_security_hardening.py
```

### Run Load Tests

```python
from src.infrastructure.load_testing import LoadTester

tester = LoadTester()

# Test all scenarios
baseline = tester.run_baseline_test(your_operation)
stress = tester.run_stress_test(your_operation)
spike = tester.run_spike_test(your_operation)
endurance = tester.run_endurance_test(your_operation)
scalability = tester.run_scalability_test(your_operation)

# Print all reports
for report in [baseline, stress, spike, endurance, scalability]:
    tester.print_report(report)
```

---

## 📈 Best Practices

### Performance

1. **Monitor continuously** - Keep system monitoring running
2. **Set appropriate thresholds** - Based on your SLAs
3. **Use percentiles** - P95, P99 more meaningful than averages
4. **Track trends** - Look for degradation over time
5. **Act on alerts** - Don't ignore warnings

### Cost Management

1. **Set realistic budgets** - Based on expected usage
2. **Enable auto-throttle** - Prevent cost overruns
3. **Review regularly** - Weekly cost analysis
4. **Optimize aggressively** - Cache, batch, choose cheaper models
5. **Predict ahead** - Use monthly predictions

### Security

1. **Validate all inputs** - Never trust user data
2. **Encrypt secrets** - Use Secret Manager
3. **Rate limit APIs** - Prevent abuse
4. **Monitor security events** - Review daily
5. **Rotate keys regularly** - Monthly rotation recommended

### Caching

1. **Cache aggressively** - But with appropriate TTLs
2. **Monitor hit rates** - Target > 60%
3. **Use semantic similarity** - Reuse similar queries
4. **Invalidate smartly** - When content changes
5. **Warm critical caches** - Pre-load frequently used data

---

## 🚨 Troubleshooting

### High Latency

```python
# Check performance stats
stats = monitor.get_metric_statistics(MetricType.LATENCY)
print(f"Average: {stats['mean']:.2f}ms")
print(f"P95: {stats['p95']:.2f}ms")

# Check bottlenecks
# - Database queries slow?
# - AI API calls slow?
# - Cache miss rate high?

# Solutions:
# - Enable caching
# - Optimize queries
# - Add indexes
# - Scale resources
```

### Budget Exceeded

```python
# Check what's consuming budget
report = controller.get_cost_report(group_by="category")
for category, data in report['breakdown'].items():
    if data['cost'] > 0:
        print(f"{category}: ${data['cost']:.2f}")

# Solutions:
# - Enable auto-throttle
# - Increase caching
# - Use cheaper models
# - Optimize operations
```

### Security Issues

```python
# Check recent events
report = security.auditor.get_security_report(hours=1)
print(f"Events: {report['events_by_type']}")
print(f"Blocked IPs: {report['blocked_ips']}")

# Unblock if needed
security.auditor.unblock_ip("192.168.1.1")

# Solutions:
# - Review blocked IPs/users
# - Adjust rate limits
# - Check for false positives
# - Strengthen validation
```

---

## 📚 Additional Resources

- [PHASE_5_COMPLETE.md](PHASE_5_COMPLETE.md) - Full implementation details
- [ARCHITECTURE_REVIEW_SUMMARY.md](ARCHITECTURE_REVIEW_SUMMARY.md) - Architecture review
- [examples/phase5_integration_example.py](examples/phase5_integration_example.py) - Complete integration example

---

## ✅ Success Checklist

Before deploying to production:

- [ ] Performance monitoring configured
- [ ] Budget limits set appropriately
- [ ] Security hardening enabled
- [ ] Load tests passed
- [ ] Cache hit rate > 60%
- [ ] Alert thresholds configured
- [ ] Auto-throttle enabled
- [ ] Secrets encrypted
- [ ] Rate limiting active
- [ ] Monitoring dashboards set up
- [ ] Cost alerts configured
- [ ] Security audit log enabled

---

## 🎯 Next Steps

1. **Run integration example** to verify setup
2. **Configure thresholds** based on your requirements
3. **Set up dashboards** in Google Cloud Monitoring
4. **Run load tests** to validate capacity
5. **Enable monitoring** in production
6. **Review metrics daily** and optimize

---

**Phase 5 Status:** ✅ COMPLETE and ready for production!
