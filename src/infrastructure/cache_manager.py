"""
Cache Manager

Implements a 3-tier caching strategy:
- L1: In-memory application cache (agent prompts, templates)
- L2: Redis/Memorystore (AI responses, research results)
- L3: CDN-ready cache preparation (published content, media)
"""

import json
import hashlib
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from functools import lru_cache
import threading

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from ..monitoring.logger import StructuredLogger


class CacheManager:
    """Multi-tier cache manager for content generation system"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Cache Manager
        
        Args:
            config: Cache configuration including Redis connection details
        """
        self.config = config
        self.logger = StructuredLogger("CacheManager")
        
        # L1: In-memory cache (thread-safe)
        self.l1_cache: Dict[str, Dict[str, Any]] = {}
        self.l1_lock = threading.RLock()
        self.l1_ttl = config.get("l1_ttl_seconds", 3600)  # 1 hour default
        
        # L2: Redis/Memorystore
        self.redis_client = None
        self.l2_enabled = False
        
        if REDIS_AVAILABLE and config.get("redis_enabled", False):
            self._initialize_redis(config)
        else:
            self.logger.warning("Redis not available or not enabled. L2 cache disabled.")
        
        # Cache statistics
        self.stats = {
            "l1_hits": 0,
            "l1_misses": 0,
            "l2_hits": 0,
            "l2_misses": 0,
            "l1_evictions": 0,
            "l2_errors": 0
        }
        
        self.logger.info("Cache Manager initialized",
            l1_enabled=True,
            l2_enabled=self.l2_enabled,
            l1_ttl=self.l1_ttl
        )
    
    def _initialize_redis(self, config: Dict[str, Any]):
        """Initialize Redis connection"""
        try:
            redis_config = config.get("redis", {})
            
            self.redis_client = redis.Redis(
                host=redis_config.get("host", "localhost"),
                port=redis_config.get("port", 6379),
                db=redis_config.get("db", 0),
                password=redis_config.get("password"),
                socket_connect_timeout=redis_config.get("timeout", 5),
                decode_responses=True
            )
            
            # Test connection
            self.redis_client.ping()
            self.l2_enabled = True
            
            self.logger.info("Redis connection established",
                host=redis_config.get("host"),
                port=redis_config.get("port")
            )
            
        except Exception as e:
            self.logger.error("Failed to initialize Redis", error=str(e))
            self.redis_client = None
            self.l2_enabled = False
    
    def get(self, key: str, cache_level: str = "auto") -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            cache_level: "l1", "l2", or "auto" (checks both)
        
        Returns:
            Cached value or None if not found
        """
        # Try L1 cache first
        if cache_level in ("l1", "auto"):
            l1_value = self._get_l1(key)
            if l1_value is not None:
                self.stats["l1_hits"] += 1
                return l1_value
            else:
                self.stats["l1_misses"] += 1
        
        # Try L2 cache if L1 missed
        if cache_level in ("l2", "auto") and self.l2_enabled:
            l2_value = self._get_l2(key)
            if l2_value is not None:
                self.stats["l2_hits"] += 1
                # Promote to L1
                self._set_l1(key, l2_value, self.l1_ttl)
                return l2_value
            else:
                self.stats["l2_misses"] += 1
        
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        cache_level: str = "auto"
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None = use defaults)
            cache_level: "l1", "l2", or "auto" (sets in both)
        
        Returns:
            True if successful
        """
        success = True
        
        # Set in L1
        if cache_level in ("l1", "auto"):
            l1_ttl = ttl if ttl is not None else self.l1_ttl
            success = self._set_l1(key, value, l1_ttl) and success
        
        # Set in L2
        if cache_level in ("l2", "auto") and self.l2_enabled:
            l2_ttl = ttl if ttl is not None else self.config.get("l2_ttl_seconds", 86400)
            success = self._set_l2(key, value, l2_ttl) and success
        
        return success
    
    def delete(self, key: str, cache_level: str = "auto") -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key
            cache_level: "l1", "l2", or "auto" (deletes from both)
        
        Returns:
            True if successful
        """
        success = True
        
        if cache_level in ("l1", "auto"):
            success = self._delete_l1(key) and success
        
        if cache_level in ("l2", "auto") and self.l2_enabled:
            success = self._delete_l2(key) and success
        
        return success
    
    def clear(self, cache_level: str = "auto"):
        """Clear cache(s)"""
        if cache_level in ("l1", "auto"):
            self._clear_l1()
        
        if cache_level in ("l2", "auto") and self.l2_enabled:
            self._clear_l2()
    
    # L1 Cache Methods (In-Memory)
    
    def _get_l1(self, key: str) -> Optional[Any]:
        """Get from L1 cache"""
        with self.l1_lock:
            if key in self.l1_cache:
                entry = self.l1_cache[key]
                
                # Check expiration
                if datetime.utcnow() < entry["expires_at"]:
                    return entry["value"]
                else:
                    # Expired - remove
                    del self.l1_cache[key]
                    self.stats["l1_evictions"] += 1
        
        return None
    
    def _set_l1(self, key: str, value: Any, ttl: int) -> bool:
        """Set in L1 cache"""
        try:
            with self.l1_lock:
                self.l1_cache[key] = {
                    "value": value,
                    "expires_at": datetime.utcnow() + timedelta(seconds=ttl),
                    "created_at": datetime.utcnow()
                }
            return True
        except Exception as e:
            self.logger.error("L1 cache set failed", key=key, error=str(e))
            return False
    
    def _delete_l1(self, key: str) -> bool:
        """Delete from L1 cache"""
        try:
            with self.l1_lock:
                if key in self.l1_cache:
                    del self.l1_cache[key]
            return True
        except Exception as e:
            self.logger.error("L1 cache delete failed", key=key, error=str(e))
            return False
    
    def _clear_l1(self):
        """Clear L1 cache"""
        with self.l1_lock:
            cleared_count = len(self.l1_cache)
            self.l1_cache.clear()
        
        self.logger.info("L1 cache cleared", entries_cleared=cleared_count)
    
    # L2 Cache Methods (Redis)
    
    def _get_l2(self, key: str) -> Optional[Any]:
        """Get from L2 cache (Redis)"""
        if not self.l2_enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
            
        except Exception as e:
            self.logger.error("L2 cache get failed", key=key, error=str(e))
            self.stats["l2_errors"] += 1
            return None
    
    def _set_l2(self, key: str, value: Any, ttl: int) -> bool:
        """Set in L2 cache (Redis)"""
        if not self.l2_enabled:
            return False
        
        try:
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
            return True
            
        except Exception as e:
            self.logger.error("L2 cache set failed", key=key, error=str(e))
            self.stats["l2_errors"] += 1
            return False
    
    def _delete_l2(self, key: str) -> bool:
        """Delete from L2 cache (Redis)"""
        if not self.l2_enabled:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
            
        except Exception as e:
            self.logger.error("L2 cache delete failed", key=key, error=str(e))
            self.stats["l2_errors"] += 1
            return False
    
    def _clear_l2(self):
        """Clear L2 cache (Redis) - use with caution!"""
        if not self.l2_enabled:
            return
        
        try:
            self.redis_client.flushdb()
            self.logger.info("L2 cache cleared")
            
        except Exception as e:
            self.logger.error("L2 cache clear failed", error=str(e))
            self.stats["l2_errors"] += 1
    
    # Specialized Cache Methods
    
    def cache_ai_response(
        self,
        prompt: str,
        response: str,
        model: str,
        ttl: int = 86400  # 24 hours
    ) -> bool:
        """
        Cache AI model response
        
        Args:
            prompt: The prompt sent to the AI
            response: The AI's response
            model: Model name used
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        # Generate cache key from prompt and model
        cache_key = self._generate_cache_key("ai_response", prompt, model)
        
        cache_value = {
            "prompt": prompt,
            "response": response,
            "model": model,
            "cached_at": datetime.utcnow().isoformat()
        }
        
        return self.set(cache_key, cache_value, ttl=ttl, cache_level="l2")
    
    def get_cached_ai_response(self, prompt: str, model: str) -> Optional[str]:
        """
        Get cached AI response
        
        Args:
            prompt: The prompt
            model: Model name
        
        Returns:
            Cached response or None
        """
        cache_key = self._generate_cache_key("ai_response", prompt, model)
        cached = self.get(cache_key, cache_level="auto")
        
        if cached:
            self.logger.info("AI response cache hit", {
                "model": model,
                "prompt_length": len(prompt)
            })
            return cached["response"]
        
        return None
    
    def cache_research_results(
        self,
        topic: str,
        results: Dict[str, Any],
        ttl: int = 604800  # 7 days
    ) -> bool:
        """
        Cache research results
        
        Args:
            topic: Research topic
            results: Research results
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        cache_key = self._generate_cache_key("research", topic)
        
        cache_value = {
            "topic": topic,
            "results": results,
            "cached_at": datetime.utcnow().isoformat()
        }
        
        return self.set(cache_key, cache_value, ttl=ttl, cache_level="l2")
    
    def get_cached_research(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get cached research results"""
        cache_key = self._generate_cache_key("research", topic)
        cached = self.get(cache_key, cache_level="auto")
        
        if cached:
            self.logger.info("Research cache hit", topic=topic)
            return cached["results"]
        
        return None
    
    def cache_template(self, template_name: str, template_content: str) -> bool:
        """
        Cache template (prompts, etc.) in L1
        
        Args:
            template_name: Name of the template
            template_content: Template content
        
        Returns:
            True if cached successfully
        """
        cache_key = f"template:{template_name}"
        return self.set(cache_key, template_content, cache_level="l1")
    
    def get_cached_template(self, template_name: str) -> Optional[str]:
        """Get cached template"""
        cache_key = f"template:{template_name}"
        return self.get(cache_key, cache_level="l1")
    
    def _generate_cache_key(self, prefix: str, *args) -> str:
        """Generate consistent cache key from arguments"""
        # Create a hash of the arguments
        combined = ":".join(str(arg) for arg in args)
        hash_value = hashlib.sha256(combined.encode()).hexdigest()[:16]
        
        return f"{prefix}:{hash_value}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        l1_size = len(self.l1_cache)
        
        # Calculate hit rates
        total_l1_requests = self.stats["l1_hits"] + self.stats["l1_misses"]
        total_l2_requests = self.stats["l2_hits"] + self.stats["l2_misses"]
        
        l1_hit_rate = (self.stats["l1_hits"] / total_l1_requests * 100) if total_l1_requests > 0 else 0
        l2_hit_rate = (self.stats["l2_hits"] / total_l2_requests * 100) if total_l2_requests > 0 else 0
        
        return {
            "l1": {
                "enabled": True,
                "size": l1_size,
                "hits": self.stats["l1_hits"],
                "misses": self.stats["l1_misses"],
                "hit_rate": f"{l1_hit_rate:.1f}%",
                "evictions": self.stats["l1_evictions"]
            },
            "l2": {
                "enabled": self.l2_enabled,
                "hits": self.stats["l2_hits"],
                "misses": self.stats["l2_misses"],
                "hit_rate": f"{l2_hit_rate:.1f}%",
                "errors": self.stats["l2_errors"]
            }
        }
    
    def cleanup_expired_l1(self):
        """Clean up expired L1 cache entries"""
        with self.l1_lock:
            now = datetime.utcnow()
            expired_keys = [
                key for key, entry in self.l1_cache.items()
                if now >= entry["expires_at"]
            ]
            
            for key in expired_keys:
                del self.l1_cache[key]
                self.stats["l1_evictions"] += 1
        
        if expired_keys:
            self.logger.info("Cleaned up expired L1 entries", {
                "count": len(expired_keys)
            })


class CacheDecorator:
    """Decorator for caching function results"""
    
    def __init__(self, cache_manager: CacheManager, ttl: int = 3600, cache_level: str = "auto"):
        """
        Initialize cache decorator
        
        Args:
            cache_manager: CacheManager instance
            ttl: Time to live in seconds
            cache_level: Cache level to use
        """
        self.cache_manager = cache_manager
        self.ttl = ttl
        self.cache_level = cache_level
    
    def __call__(self, func):
        """Wrap function with caching"""
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = self._generate_key(func.__name__, args, kwargs)
            
            # Try to get from cache
            cached = self.cache_manager.get(cache_key, cache_level=self.cache_level)
            if cached is not None:
                return cached
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            self.cache_manager.set(cache_key, result, ttl=self.ttl, cache_level=self.cache_level)
            
            return result
        
        return wrapper
    
    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key from function name and arguments"""
        # Combine all arguments
        all_args = str(args) + str(sorted(kwargs.items()))
        hash_value = hashlib.sha256(all_args.encode()).hexdigest()[:16]
        
        return f"func:{func_name}:{hash_value}"
