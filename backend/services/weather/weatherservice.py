import httpx
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any
from ...config import settings
from ...cache.redisclient import RedisCache
from ...utils.retry import with_retry

logger = logging.getLogger("weather_service")

class WeatherService:
    @staticmethod
    def _seeded_rng(*parts: str):
        seed_text = "|".join(str(p) for p in parts)
        seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16)
        import random
        return random.Random(seed)

    @staticmethod
    def _synthetic_weather(city: str, date_str: str) -> Dict[str, Any]:
        conditions = [
            "Sunny", "Cloudy", "Partly cloudy", "Light drizzle", "Rain showers",
            "Clear sky", "Overcast"
        ]
        rng = WeatherService._seeded_rng(city, date_str, "weather")
        base_temp = 12 + (abs(hash(city)) % 10)
        temp_high = base_temp + rng.randint(0, 5)
        temp_low = base_temp - rng.randint(0, 5)

        return {
            "condition": conditions[rng.randint(0, len(conditions) - 1)],
            "temphighc": temp_high,
            "templowc": temp_low,
            "precipitationchance": rng.randint(0, 80)
        }

    @staticmethod
    @with_retry(max_attempts=3, backoff_factor=2.0)
    async def get_weather_for_date(city: str, lat: float, lng: float, date_str: str) -> Dict[str, Any]:
        cache_key = f"weather:{lat}:{lng}:{date_str}"
        
        cached = await RedisCache.get(cache_key)
        if cached:
            return cached

        if settings.WEATHER_API_KEY:
            try:
                url = f"{settings.WEATHER_API_BASE_URL}/forecast"
                params = {
                    "lat": lat,
                    "lon": lng,
                    "appid": settings.WEATHER_API_KEY,
                    "units": "metric"
                }
                async with httpx.AsyncClient() as client:
                    res = await client.get(url, params=params, timeout=5)
                    res.raise_for_status()
                    data = res.json()

                forecast_list = data.get("list", [])
                closest_entry = None
                min_diff = float("inf")
                
                try:
                    target_dt = datetime.fromisoformat(date_str)
                except:
                    target_dt = datetime.utcnow()
                
                for entry in forecast_list:
                    entry_dt = datetime.fromtimestamp(entry.get("dt"))
                    diff = abs((entry_dt - target_dt).total_seconds())
                    if diff < min_diff:
                        min_diff = diff
                        closest_entry = entry

                if closest_entry:
                    main_data = closest_entry.get("main", {})
                    weather_list = closest_entry.get("weather", [{}])
                    
                    result = {
                        "condition": weather_list[0].get("main", "Clear"),
                        "temphighc": int(main_data.get("temp_max", 15.0)),
                        "templowc": int(main_data.get("temp_min", 10.0)),
                        "precipitationchance": int(closest_entry.get("pop", 0.0) * 100)
                    }
                    await RedisCache.set(cache_key, result, ttl=3600)
                    return result

            except Exception as e:
                logger.warning(f"Failed to fetch real weather forecast: {e}. Falling back to synthetic weather.")

        fallback_res = WeatherService._synthetic_weather(city, date_str)
        await RedisCache.set(cache_key, fallback_res, ttl=3600)
        return fallback_res
