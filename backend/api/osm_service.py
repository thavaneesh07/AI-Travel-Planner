import requests
import time
from typing import List, Dict, Any, Optional
import json
import os

# --- Local JSON fallback loader ---
def load_local_fallback_spots(destination: str, activity_label: str):
    """
    Load POIs from local tourist_spots.json when OSM fails.
    """
    try:
        json_path = os.path.join(os.path.dirname(__file__), "tourist_spots.json")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        city_data = data.get(destination)
        if not city_data:
            return []

        spots = city_data.get(activity_label, [])
        return [
            {"name": s, "lat": None, "lon": None, "tags": {"fallback": "true"}}
            for s in spots
        ]
    except Exception:
        return []


# ------------------ OSM ---------------------
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter"
]
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


_HINT_TO_OSM = {
    "tourism": ("tourism", None),
    "attraction": ("tourism", "attraction"),
    "museum": ("tourism", "museum"),
    "viewpoint": ("tourism", "viewpoint"),
    "historic": ("historic", None),
    "monument": ("historic", "monument"),
    "park": ("leisure", "park"),
    "leisure": ("leisure", None),
    "beach": ("natural", "beach"),
    "natural": ("natural", None),
    "restaurant": ("amenity", "restaurant"),
    "cafe": ("amenity", "cafe"),
    "shop": ("shop", None),
    "marketplace": ("amenity", "marketplace"),
    "market": ("amenity", "marketplace"),
    "amenity": ("amenity", None),
    "place_of_worship": ("amenity", "place_of_worship"),
}

HEADERS = {"User-Agent": "AI-Travel-Planner/1.0 (your-email@example.com)"}


def geocode(q: str, limit: int = 1, countrycodes: Optional[str] = None) -> Dict[str, Any]:
    params = {"format": "json", "q": q, "limit": limit}
    if countrycodes:
        params["countrycodes"] = countrycodes
    r = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    data = r.json()
    if not data:
        raise ValueError("Geocode: no results")
    return data[0]


def _build_overpass_query(lat: float, lon: float, radius: int, osm_filters, limit=50):
    blocks = []
    for f in osm_filters:
        k = f["k"]
        v = f.get("v")
        if v:
            blocks.append(f'node["{k}"="{v}"](around:{radius},{lat},{lon});')
            blocks.append(f'way["{k}"="{v}"](around:{radius},{lat},{lon});')
            blocks.append(f'relation["{k}"="{v}"](around:{radius},{lat},{lon});')
        else:
            blocks.append(f'node["{k}"](around:{radius},{lat},{lon});')
            blocks.append(f'way["{k}"](around:{radius},{lat},{lon});')
            blocks.append(f'relation["{k}"](around:{radius},{lat},{lon});')

    body = "[out:json][timeout:25];\n(\n" + "\n".join(blocks) + "\n);\nout center %d;" % limit
    return body


def _hints_to_filters(hints: List[str]):
    filters = []
    for h in hints:
        h = h.lower()
        if h in _HINT_TO_OSM:
            k, v = _HINT_TO_OSM[h]
            filters.append({"k": k, "v": v})
        else:
            filters.append({"k": "tourism", "v": h})

    # de-dup
    seen = set()
    out = []
    for f in filters:
        tup = (f["k"], f.get("v"))
        if tup not in seen:
            seen.add(tup)
            out.append(f)
    return out


def search_pois(lat: float, lon: float, kinds: List[str], radius: int = 3000, limit: int = 20):
    if lat is None or lon is None:
        return []

    filters = _hints_to_filters(kinds)
    query = _build_overpass_query(lat, lon, radius, filters, limit=limit)

    time.sleep(1)

    res = None

    for url in OVERPASS_URLS:
        try:
            r = requests.post(url, data=query.encode("utf-8"), headers=HEADERS, timeout=25)
            r.raise_for_status()
            res = r.json()
            if "elements" in res and len(res["elements"]) > 0:
                break
        except Exception:
            continue

    if not res or "elements" not in res or len(res["elements"]) == 0:
        return []  # itinerary will handle JSON fallback

    elements = res.get("elements", [])
    pois = []

    for el in elements:
        tags = el.get("tags") or {}
        name = tags.get("name")

        if not name:
            continue

        if el.get("type") == "node":
            plat, plon = el.get("lat"), el.get("lon")
        else:
            center = el.get("center") or {}
            plat, plon = center.get("lat"), center.get("lon")

        if not plat or not plon:
            continue

        pois.append({
            "name": name,
            "lat": float(plat),
            "lon": float(plon),
            "tags": tags
        })

    # dedupe
    seen = set()
    unique = []
    for p in pois:
        key = (p["name"], round(p["lat"], 5), round(p["lon"], 5))
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return unique[:limit]


def placeholder_place(activity_label: str, destination: str):
    pretty = activity_label.replace("_", " ").title()
    return {
        "name": f"{pretty} near {destination}",
        "lat": None,
        "lon": None,
        "tags": {"placeholder": "true", "activity": activity_label},
    }
