# backend/api/weather_service.py
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import hashlib

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
def _seeded_rng(*parts: str):
    seed_text = "|".join(str(p) for p in parts)
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16)
    import random
    return random.Random(seed)


def _synthetic_weather(city: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    start = datetime.fromisoformat(start_date).date()
    end = datetime.fromisoformat(end_date).date()
    days_count = (end - start).days + 1

    conditions = [
        "Sunny", "Cloudy", "Partly cloudy", "Light drizzle", "Rain showers",
        "Clear sky", "Overcast"
    ]
    rng = _seeded_rng(city, start_date, end_date, "weather")
    base_temp = 12 + (abs(hash(city)) % 10)

    result = []
    for i in range(days_count):
        result.append({
            "temp": base_temp + rng.randint(-3, 3),
            "desc": conditions[(rng.randint(0, len(conditions) - 1) + i) % len(conditions)],
        })
    return result


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
    # 1) Local fallback JSON
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
    # 2) Synthetic deterministic fallback (no network)
    # ---------------------------------------------------------------
    return _synthetic_weather(city, start.isoformat(), end.isoformat())
