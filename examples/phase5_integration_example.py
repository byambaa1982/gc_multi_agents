"""
Phase 5 Integration Example

Demonstrates how to integrate all Phase 5 components:
- Performance Monitoring
- Budget Control
- Advanced Caching
- Load Testing
- Security Hardening
"""

import os
import time
from typing import Dict, Any

# Phase 5 Components
from src.infrastructure.performance_monitor import (
    PerformanceMonitor,
    MetricType,
    PerformanceContext
)
from src.infrastructure.budget_controller import (
    BudgetController,
    CostCategory
)
from src.infrastructure.cache_manager import CacheManager
from src.infrastructure.security_hardening import (
    SecurityHardening,
    SecurityEventType
)

# Phase 4 Components
from src.agents.content_agent import ContentAgent
from src.infrastructure.firestore import FirestoreManager


class OptimizedContentPipeline:
    """
    Production-ready content generation pipeline with Phase 5 optimizations
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize optimized pipeline"""
        self.config = config
        
        # Phase 5: Performance Monitoring
        self.performance_monitor = PerformanceMonitor(config={
            "project_id": config.get("project_id"),
            "latency_threshold_ms": 200,
            "error_rate_threshold": 0.05
        })
        print("✅ Performance Monitor initialized")
        
        # Phase 5: Budget Control
        self.budget_controller = BudgetController(config={
            "total_monthly_budget": 250.0,
            "ai_api_budget": 100.0,
            "warning_threshold": 0.8,
            "critical_threshold": 0.95,
            "auto_throttle": True
        })
        print("✅ Budget Controller initialized")
        
        # Phase 5: Security Hardening
        self.security = SecurityHardening(config={})
        print("✅ Security Hardening initialized")
        
        # Phase 2: Cache Manager (enhanced)
        cache_config = {
            "redis_enabled": config.get("redis_enabled", False),
            "l1_ttl_seconds": 3600,  # 1 hour
            "l2_ttl_seconds": 86400  # 24 hours
        }
        if config.get("redis_enabled"):
            cache_config["redis"] = {
                "host": os.getenv("REDIS_HOST", "localhost"),
                "port": int(os.getenv("REDIS_PORT", 6379)),
                "password": os.getenv("REDIS_PASSWORD")
            }
        
        self.cache_manager = CacheManager(cache_config)
        print("✅ Cache Manager initialized")
        
        # Phase 1: Content Agent
        self.content_agent = ContentAgent(
            project_id=config.get("project_id"),
            location=config.get("location", "us-central1")
        )
        print("✅ Content Agent initialized")
        
        # Firestore
        self.firestore = FirestoreManager(
            project_id=config.get("project_id")
        )
        print("✅ Firestore initialized")
        
        # Start background monitoring
        self.performance_monitor.start_system_monitoring(interval_seconds=60)
        print("✅ System monitoring started")
    
    def generate_content(self,
                        topic: str,
                        content_type: str = "blog",
                        user_id: str = None,
                        ip_address: str = None) -> Dict[str, Any]:
        """
        Generate content with full Phase 5 optimizations
        
        Args:
            topic: Content topic
            content_type: Type of content
            user_id: User identifier
            ip_address: Request IP address
            
        Returns:
            Generated content and metadata
        """
        
        # Phase 5: Security Validation
        valid, reason = self.security.validate_request(
            user_id=user_id,
            ip_address=ip_address,
            data={"topic": topic, "content_type": content_type}
        )
        
        if not valid:
            self.security.auditor.log_event(
                SecurityEventType.AUTHORIZATION_FAILURE,
                "HIGH",
                f"Request blocked: {reason}",
                user_id=user_id,
                ip_address=ip_address
            )
            return {
                "success": False,
                "error": reason
            }
        
        # Phase 5: Input Sanitization
        topic = self.security.validator.sanitize_text(topic, max_length=500)
        
        # Check cache first
        cache_key = f"content:{content_type}:{topic}"
        cached_content = self.cache_manager.get(cache_key)
        
        if cached_content:
            print(f"✅ Cache hit for: {topic}")
            self.performance_monitor.record_metric(
                MetricType.CACHE_HIT_RATE,
                1.0,
                labels={"operation": "content_generation"}
            )
            return cached_content
        
        print(f"❌ Cache miss for: {topic}")
        self.performance_monitor.record_metric(
            MetricType.CACHE_HIT_RATE,
            0.0,
            labels={"operation": "content_generation"}
        )
        
        # Phase 5: Estimate and check cost
        estimated_cost = self.budget_controller.estimate_operation_cost(
            "content_generation",
            {
                "model": "gemini-1.5-flash",
                "input_chars": len(topic) + 500,  # topic + prompt template
                "output_chars": 5000  # expected output
            }
        )
        
        print(f"💰 Estimated cost: ${estimated_cost:.4f}")
        
        # Check if we can afford this operation
        status = self.budget_controller.get_budget_status()
        if status["categories"]["ai_api_calls"]["throttled"]:
            return {
                "success": False,
                "error": "Budget limit reached for AI API calls. Please try again later."
            }
        
        # Phase 5: Performance tracking
        with PerformanceContext(self.performance_monitor, "content_generation"):
            try:
                # Generate content
                result = self.content_agent.generate_content(
                    topic=topic,
                    content_type=content_type,
                    additional_requirements=f"Generate high-quality {content_type} content"
                )
                
                # Phase 5: Record actual cost
                actual_cost = self.budget_controller.calculate_ai_cost(
                    model="gemini-1.5-flash",
                    input_chars=len(topic) + 500,
                    output_chars=len(result.get("content", ""))
                )
                
                self.budget_controller.record_cost(
                    category=CostCategory.AI_API_CALLS,
                    amount=actual_cost,
                    description=f"Content generation: {topic}",
                    service="vertex-ai",
                    metadata={
                        "model": "gemini-1.5-flash",
                        "content_type": content_type,
                        "user_id": user_id
                    }
                )
                
                print(f"💰 Actual cost recorded: ${actual_cost:.4f}")
                
                # Cache the result
                self.cache_manager.set(
                    cache_key,
                    result,
                    ttl=3600  # Cache for 1 hour
                )
                
                # Save to Firestore
                self.firestore.create_document(
                    "generated_content",
                    {
                        "topic": topic,
                        "content_type": content_type,
                        "content": result.get("content"),
                        "cost": actual_cost,
                        "user_id": user_id,
                        "created_at": time.time()
                    }
                )
                
                # Record success metric
                self.performance_monitor.record_metric(
                    MetricType.ERROR_RATE,
                    0.0,
                    labels={"operation": "content_generation", "status": "success"}
                )
                
                return {
                    "success": True,
                    "content": result.get("content"),
                    "metadata": result.get("metadata", {}),
                    "cost": actual_cost,
                    "cached": False
                }
                
            except Exception as e:
                # Record error
                self.performance_monitor.record_metric(
                    MetricType.ERROR_RATE,
                    1.0,
                    labels={"operation": "content_generation", "status": "error"}
                )
                
                # Log security event if it looks suspicious
                error_str = str(e).lower()
                if any(word in error_str for word in ["permission", "unauthorized", "forbidden"]):
                    self.security.auditor.log_event(
                        SecurityEventType.AUTHENTICATION_FAILURE,
                        "MEDIUM",
                        f"Authentication error during content generation: {str(e)}",
                        user_id=user_id
                    )
                
                return {
                    "success": False,
                    "error": str(e)
                }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        return self.performance_monitor.get_performance_report(time_window_hours=24)
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status"""
        return self.budget_controller.get_budget_status()
    
    def get_security_report(self) -> Dict[str, Any]:
        """Get security report"""
        return self.security.auditor.get_security_report(hours=24)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache_manager.get_stats()
    
    def shutdown(self):
        """Graceful shutdown"""
        print("\n🛑 Shutting down pipeline...")
        
        # Stop monitoring
        self.performance_monitor.stop_system_monitoring()
        
        # Export reports
        print("\n📊 Generating final reports...")
        
        perf_report = self.get_performance_report()
        print(f"   Performance: {perf_report['metrics']}")
        
        budget_status = self.get_budget_status()
        print(f"   Budget: ${budget_status['total']['spent']:.2f} / ${budget_status['total']['budget']:.2f}")
        
        security_report = self.get_security_report()
        print(f"   Security Events: {security_report['total_events']}")
        
        cache_stats = self.get_cache_stats()
        print(f"   Cache: {cache_stats}")
        
        print("✅ Shutdown complete")


# Example usage
def main():
    """Example Phase 5 integration"""
    
    config = {
        "project_id": os.getenv("GOOGLE_CLOUD_PROJECT"),
        "location": "us-central1",
        "redis_enabled": False  # Set to True if Redis is available
    }
    
    # Initialize pipeline
    pipeline = OptimizedContentPipeline(config)
    
    print("\n" + "="*80)
    print("Phase 5 Optimized Content Generation Pipeline")
    print("="*80 + "\n")
    
    # Generate content
    topics = [
        "The Future of Artificial Intelligence",
        "Sustainable Energy Solutions",
        "Remote Work Best Practices"
    ]
    
    for topic in topics:
        print(f"\n{'='*80}")
        print(f"Generating content for: {topic}")
        print(f"{'='*80}\n")
        
        result = pipeline.generate_content(
            topic=topic,
            content_type="blog",
            user_id="user123",
            ip_address="192.168.1.1"
        )
        
        if result["success"]:
            print(f"✅ Content generated successfully")
            print(f"   Length: {len(result['content'])} characters")
            print(f"   Cost: ${result['cost']:.4f}")
            print(f"   Cached: {result.get('cached', False)}")
        else:
            print(f"❌ Generation failed: {result['error']}")
        
        # Small delay between requests
        time.sleep(2)
    
    # Get final reports
    print("\n" + "="*80)
    print("Final Reports")
    print("="*80 + "\n")
    
    print("📊 Performance Report:")
    perf_report = pipeline.get_performance_report()
    print(f"   Metrics collected: {len(perf_report['metrics'])}")
    print(f"   Alerts: {perf_report['alerts']}")
    
    print("\n💰 Budget Status:")
    budget = pipeline.get_budget_status()
    print(f"   Total spent: ${budget['total']['spent']:.2f}")
    print(f"   Budget remaining: ${budget['total']['remaining']:.2f}")
    print(f"   Percentage used: {budget['total']['percentage_used']:.1f}%")
    
    print("\n🔐 Security Report:")
    security = pipeline.get_security_report()
    print(f"   Total events: {security['total_events']}")
    print(f"   Events by severity: {security['events_by_severity']}")
    
    print("\n🚀 Cache Statistics:")
    cache_stats = pipeline.get_cache_stats()
    print(f"   Stats: {cache_stats}")
    
    # Shutdown
    pipeline.shutdown()


if __name__ == "__main__":
    main()
