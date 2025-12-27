"""
Performance Monitoring - Real-time system and agent performance tracking

Monitors:
- Agent execution times and success rates
- API response times
- Resource utilization
- Error rates and exceptions
- Cost per operation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import time
import threading
from contextlib import contextmanager
from src.monitoring import StructuredLogger


class PerformanceMonitor:
    """Real-time performance monitoring and metrics collection"""
    
    def __init__(self, window_size: int = 1000):
        """
        Initialize performance monitor
        
        Args:
            window_size: Number of recent measurements to keep in memory
        """
        self.logger = StructuredLogger(name='performance_monitor')
        self.window_size = window_size
        
        # Metrics storage (in-memory for recent data)
        self.metrics = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'errors': 0,
            'recent_times': deque(maxlen=window_size)
        })
        
        # Thread-safe lock
        self.lock = threading.Lock()
        
        # Alerts configuration
        self.alert_thresholds = {
            'response_time_ms': 500,
            'error_rate': 0.05,
            'queue_size': 100
        }
        
        self.logger.info("Performance monitor initialized", window_size=window_size)
    
    @contextmanager
    def track_operation(
        self,
        operation_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager to track operation performance
        
        Usage:
            with monitor.track_operation('agent.research'):
                # Your code here
                result = do_work()
        
        Args:
            operation_name: Name of the operation to track
            metadata: Optional metadata about the operation
        """
        start_time = time.time()
        error_occurred = False
        error_details = None
        
        try:
            yield
        except Exception as e:
            error_occurred = True
            error_details = str(e)
            raise
        finally:
            execution_time = time.time() - start_time
            
            self.record_operation(
                operation_name=operation_name,
                execution_time=execution_time,
                success=not error_occurred,
                error=error_details,
                metadata=metadata
            )
    
    def record_operation(
        self,
        operation_name: str,
        execution_time: float,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record a completed operation
        
        Args:
            operation_name: Name of the operation
            execution_time: Execution time in seconds
            success: Whether operation succeeded
            error: Error message if failed
            metadata: Additional metadata
        """
        with self.lock:
            metric = self.metrics[operation_name]
            
            # Update counters
            metric['count'] += 1
            metric['total_time'] += execution_time
            metric['min_time'] = min(metric['min_time'], execution_time)
            metric['max_time'] = max(metric['max_time'], execution_time)
            
            if not success:
                metric['errors'] += 1
            
            # Add to recent times
            metric['recent_times'].append({
                'time': execution_time,
                'success': success,
                'timestamp': datetime.utcnow().isoformat(),
                'error': error,
                'metadata': metadata
            })
        
        # Log if performance is degraded
        if execution_time > 5.0:  # 5 seconds threshold
            self.logger.warning(
                f"Slow operation detected: {operation_name}",
                execution_time=execution_time,
                operation=operation_name
            )
        
        if not success:
            self.logger.error(
                f"Operation failed: {operation_name}",
                error=error,
                operation=operation_name
            )
    
    def get_metrics(
        self,
        operation_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get metrics for an operation or all operations
        
        Args:
            operation_name: Optional specific operation name
            
        Returns:
            Metrics dictionary
        """
        with self.lock:
            if operation_name:
                if operation_name not in self.metrics:
                    return {}
                
                return self._calculate_metrics(operation_name, self.metrics[operation_name])
            
            # Return all metrics
            all_metrics = {}
            for op_name, op_data in self.metrics.items():
                all_metrics[op_name] = self._calculate_metrics(op_name, op_data)
            
            return all_metrics
    
    def _calculate_metrics(
        self,
        operation_name: str,
        metric_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate derived metrics from raw data"""
        count = metric_data['count']
        
        if count == 0:
            return {
                'operation': operation_name,
                'count': 0,
                'average_time': 0,
                'min_time': 0,
                'max_time': 0,
                'error_rate': 0,
                'p95_time': 0,
                'p99_time': 0
            }
        
        avg_time = metric_data['total_time'] / count
        error_rate = metric_data['errors'] / count
        
        # Calculate percentiles
        recent_times_sorted = sorted([t['time'] for t in metric_data['recent_times']])
        p95_time = self._percentile(recent_times_sorted, 95)
        p99_time = self._percentile(recent_times_sorted, 99)
        
        return {
            'operation': operation_name,
            'count': count,
            'average_time': round(avg_time, 4),
            'min_time': round(metric_data['min_time'], 4),
            'max_time': round(metric_data['max_time'], 4),
            'error_rate': round(error_rate, 4),
            'errors': metric_data['errors'],
            'p95_time': round(p95_time, 4),
            'p99_time': round(p99_time, 4),
            'success_rate': round(1 - error_rate, 4)
        }
    
    def _percentile(self, sorted_values: List[float], percentile: int) -> float:
        """Calculate percentile from sorted values"""
        if not sorted_values:
            return 0.0
        
        index = int(len(sorted_values) * percentile / 100)
        index = min(index, len(sorted_values) - 1)
        return sorted_values[index]
    
    def get_agent_performance(self) -> Dict[str, Any]:
        """Get performance metrics for all agents"""
        agent_metrics = {}
        
        with self.lock:
            for op_name in self.metrics.keys():
                if op_name.startswith('agent.'):
                    agent_name = op_name.replace('agent.', '')
                    agent_metrics[agent_name] = self._calculate_metrics(
                        op_name,
                        self.metrics[op_name]
                    )
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'agents': agent_metrics,
            'summary': self._get_agent_summary(agent_metrics)
        }
    
    def _get_agent_summary(self, agent_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary of agent performance"""
        if not agent_metrics:
            return {}
        
        total_operations = sum(m['count'] for m in agent_metrics.values())
        total_errors = sum(m['errors'] for m in agent_metrics.values())
        avg_time = sum(m['average_time'] * m['count'] for m in agent_metrics.values()) / total_operations if total_operations > 0 else 0
        
        # Find slowest and fastest agents
        slowest = max(agent_metrics.items(), key=lambda x: x[1]['average_time'])
        fastest = min(agent_metrics.items(), key=lambda x: x[1]['average_time'])
        
        return {
            'total_operations': total_operations,
            'total_errors': total_errors,
            'overall_error_rate': round(total_errors / total_operations, 4) if total_operations > 0 else 0,
            'average_time': round(avg_time, 4),
            'slowest_agent': {'name': slowest[0], 'avg_time': slowest[1]['average_time']},
            'fastest_agent': {'name': fastest[0], 'avg_time': fastest[1]['average_time']}
        }
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get active performance alerts"""
        alerts = []
        
        with self.lock:
            for op_name, op_data in self.metrics.items():
                metrics = self._calculate_metrics(op_name, op_data)
                
                # Check for high error rate
                if metrics['error_rate'] > self.alert_thresholds['error_rate']:
                    alerts.append({
                        'severity': 'critical' if metrics['error_rate'] > 0.1 else 'warning',
                        'type': 'high_error_rate',
                        'operation': op_name,
                        'message': f"High error rate for {op_name}: {metrics['error_rate']:.2%}",
                        'value': metrics['error_rate'],
                        'threshold': self.alert_thresholds['error_rate']
                    })
                
                # Check for slow response times
                if metrics['p95_time'] > (self.alert_thresholds['response_time_ms'] / 1000):
                    alerts.append({
                        'severity': 'warning',
                        'type': 'slow_response',
                        'operation': op_name,
                        'message': f"Slow response time for {op_name}: {metrics['p95_time']:.2f}s (p95)",
                        'value': metrics['p95_time'],
                        'threshold': self.alert_thresholds['response_time_ms'] / 1000
                    })
        
        return alerts
    
    def reset_metrics(self, operation_name: Optional[str] = None):
        """
        Reset metrics
        
        Args:
            operation_name: Optional specific operation to reset
        """
        with self.lock:
            if operation_name:
                if operation_name in self.metrics:
                    del self.metrics[operation_name]
                    self.logger.info(f"Reset metrics for {operation_name}")
            else:
                self.metrics.clear()
                self.logger.info("Reset all metrics")
    
    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics for external storage/analysis"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': self.get_metrics(),
            'alerts': self.get_alerts(),
            'window_size': self.window_size
        }


class ResourceMonitor:
    """Monitor system resource usage"""
    
    def __init__(self):
        """Initialize resource monitor"""
        self.logger = StructuredLogger(name='resource_monitor')
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """
        Get current resource usage
        
        Returns:
            Resource usage metrics
        """
        try:
            # In production, use psutil or Google Cloud Monitoring API
            # import psutil
            # cpu_percent = psutil.cpu_percent(interval=1)
            # memory = psutil.virtual_memory()
            # disk = psutil.disk_usage('/')
            
            # Simulated data
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu': {
                    'percent': 45.2,
                    'count': 4
                },
                'memory': {
                    'total_gb': 16.0,
                    'used_gb': 8.3,
                    'percent': 51.9
                },
                'disk': {
                    'total_gb': 256.0,
                    'used_gb': 128.5,
                    'percent': 50.2
                },
                'network': {
                    'bytes_sent': 1024000,
                    'bytes_received': 2048000
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to get resource usage: {e}")
            return {}
    
    def check_resource_limits(self) -> List[Dict[str, Any]]:
        """Check if resource usage exceeds limits"""
        usage = self.get_resource_usage()
        alerts = []
        
        # CPU threshold: 80%
        if usage.get('cpu', {}).get('percent', 0) > 80:
            alerts.append({
                'severity': 'warning',
                'resource': 'cpu',
                'message': f"High CPU usage: {usage['cpu']['percent']}%",
                'value': usage['cpu']['percent'],
                'threshold': 80
            })
        
        # Memory threshold: 85%
        if usage.get('memory', {}).get('percent', 0) > 85:
            alerts.append({
                'severity': 'warning',
                'resource': 'memory',
                'message': f"High memory usage: {usage['memory']['percent']}%",
                'value': usage['memory']['percent'],
                'threshold': 85
            })
        
        # Disk threshold: 90%
        if usage.get('disk', {}).get('percent', 0) > 90:
            alerts.append({
                'severity': 'critical',
                'resource': 'disk',
                'message': f"High disk usage: {usage['disk']['percent']}%",
                'value': usage['disk']['percent'],
                'threshold': 90
            })
        
        return alerts


# Global instances
performance_monitor = PerformanceMonitor()
resource_monitor = ResourceMonitor()
