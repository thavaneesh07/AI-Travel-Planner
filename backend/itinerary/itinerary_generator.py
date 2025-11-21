from typing import List, Dict, Any
from api.groq_service import generate_activity_types
from api.osm_service import geocode, search_pois, placeholder_place
from state import get_trip, set_trip
from datetime import datetime, timedelta
import requests

# Map activity labels → category hints for OSM
_ACTIVITY_TO_HINTS = {
    "museum": ["museum"],
    "art_museum": ["museum", "art"],
    "historic_site": ["historic", "monument"],
    "temple": ["temple", "religion"],
    "church": ["church", "religion"],
    "park": ["park", "leisure"],
    "beach": ["beach"],
    "food_experience": ["restaurant", "food", "market"],
    "local_market": ["marketplace", "market"],
    "sightseeing": ["attraction", "viewpoint"],
    "shopping": ["shop"],
    "architecture": ["architecture", "building"],
    "local_dinner": ["restaurant"],
}

def _map_activity_to_hints(label: str) -> List[str]:
    if not label:
        return ["attraction"]
    return _ACTIVITY_TO_HINTS.get(label.lower(), [label.lower()])


# -----------------------------------------------------
# WEATHER API INTEGRATION
# -----------------------------------------------------
def fetch_weather(lat: float, lon: float, date: str):
    """
    Fetch simple weather forecast using Open-Meteo (free, no API key needed).
    date format: YYYY-MM-DD
    """
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&hourly=temperature_2m,weathercode"
            f"&start_date={date}&end_date={date}"
        )
        r = requests.get(url, timeout=10)
        data = r.json()

        if "hourly" not in data:
            return None

        # Pick midday reading (12:00)
        hourly = data["hourly"]
        times = hourly["time"]
        temps = hourly["temperature_2m"]
        codes = hourly["weathercode"]

        if "12:00" in times[0]:
            idx = 0
        else:
            # safest fallback: just pick index 12
            idx = min(12, len(times) - 1)

        return {
            "temperature": temps[idx],
            "weathercode": codes[idx],
        }
    except Exception:
        return None


# -----------------------------------------------------
# MAIN ITINERARY GENERATOR
# -----------------------------------------------------
def generate_itinerary(
    destination: str,
    start_date: str,
    end_date: str,
    interests: List[str],
    budget: float,
) -> Dict[str, Any]:

    # 1) Ask Groq for activity plan
    activity_plan = generate_activity_types(destination, start_date, end_date, interests, budget)

    # Calculate days count
    try:
        sd = datetime.fromisoformat(start_date).date()
        ed = datetime.fromisoformat(end_date).date()
        days_expected = (ed - sd).days + 1
    except:
        days_expected = len(activity_plan) if activity_plan else 3

    # 2) Geocode destination
    try:
        center = geocode(destination)
        lat = float(center["lat"])
        lon = float(center["lon"])
    except Exception:
        lat = None
        lon = None

    # -------------------------------------------------
    # Budget estimation
    # -------------------------------------------------
    # Simple heuristic:
    # morning = ₹700, afternoon = ₹1000, evening = ₹1300 (avg spend)
    COST_MAP = {"morning": 700, "afternoon": 1000, "evening": 1300}
    total_estimated_budget = 0

    days_out = []
    cur_date = sd

    for idx, day_obj in enumerate(activity_plan[:days_expected]):
        dnum = int(day_obj.get("day", idx + 1))
        day_entry = {"day": dnum, "date": cur_date.isoformat(), "morning": None, "afternoon": None, "evening": None}

        # ---------------------------
        # Weather for the day
        # ---------------------------
        if lat is not None and lon is not None:
            weather = fetch_weather(lat, lon, cur_date.isoformat())
        else:
            weather = None

        day_entry["weather"] = weather

        # ---------------------------
        # Fill activity slots
        # ---------------------------
        for slot in ("morning", "afternoon", "evening"):

            activity_label = day_obj.get(slot) or "sightseeing"
            hints = _map_activity_to_hints(activity_label)

            # radius based on budget
            radius = max(1000, min(10000, int((budget or 1000) / 2)))

            place = None
            if lat is not None and lon is not None:
                candidates = search_pois(lat=lat, lon=lon, kinds=hints, radius=radius, limit=6)
                if candidates:
                    c = candidates[0]
                    place = {
                        "name": c.get("name"),
                        "lat": c.get("lat"),
                        "lon": c.get("lon"),
                        "tags": c.get("tags", {}),
                        "activity_label": activity_label,
                    }

            # fallback
            if not place:
                ph = placeholder_place(activity_label, destination)
                place = {
                    "name": ph["name"],
                    "lat": ph.get("lat"),
                    "lon": ph.get("lon"),
                    "tags": ph.get("tags", {}),
                    "activity_label": activity_label,
                }

            day_entry[slot] = place
            total_estimated_budget += COST_MAP.get(slot, 800)

        days_out.append(day_entry)
        cur_date = cur_date + timedelta(days=1)

    # -------------------------------------------------
    # Save in global backend state
    # -------------------------------------------------
    trip = get_trip()
    trip["destination"] = destination
    trip["start_date"] = start_date
    trip["end_date"] = end_date
    trip["itinerary"] = days_out
    trip["interests"] = interests or []
    trip["budget"] = budget or trip.get("budget", 1000.0)
    trip["total_estimated_budget"] = total_estimated_budget
    set_trip(trip)

    # -------------------------------------------------
    # FINAL RESPONSE
    # -------------------------------------------------
    return {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "days": days_out,
        "total_estimated_budget": total_estimated_budget,
    }
