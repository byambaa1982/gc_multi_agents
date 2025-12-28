"""
Budget Controller and Cost Optimization

Implements comprehensive budget management, cost tracking, and optimization
recommendations for the multi-agent content generation system.
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading


class AlertLevel(Enum):
    """Budget alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class CostCategory(Enum):
    """Cost categories for tracking"""
    AI_API_CALLS = "ai_api_calls"
    STORAGE = "storage"
    COMPUTE = "compute"
    NETWORK = "network"
    DATABASE = "database"
    CACHING = "caching"
    MONITORING = "monitoring"
    OTHER = "other"


@dataclass
class BudgetAlert:
    """Budget alert when thresholds are exceeded"""
    level: AlertLevel
    category: CostCategory
    message: str
    current_cost: float
    budget_limit: float
    percentage_used: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    actions_taken: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class CostEntry:
    """Individual cost entry"""
    category: CostCategory
    amount: float
    description: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    service: Optional[str] = None
    resource_id: Optional[str] = None


class BudgetController:
    """
    Comprehensive budget control and cost optimization system
    
    Features:
    - Real-time cost tracking per category
    - Budget enforcement with automatic throttling
    - Predictive budget alerts
    - Cost optimization recommendations
    - Detailed cost reporting and analytics
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Budget Controller
        
        Args:
            config: Configuration with budget limits and settings
        """
        self.config = config or {}
        
        # Budget limits per category (monthly)
        self.budgets: Dict[CostCategory, float] = {
            CostCategory.AI_API_CALLS: self.config.get("ai_api_budget", 100.0),
            CostCategory.STORAGE: self.config.get("storage_budget", 20.0),
            CostCategory.COMPUTE: self.config.get("compute_budget", 50.0),
            CostCategory.NETWORK: self.config.get("network_budget", 10.0),
            CostCategory.DATABASE: self.config.get("database_budget", 30.0),
            CostCategory.CACHING: self.config.get("caching_budget", 10.0),
            CostCategory.MONITORING: self.config.get("monitoring_budget", 5.0),
            CostCategory.OTHER: self.config.get("other_budget", 25.0)
        }
        
        # Total monthly budget
        self.total_budget = self.config.get("total_monthly_budget", 250.0)
        
        # Cost tracking
        self.cost_entries: List[CostEntry] = []
        self.cost_lock = threading.RLock()
        
        # Alert thresholds (percentage of budget)
        self.warning_threshold = self.config.get("warning_threshold", 0.8)  # 80%
        self.critical_threshold = self.config.get("critical_threshold", 0.95)  # 95%
        
        # Alerts
        self.alerts: List[BudgetAlert] = []
        
        # Auto-throttle settings
        self.auto_throttle_enabled = self.config.get("auto_throttle", True)
        self.throttled_categories: set = set()
        
        # Pricing models (per 1K units unless specified)
        self.pricing = {
            "gemini-1.5-flash": {
                "input_per_1k_chars": 0.00002,
                "output_per_1k_chars": 0.00006
            },
            "gemini-1.5-pro": {
                "input_per_1k_chars": 0.00005,
                "output_per_1k_chars": 0.00015
            },
            "gemini-pro-vision": {
                "input_per_1k_chars": 0.00005,
                "image": 0.0025
            },
            "storage_per_gb_month": 0.02,
            "egress_per_gb": 0.12,
            "firestore_read_per_100k": 0.06,
            "firestore_write_per_100k": 0.18,
            "cloud_run_vcpu_second": 0.00002400,
            "cloud_run_gb_second": 0.00000250,
            "redis_gb_month": 0.054
        }
        
        print("✅ Budget Controller initialized")
        self._print_budget_summary()
    
    def record_cost(self,
                   category: CostCategory,
                   amount: float,
                   description: str,
                   metadata: Optional[Dict[str, Any]] = None,
                   service: Optional[str] = None,
                   resource_id: Optional[str] = None) -> bool:
        """
        Record a cost entry
        
        Args:
            category: Cost category
            amount: Cost amount in USD
            description: Cost description
            metadata: Additional metadata
            service: GCP service name
            resource_id: Resource identifier
            
        Returns:
            True if cost was recorded, False if throttled
        """
        # Check if category is throttled
        if category in self.throttled_categories:
            print(f"⚠️ Cost recording blocked - {category.value} is throttled")
            return False
        
        # Create cost entry
        entry = CostEntry(
            category=category,
            amount=amount,
            description=description,
            metadata=metadata or {},
            service=service,
            resource_id=resource_id
        )
        
        with self.cost_lock:
            self.cost_entries.append(entry)
        
        # Check budget and generate alerts
        self._check_budget(category)
        
        return True
    
    def calculate_ai_cost(self,
                         model: str,
                         input_chars: int,
                         output_chars: int = 0,
                         images: int = 0) -> float:
        """
        Calculate AI API call cost
        
        Args:
            model: Model name
            input_chars: Input character count
            output_chars: Output character count
            images: Number of images (for vision models)
            
        Returns:
            Estimated cost in USD
        """
        if model not in self.pricing:
            print(f"⚠️ Unknown model: {model}, using default pricing")
            model = "gemini-1.5-flash"
        
        pricing = self.pricing[model]
        cost = 0.0
        
        # Calculate text cost
        if "input_per_1k_chars" in pricing:
            cost += (input_chars / 1000) * pricing["input_per_1k_chars"]
        
        if output_chars > 0 and "output_per_1k_chars" in pricing:
            cost += (output_chars / 1000) * pricing["output_per_1k_chars"]
        
        # Calculate image cost
        if images > 0 and "image" in pricing:
            cost += images * pricing["image"]
        
        return cost
    
    def estimate_operation_cost(self,
                               operation_type: str,
                               params: Dict[str, Any]) -> float:
        """
        Estimate cost for a planned operation
        
        Args:
            operation_type: Type of operation
            params: Operation parameters
            
        Returns:
            Estimated cost in USD
        """
        if operation_type == "content_generation":
            return self.calculate_ai_cost(
                model=params.get("model", "gemini-1.5-flash"),
                input_chars=params.get("input_chars", 2000),
                output_chars=params.get("output_chars", 5000)
            )
        
        elif operation_type == "image_generation":
            return self.pricing.get("gemini-pro-vision", {}).get("image", 0.0025)
        
        elif operation_type == "storage":
            gb_months = params.get("gb_months", 1)
            return gb_months * self.pricing["storage_per_gb_month"]
        
        return 0.0
    
    def _check_budget(self, category: CostCategory):
        """Check budget limits and generate alerts"""
        current_cost = self.get_current_cost(category, period_days=30)
        budget_limit = self.budgets.get(category, 0)
        
        if budget_limit == 0:
            return
        
        percentage_used = current_cost / budget_limit
        
        # Generate alerts based on thresholds
        if percentage_used >= self.critical_threshold:
            self._create_alert(
                AlertLevel.CRITICAL,
                category,
                current_cost,
                budget_limit,
                percentage_used
            )
            
            # Auto-throttle if enabled
            if self.auto_throttle_enabled:
                self._throttle_category(category)
        
        elif percentage_used >= self.warning_threshold:
            self._create_alert(
                AlertLevel.WARNING,
                category,
                current_cost,
                budget_limit,
                percentage_used
            )
    
    def _create_alert(self,
                     level: AlertLevel,
                     category: CostCategory,
                     current_cost: float,
                     budget_limit: float,
                     percentage_used: float):
        """Create a budget alert"""
        alert = BudgetAlert(
            level=level,
            category=category,
            message=f"{category.value} budget at {percentage_used*100:.1f}%",
            current_cost=current_cost,
            budget_limit=budget_limit,
            percentage_used=percentage_used,
            recommendations=self._get_cost_optimization_recommendations(category)
        )
        
        self.alerts.append(alert)
        
        icon = "🚨" if level == AlertLevel.CRITICAL else "⚠️"
        print(f"{icon} [{level.value.upper()}] {alert.message}: ${current_cost:.2f} / ${budget_limit:.2f}")
    
    def _throttle_category(self, category: CostCategory):
        """Throttle a category that exceeded budget"""
        if category not in self.throttled_categories:
            self.throttled_categories.add(category)
            print(f"🛑 Auto-throttle enabled for {category.value}")
            
            # Find the latest alert for this category
            for alert in reversed(self.alerts):
                if alert.category == category:
                    alert.actions_taken.append(f"Auto-throttled at {datetime.utcnow().isoformat()}")
                    break
    
    def unthrottle_category(self, category: CostCategory):
        """Remove throttle from a category"""
        if category in self.throttled_categories:
            self.throttled_categories.remove(category)
            print(f"✅ Throttle removed from {category.value}")
    
    def get_current_cost(self,
                        category: Optional[CostCategory] = None,
                        period_days: int = 30) -> float:
        """
        Get current cost for a category or total
        
        Args:
            category: Cost category (None for total)
            period_days: Time period in days
            
        Returns:
            Total cost in USD
        """
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        
        with self.cost_lock:
            filtered_entries = [
                entry for entry in self.cost_entries
                if entry.timestamp >= cutoff_date
            ]
            
            if category:
                filtered_entries = [e for e in filtered_entries if e.category == category]
            
            return sum(entry.amount for entry in filtered_entries)
    
    def get_budget_status(self) -> Dict[str, Any]:
        """
        Get comprehensive budget status
        
        Returns:
            Dictionary with budget status for all categories
        """
        status = {
            "total": {
                "budget": self.total_budget,
                "spent": self.get_current_cost(period_days=30),
                "remaining": 0,
                "percentage_used": 0
            },
            "categories": {},
            "alerts": {
                "critical": len([a for a in self.alerts if a.level == AlertLevel.CRITICAL]),
                "warning": len([a for a in self.alerts if a.level == AlertLevel.WARNING]),
                "info": len([a for a in self.alerts if a.level == AlertLevel.INFO])
            },
            "throttled_categories": [c.value for c in self.throttled_categories]
        }
        
        # Calculate total
        total_spent = status["total"]["spent"]
        status["total"]["remaining"] = self.total_budget - total_spent
        status["total"]["percentage_used"] = (total_spent / self.total_budget) * 100
        
        # Calculate per category
        for category in CostCategory:
            budget = self.budgets.get(category, 0)
            spent = self.get_current_cost(category, period_days=30)
            
            status["categories"][category.value] = {
                "budget": budget,
                "spent": spent,
                "remaining": budget - spent,
                "percentage_used": (spent / budget * 100) if budget > 0 else 0,
                "throttled": category in self.throttled_categories
            }
        
        return status
    
    def _get_cost_optimization_recommendations(self, category: CostCategory) -> List[str]:
        """Get cost optimization recommendations for a category"""
        recommendations = []
        
        if category == CostCategory.AI_API_CALLS:
            recommendations = [
                "Implement aggressive caching for similar prompts",
                "Use cheaper models (flash vs pro) when appropriate",
                "Batch API calls to reduce overhead",
                "Optimize prompt length and complexity",
                "Implement request deduplication",
                "Use semantic similarity to reuse previous results"
            ]
        
        elif category == CostCategory.STORAGE:
            recommendations = [
                "Implement lifecycle policies for old content",
                "Use nearline/coldline storage for archives",
                "Compress media files before storage",
                "Delete temporary/intermediate files",
                "Review and remove duplicate content"
            ]
        
        elif category == CostCategory.COMPUTE:
            recommendations = [
                "Right-size Cloud Run instances",
                "Use autoscaling to reduce idle costs",
                "Implement request batching",
                "Use preemptible VMs for batch jobs",
                "Optimize cold start times"
            ]
        
        elif category == CostCategory.DATABASE:
            recommendations = [
                "Optimize Firestore queries and indexes",
                "Implement read caching",
                "Batch read/write operations",
                "Archive old data to BigQuery",
                "Use composite indexes efficiently"
            ]
        
        elif category == CostCategory.CACHING:
            recommendations = [
                "Optimize Redis memory usage",
                "Adjust TTL values appropriately",
                "Use compression for cached data",
                "Right-size Redis instance"
            ]
        
        return recommendations
    
    def get_cost_report(self,
                       period_days: int = 30,
                       group_by: str = "category") -> Dict[str, Any]:
        """
        Generate detailed cost report
        
        Args:
            period_days: Time period for report
            group_by: Group by 'category', 'service', or 'day'
            
        Returns:
            Cost report dictionary
        """
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        
        with self.cost_lock:
            entries = [
                entry for entry in self.cost_entries
                if entry.timestamp >= cutoff_date
            ]
        
        report = {
            "period": {
                "start": cutoff_date.isoformat(),
                "end": datetime.utcnow().isoformat(),
                "days": period_days
            },
            "total_cost": sum(e.amount for e in entries),
            "entry_count": len(entries),
            "breakdown": {}
        }
        
        # Group entries
        if group_by == "category":
            for category in CostCategory:
                category_entries = [e for e in entries if e.category == category]
                report["breakdown"][category.value] = {
                    "cost": sum(e.amount for e in category_entries),
                    "count": len(category_entries),
                    "budget": self.budgets.get(category, 0)
                }
        
        elif group_by == "service":
            services = set(e.service for e in entries if e.service)
            for service in services:
                service_entries = [e for e in entries if e.service == service]
                report["breakdown"][service] = {
                    "cost": sum(e.amount for e in service_entries),
                    "count": len(service_entries)
                }
        
        elif group_by == "day":
            # Group by day
            daily_costs: Dict[str, float] = {}
            for entry in entries:
                day_key = entry.timestamp.strftime("%Y-%m-%d")
                daily_costs[day_key] = daily_costs.get(day_key, 0) + entry.amount
            
            report["breakdown"] = daily_costs
        
        return report
    
    def predict_monthly_cost(self) -> Tuple[float, bool]:
        """
        Predict end-of-month cost based on current spending rate
        
        Returns:
            Tuple of (predicted_cost, will_exceed_budget)
        """
        # Get spending for last 7 days
        recent_cost = self.get_current_cost(period_days=7)
        daily_average = recent_cost / 7
        
        # Predict for 30 days
        predicted_monthly = daily_average * 30
        
        will_exceed = predicted_monthly > self.total_budget
        
        if will_exceed:
            print(f"⚠️ Predicted monthly cost: ${predicted_monthly:.2f} (exceeds budget: ${self.total_budget:.2f})")
        
        return predicted_monthly, will_exceed
    
    def export_cost_data(self, filepath: str):
        """Export cost data to JSON file"""
        with self.cost_lock:
            data = {
                "exported_at": datetime.utcnow().isoformat(),
                "total_entries": len(self.cost_entries),
                "entries": [
                    {
                        "category": entry.category.value,
                        "amount": entry.amount,
                        "description": entry.description,
                        "timestamp": entry.timestamp.isoformat(),
                        "service": entry.service,
                        "resource_id": entry.resource_id,
                        "metadata": entry.metadata
                    }
                    for entry in self.cost_entries
                ]
            }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Cost data exported to {filepath}")
    
    def _print_budget_summary(self):
        """Print budget summary on initialization"""
        print("\n📊 Budget Summary:")
        print(f"   Total Monthly Budget: ${self.total_budget:.2f}")
        print(f"   Warning Threshold: {self.warning_threshold*100:.0f}%")
        print(f"   Critical Threshold: {self.critical_threshold*100:.0f}%")
        print(f"   Auto-throttle: {'Enabled' if self.auto_throttle_enabled else 'Disabled'}")
