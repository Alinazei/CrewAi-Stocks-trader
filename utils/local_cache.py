import json
import os
from datetime import datetime, timedelta

CACHE_FILE = "local_cache.json"
CACHE_EXPIRY_MINUTES = 15

def load_cache():
    """Load cache from file with error handling"""
    if not os.path.exists(CACHE_FILE):
        return {}
    
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # If cache file is corrupted, return empty cache
        return {}

def save_cache(cache):
    """Save cache to file with error handling"""
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except IOError:
        # If we can't write to cache, silently continue
        pass

def get_cached_result(key):
    """Get cached result if not expired"""
    try:
        cache = load_cache()
        entry = cache.get(key)
        if entry:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            if datetime.now() - timestamp < timedelta(minutes=CACHE_EXPIRY_MINUTES):
                return entry["result"]
    except (ValueError, KeyError):
        # If timestamp parsing fails, treat as expired
        pass
    return None

def set_cached_result(key, result):
    """Set cached result with timestamp"""
    cache = load_cache()
    cache[key] = {
        "timestamp": datetime.now().isoformat(),
        "result": result
    }
    save_cache(cache)

def clear_cache():
    """Clear all cached results"""
    try:
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
    except IOError:
        pass 