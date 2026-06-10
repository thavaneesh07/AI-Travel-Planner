import httpx
import logging
import hashlib
from typing import List, Dict, Any

from ...config import settings
from ...cache.redisclient import RedisCache
from ...utils.retry import with_retry

logger = logging.getLogger("routing_service")

class RoutingService:
    @staticmethod
    @with_retry(max_attempts=3, backoff_factor=2.0)
    async def get_route(waypoints: List[Dict[str, float]], mode: str = "drive") -> Dict[str, Any]:
        if not settings.GEOAPIFY_API_KEY or len(waypoints) < 2:
            return {}

        wp_str = "|".join([f"{w['lat']},{w['lng']}" for w in waypoints])
        wp_hash = hashlib.md5(f"{wp_str}:{mode}".encode()).hexdigest()
        cache_key = f"route:{wp_hash}"

        cached = await RedisCache.get(cache_key)
        if cached:
            return cached

        url = "https://api.geoapify.com/v1/routing"
        params = {
            "waypoints": wp_str,
            "mode": mode,
            "apiKey": settings.GEOAPIFY_API_KEY
        }

        async with httpx.AsyncClient() as client:
            res = await client.get(url, params=params, timeout=15)
            res.raise_for_status()
            data = res.json()

        features = data.get("features", [])
        if features:
            props = features[0]["properties"]
            geom = features[0]["geometry"]["coordinates"]
            result = {
                "route_geometry": geom,
                "total_distance_m": props.get("distance", 0.0),
                "total_duration_s": props.get("time", 0.0)
            }
            await RedisCache.set(cache_key, result, ttl=3600) # 1 hour
            return result

        return {}
