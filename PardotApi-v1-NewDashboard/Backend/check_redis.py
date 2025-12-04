#!/usr/bin/env python3
"""
Redis Health Check Script
Checks if Redis is available and working properly
"""

import redis
import os
from dotenv import load_dotenv

def check_redis():
    """Check Redis connection and health"""
    load_dotenv()
    
    # Redis configuration
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    print(f"🔍 Checking Redis connection...")
    print(f"   Host: {REDIS_HOST}")
    print(f"   Port: {REDIS_PORT}")
    print(f"   Password: {'Set' if REDIS_PASSWORD else 'None'}")
    
    try:
        # Create Redis client with timeout
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
            username="default",
            password=REDIS_PASSWORD,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
        
        # Test basic operations
        print("⏳ Testing Redis connection...")
        redis_client.ping()
        print("✅ Redis PING successful")
        
        # Test set/get operations
        test_key = "health_check_test"
        test_value = "test_value_123"
        
        print("⏳ Testing Redis SET operation...")
        redis_client.set(test_key, test_value, ex=10)  # Expire in 10 seconds
        print("✅ Redis SET successful")
        
        print("⏳ Testing Redis GET operation...")
        retrieved_value = redis_client.get(test_key)
        if retrieved_value == test_value:
            print("✅ Redis GET successful")
        else:
            print(f"❌ Redis GET failed: expected '{test_value}', got '{retrieved_value}'")
            return False
        
        # Clean up test key
        redis_client.delete(test_key)
        print("✅ Redis DELETE successful")
        
        # Get Redis info
        info = redis_client.info()
        print(f"📊 Redis Version: {info.get('redis_version', 'Unknown')}")
        print(f"📊 Connected Clients: {info.get('connected_clients', 'Unknown')}")
        print(f"📊 Used Memory: {info.get('used_memory_human', 'Unknown')}")
        
        print("🎉 Redis is healthy and ready!")
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Redis connection failed: {e}")
        print("💡 Make sure Redis server is running and accessible")
        return False
    except redis.TimeoutError as e:
        print(f"❌ Redis timeout: {e}")
        print("💡 Redis server may be overloaded or network issues")
        return False
    except Exception as e:
        print(f"❌ Redis error: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Pardot API - Redis Health Check")
    print("=" * 40)
    
    if check_redis():
        print("\n✅ Redis check passed - server can use caching")
        exit(0)
    else:
        print("\n⚠️  Redis check failed - server will run without caching")
        print("   This may impact performance but won't prevent startup")
        exit(1)

if __name__ == '__main__':
    main()