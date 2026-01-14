# Redis Cache Setup Guide

## Overview
This application now uses Redis for caching instead of in-memory dictionaries. Redis provides:
- ✅ Data persistence across server restarts
- ✅ Scalability across multiple server instances
- ✅ Automatic data expiration (TTL)
- ✅ Thread-safe operations
- ✅ Production-ready caching

## Installation

### Windows
1. **Download Redis for Windows:**
   - Visit: https://github.com/microsoftarchive/redis/releases
   - Download: `Redis-x64-3.0.504.msi`
   - Install and run Redis service

2. **Or use Docker:**
   ```bash
   docker run -d -p 6379:6379 --name redis redis:latest
   ```

### Linux/Mac
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Mac
brew install redis
brew services start redis
```

## Configuration

Add to your `.env` file:
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

## Python Dependencies

Install Redis package:
```bash
pip install redis
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Cache Keys Structure

The application uses the following cache key patterns:
- `forms:{token}` - Form statistics (TTL: 30 minutes)
- `landing_pages:{token}` - Landing page data (TTL: 30 minutes)
- `prospects:{token}` - Prospect health data (TTL: 30 minutes)
- `engagement:{token}` - Engagement program data (TTL: 30 minutes)

## Testing Redis Connection

```python
from cache import redis_client

# Test connection
try:
    redis_client.ping()
    print("✓ Redis connected successfully")
except:
    print("✗ Redis connection failed")
```

## Fallback Behavior

If Redis is not available:
- The application will continue to work
- Cache operations will fail silently
- Fresh data will be fetched on every request
- A warning message will be logged

## Cache Management

Clear all cache:
```python
from cache import clear_all_cache
clear_all_cache()
```

Delete specific cache:
```python
from cache import delete_cached_data
delete_cached_data("forms:abc123")
```

## Production Recommendations

1. **Use Redis Cluster** for high availability
2. **Set up Redis persistence** (RDB + AOF)
3. **Monitor Redis memory** usage
4. **Use Redis password** authentication
5. **Configure maxmemory-policy** to `allkeys-lru`

## Troubleshooting

**Redis not connecting?**
- Check if Redis service is running: `redis-cli ping`
- Verify port 6379 is not blocked
- Check Redis logs for errors

**Cache not working?**
- Application will work without Redis
- Check console for Redis connection messages
- Verify environment variables are set correctly
