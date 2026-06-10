import httpx
import logging
from ...config import settings
from ...cache.redisclient import RedisCache
from ...utils.retry import with_retry

logger = logging.getLogger("geocoding_service")

class GeocodingService:
    @staticmethod
    @with_retry(max_attempts=3, backoff_factor=2.0)
    async def geocode(place_name: str) -> dict:
        if not settings.GEOAPIFY_API_KEY:
            logger.warning("GEOAPIFY_API_KEY is not set.")
            return {}

        cache_key = f"geocode:{place_name.lower().strip()}"
        cached = await RedisCache.get(cache_key)
        if cached:
            return cached

        url = "https://api.geoapify.com/v1/geocode/search"
        params = {
            "text": place_name,
            "apiKey": settings.GEOAPIFY_API_KEY,
            "limit": 1
        }

        async with httpx.AsyncClient() as client:
            res = await client.get(url, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()

        features = data.get("features", [])
        if features:
            prop = features[0]["properties"]
            geom = features[0]["geometry"]["coordinates"]
            result = {
                "lat": geom[1],
                "lng": geom[0],
                "formattedaddress": prop.get("formatted"),
                "country": prop.get("country")
            }
            await RedisCache.set(cache_key, result, ttl=604800) # 7 days
            return result

        return {}
