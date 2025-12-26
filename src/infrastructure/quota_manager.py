"""
Quota Manager Service
Tracks API usage, enforces rate limits, and prevents quota exhaustion
"""

import os
import time
from typing import Dict, Any, Optional
from collections import defaultdict
from threading import Lock
from google.cloud import firestore
from src.monitoring.logger import StructuredLogger


class QuotaManager:
    """
    Manages API quotas and rate limiting for GCP services
    Implements token bucket algorithm for rate limiting
    """
    
    def __init__(self):
        """Initialize quota manager"""
        self.logger = StructuredLogger(name='quota_manager')
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        
        # Initialize Firestore for quota tracking
        self.db = firestore.Client(project=self.project_id)
        
        # In-memory token buckets for rate limiting
        self.token_buckets = defaultdict(lambda: {
            'tokens': 100,  # Start with full bucket
            'last_refill': time.time(),
            'max_tokens': 100,
            'refill_rate': 10  # tokens per second
        })
        
        self.lock = Lock()
        
        # Service quotas (requests per minute)
        self.service_quotas = {
            'vertex_ai_gemini_pro': {
                'rpm': 60,  # requests per minute
                'tpm': 1000000,  # tokens per minute
                'daily_limit': 10000
            },
            'vertex_ai_gemini_flash': {
                'rpm': 300,
                'tpm': 4000000,
                'daily_limit': 50000
            },
            'vertex_ai_imagen': {
                'rpm': 30,
                'daily_limit': 1000
            },
            'pubsub': {
                'rpm': 10000,
                'daily_limit': 1000000
            }
        }
        
        # Budget limits (in USD)
        self.budget_limits = {
            'daily': float(os.getenv('DAILY_BUDGET_LIMIT', '10.0')),
            'project': float(os.getenv('PROJECT_BUDGET_LIMIT', '1.0'))
        }
        
        # Budget alert thresholds (percentage)
        self.budget_alert_thresholds = [50, 80, 90, 95]
        self.alert_tracker = defaultdict(set)  # Track which alerts have been sent
        
        # Budget enforcement
        self.enforce_budget = os.getenv('ENFORCE_BUDGET', 'true').lower() == 'true'
        
        self.logger.info("Quota manager initialized", 
            extra={
                'daily_budget': self.budget_limits['daily'],
                'project_budget': self.budget_limits['project'],
                'enforce_budget': self.enforce_budget
            })
    
    def check_quota(
        self,
        service: str,
        operation_type: str = 'request',
        tokens: int = 1
    ) -> Dict[str, Any]:
        """
        Check if quota is available for a service operation
        
        Args:
            service: Service name (e.g., 'vertex_ai_gemini_pro')
            operation_type: Type of operation ('request' or 'tokens')
            tokens: Number of tokens/requests needed
            
        Returns:
            Dict with 'allowed' boolean and quota info
        """
        with self.lock:
            bucket_key = f"{service}:{operation_type}"
            bucket = self.token_buckets[bucket_key]
            
            # Refill tokens based on time elapsed
            self._refill_bucket(bucket)
            
            # Check if enough tokens available
            if bucket['tokens'] >= tokens:
                bucket['tokens'] -= tokens
                
                self.logger.debug(
                    f"Quota check passed for {service}",
                    service=service,
                    tokens_used=tokens,
                    tokens_remaining=bucket['tokens']
                )
                
                return {
                    'allowed': True,
                    'tokens_remaining': bucket['tokens'],
                    'service': service
                }
            else:
                # Calculate wait time
                tokens_needed = tokens - bucket['tokens']
                wait_time = tokens_needed / bucket['refill_rate']
                
                self.logger.warning(
                    f"Quota exceeded for {service}",
                    service=service,
                    tokens_needed=tokens,
                    tokens_available=bucket['tokens'],
                    wait_time_seconds=wait_time
                )
                
                return {
                    'allowed': False,
                    'tokens_remaining': bucket['tokens'],
                    'wait_time_seconds': wait_time,
                    'service': service
                }
    
    def _refill_bucket(self, bucket: Dict[str, Any]):
        """
        Refill token bucket based on elapsed time
        
        Args:
            bucket: Token bucket to refill
        """
        now = time.time()
        elapsed = now - bucket['last_refill']
        
        # Calculate tokens to add
        tokens_to_add = elapsed * bucket['refill_rate']
        
        # Refill bucket (cap at max)
        bucket['tokens'] = min(
            bucket['max_tokens'],
            bucket['tokens'] + tokens_to_add
        )
        
        bucket['last_refill'] = now
    
    def record_usage(
        self,
        project_id: str,
        service: str,
        operation: str,
        tokens_used: int,
        cost: float
    ):
        """
        Record API usage for tracking and billing
        
        Args:
            project_id: Content project ID
            service: Service used
            operation: Operation performed
            tokens_used: Number of tokens used
            cost: Cost in USD
        """
        try:
            usage_data = {
                'project_id': project_id,
                'service': service,
                'operation': operation,
                'tokens_used': tokens_used,
                'cost': cost,
                'timestamp': firestore.SERVER_TIMESTAMP
            }
            
            # Store in Firestore
            self.db.collection('api_usage').add(usage_data)
            
            self.logger.info(
                "Recorded API usage",
                project_id=project_id,
                service=service,
                cost=cost
            )
            
            # Check budget limits
            self._check_budget_limits(project_id, cost)
            
        except Exception as e:
            self.logger.error(
                "Failed to record usage",
                error=str(e),
                project_id=project_id
            )
    
    def _check_budget_limits(self, project_id: str, new_cost: float):
        """
        Check if budget limits are exceeded and send alerts
        
        Args:
            project_id: Content project ID
            new_cost: New cost to add
        """
        # Check project budget
        project_total = self.get_project_cost(project_id)
        project_budget = self.budget_limits['project']
        project_usage_percent = (project_total / project_budget) * 100 if project_budget > 0 else 0
        
        # Send alerts at thresholds
        for threshold in self.budget_alert_thresholds:
            if project_usage_percent >= threshold:
                alert_key = f"project:{project_id}:{threshold}"
                if alert_key not in self.alert_tracker[project_id]:
                    self._send_budget_alert(
                        alert_type="project",
                        project_id=project_id,
                        current_cost=project_total,
                        budget_limit=project_budget,
                        threshold_percent=threshold
                    )
                    self.alert_tracker[project_id].add(alert_key)
        
        # Enforce project budget if enabled
        if self.enforce_budget and (project_total + new_cost) > project_budget:
            raise Exception(
                f"Project budget exceeded: ${project_total:.2f} + ${new_cost:.2f} > ${project_budget:.2f}"
            )
        
        # Check daily budget
        daily_total = self.get_daily_cost()
        daily_budget = self.budget_limits['daily']
        daily_usage_percent = (daily_total / daily_budget) * 100 if daily_budget > 0 else 0
        
        # Send alerts at thresholds
        for threshold in self.budget_alert_thresholds:
            if daily_usage_percent >= threshold:
                alert_key = f"daily:{threshold}"
                if alert_key not in self.alert_tracker['daily']:
                    self._send_budget_alert(
                        alert_type="daily",
                        current_cost=daily_total,
                        budget_limit=daily_budget,
                        threshold_percent=threshold
                    )
                    self.alert_tracker['daily'].add(alert_key)
        
        # Enforce daily budget if enabled
        if self.enforce_budget and (daily_total + new_cost) > daily_budget:
            raise Exception(
                f"Daily budget exceeded: ${daily_total:.2f} + ${new_cost:.2f} > ${daily_budget:.2f}"
            )
    
    def _send_budget_alert(
        self,
        alert_type: str,
        current_cost: float,
        budget_limit: float,
        threshold_percent: int,
        project_id: Optional[str] = None
    ):
        """Send budget alert notification"""
        alert_data = {
            "alert_type": alert_type,
            "threshold_percent": threshold_percent,
            "current_cost": round(current_cost, 2),
            "budget_limit": budget_limit,
            "usage_percent": round((current_cost / budget_limit) * 100, 1),
            "remaining": round(budget_limit - current_cost, 2),
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        
        if project_id:
            alert_data["project_id"] = project_id
        
        # Store alert in Firestore
        try:
            self.db.collection('budget_alerts').add(alert_data)
        except Exception as e:
            self.logger.error("Failed to store budget alert", error=str(e))
        
        # Log critical alert
        self.logger.warning(
            f"Budget alert: {alert_type} budget at {threshold_percent}%",
            **alert_data
        )
    
    def get_project_cost(self, project_id: str) -> float:
        """
        Get total cost for a project
        
        Args:
            project_id: Content project ID
            
        Returns:
            Total cost in USD
        """
        try:
            usage_query = self.db.collection('api_usage')\
                .where('project_id', '==', project_id)
            
            total_cost = sum(doc.get('cost', 0) for doc in usage_query.stream())
            
            return total_cost
            
        except Exception as e:
            self.logger.error(
                "Failed to get project cost",
                error=str(e),
                project_id=project_id
            )
            return 0.0
    
    def get_daily_cost(self) -> float:
        """
        Get total cost for today
        
        Returns:
            Total daily cost in USD
        """
        try:
            # Get today's start timestamp
            today_start = time.time() - (time.time() % 86400)
            
            usage_query = self.db.collection('api_usage')\
                .where('timestamp', '>=', today_start)
            
            total_cost = sum(doc.get('cost', 0) for doc in usage_query.stream())
            
            return total_cost
            
        except Exception as e:
            self.logger.error("Failed to get daily cost", error=str(e))
            return 0.0
    
    def get_quota_status(self, service: str) -> Dict[str, Any]:
        """
        Get current quota status for a service
        
        Args:
            service: Service name
            
        Returns:
            Quota status information
        """
        with self.lock:
            bucket_key = f"{service}:request"
            bucket = self.token_buckets[bucket_key]
            
            # Refill before checking
            self._refill_bucket(bucket)
            
            quota_info = self.service_quotas.get(service, {})
            
            return {
                'service': service,
                'tokens_available': bucket['tokens'],
                'max_tokens': bucket['max_tokens'],
                'refill_rate': bucket['refill_rate'],
                'quota_limits': quota_info,
                'utilization_percent': (1 - bucket['tokens'] / bucket['max_tokens']) * 100
            }
    
    def wait_for_quota(
        self,
        service: str,
        tokens: int = 1,
        timeout: float = 60.0
    ) -> bool:
        """
        Wait for quota to become available
        
        Args:
            service: Service name
            tokens: Number of tokens needed
            timeout: Maximum wait time in seconds
            
        Returns:
            True if quota became available, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.check_quota(service, 'request', tokens)
            
            if result['allowed']:
                return True
            
            # Wait before retrying
            wait_time = min(result.get('wait_time_seconds', 1), timeout - (time.time() - start_time))
            
            if wait_time > 0:
                self.logger.info(
                    f"Waiting for quota to refill",
                    service=service,
                    wait_time=wait_time
                )
                time.sleep(wait_time)
        
        self.logger.error(
            "Timeout waiting for quota",
            service=service,
            timeout=timeout
        )
        
        return False
    
    def get_usage_report(self, hours: int = 24) -> Dict[str, Any]:
        """
        Generate usage report for the specified time period
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Usage report
        """
        try:
            cutoff_time = time.time() - (hours * 3600)
            
            usage_query = self.db.collection('api_usage')\
                .where('timestamp', '>=', cutoff_time)\
                .stream()
            
            # Aggregate by service
            service_usage = defaultdict(lambda: {
                'requests': 0,
                'tokens': 0,
                'cost': 0.0
            })
            
            total_cost = 0.0
            total_requests = 0
            
            for doc in usage_query:
                data = doc.to_dict()
                service = data.get('service', 'unknown')
                
                service_usage[service]['requests'] += 1
                service_usage[service]['tokens'] += data.get('tokens_used', 0)
                service_usage[service]['cost'] += data.get('cost', 0.0)
                
                total_cost += data.get('cost', 0.0)
                total_requests += 1
            
            return {
                'period_hours': hours,
                'total_requests': total_requests,
                'total_cost': round(total_cost, 4),
                'by_service': dict(service_usage),
                'budget_status': {
                    'daily_budget': self.budget_limits['daily'],
                    'daily_used': round(self.get_daily_cost(), 4),
                    'daily_remaining': round(
                        self.budget_limits['daily'] - self.get_daily_cost(), 4
                    )
                }
            }
            
        except Exception as e:
            self.logger.error("Failed to generate usage report", error=str(e))
            return {}
    
    def configure_service_quota(
        self,
        service: str,
        max_tokens: int,
        refill_rate: float
    ):
        """
        Configure quota settings for a service
        
        Args:
            service: Service name
            max_tokens: Maximum tokens in bucket
            refill_rate: Tokens per second refill rate
        """
        with self.lock:
            bucket_key = f"{service}:request"
            bucket = self.token_buckets[bucket_key]
            
            bucket['max_tokens'] = max_tokens
            bucket['refill_rate'] = refill_rate
            bucket['tokens'] = max_tokens  # Reset to full
            
            self.logger.info(
                f"Configured quota for {service}",
                service=service,
                max_tokens=max_tokens,
                refill_rate=refill_rate
            )
    
    def estimate_operation_cost(
        self,
        service: str,
        operation: str,
        **kwargs
    ) -> float:
        """
        Estimate cost for an operation before executing
        
        Args:
            service: Service name
            operation: Operation type
            **kwargs: Operation-specific parameters
        
        Returns:
            Estimated cost in USD
        """
        # Cost estimation based on service and operation
        cost_estimates = {
            "vertex-ai": {
                "gemini-pro": {
                    "input_cost_per_1k": 0.000125,
                    "output_cost_per_1k": 0.000375
                },
                "gemini-flash": {
                    "input_cost_per_1k": 0.000075,
                    "output_cost_per_1k": 0.00015
                },
                "embeddings": {
                    "cost_per_1k": 0.00025
                }
            }
        }
        
        # Example estimation logic
        if service == "vertex-ai" and operation == "generate":
            model_type = kwargs.get("model", "gemini-flash")
            input_tokens = kwargs.get("input_tokens", 1000)
            output_tokens = kwargs.get("output_tokens", 500)
            
            if "gemini-pro" in model_type:
                costs = cost_estimates["vertex-ai"]["gemini-pro"]
                estimated_cost = (
                    (input_tokens / 1000) * costs["input_cost_per_1k"] +
                    (output_tokens / 1000) * costs["output_cost_per_1k"]
                )
                return round(estimated_cost, 6)
            
            elif "gemini-flash" in model_type or "flash" in model_type:
                costs = cost_estimates["vertex-ai"]["gemini-flash"]
                estimated_cost = (
                    (input_tokens / 1000) * costs["input_cost_per_1k"] +
                    (output_tokens / 1000) * costs["output_cost_per_1k"]
                )
                return round(estimated_cost, 6)
        
        # Default estimate
        return 0.01
    
    def check_budget_available(
        self,
        estimated_cost: float,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if budget is available for estimated cost
        
        Args:
            estimated_cost: Estimated cost of operation
            project_id: Optional project ID to check
        
        Returns:
            Dict with availability and budget info
        """
        daily_cost = self.get_daily_cost()
        daily_budget = self.budget_limits['daily']
        daily_remaining = daily_budget - daily_cost
        
        result = {
            "daily_available": daily_remaining >= estimated_cost,
            "daily_budget": daily_budget,
            "daily_used": round(daily_cost, 4),
            "daily_remaining": round(daily_remaining, 4),
            "estimated_cost": round(estimated_cost, 4)
        }
        
        # Check project budget if provided
        if project_id:
            project_cost = self.get_project_cost(project_id)
            project_budget = self.budget_limits['project']
            project_remaining = project_budget - project_cost
            
            result.update({
                "project_available": project_remaining >= estimated_cost,
                "project_budget": project_budget,
                "project_used": round(project_cost, 4),
                "project_remaining": round(project_remaining, 4)
            })
            
            result["available"] = result["daily_available"] and result["project_available"]
        else:
            result["available"] = result["daily_available"]
        
        return result
    
    def reset_daily_alerts(self):
        """Reset daily budget alerts (call this at start of new day)"""
        self.alert_tracker['daily'].clear()
        self.logger.info("Daily budget alerts reset")
    
    def get_budget_status(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive budget status
        
        Args:
            project_id: Optional project ID
        
        Returns:
            Budget status information
        """
        daily_cost = self.get_daily_cost()
        daily_budget = self.budget_limits['daily']
        
        status = {
            "daily": {
                "budget": daily_budget,
                "used": round(daily_cost, 4),
                "remaining": round(daily_budget - daily_cost, 4),
                "usage_percent": round((daily_cost / daily_budget) * 100, 1) if daily_budget > 0 else 0,
                "enforce_limit": self.enforce_budget
            }
        }
        
        if project_id:
            project_cost = self.get_project_cost(project_id)
            project_budget = self.budget_limits['project']
            
            status["project"] = {
                "project_id": project_id,
                "budget": project_budget,
                "used": round(project_cost, 4),
                "remaining": round(project_budget - project_cost, 4),
                "usage_percent": round((project_cost / project_budget) * 100, 1) if project_budget > 0 else 0,
                "enforce_limit": self.enforce_budget
            }
        
        return status
