"""Tests for cache module."""

import time

import pytest

from jw_org_mcp.cache import Cache


class TestCache:
    """Tests for Cache."""

    def test_set_and_get(self) -> None:
        """Test basic set and get operations."""
        cache = Cache(ttl_seconds=60)

        cache.set("key1", value="value1")
        result = cache.get("key1")

        assert result == "value1"

    def test_get_nonexistent_key(self) -> None:
        """Test getting nonexistent key returns None."""
        cache = Cache(ttl_seconds=60)

        result = cache.get("nonexistent")

        assert result is None

    def test_expiration(self) -> None:
        """Test that entries expire after TTL."""
        cache = Cache(ttl_seconds=1)

        cache.set("key1", value="value1")

        # Should exist immediately
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.get("key1") is None

    def test_custom_ttl(self) -> None:
        """Test custom TTL for specific entry."""
        cache = Cache(ttl_seconds=10)

        cache.set("key1", value="value1", ttl_seconds=1)

        # Should exist immediately
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.get("key1") is None

    def test_cache_clear(self) -> None:
        """Test clearing cache."""
        cache = Cache(ttl_seconds=60)

        cache.set("key1", value="value1")
        cache.set("key2", value="value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cleanup_expired(self) -> None:
        """Test cleanup of expired entries."""
        cache = Cache(ttl_seconds=1)

        cache.set("key1", value="value1")
        cache.set("key2", value="value2", ttl_seconds=10)

        # Wait for first entry to expire
        time.sleep(1.1)

        cache.cleanup_expired()

        # key1 should be gone, key2 should remain
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_stats(self) -> None:
        """Test cache statistics."""
        cache = Cache(ttl_seconds=60)

        # Set some values
        cache.set("key1", value="value1")
        cache.set("key2", value="value2")

        # Get some values (hits)
        cache.get("key1")
        cache.get("key1")

        # Get nonexistent values (misses)
        cache.get("key3")

        stats = cache.get_stats()

        assert stats["entries"] == 2
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == pytest.approx(66.67, rel=0.1)

    def test_multiple_key_components(self) -> None:
        """Test cache keys with multiple components."""
        cache = Cache(ttl_seconds=60)

        cache.set("search", "peace", "all", value="results1")
        cache.set("search", "peace", "videos", value="results2")

        assert cache.get("search", "peace", "all") == "results1"
        assert cache.get("search", "peace", "videos") == "results2"
        assert cache.get("search", "peace", "audio") is None
