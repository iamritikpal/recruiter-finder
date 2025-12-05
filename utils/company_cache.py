import json
import time
import logging
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

class CompanyCache:
    """Simple in-memory cache with file backup for company data"""
    
    def __init__(self, cache_file: str = "company_cache.json", ttl_hours: int = 24):
        # Use absolute path for cache file
        import os
        self.cache_file = os.path.join(os.getcwd(), cache_file)
        self.ttl_seconds = ttl_hours * 3600
        self._cache = {}
        self._cache_timestamps = {}
        self._lock = threading.Lock()
        self._last_cache_hit = False  # Track if last get() was a hit
        
        logger.info(f"Initializing cache with file: {self.cache_file}")
        
        # Load existing cache from file
        self._load_from_file()
    
    def get(self, key: str) -> Optional[List[Dict]]:
        """Get cached data if it exists and is not expired"""
        with self._lock:
            logger.info(f"Cache get request for key: {key}")
            logger.info(f"Current cache keys: {list(self._cache.keys())}")
            
            if key not in self._cache:
                logger.info(f"Cache miss - key '{key}' not found in cache")
                self._last_cache_hit = False
                return None
            
            # Check if cache is expired
            if self._is_expired(key):
                logger.info(f"Cache expired for key: {key}")
                self._remove(key)
                self._last_cache_hit = False
                return None
            
            logger.info(f"Cache hit for key: {key} - returning {len(self._cache[key])} items")
            self._last_cache_hit = True
            return self._cache[key]
    
    def set(self, key: str, data: List[Dict]) -> None:
        """Set cache data with current timestamp"""
        with self._lock:
            self._cache[key] = data
            self._cache_timestamps[key] = time.time()
            logger.info(f"Cache set for key: {key} with {len(data)} items")
            
            # Save to file in background
            self._save_to_file_async()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self._cache_timestamps:
            return True
        
        age = time.time() - self._cache_timestamps[key]
        return age > self.ttl_seconds
    
    def _remove(self, key: str) -> None:
        """Remove cache entry"""
        self._cache.pop(key, None)
        self._cache_timestamps.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache"""
        with self._lock:
            self._cache.clear()
            self._cache_timestamps.clear()
            logger.info("Cache cleared")
            self._save_to_file_async()
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self._lock:
            total_entries = len(self._cache)
            expired_entries = sum(1 for key in self._cache.keys() if self._is_expired(key))
            
            return {
                "total_entries": total_entries,
                "expired_entries": expired_entries,
                "valid_entries": total_entries - expired_entries,
                "cache_file": self.cache_file,
                "ttl_hours": self.ttl_seconds / 3600
            }
    
    def was_last_get_hit(self) -> bool:
        """Check if the last get() call was a cache hit"""
        return self._last_cache_hit
    
    def _load_from_file(self) -> None:
        """Load cache from file if it exists"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    
                self._cache = file_data.get('cache', {})
                self._cache_timestamps = file_data.get('timestamps', {})
                
                # Clean expired entries
                expired_keys = [key for key in self._cache.keys() if self._is_expired(key)]
                for key in expired_keys:
                    self._remove(key)
                
                logger.info(f"Loaded cache from file: {len(self._cache)} entries")
            else:
                logger.info("No cache file found, starting with empty cache")
                
        except Exception as e:
            logger.error(f"Error loading cache from file: {e}")
            self._cache = {}
            self._cache_timestamps = {}
    
    def _save_to_file(self) -> None:
        """Save cache to file"""
        try:
            # Clean expired entries before saving
            expired_keys = [key for key in self._cache.keys() if self._is_expired(key)]
            for key in expired_keys:
                self._remove(key)
            
            file_data = {
                'cache': self._cache,
                'timestamps': self._cache_timestamps,
                'saved_at': time.time(),
                'version': '1.0'
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(file_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved cache to file: {len(self._cache)} entries")
            
        except Exception as e:
            logger.error(f"Error saving cache to file: {e}")
    
    def _save_to_file_async(self) -> None:
        """Save cache to file in background thread"""
        def save_worker():
            time.sleep(1)  # Small delay to batch multiple saves
            self._save_to_file()
        
        thread = threading.Thread(target=save_worker, daemon=True)
        thread.start()

# Global cache instance
company_cache = CompanyCache() 