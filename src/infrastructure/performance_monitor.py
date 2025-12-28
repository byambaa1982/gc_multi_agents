"""
Performance Monitoring and Tuning Module

Tracks system performance metrics, identifies bottlenecks, and provides
recommendations for optimization.
"""

import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
from enum import Enum
import statistics
import json

try:
    from google.cloud import monitoring_v3
    CLOUD_MONITORING_AVAILABLE = True
except ImportError:
    CLOUD_MONITORING_AVAILABLE = False


class MetricType(Enum):
    """Types of performance metrics"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    AGENT_PERFORMANCE = "agent_performance"
    API_CALLS = "api_calls"
    CACHE_HIT_RATE = "cache_hit_rate"


@dataclass
class PerformanceMetric:
    """Single performance metric data point"""
    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceAlert:
    """Performance alert when thresholds are breached"""
    severity: str  # "INFO", "WARNING", "CRITICAL"
    metric_type: MetricType
    message: str
    current_value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    recommendations: List[str] = field(default_factory=list)


class PerformanceMonitor:
    """
    Comprehensive performance monitoring and tuning system
    
    Features:
    - Real-time metric collection
    - Threshold-based alerting
    - Performance trend analysis
    - Automatic optimization recommendations
    - Integration with Google Cloud Monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Performance Monitor
        
        Args:
            config: Configuration dictionary with thresholds and settings
        """
        self.config = config or {}
        self.metrics_buffer: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=1000)
            for metric_type in MetricType
        }
        self.alerts: List[PerformanceAlert] = []
        self.alert_lock = threading.RLock()
        
        # Performance thresholds
        self.thresholds = {
            MetricType.LATENCY: self.config.get("latency_threshold_ms", 200),
            MetricType.ERROR_RATE: self.config.get("error_rate_threshold", 0.05),
            MetricType.CPU_USAGE: self.config.get("cpu_usage_threshold", 80),
            MetricType.MEMORY_USAGE: self.config.get("memory_usage_threshold", 85),
            MetricType.CACHE_HIT_RATE: self.config.get("cache_hit_rate_min", 0.6),
        }
        
        # Cloud Monitoring client
        self.cloud_monitoring_client = None
        self.project_id = self.config.get("project_id")
        
        if CLOUD_MONITORING_AVAILABLE and self.project_id:
            self._initialize_cloud_monitoring()
        
        # Background monitoring thread
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Performance baselines
        self.baselines: Dict[MetricType, float] = {}
        
        print("✅ Performance Monitor initialized")
    
    def _initialize_cloud_monitoring(self):
        """Initialize Google Cloud Monitoring client"""
        try:
            self.cloud_monitoring_client = monitoring_v3.MetricServiceClient()
            print("✅ Cloud Monitoring integration enabled")
        except Exception as e:
            print(f"⚠️ Cloud Monitoring initialization failed: {e}")
    
    def record_metric(self, 
                     metric_type: MetricType, 
                     value: float,
                     labels: Optional[Dict[str, str]] = None,
                     metadata: Optional[Dict[str, Any]] = None):
        """
        Record a performance metric
        
        Args:
            metric_type: Type of metric
            value: Metric value
            labels: Additional labels for the metric
            metadata: Additional metadata
        """
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            labels=labels or {},
            metadata=metadata or {}
        )
        
        self.metrics_buffer[metric_type].append(metric)
        
        # Check thresholds and generate alerts
        self._check_thresholds(metric)
        
        # Send to Cloud Monitoring if available
        if self.cloud_monitoring_client:
            self._send_to_cloud_monitoring(metric)
    
    def _check_thresholds(self, metric: PerformanceMetric):
        """Check if metric exceeds thresholds and generate alerts"""
        threshold = self.thresholds.get(metric.metric_type)
        if threshold is None:
            return
        
        # Different comparison logic based on metric type
        alert_triggered = False
        severity = "INFO"
        
        if metric.metric_type in [MetricType.LATENCY, MetricType.ERROR_RATE, 
                                  MetricType.CPU_USAGE, MetricType.MEMORY_USAGE]:
            if metric.value > threshold:
                alert_triggered = True
                if metric.value > threshold * 1.5:
                    severity = "CRITICAL"
                else:
                    severity = "WARNING"
        
        elif metric.metric_type == MetricType.CACHE_HIT_RATE:
            if metric.value < threshold:
                alert_triggered = True
                severity = "WARNING"
        
        if alert_triggered:
            alert = PerformanceAlert(
                severity=severity,
                metric_type=metric.metric_type,
                message=f"{metric.metric_type.value} threshold breached",
                current_value=metric.value,
                threshold=threshold,
                recommendations=self._get_recommendations(metric.metric_type, metric.value)
            )
            
            with self.alert_lock:
                self.alerts.append(alert)
                
            print(f"🚨 [{severity}] {alert.message}: {metric.value:.2f} (threshold: {threshold})")
    
    def _get_recommendations(self, metric_type: MetricType, value: float) -> List[str]:
        """Get optimization recommendations based on metric"""
        recommendations = []
        
        if metric_type == MetricType.LATENCY:
            recommendations = [
                "Enable caching for frequently accessed data",
                "Optimize database queries with indexes",
                "Consider implementing request batching",
                "Review and optimize agent prompt complexity",
                "Enable Cloud CDN for static content"
            ]
        
        elif metric_type == MetricType.CPU_USAGE:
            recommendations = [
                "Scale horizontally by adding more instances",
                "Optimize compute-intensive operations",
                "Implement job queuing for background tasks",
                "Consider using preemptible VMs for batch jobs"
            ]
        
        elif metric_type == MetricType.MEMORY_USAGE:
            recommendations = [
                "Implement pagination for large result sets",
                "Optimize in-memory caching strategy",
                "Review and fix memory leaks",
                "Increase instance memory allocation"
            ]
        
        elif metric_type == MetricType.ERROR_RATE:
            recommendations = [
                "Review error logs for common failures",
                "Implement circuit breakers for external APIs",
                "Add retry logic with exponential backoff",
                "Improve input validation"
            ]
        
        elif metric_type == MetricType.CACHE_HIT_RATE:
            recommendations = [
                "Review cache TTL settings",
                "Increase cache size allocation",
                "Implement predictive pre-caching",
                "Analyze cache access patterns"
            ]
        
        return recommendations
    
    def _send_to_cloud_monitoring(self, metric: PerformanceMetric):
        """Send metric to Google Cloud Monitoring"""
        if not self.cloud_monitoring_client or not self.project_id:
            return
        
        try:
            # Create time series
            series = monitoring_v3.TimeSeries()
            series.metric.type = f"custom.googleapis.com/{metric.metric_type.value}"
            
            # Add labels
            for key, value in metric.labels.items():
                series.metric.labels[key] = value
            
            # Add resource
            series.resource.type = "global"
            series.resource.labels["project_id"] = self.project_id
            
            # Add data point
            point = monitoring_v3.Point()
            point.value.double_value = metric.value
            point.interval.end_time.FromDatetime(metric.timestamp)
            series.points = [point]
            
            # Write time series
            project_name = f"projects/{self.project_id}"
            self.cloud_monitoring_client.create_time_series(
                name=project_name,
                time_series=[series]
            )
        except Exception as e:
            print(f"⚠️ Failed to send metric to Cloud Monitoring: {e}")
    
    def get_metric_statistics(self, 
                             metric_type: MetricType,
                             time_window_minutes: int = 5) -> Dict[str, float]:
        """
        Get statistical analysis of a metric
        
        Args:
            metric_type: Type of metric to analyze
            time_window_minutes: Time window for analysis
            
        Returns:
            Dictionary with statistical measures
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        
        recent_metrics = [
            m.value for m in self.metrics_buffer[metric_type]
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        return {
            "count": len(recent_metrics),
            "mean": statistics.mean(recent_metrics),
            "median": statistics.median(recent_metrics),
            "min": min(recent_metrics),
            "max": max(recent_metrics),
            "stdev": statistics.stdev(recent_metrics) if len(recent_metrics) > 1 else 0,
            "p95": self._percentile(recent_metrics, 95),
            "p99": self._percentile(recent_metrics, 99)
        }
    
    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def get_active_alerts(self, 
                         severity: Optional[str] = None,
                         hours: int = 1) -> List[PerformanceAlert]:
        """
        Get active performance alerts
        
        Args:
            severity: Filter by severity level
            hours: Look back period in hours
            
        Returns:
            List of active alerts
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self.alert_lock:
            alerts = [
                alert for alert in self.alerts
                if alert.timestamp >= cutoff_time
            ]
            
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
        
        return alerts
    
    def start_system_monitoring(self, interval_seconds: int = 60):
        """
        Start background system resource monitoring
        
        Args:
            interval_seconds: Monitoring interval
        """
        if self.monitoring_active:
            print("⚠️ System monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitor_system_resources,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitoring_thread.start()
        print(f"✅ System monitoring started (interval: {interval_seconds}s)")
    
    def stop_system_monitoring(self):
        """Stop background system monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("✅ System monitoring stopped")
    
    def _monitor_system_resources(self, interval_seconds: int):
        """Background thread for monitoring system resources"""
        while self.monitoring_active:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.record_metric(MetricType.CPU_USAGE, cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.record_metric(MetricType.MEMORY_USAGE, memory.percent)
                
                # Could add disk I/O, network I/O, etc.
                
                time.sleep(interval_seconds)
            except Exception as e:
                print(f"⚠️ System monitoring error: {e}")
                time.sleep(interval_seconds)
    
    def measure_execution_time(self, operation_name: str) -> Callable:
        """
        Decorator to measure execution time of operations
        
        Args:
            operation_name: Name of the operation being measured
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time_ms = (time.time() - start_time) * 1000
                    
                    self.record_metric(
                        MetricType.LATENCY,
                        execution_time_ms,
                        labels={"operation": operation_name}
                    )
                    
                    return result
                except Exception as e:
                    execution_time_ms = (time.time() - start_time) * 1000
                    self.record_metric(
                        MetricType.LATENCY,
                        execution_time_ms,
                        labels={"operation": operation_name, "status": "error"}
                    )
                    raise
            return wrapper
        return decorator
    
    def get_performance_report(self, 
                              time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Generate comprehensive performance report
        
        Args:
            time_window_hours: Time window for report
            
        Returns:
            Performance report dictionary
        """
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "time_window_hours": time_window_hours,
            "metrics": {},
            "alerts": {
                "critical": len([a for a in self.get_active_alerts(hours=time_window_hours) if a.severity == "CRITICAL"]),
                "warning": len([a for a in self.get_active_alerts(hours=time_window_hours) if a.severity == "WARNING"]),
                "info": len([a for a in self.get_active_alerts(hours=time_window_hours) if a.severity == "INFO"])
            },
            "recommendations": []
        }
        
        # Add statistics for each metric type
        for metric_type in MetricType:
            stats = self.get_metric_statistics(metric_type, time_window_hours * 60)
            if stats:
                report["metrics"][metric_type.value] = stats
        
        # Add top recommendations
        recent_alerts = self.get_active_alerts(hours=time_window_hours)
        all_recommendations = []
        for alert in recent_alerts:
            all_recommendations.extend(alert.recommendations)
        
        # Get unique recommendations
        report["recommendations"] = list(set(all_recommendations))
        
        return report
    
    def export_metrics(self, filepath: str, format: str = "json"):
        """
        Export metrics to file
        
        Args:
            filepath: Output file path
            format: Export format (json, csv)
        """
        if format == "json":
            data = {
                metric_type.value: [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "value": m.value,
                        "labels": m.labels,
                        "metadata": m.metadata
                    }
                    for m in self.metrics_buffer[metric_type]
                ]
                for metric_type in MetricType
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Metrics exported to {filepath}")
        else:
            raise ValueError(f"Unsupported format: {format}")


# Context manager for measuring performance
class PerformanceContext:
    """Context manager for measuring operation performance"""
    
    def __init__(self, monitor: PerformanceMonitor, operation_name: str):
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time_ms = (time.time() - self.start_time) * 1000
        
        labels = {"operation": self.operation_name}
        if exc_type:
            labels["status"] = "error"
            self.monitor.record_metric(MetricType.ERROR_RATE, 1.0, labels=labels)
        else:
            labels["status"] = "success"
        
        self.monitor.record_metric(MetricType.LATENCY, execution_time_ms, labels=labels)
