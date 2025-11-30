# backend/itinerary/itinerary_generator.py
from typing import List, Dict, Any, Optional
from api.groq_service import generate_activity_types
from api.osm_service import geocode, search_pois, placeholder_place, load_local_fallback_spots
from api.weather_service import get_weather_forecast
from state import get_trip, set_trip
__all__ = ["generate_itinerary", "apply_itinerary_modification"]
from datetime import datetime, timedelta
import random
import math
import os

# Map activity → friendly OSM hint tokens
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

_SLOT_WEIGHTS = {"morning": 0.25, "afternoon": 0.35, "evening": 0.40}


def _map_activity_to_hints(label: Optional[str]) -> List[str]:
    if not label:
        return ["tourism"]
    return _ACTIVITY_TO_HINTS.get(label.lower(), [label.lower(), "tourism"])


# WEATHER NORMALIZER ----------------------------------------------------------
def _normalize_weather(raw: Any, start_date: datetime.date, days_count: int) -> List[Dict[str, Any]]:
    """
    Supports BOTH:
    - API format: {temp_max, temp_min, weathercode}
    - Fallback format: {temp, desc}
    """

    # Build structure for N days
    out = [{
        "date": (start_date + timedelta(days=i)).isoformat(),
        "temp": None,
        "desc": "Weather unavailable"
    } for i in range(days_count)]

    if not raw:
        return out

    # -------------------------------------------------------------------
    # 1️⃣ FALLBACK FORMAT:  { "temp": X, "desc": "Sunny" }
    # -------------------------------------------------------------------
    try:
        # Check if raw is a list AND contains fallback keys
        if isinstance(raw, list) and len(raw) > 0 and isinstance(raw[0], dict) and "temp" in raw[0]:
            for i in range(days_count):
                src = raw[i % len(raw)]  # loop values if fewer entries
                out[i]["temp"] = src.get("temp")
                out[i]["desc"] = src.get("desc", "Weather unavailable")
            return out
    except:
        pass

    # -------------------------------------------------------------------
    # 2️⃣ API (Open-Meteo) LIST FORMAT
    # -------------------------------------------------------------------

    code_map = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Fog", 51: "Light drizzle", 61: "Rain", 63: "Rain",
        71: "Snow", 80: "Rain showers", 95: "Thunderstorm",
    }

    if isinstance(raw, list):
        for i in range(min(days_count, len(raw))):
            r = raw[i]

            # Temperature
            tmax = r.get("temp_max")
            tmin = r.get("temp_min")
            temp_val = None

            if tmax is not None and tmin is not None:
                try:
                    temp_val = (float(tmax) + float(tmin)) / 2
                except:
                    temp_val = tmax
            else:
                temp_val = tmax if tmax is not None else tmin

            out[i]["temp"] = temp_val

            # Description
            wc = r.get("weathercode")
            if wc is not None:
                out[i]["desc"] = code_map.get(int(wc), "Weather unavailable")

        return out

    # -------------------------------------------------------------------
    # 3️⃣ API DICT FORMAT
    # -------------------------------------------------------------------

    if isinstance(raw, dict):
        daily = raw.get("daily") or {}
        times = daily.get("time") or []
        tmax = daily.get("temperature_2m_max") or []
        tmin = daily.get("temperature_2m_min") or []
        codes = daily.get("weathercode") or []

        for i in range(days_count):
            if i < len(times):
                out[i]["temp"] = tmax[i] if i < len(tmax) else tmin[i]
                if i < len(codes):
                    out[i]["desc"] = code_map.get(int(codes[i]), "Weather unavailable")

        return out

    return out



# SCORING FUNCTION ------------------------------------------------------------
def _score_candidate_for_activity(candidate: Dict[str, Any], activity_label: str) -> float:
    tags = candidate.get("tags", {}) or {}
    score = 0

    if tags.get("name"):
        score += 2

    tourism = tags.get("tourism")
    amenity = tags.get("amenity")
    historic = tags.get("historic")

    if activity_label in ("museum", "art_museum") and tourism == "museum":
        score += 5
    if activity_label in ("sightseeing", "architecture", "historic_site") and tourism in ("attraction", "viewpoint", "museum"):
        score += 4
    if activity_label in ("food_experience", "local_dinner") and amenity in ("restaurant", "cafe", "fast_food"):
        score += 4

    if tourism:
        score += 1.5
    if historic:
        score += 1.2
    if amenity:
        score += 1.0

    if amenity in ("bank", "atm", "parking"):
        score -= 5

    if tags.get("wikipedia") or tags.get("wikidata"):
        score += 1.5

    return score


# MAIN ITINERARY GENERATOR ----------------------------------------------------
def generate_itinerary(destination, start_date, end_date, interests, budget):
    activity_plan = generate_activity_types(destination, start_date, end_date, interests, budget)

    # Dates
    try:
        sd = datetime.fromisoformat(start_date).date()
        ed = datetime.fromisoformat(end_date).date()
        days_count = max(1, (ed - sd).days + 1)
    except:
        sd = datetime.utcnow().date()
        days_count = len(activity_plan) if activity_plan else 3

    # Geocode
    try:
        coords = geocode(destination)
        lat = float(coords["lat"])
        lon = float(coords["lon"])
    except:
        lat = lon = None

    # WEATHER FETCH + FALLBACK ------------------------------------------------
    try:
        raw_weather = get_weather_forecast(destination, start_date, end_date)
    except:
        raw_weather = None

    if not raw_weather or len(raw_weather) == 0:
        try:
            from api.weather_service import load_weather_fallback
            fallback = load_weather_fallback(destination)
        except:
            fallback = None

        if fallback:
            raw_weather = fallback
        else:
            raw_weather = None

    weather_days = _normalize_weather(raw_weather, sd, days_count)

    used_names = set()
    global_json_tracker = {}
    days_out = []
    total_cost = 0

    # Build itinerary
    for i in range(days_count):
        ap = activity_plan[i] if i < len(activity_plan) else {}
        current_date = (sd + timedelta(days=i)).isoformat()
        day_weather = weather_days[i]

        day_entry = {
            "day": i + 1,
            "date": current_date,
            "weather": {
                "temp": day_weather["temp"],
                "desc": day_weather["desc"]
            },
        }

        per_day_budget = max(float(budget) / days_count, 60)
        day_cost = 0

        # SLOTS LOOP --------------------------------------------------------
        for slot in ("morning", "afternoon", "evening"):
            label = ap.get(slot) or "sightseeing"
            hints = _map_activity_to_hints(label)

            candidate_place = None
            candidates = []

            # OSM SEARCH -----------------------------------------------------
            if lat is not None and lon is not None:
                for radius in (3000, 8000):
                    try:
                        candidates = search_pois(lat, lon, hints, radius, 30) or []
                    except:
                        candidates = []
                    if candidates:
                        break

                if not candidates:
                    try:
                        candidates = search_pois(lat, lon, ["tourism", "amenity"], 8000, 30) or []
                    except:
                        candidates = []

                scored = []
                for c in candidates:
                    name = (c.get("name") or "").strip()
                    if not name or name.lower() in used_names:
                        continue

                    score = _score_candidate_for_activity(c, label)
                    lname = name.lower()

                    if any(w in lname for w in ("museum", "temple", "fort", "park", "garden", "view", "monument", "palace", "beach", "zoo")):
                        score += 1.5

                    scored.append((score, c))

                scored.sort(key=lambda x: x[0], reverse=True)
                if scored:
                    candidate_place = scored[0][1]

            # IF OSM SUCCESS -------------------------------------------------
            if candidate_place:
                place_obj = {
                    "name": candidate_place["name"],
                    "lat": candidate_place["lat"],
                    "lon": candidate_place["lon"],
                    "tags": candidate_place.get("tags", {}),
                    "activity_label": label,
                }
                used_names.add(place_obj["name"].lower())

            # JSON FALLBACK --------------------------------------------------
            else:
                fallback = load_local_fallback_spots(destination, label)

                if fallback:
                    key = f"{destination}_{label}"
                    used_list = global_json_tracker.get(key, [])
                    available = [x for x in fallback if x["name"].lower() not in used_list]

                    if not available:
                        used_list = []
                        available = fallback

                    chosen = random.choice(available)
                    used_list.append(chosen["name"].lower())
                    global_json_tracker[key] = used_list

                    place_obj = {
                        "name": chosen["name"],
                        "lat": None,
                        "lon": None,
                        "tags": {"fallback": "true"},
                        "activity_label": label,
                    }
                    used_names.add(place_obj["name"].lower())

                else:
                    ph = placeholder_place(label, destination)
                    place_obj = {
                        "name": ph["name"],
                        "lat": ph.get("lat"),
                        "lon": ph.get("lon"),
                        "tags": ph.get("tags", {}),
                        "activity_label": label,
                    }

            day_entry[slot] = place_obj

            slot_cost = round(per_day_budget * _SLOT_WEIGHTS.get(slot, 1/3), 2)
            slot_cost = max(10, min(slot_cost, per_day_budget * 0.6))
            day_cost += slot_cost

        day_entry["estimated_cost"] = round(day_cost, 2)
        total_cost += day_cost
        days_out.append(day_entry)

    # FINAL OBJECT -----------------------------------------------------------
    final = {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "days": days_out,
        "total_estimated_cost": round(total_cost, 2),
    }

    try:
        trip = get_trip()
        trip["destination"] = destination
        trip["start_date"] = start_date
        trip["end_date"] = end_date
        trip["itinerary"] = final
        trip["interests"] = interests
        trip["budget"] = budget
        set_trip(trip)
    except:
        pass

    return final
# --- NEW: MODIFY EXISTING ITINERARY SLOT -----------------------------------
def apply_itinerary_modification(itinerary: dict, changes: dict):
    """
    Example 'changes':
    {
        "day2": { "morning": "Eiffel Tower" },
        "day3": { "evening": "Louvre Museum" }
    }
    """
    days = itinerary.get("days", [])

    for day_key, day_changes in changes.items():
        try:
            index = int(day_key.replace("day", "")) - 1
            if index < 0 or index >= len(days):
                continue

            day = days[index]

            for slot, new_value in day_changes.items():
                if slot in ("morning", "afternoon", "evening"):

                    # If AI sends only the name (string)
                    if isinstance(new_value, str):
                        if isinstance(day.get(slot), dict):
                            day[slot]["name"] = new_value
                        else:
                            day[slot] = {"name": new_value}
                    else:
                        # AI sent full object
                        day[slot] = new_value

        except Exception as e:
            print("Modification error:", e)

    return itinerary
