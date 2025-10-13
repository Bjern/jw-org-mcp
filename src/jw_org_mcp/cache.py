"""Caching layer for JW.Org MCP Tool."""

import hashlib
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class CacheEntry:
    """A cache entry with expiration."""

    def __init__(self, data: Any, ttl_seconds: int) -> None:
        """Initialize cache entry.

        Args:
            data: Data to cache
            ttl_seconds: Time to live in seconds
        """
        self.data = data
        self.created_at = datetime.now(UTC)
        self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)

    def is_expired(self) -> bool:
        """Check if cache entry is expired.

        Returns:
            True if expired
        """
        return datetime.now(UTC) >= self.expires_at


class Cache:
    """Simple in-memory cache with TTL."""

    def __init__(self, ttl_seconds: int = 900) -> None:
        """Initialize cache.

        Args:
            ttl_seconds: Default time to live in seconds
        """
        self._cache: dict[str, CacheEntry] = {}
        self._ttl_seconds = ttl_seconds
        self._hits = 0
        self._misses = 0

    def _make_key(self, *args: Any) -> str:
        """Create cache key from arguments.

        Args:
            *args: Arguments to use for key

        Returns:
            Cache key string
        """
        key_str = "|".join(str(arg) for arg in args)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def get(self, *args: Any) -> Any | None:
        """Get value from cache.

        Args:
            *args: Cache key components

        Returns:
            Cached value or None if not found or expired
        """
        key = self._make_key(*args)
        entry = self._cache.get(key)

        if entry is None:
            self._misses += 1
            logger.debug(f"Cache miss: {key}")
            return None

        if entry.is_expired():
            # Remove expired entry
            del self._cache[key]
            self._misses += 1
            logger.debug(f"Cache expired: {key}")
            return None

        self._hits += 1
        logger.debug(f"Cache hit: {key}")
        return entry.data

    def set(self, *args: Any, value: Any, ttl_seconds: int | None = None) -> None:
        """Set value in cache.

        Args:
            *args: Cache key components (last arg is the value)
            value: Value to cache
            ttl_seconds: Optional custom TTL
        """
        key = self._make_key(*args)
        ttl = ttl_seconds if ttl_seconds is not None else self._ttl_seconds

        self._cache[key] = CacheEntry(value, ttl)
        logger.debug(f"Cache set: {key} (TTL: {ttl}s)")

    def clear(self) -> None:
        """Clear all cache entries."""
        count = len(self._cache)
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info(f"Cache cleared: {count} entries removed")

    def cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        expired_keys = [key for key, entry in self._cache.items() if entry.is_expired()]

        for key in expired_keys:
            del self._cache[key]

        removed = len(expired_keys)
        if removed > 0:
            logger.info(f"Cache cleanup: {removed} expired entries removed")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "entries": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2),
        }
