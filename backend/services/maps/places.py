import httpx
import logging
from typing import List, Dict, Any
from ...config import settings
from ...cache.redisclient import RedisCache
from ...utils.retry import with_retry

logger = logging.getLogger("places_service")

INTEREST_CATEGORY_MAP = {
    "food": ["catering.restaurant"],
    "art": ["entertainment.museum", "entertainment.culture"],
    "history": ["tourism.attraction", "tourism.sights"],
    "adventure": ["tourism.attraction"],
    "shopping": ["commercial.shopping_mall"],
    "beaches": ["natural.beach"],
    "hiking": ["leisure.park"],
    "culture": ["entertainment.culture"],
    "nature": ["leisure.park"],
    "nightlife": ["catering.bar", "catering.pub"],
    "relaxation": ["leisure.spa", "leisure.park"]
}

class PlacesService:
    @staticmethod
    @with_retry(max_attempts=3, backoff_factor=2.0)
    async def search_places(lat: float, lng: float, interests: List[str], radius: int = 5000) -> List[Dict[str, Any]]:
        if not settings.GEOAPIFY_API_KEY:
            logger.warning("GEOAPIFY_API_KEY is not set.")
            return []

        categories = []
        for interest in interests:
            cats = INTEREST_CATEGORY_MAP.get(interest.lower())
            if cats:
                categories.extend(cats)
        if not categories:
            categories = ["tourism.attraction"]

        categories_str = ",".join(sorted(list(set(categories))))
        cache_key = f"places:{lat}:{lng}:{categories_str}:{radius}"
        cached = await RedisCache.get(cache_key)
        if cached:
            return cached

        url = "https://api.geoapify.com/v2/places"
        params = {
            "categories": categories_str,
            "filter": f"circle:{lng},{lat},{radius}",
            "limit": 20,
            "apiKey": settings.GEOAPIFY_API_KEY
        }

        async with httpx.AsyncClient() as client:
            res = await client.get(url, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()

        features = data.get("features", [])
        places = []
        for f in features:
            props = f["properties"]
            geom = f["geometry"]["coordinates"]
            places.append({
                "name": props.get("name") or props.get("formatted", "Unknown Place"),
                "coordinates": {
                    "lat": geom[1],
                    "lng": geom[0]
                },
                "category": props.get("categories", [None])[0],
                "openinghours": props.get("opening_hours")
            })

        await RedisCache.set(cache_key, places, ttl=86400) # 24 hours
        return places
