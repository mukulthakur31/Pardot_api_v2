# Quick Start Guide - Redis Cache Migration

## 🚀 Installation Steps

### 1. Install Redis

**Windows (Easiest - Using Docker):**
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

**Windows (Native):**
- Download: https://github.com/microsoftarchive/redis/releases
- Install `Redis-x64-3.0.504.msi`
- Redis will start automatically as a service

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Mac:**
```bash
brew install redis
brew services start redis
```

### 2. Install Python Dependencies

```bash
cd Backend
pip install -r requirements.txt
```

### 3. Configure Environment

Add to your `.env` file (optional - defaults work for local):
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

### 4. Test Redis Connection

```bash
# Test if Redis is running
redis-cli ping
# Should return: PONG
```

### 5. Start Your Application

```bash
python app.py
```

You should see:
```
✓ Redis connected successfully
```

## ✅ What's Working Now?

- ✅ All form endpoints with Redis cache
- ✅ All landing page endpoints with Redis cache
- ✅ All prospect endpoints with Redis cache
- ✅ All engagement endpoints with Redis cache
- ✅ 30-minute cache expiration (TTL)
- ✅ Graceful fallback if Redis is down

## 🔍 Verify It's Working

### Test Cache Storage:
```bash
# After calling any endpoint, check Redis:
redis-cli
> KEYS *
# Should show: forms:xxx, landing_pages:xxx, etc.

> GET forms:xxx
# Should show cached JSON data

> TTL forms:xxx
# Should show remaining seconds (max 1800)
```

## 🛠️ Troubleshooting

**"Redis connection failed"**
- Check if Redis is running: `redis-cli ping`
- Verify port 6379 is not blocked
- Application will still work, just without caching

**"Module 'redis' not found"**
```bash
pip install redis
```

**Cache not expiring?**
- Default TTL is 1800 seconds (30 minutes)
- Check with: `redis-cli TTL forms:xxx`

## 📊 Cache Performance

Before (In-Memory Dict):
- ❌ Lost on server restart
- ❌ Not shared between workers
- ❌ Memory grows indefinitely

After (Redis):
- ✅ Persists across restarts
- ✅ Shared between all workers
- ✅ Auto-expires after 30 minutes

## 🎯 Next Steps

1. Monitor Redis memory usage in production
2. Consider Redis Cluster for high availability
3. Set up Redis persistence (RDB + AOF)
4. Configure Redis password for security

## 📚 Documentation

- Full setup: `REDIS_SETUP.md`
- Migration details: `MIGRATION_SUMMARY.md`
- Redis docs: https://redis.io/documentation

## 🆘 Need Help?

1. Check if Redis is running
2. Verify environment variables
3. Check application logs
4. Test Redis connection manually
