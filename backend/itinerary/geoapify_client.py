import os
import json
import requests
import redis
from typing import Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential

# Redis Cache Setup
redis_url = os.getenv("REDIS_URL")
cache = redis.Redis.from_url(redis_url, decode_responses=True) if redis_url else None

def _get_cache(key: str):
    if cache:
        val = cache.get(key)
        if val: return json.loads(val)
    return None

def _set_cache(key: str, value: Any, ttl: int = 86400):
    if cache:
        cache.setex(key, ttl, json.dumps(value))

class GeoapifyClient:
    API_KEY = os.getenv("GEOAPIFY_API_KEY", "")
    BASE_URL = "https://api.geoapify.com/v2"
    V1_BASE_URL = "https://api.geoapify.com/v1"

    @classmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def geocode(cls, query: str) -> Dict[str, Any]:
        if not cls.API_KEY: return {}
        
        cache_key = f"geoapify:geocode:{query}"
        cached = _get_cache(cache_key)
        if cached: return cached

        url = f"{cls.V1_BASE_URL}/geocode/search"
        params = {"text": query, "apiKey": cls.API_KEY, "limit": 1}
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        features = res.json().get("features", [])
        if features:
            coords = features[0]["geometry"]["coordinates"]
            result = {
                "lat": coords[1],
                "lon": coords[0],
                "name": features[0]["properties"].get("formatted", query)
            }
            _set_cache(cache_key, result, ttl=2592000) # Cache geocoding for 30 days
            return result
        return {}

    @classmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def search_places(cls, categories: list, lat: float, lon: float, radius: int = 5000) -> List[Dict[str, Any]]:
        if not cls.API_KEY: return []

        cache_key = f"geoapify:places:{lat},{lon}:{'-'.join(categories)}"
        cached = _get_cache(cache_key)
        if cached: return cached

        url = f"{cls.BASE_URL}/places"
        cat_str = ",".join(categories)
        params = {
            "categories": cat_str,
            "filter": f"circle:{lon},{lat},{radius}",
            "limit": 20,
            "apiKey": cls.API_KEY
        }
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        features = res.json().get("features", [])
        places = []
        for f in features:
            props = f["properties"]
            places.append({
                "name": props.get("name") or props.get("formatted", "Unknown Place"),
                "lat": props.get("lat"),
                "lon": props.get("lon"),
                "address": props.get("formatted"),
                "categories": props.get("categories", [])
            })
        
        _set_cache(cache_key, places, ttl=86400) # Cache places for 24h
        return places

    @classmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_route(cls, waypoints: list) -> Dict[str, Any]:
        if not cls.API_KEY or len(waypoints) < 2: return {}
        url = f"{cls.V1_BASE_URL}/routing"
        wp_str = "|".join([f"{w['lat']},{w['lon']}" for w in waypoints])
        params = {"waypoints": wp_str, "mode": "drive", "apiKey": cls.API_KEY}
        
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        if "features" in data and data["features"]:
            props = data["features"][0]["properties"]
            return {
                "distance": props.get("distance"),
                "time": props.get("time"),
                "legs": props.get("legs", [])
            }
        return {}

    @classmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_route_matrix(cls, sources: list, targets: list) -> List[List[Dict[str, Any]]]:
        if not cls.API_KEY or not sources or not targets: return []
        url = f"{cls.V1_BASE_URL}/routematrix"
        params = {"apiKey": cls.API_KEY, "mode": "drive"}
        body = {
            "mode": "drive",
            "sources": [{"location": [s["lon"], s["lat"]]} for s in sources],
            "targets": [{"location": [t["lon"], t["lat"]]} for t in targets]
        }
        
        res = requests.post(url, params=params, json=body, timeout=10)
        res.raise_for_status()
        return res.json().get("sources_to_targets", [])