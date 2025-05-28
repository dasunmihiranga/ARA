from typing import Dict, Any, List, Optional, Union
import json
import os
import hashlib
from datetime import datetime, timedelta
import pickle
from pathlib import Path

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class CacheManager:
    """Manages caching of research results and analysis data."""

    def __init__(
        self,
        cache_dir: str = "data/cache",
        max_size: int = 1000,
        ttl: int = 86400  # 24 hours in seconds
    ):
        """
        Initialize the cache manager.

        Args:
            cache_dir: Directory to store cache files
            max_size: Maximum number of cache entries
            ttl: Time-to-live for cache entries in seconds
        """
        self.cache_dir = Path(cache_dir)
        self.max_size = max_size
        self.ttl = ttl
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Ensure cache directory exists."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating cache directory: {str(e)}")
            raise

    def _generate_key(self, data: Union[str, Dict[str, Any]]) -> str:
        """
        Generate a cache key from data.

        Args:
            data: Data to generate key from

        Returns:
            Cache key
        """
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        return hashlib.md5(data.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """
        Get cache file path for a key.

        Args:
            key: Cache key

        Returns:
            Path to cache file
        """
        return self.cache_dir / f"{key}.pkl"

    def _is_expired(self, timestamp: datetime) -> bool:
        """
        Check if a cache entry is expired.

        Args:
            timestamp: Entry timestamp

        Returns:
            True if expired, False otherwise
        """
        return datetime.utcnow() - timestamp > timedelta(seconds=self.ttl)

    def _cleanup_expired(self) -> None:
        """Remove expired cache entries."""
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                try:
                    with open(cache_file, "rb") as f:
                        data = pickle.load(f)
                        if self._is_expired(data["timestamp"]):
                            cache_file.unlink()
                except Exception:
                    cache_file.unlink()
        except Exception as e:
            logger.error(f"Error cleaning up expired cache: {str(e)}")

    def _enforce_size_limit(self) -> None:
        """Enforce maximum cache size."""
        try:
            cache_files = list(self.cache_dir.glob("*.pkl"))
            if len(cache_files) > self.max_size:
                # Sort by modification time
                cache_files.sort(key=lambda x: x.stat().st_mtime)
                # Remove oldest files
                for cache_file in cache_files[:len(cache_files) - self.max_size]:
                    cache_file.unlink()
        except Exception as e:
            logger.error(f"Error enforcing cache size limit: {str(e)}")

    def get(self, key: Union[str, Dict[str, Any]]) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key or data to generate key from

        Returns:
            Cached value or None if not found/expired
        """
        try:
            cache_key = key if isinstance(key, str) else self._generate_key(key)
            cache_path = self._get_cache_path(cache_key)

            if not cache_path.exists():
                return None

            with open(cache_path, "rb") as f:
                data = pickle.load(f)

            if self._is_expired(data["timestamp"]):
                cache_path.unlink()
                return None

            return data["value"]

        except Exception as e:
            logger.error(f"Error getting from cache: {str(e)}")
            return None

    def set(
        self,
        key: Union[str, Dict[str, Any]],
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Set a value in cache.

        Args:
            key: Cache key or data to generate key from
            value: Value to cache
            ttl: Optional time-to-live override
        """
        try:
            cache_key = key if isinstance(key, str) else self._generate_key(key)
            cache_path = self._get_cache_path(cache_key)

            data = {
                "value": value,
                "timestamp": datetime.utcnow(),
                "ttl": ttl or self.ttl
            }

            with open(cache_path, "wb") as f:
                pickle.dump(data, f)

            self._cleanup_expired()
            self._enforce_size_limit()

        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")

    def delete(self, key: Union[str, Dict[str, Any]]) -> bool:
        """
        Delete a value from cache.

        Args:
            key: Cache key or data to generate key from

        Returns:
            True if deleted, False if not found
        """
        try:
            cache_key = key if isinstance(key, str) else self._generate_key(key)
            cache_path = self._get_cache_path(cache_key)

            if cache_path.exists():
                cache_path.unlink()
                return True
            return False

        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
            return False

    def clear(self) -> None:
        """Clear all cache entries."""
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        try:
            cache_files = list(self.cache_dir.glob("*.pkl"))
            total_size = sum(f.stat().st_size for f in cache_files)
            expired_count = sum(
                1 for f in cache_files
                if self._is_expired(datetime.fromtimestamp(f.stat().st_mtime))
            )

            return {
                "total_entries": len(cache_files),
                "expired_entries": expired_count,
                "total_size_bytes": total_size,
                "max_size": self.max_size,
                "ttl_seconds": self.ttl
            }

        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {
                "total_entries": 0,
                "expired_entries": 0,
                "total_size_bytes": 0,
                "max_size": self.max_size,
                "ttl_seconds": self.ttl
            } 