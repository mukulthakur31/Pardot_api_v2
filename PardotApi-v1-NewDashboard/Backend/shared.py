# Redis cache utility
from cache import get_cached_data, set_cached_data, delete_cached_data, clear_all_cache

# Cache key helpers
def get_cache_key(category: str, access_token: str) -> str:
    """Generate cache key for Redis"""
    return f"{category}:{access_token[:20]}"  # Use first 20 chars of token

# Backward compatibility - deprecated, will be removed
data_cache = {'forms': {}, 'landing_pages': {}, 'prospects': {}, 'engagement': {}}