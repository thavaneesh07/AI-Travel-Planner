# backend/api/weather_service.py
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "AI-Travel-Planner/1.0 (your-email@example.com)"}

def geocode_city(city: str) -> Dict[str, Any]:
    params = {"format": "json", "q": city, "limit": 1}
    r = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=8)
    r.raise_for_status()
    data = r.json()
    if not data:
        raise ValueError("No geocode result")
    return data[0]


def get_weather_forecast(city: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns daily weather information for the date range (inclusive).
    Output: list of dicts for each day, with keys: time, temp_max, temp_min, weathercode
    If start/end omitted, returns 3-day forecast starting today.
    """
    # geocode
    geo = geocode_city(city)
    lat = float(geo["lat"])
    lon = float(geo["lon"])

    if start_date:
        start = datetime.fromisoformat(start_date).date()
    else:
        start = datetime.utcnow().date()
    if end_date:
        end = datetime.fromisoformat(end_date).date()
    else:
        end = start + timedelta(days=2)

    # Open-Meteo expects ISO dates
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
    daily = data.get("daily", {})
    times = daily.get("time", [])
    tmax = daily.get("temperature_2m_max", [])
    tmin = daily.get("temperature_2m_min", [])
    wc = daily.get("weathercode", [])

    out = []
    for i, day in enumerate(times):
        out.append({
            "time": day,
            "temp_max": tmax[i] if i < len(tmax) else None,
            "temp_min": tmin[i] if i < len(tmin) else None,
            "weathercode": wc[i] if i < len(wc) else None,
        })
    return out
