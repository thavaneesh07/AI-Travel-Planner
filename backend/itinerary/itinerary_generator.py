# backend/itinerary/itinerary_generator.py
from typing import List, Dict, Any, Optional
from api.groq_service import generate_activity_types
from api.osm_service import geocode, search_pois, placeholder_place
from api.weather_service import get_weather_forecast
from state import get_trip, set_trip
from datetime import datetime, timedelta
import random
import math

# Map activity → friendly OSM hint tokens (will be converted to filters by osm_service)
_ACTIVITY_TO_HINTS = {
    "museum": ["museum", "tourism"],
    "art_museum": ["museum", "art", "tourism"],
    "historic_site": ["historic", "monument", "tourism"],
    "temple": ["place_of_worship", "tourism"],
    "church": ["place_of_worship", "tourism"],
    "park": ["park", "leisure"],
    "beach": ["beach", "natural"],
    "food_experience": ["restaurant", "cafe", "amenity", "market"],
    "local_market": ["market", "shop", "amenity"],
    "sightseeing": ["attraction", "viewpoint", "tourism"],
    "shopping": ["shop", "retail"],
    "architecture": ["tourism", "attraction"],
    "local_dinner": ["restaurant", "cafe", "amenity"],
}

# Simple per-slot cost estimate (USD)
COST_MAP = {"morning": 25.0, "afternoon": 35.0, "evening": 45.0}


def _map_activity_to_hints(label: Optional[str]) -> List[str]:
    if not label:
        return ["tourism"]
    return _ACTIVITY_TO_HINTS.get(label.lower(), [label.lower(), "tourism"])


def _normalize_weather(raw: Any, start_date: datetime.date, days_count: int) -> List[Dict[str, Any]]:
    """
    Normalize weather output into a list of day objects:
    { "date": "YYYY-MM-DD", "temp": float|None, "desc": str }
    Accepts several formats:
      - list of dicts (already normalized)
      - dict with 'daily' Open-Meteo style
      - None or unexpected -> return list of placeholders
    """
    out = []
    # default placeholder
    for i in range(days_count):
        day = {"date": (start_date + timedelta(days=i)).isoformat(), "temp": None, "desc": "Weather unavailable"}
        out.append(day)

    if not raw:
        return out

    # If already a list of day dicts
    if isinstance(raw, list):
        for i in range(min(days_count, len(raw))):
            r = raw[i] or {}
            out[i]["temp"] = r.get("temp") or r.get("temperature") or r.get("temp_max") or r.get("temp_avg")
            out[i]["desc"] = r.get("desc") or r.get("description") or r.get("weather") or out[i]["desc"]
        return out

    # If Open-Meteo style dict with daily.* arrays
    if isinstance(raw, dict):
        daily = raw.get("daily") or {}
        times = daily.get("time") or []
        tmax = daily.get("temperature_2m_max") or daily.get("temp_max") or daily.get("temperature_max")
        tmin = daily.get("temperature_2m_min") or daily.get("temp_min") or daily.get("temperature_min")
        codes = daily.get("weathercode") or daily.get("weather_code")
        # try to align by date from start_date
        for i in range(days_count):
            idx = None
            # prefer matching by index (assuming API returned days in chronological order)
            if times and i < len(times):
                idx = i
            if idx is not None:
                temp_val = None
                # prefer tmax then tmin
                if isinstance(tmax, (list, tuple)) and idx < len(tmax):
                    temp_val = tmax[idx]
                elif isinstance(tmin, (list, tuple)) and idx < len(tmin):
                    temp_val = tmin[idx]
                code_val = None
                if isinstance(codes, (list, tuple)) and idx < len(codes):
                    code_val = codes[idx]
                out[i]["temp"] = temp_val
                # map some WMO weather codes to text
                code_map = {
                    0: "Clear sky",
                    1: "Mainly clear",
                    2: "Partly cloudy",
                    3: "Overcast",
                    45: "Fog",
                    48: "Fog",
                    51: "Light drizzle",
                    61: "Rain",
                    71: "Snow",
                }
                if code_val is not None:
                    out[i]["desc"] = code_map.get(int(code_val), "Weather unavailable")
        return out

    # fallback: unknown format
    return out


def _score_candidate_for_activity(candidate: Dict[str, Any], activity_label: str) -> float:
    """
    Simple heuristic to score candidates for a given activity_label.
    Higher is better. This helps prefer museums/attractions over random amenities.
    """
    tags = candidate.get("tags", {}) or {}
    score = 0.0
    # presence of name is important
    if tags.get("name"):
        score += 2.0
    tourism = tags.get("tourism")
    amenity = tags.get("amenity")
    historic = tags.get("historic")
    shop = tags.get("shop")
    # prefer exact matches
    if activity_label in ("museum", "art_museum") and tourism in ("museum",):
        score += 5.0
    if activity_label in ("sightseeing", "architecture", "historic_site") and tourism in ("attraction", "viewpoint", "museum"):
        score += 4.0
    if activity_label in ("food_experience", "local_dinner") and amenity in ("restaurant", "cafe", "fast_food"):
        score += 4.0
    # generic tourism nodes get a boost
    if tourism:
        score += 1.5
    if historic:
        score += 1.2
    if amenity:
        score += 1.0
    # penalize clearly inappropriate tags
    if amenity in ("bank", "atm", "parking") and activity_label not in ("local_dinner", "food_experience"):
        score -= 5.0
    # prefer nodes with wikipedia/wikidata (likely notable)
    if tags.get("wikipedia") or tags.get("wikidata"):
        score += 1.5
    return score


def generate_itinerary(
    destination: str,
    start_date: str,
    end_date: str,
    interests: List[str],
    budget: float,
) -> Dict[str, Any]:
    """
    Generate itinerary: queries Groq for activity labels, geocodes destination, fetches weather,
    looks up POIs from Overpass via api.osm_service.search_pois, ranks candidates, builds days.
    Returns dict:
      { destination, start_date, end_date, days: [...], total_estimated_cost }
    """

    # 1) Activity plan (labels)
    activity_plan = generate_activity_types(destination, start_date, end_date, interests, budget)

    # 2) parse dates
    try:
        sd = datetime.fromisoformat(start_date).date()
        ed = datetime.fromisoformat(end_date).date()
        days_count = max(1, (ed - sd).days + 1)
    except Exception:
        # fallback
        sd = datetime.utcnow().date()
        days_count = len(activity_plan) if activity_plan else 3

    # 3) geocode destination (Nominatim)
    lat = lon = None
    try:
        center = geocode(destination)
        lat = float(center.get("lat"))
        lon = float(center.get("lon"))
    except Exception:
        lat = lon = None

    # 4) weather fetch & normalize
    try:
        raw_weather = get_weather_forecast(destination, start_date, end_date)
    except Exception:
        raw_weather = None
    weather_days = _normalize_weather(raw_weather, sd, days_count)

    days_out: List[Dict[str, Any]] = []
    total_cost = 0.0
    used_names = set()

    # iterate days, but guard against Groq returning fewer/extra days
    for i in range(days_count):
        # safe get for activity_plan
        ap = activity_plan[i] if i < len(activity_plan) else {}
        current_date = (sd + timedelta(days=i)).isoformat()

        day_weather = weather_days[i] if i < len(weather_days) else {"date": current_date, "temp": None, "desc": "Weather unavailable"}

        day_entry: Dict[str, Any] = {
            "day": i + 1,
            "date": current_date,
            "weather": {"temp": day_weather.get("temp"), "desc": day_weather.get("desc")},
        }

        day_cost = 0.0

        for slot in ("morning", "afternoon", "evening"):
            label = (ap.get(slot) or ap.get(slot.lower()) or "sightseeing")
            hints = _map_activity_to_hints(label)

            candidate_place: Optional[Dict[str, Any]] = None
            # try OSM lookup if we have lat/lon
            if lat is not None and lon is not None:
                try:
                    candidates = search_pois(lat=lat, lon=lon, kinds=hints, radius=5000, limit=20) or []
                except Exception:
                    candidates = []

                # score & choose best candidate not previously used, with a name and coords
                scored = []
                for c in candidates:
                    name = (c.get("name") or "").strip()
                    if not name:
                        continue
                    key_name = name.lower()
                    if key_name in used_names:
                        continue
                    # simple heuristic: avoid names that are obviously not attractions
                    tags = c.get("tags", {}) or {}
                    # compute score
                    score = _score_candidate_for_activity(c, label)
                    # prefer nodes whose name contains typical attraction words for museums/temples etc.
                    lower_name = name.lower()
                    if any(word in lower_name for word in ("museum", "gallery", "temple", "fort", "park", "garden", "viewpoint", "monument", "gallery", "palace", "beach", "zoo")):
                        score += 1.5
                    scored.append((score, c))
                # sort by score desc
                scored.sort(key=lambda x: x[0], reverse=True)
                if scored and scored[0][0] > -100:  # if best is not heavily penalized
                    candidate_place = scored[0][1]

            # Build place object (either from candidate or placeholder)
            if candidate_place:
                place_obj = {
                    "name": candidate_place.get("name"),
                    "lat": candidate_place.get("lat"),
                    "lon": candidate_place.get("lon"),
                    "tags": candidate_place.get("tags", {}),
                    "activity_label": label,
                }
                used_names.add(place_obj["name"].lower())
            else:
                # fallback placeholder
                ph = placeholder_place(label, destination)
                place_obj = {
                    "name": ph["name"],
                    "lat": ph.get("lat"),
                    "lon": ph.get("lon"),
                    "tags": ph.get("tags", {}),
                    "activity_label": label,
                }

            day_entry[slot] = place_obj
            # cost calc
            day_cost += COST_MAP.get(slot, 0.0)

        day_entry["estimated_cost"] = round(day_cost, 2)
        total_cost += day_cost
        days_out.append(day_entry)

    final = {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "days": days_out,
        "total_estimated_cost": round(total_cost, 2),
    }

    # persist to single-user state
    try:
        trip = get_trip()
        trip["destination"] = destination
        trip["start_date"] = start_date
        trip["end_date"] = end_date
        trip["itinerary"] = final
        trip["interests"] = interests or []
        trip["budget"] = budget or trip.get("budget", 1000.0)
        set_trip(trip)
    except Exception:
        # don't fail the API if persistence fails
        pass

    return final
