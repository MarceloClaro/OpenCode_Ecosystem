"""
Testes do TTLCache (core/cache.py)

Cobre:
- get / set / delete
- TTL expiration
- LRU eviction (maxsize)
- has / contains
- clear
- Estatisticas: hits, misses, hit_ratio
- keys, is_empty, size
- Thread safety (lock)
- stats() dict
"""

import time

import pytest

from core.cache import TTLCache


class TestTTLCacheBasic:
    """Operacoes basicas de cache."""

    def test_set_and_get(self):
        cache = TTLCache()
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_default(self):
        cache = TTLCache()
        assert cache.get("missing", 42) == 42
        assert cache.get("missing") is None

    def test_set_overwrite(self):
        cache = TTLCache()
        cache.set("key", "old")
        cache.set("key", "new")
        assert cache.get("key") == "new"

    def test_delete_existing(self):
        cache = TTLCache()
        cache.set("key", "value")
        assert cache.delete("key") is True
        assert cache.get("key") is None

    def test_delete_missing(self):
        cache = TTLCache()
        assert cache.delete("nonexistent") is False

    def test_has_existing(self):
        cache = TTLCache()
        cache.set("key", "value")
        assert cache.has("key") is True
        assert "key" in cache

    def test_has_missing(self):
        cache = TTLCache()
        assert cache.has("missing") is False
        assert "missing" not in cache

    def test_clear(self):
        cache = TTLCache()
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.is_empty is True
        assert cache.size == 0
        assert cache.hits == 0
        assert cache.misses == 0

    def test_is_empty(self):
        cache = TTLCache()
        assert cache.is_empty is True
        cache.set("k", "v")
        assert cache.is_empty is False


class TestTTLCacheTTL:
    """Testa expiracao por TTL."""

    def test_expires_after_ttl(self):
        cache = TTLCache(default_ttl=0.05)
        cache.set("key", "value")
        assert cache.get("key") == "value"
        time.sleep(0.06)
        assert cache.get("key") is None

    def test_per_item_ttl(self):
        cache = TTLCache(default_ttl=60)
        cache.set("short", "quick", ttl=0.05)
        cache.set("long", "slow", ttl=60)
        time.sleep(0.06)
        assert cache.get("short") is None
        assert cache.get("long") == "slow"

    def test_no_expiration_when_ttl_none(self):
        cache = TTLCache(default_ttl=None)
        cache.set("eternal", "forever")
        assert cache.get("eternal") == "forever"

    def test_has_respects_expiry(self):
        cache = TTLCache(default_ttl=0.05)
        cache.set("key", "value")
        assert cache.has("key") is True
        time.sleep(0.06)
        assert cache.has("key") is False


class TestTTLCacheLRU:
    """Testa eviccao LRU no limite de tamanho."""

    def test_eviction_when_full(self):
        cache = TTLCache(maxsize=3, default_ttl=None)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.set("d", 4)  # deve expulsar 'a' (LRU)
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3
        assert cache.get("d") == 4
        assert cache.size == 3

    def test_access_moves_to_end(self):
        cache = TTLCache(maxsize=2, default_ttl=None)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.get("a")  # a vira MRU
        cache.set("c", 3)  # expulsa 'b'
        assert cache.get("a") == 1
        assert cache.get("b") is None
        assert cache.get("c") == 3

    def test_zero_maxsize_no_eviction(self):
        cache = TTLCache(maxsize=0, default_ttl=None)
        for i in range(100):
            cache.set(f"k{i}", i)
        assert cache.size == 100


class TestTTLCacheStats:
    """Testa coleta de estatisticas."""

    def test_hits_and_misses(self):
        cache = TTLCache()
        cache.set("key", "value")
        cache.get("key")   # hit
        cache.get("miss")  # miss
        assert cache.hits == 1
        assert cache.misses == 1

    def test_hit_ratio(self):
        cache = TTLCache()
        assert cache.hit_ratio == 0.0
        cache.set("k", "v")
        cache.get("k")   # hit
        cache.get("k")   # hit
        cache.get("x")   # miss
        assert cache.hit_ratio == pytest.approx(2 / 3)

    def test_stats_dict(self):
        cache = TTLCache(maxsize=100, default_ttl=30)
        cache.set("k", "v")
        cache.get("k")
        stats = cache.stats()
        assert stats["size"] == 1
        assert stats["maxsize"] == 100
        assert stats["default_ttl"] == 30
        assert stats["hits"] == 1
        assert stats["hit_ratio"] > 0


class TestTTLCacheThreadSafety:
    """Testa comportamento thread-safe."""

    def test_concurrent_access(self):
        import threading
        cache = TTLCache(maxsize=50, default_ttl=None)
        errors = []

        def worker(start):
            try:
                for i in range(20):
                    key = f"k{start + i}"
                    cache.set(key, i)
                    cache.get(key)
                    cache.has(key)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i * 20,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0

    def test_size_under_concurrency(self):
        import threading
        cache = TTLCache(maxsize=10, default_ttl=None)
        for i in range(10):
            cache.set(f"k{i}", i)

        def evict_reader():
            for _ in range(50):
                cache.get("k0")

        threads = [threading.Thread(target=evict_reader) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        # Nao deve crashar - e o que importa


class TestTTLCacheEdgeCases:
    """Casos extremos."""

    def test_negative_maxsize_raises(self):
        with pytest.raises(ValueError, match="maxsize"):
            TTLCache(maxsize=-1)

    def test_large_values(self):
        cache = TTLCache(maxsize=10)
        large = "x" * 100_000
        cache.set("big", large)
        assert cache.get("big") == large

    def test_none_value(self):
        cache = TTLCache()
        cache.set("null", None)
        assert cache.get("null") is None

    def test_dict_value(self):
        cache = TTLCache()
        data = {"a": 1, "b": [2, 3]}
        cache.set("dict", data)
        assert cache.get("dict") == data

    def test_keys_list(self):
        cache = TTLCache()
        cache.set("b", 2)
        cache.set("a", 1)
        cache.set("c", 3)
        assert sorted(cache.keys) == ["a", "b", "c"]

    def test_len(self):
        cache = TTLCache()
        assert len(cache) == 0
        cache.set("k", "v")
        assert len(cache) == 1

    def test_repr(self):
        cache = TTLCache(maxsize=100)
        cache.set("k", "v")
        r = repr(cache)
        assert "TTLCache" in r
        assert "size=" in r
