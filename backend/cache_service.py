"""
Cache Service Module
=====================
LRU-based embedding cache to avoid recomputing embeddings
for identical images within a session.
Uses SHA-256 hash of image bytes as cache key.
"""

import hashlib
import logging
import time
from collections import OrderedDict
from threading import Lock

import numpy as np

logger = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────────
MAX_CACHE_SIZE = 128  # Maximum number of cached embeddings


class EmbeddingCache:
    """
    Thread-safe LRU cache for face embeddings.

    Keyed by SHA-256 hash of image bytes. Stores embedding vectors
    and metadata (timestamp, hit count) for observability.
    """

    def __init__(self, max_size: int = MAX_CACHE_SIZE):
        self._cache: OrderedDict[str, dict] = OrderedDict()
        self._max_size = max_size
        self._lock = Lock()
        self._hits = 0
        self._misses = 0

    def _compute_key(self, image_bytes: bytes) -> str:
        """Compute SHA-256 hash of image bytes as cache key."""
        return hashlib.sha256(image_bytes).hexdigest()

    def get(self, image_bytes: bytes) -> np.ndarray | None:
        """
        Look up cached embedding for the given image bytes.

        Args:
            image_bytes: Raw image data.

        Returns:
            Cached embedding vector, or None if not found.
        """
        key = self._compute_key(image_bytes)

        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                self._cache[key]["hit_count"] += 1
                self._hits += 1
                logger.debug(f"Cache HIT for {key[:12]}... (hits: {self._hits})")
                return self._cache[key]["embedding"].copy()

            self._misses += 1
            logger.debug(f"Cache MISS for {key[:12]}... (misses: {self._misses})")
            return None

    def put(self, image_bytes: bytes, embedding: np.ndarray) -> None:
        """
        Store an embedding in the cache.

        Args:
            image_bytes: Raw image data (used to compute key).
            embedding: The embedding vector to cache.
        """
        key = self._compute_key(image_bytes)

        with self._lock:
            if key in self._cache:
                # Update existing entry
                self._cache.move_to_end(key)
                self._cache[key]["embedding"] = embedding.copy()
                return

            # Evict oldest if at capacity
            if len(self._cache) >= self._max_size:
                evicted_key, _ = self._cache.popitem(last=False)
                logger.debug(f"Cache EVICT: {evicted_key[:12]}...")

            self._cache[key] = {
                "embedding": embedding.copy(),
                "timestamp": time.time(),
                "hit_count": 0,
            }

    def clear(self) -> None:
        """Clear all cached embeddings."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
        logger.info("Embedding cache cleared")

    @property
    def stats(self) -> dict:
        """Return cache statistics for observability."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate_pct": round(hit_rate, 1),
            }


# ── Singleton ────────────────────────────────────────────────────────
_embedding_cache: EmbeddingCache | None = None


def get_embedding_cache() -> EmbeddingCache:
    """Get or create the global embedding cache singleton."""
    global _embedding_cache
    if _embedding_cache is None:
        _embedding_cache = EmbeddingCache()
        logger.info(f"✅ Embedding cache initialized (max_size={MAX_CACHE_SIZE})")
    return _embedding_cache
