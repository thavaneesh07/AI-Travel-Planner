# backend/api/weather_service.py
import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "AI-Travel-Planner/1.0 (your-email@example.com)"}

FALLBACK_PATH = os.path.join(os.path.dirname(__file__), "weather_fallback.json")


# ---------------------------------------------------------------
# Load fallback JSON
# ---------------------------------------------------------------
def load_weather_fallback(city: str) -> Optional[List[Dict[str, Any]]]:
    try:
        with open(FALLBACK_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(city)
    except:
        return None


# ---------------------------------------------------------------
# Geocode city
# ---------------------------------------------------------------
def geocode_city(city: str) -> Dict[str, Any]:
    params = {"format": "json", "q": city, "limit": 1}
    r = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=8)
    r.raise_for_status()
    data = r.json()
    if not data:
        raise ValueError("No geocode result")
    return data[0]


# ---------------------------------------------------------------
# Get weather forecast (API + fallback)
# ---------------------------------------------------------------
def get_weather_forecast(city: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:

    # Date range
    if start_date:
        start = datetime.fromisoformat(start_date).date()
    else:
        start = datetime.utcnow().date()

    if end_date:
        end = datetime.fromisoformat(end_date).date()
    else:
        end = start + timedelta(days=2)

    days_count = (end - start).days + 1

    # ---------------------------------------------------------------
    # 1) Try API (Open-Meteo)
    # ---------------------------------------------------------------
    try:
        geo = geocode_city(city)
        lat = float(geo["lat"])
        lon = float(geo["lon"])

        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,weathercode",
            "timezone": "auto",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        }

        r = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        r.raise_for_status()

        data = r.json()
        daily = data.get("daily") or {}

        times = daily.get("time", [])
        tmax = daily.get("temperature_2m_max", [])
        tmin = daily.get("temperature_2m_min", [])
        codes = daily.get("weathercode", [])

        # If API returned no days → trigger fallback
        if not times:
            raise Exception("API returned no data")

        # Build API-style list (itinerary understands temp_max/temp_min format)
        result = []
        for i in range(len(times)):
            result.append({
                "time": times[i],
                "temp_max": tmax[i] if i < len(tmax) else None,
                "temp_min": tmin[i] if i < len(tmin) else None,
                "weathercode": codes[i] if i < len(codes) else None
            })

        return result

    except Exception as e:
        print(f"[weather] API failed → fallback used ({city}) | {e}")

    # ---------------------------------------------------------------
    # 2) Fallback JSON
    # ---------------------------------------------------------------
    fallback = load_weather_fallback(city)

    if fallback:
        # Example fallback entry:
        # { "temp": 30, "desc": "Sunny" }
        result = []
        for i in range(days_count):
            src = fallback[i % len(fallback)]
            result.append({
                "temp": src.get("temp"),
                "desc": src.get("desc")
            })
        return result

    # ---------------------------------------------------------------
    # 3) Final fallback (empty values)
    # ---------------------------------------------------------------
    return [{"temp": None, "desc": "Weather unavailable"} for _ in range(days_count)]
