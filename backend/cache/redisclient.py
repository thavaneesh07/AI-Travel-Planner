import os
import json
import logging
from typing import Any, Optional
import redis.asyncio as aioredis
from ..config import settings

logger = logging.getLogger("redis_cache")

class RedisCache:
    _redis = None

    @classmethod
    def get_client(cls):
        if cls._redis is None and settings.REDIS_URL:
            try:
                cls._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception as e:
                logger.warning(f"Could not connect to Redis: {e}")
        return cls._redis

    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        client = cls.get_client()
        if client:
            try:
                val = await client.get(key)
                if val:
                    return json.loads(val)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        return None

    @classmethod
    async def set(cls, key: str, value: Any, ttl: int = 3600) -> bool:
        client = cls.get_client()
        if client:
            try:
                await client.setex(key, ttl, json.dumps(value))
                return True
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
        return False

    @classmethod
    async def delete(cls, key: str) -> bool:
        client = cls.get_client()
        if client:
            try:
                await client.delete(key)
                return True
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")
        return False
