import os
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://192.168.1.5:6379")
redis_client = redis.Redis.from_url(REDIS_URL)