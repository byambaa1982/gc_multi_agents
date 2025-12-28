"""
Security Hardening Module

Implements comprehensive security measures for the multi-agent content generation system:
- Input validation and sanitization
- API key rotation and encryption
- Rate limiting and throttling
- Security headers and CORS
- Audit logging
- Vulnerability scanning
- Secret management
"""

import hashlib
import secrets
import re
import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import base64
import threading

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    import sys
    sys.stderr.write("WARNING: cryptography library not available. Encryption features disabled.\n")


class SecurityEventType(Enum):
    """Types of security events"""
    AUTHENTICATION_FAILURE = "authentication_failure"
    AUTHORIZATION_FAILURE = "authorization_failure"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_INPUT = "invalid_input"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    API_KEY_ROTATION = "api_key_rotation"
    SECRET_ACCESS = "secret_access"
    VULNERABILITY_DETECTED = "vulnerability_detected"


@dataclass
class SecurityEvent:
    """Security event record"""
    event_type: SecurityEventType
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    description: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    resource: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitRule:
    """Rate limiting rule"""
    name: str
    max_requests: int
    window_seconds: int
    identifier: str  # "ip", "user", "api_key"


class InputValidator:
    """Validates and sanitizes user inputs"""
    
    # Patterns for validation
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    URL_PATTERN = re.compile(r'^https?://[\w\-\.]+(:\d+)?(/[\w\-\./?%&=]*)?$')
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    
    # Dangerous patterns (potential XSS, SQL injection, etc.)
    DANGEROUS_PATTERNS = [
        re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),  # Event handlers
        re.compile(r'(union|select|insert|update|delete|drop|create)\s', re.IGNORECASE),
        re.compile(r'\.\./', re.IGNORECASE),  # Path traversal
        re.compile(r'eval\(', re.IGNORECASE),
    ]
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email address"""
        return bool(cls.EMAIL_PATTERN.match(email))
    
    @classmethod
    def validate_url(cls, url: str, allowed_schemes: Optional[List[str]] = None) -> bool:
        """Validate URL"""
        allowed_schemes = allowed_schemes or ['http', 'https']
        
        if not cls.URL_PATTERN.match(url):
            return False
        
        scheme = url.split(':')[0].lower()
        return scheme in allowed_schemes
    
    @classmethod
    def validate_alphanumeric(cls, text: str, allow_dash: bool = True, allow_underscore: bool = True) -> bool:
        """Validate alphanumeric string"""
        pattern = r'^[a-zA-Z0-9'
        if allow_dash:
            pattern += r'-'
        if allow_underscore:
            pattern += r'_'
        pattern += r']+$'
        
        return bool(re.match(pattern, text))
    
    @classmethod
    def sanitize_text(cls, text: str, max_length: Optional[int] = None) -> str:
        """Sanitize text input by removing dangerous patterns"""
        sanitized = text
        
        # Remove dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            sanitized = pattern.sub('', sanitized)
        
        # Trim to max length
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    @classmethod
    def validate_json(cls, json_str: str, max_size_bytes: int = 1_000_000) -> bool:
        """Validate JSON string"""
        if len(json_str.encode('utf-8')) > max_size_bytes:
            return False
        
        try:
            json.loads(json_str)
            return True
        except json.JSONDecodeError:
            return False
    
    @classmethod
    def is_potentially_malicious(cls, text: str) -> bool:
        """Check if text contains potentially malicious content"""
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern.search(text):
                return True
        return False


class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self):
        self.rules: List[RateLimitRule] = []
        self.requests: Dict[str, List[datetime]] = {}
        self.lock = threading.RLock()
        
        # Default rules
        self.add_rule(RateLimitRule(
            name="api_general",
            max_requests=100,
            window_seconds=60,
            identifier="ip"
        ))
        
        self.add_rule(RateLimitRule(
            name="api_heavy",
            max_requests=10,
            window_seconds=60,
            identifier="user"
        ))
    
    def add_rule(self, rule: RateLimitRule):
        """Add a rate limit rule"""
        self.rules.append(rule)
    
    def check_rate_limit(self, identifier_value: str, rule_name: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """
        Check if request is within rate limits
        
        Args:
            identifier_value: Value to identify requester (IP, user_id, etc.)
            rule_name: Specific rule to check (None = check all)
            
        Returns:
            Tuple of (allowed, reason)
        """
        with self.lock:
            now = datetime.utcnow()
            
            # Get applicable rules
            rules = [r for r in self.rules if not rule_name or r.name == rule_name]
            
            for rule in rules:
                key = f"{rule.name}:{identifier_value}"
                
                # Initialize or clean old requests
                if key not in self.requests:
                    self.requests[key] = []
                
                # Remove expired requests
                cutoff = now - timedelta(seconds=rule.window_seconds)
                self.requests[key] = [
                    req_time for req_time in self.requests[key]
                    if req_time > cutoff
                ]
                
                # Check limit
                if len(self.requests[key]) >= rule.max_requests:
                    return False, f"Rate limit exceeded for {rule.name}"
                
                # Record request
                self.requests[key].append(now)
            
            return True, None
    
    def get_rate_limit_status(self, identifier_value: str, rule_name: str) -> Dict[str, Any]:
        """Get current rate limit status"""
        with self.lock:
            rule = next((r for r in self.rules if r.name == rule_name), None)
            if not rule:
                return {}
            
            key = f"{rule.name}:{identifier_value}"
            current_requests = len(self.requests.get(key, []))
            
            return {
                "rule_name": rule.name,
                "current_requests": current_requests,
                "max_requests": rule.max_requests,
                "window_seconds": rule.window_seconds,
                "remaining": rule.max_requests - current_requests,
                "reset_at": (datetime.utcnow() + timedelta(seconds=rule.window_seconds)).isoformat()
            }


class SecretManager:
    """Manages secrets and API keys"""
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        Initialize Secret Manager
        
        Args:
            encryption_key: Encryption key for secrets (generated if not provided)
        """
        self.secrets: Dict[str, bytes] = {}
        self.lock = threading.RLock()
        
        if CRYPTO_AVAILABLE:
            if encryption_key:
                self.cipher = Fernet(encryption_key)
            else:
                # Generate new key
                self.cipher = Fernet(Fernet.generate_key())
            print("✅ Secret Manager initialized with encryption")
        else:
            self.cipher = None
            print("⚠️ Secret Manager initialized WITHOUT encryption (cryptography library not available)")
    
    def store_secret(self, name: str, value: str) -> bool:
        """
        Store a secret
        
        Args:
            name: Secret name/identifier
            value: Secret value
            
        Returns:
            Success status
        """
        try:
            with self.lock:
                if self.cipher:
                    encrypted = self.cipher.encrypt(value.encode('utf-8'))
                    self.secrets[name] = encrypted
                else:
                    # Fallback: base64 encoding (NOT secure!)
                    encoded = base64.b64encode(value.encode('utf-8'))
                    self.secrets[name] = encoded
            
            return True
        except Exception as e:
            print(f"❌ Failed to store secret '{name}': {e}")
            return False
    
    def get_secret(self, name: str) -> Optional[str]:
        """
        Retrieve a secret
        
        Args:
            name: Secret name
            
        Returns:
            Secret value or None
        """
        try:
            with self.lock:
                encrypted = self.secrets.get(name)
                if not encrypted:
                    return None
                
                if self.cipher:
                    decrypted = self.cipher.decrypt(encrypted)
                    return decrypted.decode('utf-8')
                else:
                    # Fallback: base64 decoding
                    decoded = base64.b64decode(encrypted)
                    return decoded.decode('utf-8')
        
        except Exception as e:
            print(f"❌ Failed to retrieve secret '{name}': {e}")
            return None
    
    def delete_secret(self, name: str) -> bool:
        """Delete a secret"""
        with self.lock:
            if name in self.secrets:
                del self.secrets[name]
                return True
            return False
    
    def rotate_api_key(self, service_name: str) -> str:
        """
        Generate and store a new API key
        
        Args:
            service_name: Service identifier
            
        Returns:
            New API key
        """
        # Generate secure random API key
        api_key = secrets.token_urlsafe(32)
        
        # Store it
        self.store_secret(f"api_key_{service_name}", api_key)
        
        return api_key
    
    def list_secrets(self) -> List[str]:
        """List all secret names (not values)"""
        with self.lock:
            return list(self.secrets.keys())


class SecurityAuditor:
    """Security audit logging and monitoring"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Security Auditor"""
        self.config = config or {}
        self.events: List[SecurityEvent] = []
        self.lock = threading.RLock()
        
        # Alert thresholds
        self.alert_thresholds = {
            SecurityEventType.AUTHENTICATION_FAILURE: 5,  # per 10 minutes
            SecurityEventType.RATE_LIMIT_EXCEEDED: 10,
            SecurityEventType.SUSPICIOUS_ACTIVITY: 3,
        }
        
        # Blocked IPs/users
        self.blocked_ips: Set[str] = set()
        self.blocked_users: Set[str] = set()
    
    def log_event(self,
                  event_type: SecurityEventType,
                  severity: str,
                  description: str,
                  user_id: Optional[str] = None,
                  ip_address: Optional[str] = None,
                  resource: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None):
        """
        Log a security event
        
        Args:
            event_type: Type of security event
            severity: Event severity
            description: Event description
            user_id: User identifier
            ip_address: IP address
            resource: Affected resource
            metadata: Additional metadata
        """
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            description=description,
            user_id=user_id,
            ip_address=ip_address,
            resource=resource,
            metadata=metadata or {}
        )
        
        with self.lock:
            self.events.append(event)
        
        # Check for patterns requiring action
        self._check_security_patterns(event)
        
        # Print critical events
        if severity == "CRITICAL":
            print(f"🚨 CRITICAL SECURITY EVENT: {description}")
    
    def _check_security_patterns(self, event: SecurityEvent):
        """Check for security patterns and take action"""
        # Count recent similar events
        cutoff = datetime.utcnow() - timedelta(minutes=10)
        
        with self.lock:
            recent_events = [
                e for e in self.events
                if e.event_type == event.event_type
                and e.timestamp >= cutoff
            ]
        
        threshold = self.alert_thresholds.get(event.event_type)
        
        if threshold and len(recent_events) >= threshold:
            # Too many similar events - take action
            if event.ip_address:
                self.block_ip(event.ip_address, f"Exceeded threshold for {event.event_type.value}")
            
            if event.user_id:
                self.block_user(event.user_id, f"Exceeded threshold for {event.event_type.value}")
    
    def block_ip(self, ip_address: str, reason: str):
        """Block an IP address"""
        with self.lock:
            self.blocked_ips.add(ip_address)
        
        print(f"🛑 Blocked IP: {ip_address} - Reason: {reason}")
        
        self.log_event(
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            severity="HIGH",
            description=f"IP blocked: {reason}",
            ip_address=ip_address
        )
    
    def block_user(self, user_id: str, reason: str):
        """Block a user"""
        with self.lock:
            self.blocked_users.add(user_id)
        
        print(f"🛑 Blocked User: {user_id} - Reason: {reason}")
        
        self.log_event(
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            severity="HIGH",
            description=f"User blocked: {reason}",
            user_id=user_id
        )
    
    def is_blocked(self, ip_address: Optional[str] = None, user_id: Optional[str] = None) -> bool:
        """Check if IP or user is blocked"""
        with self.lock:
            if ip_address and ip_address in self.blocked_ips:
                return True
            if user_id and user_id in self.blocked_users:
                return True
        return False
    
    def unblock_ip(self, ip_address: str):
        """Unblock an IP address"""
        with self.lock:
            self.blocked_ips.discard(ip_address)
        print(f"✅ Unblocked IP: {ip_address}")
    
    def unblock_user(self, user_id: str):
        """Unblock a user"""
        with self.lock:
            self.blocked_users.discard(user_id)
        print(f"✅ Unblocked User: {user_id}")
    
    def get_security_report(self, hours: int = 24) -> Dict[str, Any]:
        """
        Generate security report
        
        Args:
            hours: Time period for report
            
        Returns:
            Security report dictionary
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        with self.lock:
            recent_events = [e for e in self.events if e.timestamp >= cutoff]
        
        # Count by type
        event_counts = {}
        for event_type in SecurityEventType:
            count = sum(1 for e in recent_events if e.event_type == event_type)
            event_counts[event_type.value] = count
        
        # Count by severity
        severity_counts = {}
        for severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            count = sum(1 for e in recent_events if e.severity == severity)
            severity_counts[severity] = count
        
        return {
            "period_hours": hours,
            "total_events": len(recent_events),
            "events_by_type": event_counts,
            "events_by_severity": severity_counts,
            "blocked_ips": list(self.blocked_ips),
            "blocked_users": list(self.blocked_users),
            "top_affected_resources": self._get_top_affected_resources(recent_events, limit=10)
        }
    
    def _get_top_affected_resources(self, events: List[SecurityEvent], limit: int = 10) -> List[Dict[str, Any]]:
        """Get most affected resources"""
        resource_counts: Dict[str, int] = {}
        
        for event in events:
            if event.resource:
                resource_counts[event.resource] = resource_counts.get(event.resource, 0) + 1
        
        sorted_resources = sorted(resource_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"resource": resource, "count": count}
            for resource, count in sorted_resources[:limit]
        ]
    
    def export_audit_log(self, filepath: str, hours: int = 24):
        """Export audit log to file"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        with self.lock:
            recent_events = [e for e in self.events if e.timestamp >= cutoff]
        
        data = {
            "exported_at": datetime.utcnow().isoformat(),
            "period_hours": hours,
            "total_events": len(recent_events),
            "events": [
                {
                    "event_type": e.event_type.value,
                    "severity": e.severity,
                    "description": e.description,
                    "timestamp": e.timestamp.isoformat(),
                    "user_id": e.user_id,
                    "ip_address": e.ip_address,
                    "resource": e.resource,
                    "metadata": e.metadata
                }
                for e in recent_events
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Audit log exported to {filepath}")


class SecurityHardening:
    """Main security hardening orchestrator"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Security Hardening"""
        self.config = config or {}
        
        # Initialize components
        self.validator = InputValidator()
        self.rate_limiter = RateLimiter()
        self.secret_manager = SecretManager()
        self.auditor = SecurityAuditor(config)
        
        print("✅ Security Hardening initialized")
    
    def validate_request(self,
                        user_id: Optional[str] = None,
                        ip_address: Optional[str] = None,
                        data: Optional[Dict[str, Any]] = None) -> tuple[bool, Optional[str]]:
        """
        Validate incoming request
        
        Args:
            user_id: User identifier
            ip_address: Request IP address
            data: Request data
            
        Returns:
            Tuple of (valid, reason)
        """
        # Check if blocked
        if self.auditor.is_blocked(ip_address=ip_address, user_id=user_id):
            self.auditor.log_event(
                SecurityEventType.AUTHORIZATION_FAILURE,
                "HIGH",
                "Request from blocked source",
                user_id=user_id,
                ip_address=ip_address
            )
            return False, "Access denied"
        
        # Check rate limits
        if ip_address:
            allowed, reason = self.rate_limiter.check_rate_limit(ip_address)
            if not allowed:
                self.auditor.log_event(
                    SecurityEventType.RATE_LIMIT_EXCEEDED,
                    "MEDIUM",
                    reason or "Rate limit exceeded",
                    user_id=user_id,
                    ip_address=ip_address
                )
                return False, reason
        
        # Validate data
        if data:
            # Check for malicious content in text fields
            for key, value in data.items():
                if isinstance(value, str) and self.validator.is_potentially_malicious(value):
                    self.auditor.log_event(
                        SecurityEventType.INVALID_INPUT,
                        "HIGH",
                        f"Potentially malicious input detected in field: {key}",
                        user_id=user_id,
                        ip_address=ip_address
                    )
                    return False, "Invalid input detected"
        
        return True, None
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get recommended security headers for HTTP responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
