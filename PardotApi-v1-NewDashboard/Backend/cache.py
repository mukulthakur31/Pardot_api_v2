import redis
import json
import os
from typing import Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# Initialize Redis client
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        username="default",
        password=REDIS_PASSWORD,

    )
    # Test connection
    redis_client.ping()
    print("[OK] Redis connected successfully")
except Exception as e:
    print(f"[ERROR] Redis connection failed: {e}")
    redis_client = None

def get_cached_data(key: str) -> Optional[Any]:
    """Get data from Redis cache"""
    if not redis_client:
        return None
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        print(f"Error getting cached data for key {key}: {e}")
        return None

def set_cached_data(key: str, value: Any, ttl: int = 3600) -> bool:
    """Set data in Redis cache with TTL (default 1 hour)"""
    if not redis_client:
        return False
    try:
        redis_client.setex(key, ttl, json.dumps(value))
        return True
    except Exception as e:
        print(f"Error setting cached data for key {key}: {e}")
        return False

def delete_cached_data(key: str) -> bool:
    """Delete data from Redis cache"""
    if not redis_client:
        return False
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Error deleting cached data for key {key}: {e}")
        return False

def clear_all_cache() -> bool:
    """Clear all cache data"""
    if not redis_client:
        return False
    try:
        redis_client.flushdb()
        return True
    except Exception as e:
        print(f"Error clearing cache: {e}")
        return False
