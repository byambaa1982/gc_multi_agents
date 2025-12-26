"""
Structured logging with Google Cloud Logging integration
"""

import os
import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from google.cloud import logging as cloud_logging


class StructuredLogger:
    """Structured logger with Cloud Logging integration"""
    
    def __init__(self, name: str = __name__, use_cloud_logging: bool = True):
        """
        Initialize structured logger
        
        Args:
            name: Logger name
            use_cloud_logging: Whether to use Google Cloud Logging
        """
        self.name = name
        self.use_cloud_logging = use_cloud_logging
        
        # Set up local logging
        self.logger = logging.getLogger(name)
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.logger.setLevel(getattr(logging, log_level))
        
        # Console handler with JSON formatting
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(self._get_formatter())
            self.logger.addHandler(handler)
        
        # Cloud Logging client (if enabled)
        self.cloud_logger = None
        if self.use_cloud_logging:
            try:
                client = cloud_logging.Client()
                self.cloud_logger = client.logger(name)
            except Exception as e:
                self.logger.warning(f"Could not initialize Cloud Logging: {e}")
    
    def _get_formatter(self) -> logging.Formatter:
        """Get JSON formatter for local logging"""
        return JsonFormatter()
    
    def _log(
        self, 
        level: str, 
        message: str, 
        correlation_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Internal logging method
        
        Args:
            level: Log level (INFO, WARNING, ERROR, etc.)
            message: Log message
            correlation_id: Optional correlation ID for tracing
            **kwargs: Additional structured data
        """
        # Build structured log entry
        log_data = {
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            **kwargs
        }
        
        if correlation_id:
            log_data['correlation_id'] = correlation_id
        
        # Log to console
        log_method = getattr(self.logger, level.lower())
        log_method(json.dumps(log_data))
        
        # Log to Cloud Logging
        if self.cloud_logger:
            try:
                severity = level.upper()
                self.cloud_logger.log_struct(log_data, severity=severity)
            except Exception as e:
                self.logger.error(f"Failed to log to Cloud Logging: {e}")
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        self._log('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        self._log('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        self._log('ERROR', message, **kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        self._log('DEBUG', message, **kwargs)
    
    def agent_start(
        self, 
        agent_name: str, 
        project_id: str, 
        **kwargs
    ) -> None:
        """Log agent start"""
        self.info(
            f"Agent {agent_name} started",
            agent=agent_name,
            project_id=project_id,
            event='agent_start',
            **kwargs
        )
    
    def agent_complete(
        self, 
        agent_name: str, 
        project_id: str, 
        duration_seconds: float,
        **kwargs
    ) -> None:
        """Log agent completion"""
        self.info(
            f"Agent {agent_name} completed",
            agent=agent_name,
            project_id=project_id,
            duration_seconds=duration_seconds,
            event='agent_complete',
            **kwargs
        )
    
    def agent_error(
        self, 
        agent_name: str, 
        project_id: str, 
        error: Exception,
        **kwargs
    ) -> None:
        """Log agent error"""
        self.error(
            f"Agent {agent_name} failed: {str(error)}",
            agent=agent_name,
            project_id=project_id,
            error_type=type(error).__name__,
            error_message=str(error),
            event='agent_error',
            **kwargs
        )
    
    def cost_tracking(
        self, 
        project_id: str, 
        operation: str, 
        cost: float,
        **kwargs
    ) -> None:
        """Log cost tracking"""
        self.info(
            f"Cost tracking: {operation}",
            project_id=project_id,
            operation=operation,
            cost_usd=cost,
            event='cost_tracking',
            **kwargs
        )


class JsonFormatter(logging.Formatter):
    """JSON formatter for log records"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        # Check if message is already JSON
        try:
            # If message is already a JSON string, return it
            json.loads(record.getMessage())
            return record.getMessage()
        except (json.JSONDecodeError, ValueError):
            # Otherwise, create structured log
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
            }
            
            if record.exc_info:
                log_data['exception'] = self.formatException(record.exc_info)
            
            return json.dumps(log_data)
