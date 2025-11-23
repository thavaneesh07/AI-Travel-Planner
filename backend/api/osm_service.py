# backend/api/osm_service.py
import requests
import time
from typing import List, Dict, Any, Optional

OVERPASS_URLS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter"
]
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# Map short hint -> (osm_key, osm_value or None).
# If value is None we match any node with that key (e.g. historic).
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
    "market": ("marketplace", None),
    "amenity": ("amenity", None),
    "place_of_worship": ("amenity", "place_of_worship"),
}

HEADERS = {"User-Agent": "AI-Travel-Planner/1.0 (your-email@example.com)"}


def geocode(q: str, limit: int = 1, countrycodes: Optional[str] = None) -> Dict[str, Any]:
    """
    Geocode a city/place using Nominatim. Returns the first result dict.
    """
    params = {"format": "json", "q": q, "limit": limit}
    if countrycodes:
        params["countrycodes"] = countrycodes
    r = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    data = r.json()
    if not data:
        raise ValueError("Geocode: no results")
    return data[0]


def _build_overpass_query(lat: float, lon: float, radius: int, osm_filters: List[Dict[str, Optional[str]]], limit: int = 50) -> str:
    """
    Constructs an Overpass QL query that attempts to find nodes/ways/relations matching one of the filters.
    osm_filters: list of dicts { "k": key, "v": value_or_None }
    """
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


def _hints_to_filters(hints: List[str]) -> List[Dict[str, Optional[str]]]:
    """
    Convert human hints list into OSM key/value filters.
    Example: ["museum","tourism"] -> [{"k":"tourism","v":"museum"}, {"k":"tourism","v":None}]
    """
    filters = []
    for h in hints:
        h = h.lower()
        if h in _HINT_TO_OSM:
            k, v = _HINT_TO_OSM[h]
            filters.append({"k": k, "v": v})
        else:
            # if unknown hint, try as tourism value fallback
            filters.append({"k": "tourism", "v": h})
    # de-dup keeping order
    seen = set()
    out = []
    for f in filters:
        tup = (f["k"], f.get("v"))
        if tup not in seen:
            seen.add(tup)
            out.append(f)
    return out


def search_pois(lat: float, lon: float, kinds: List[str], radius: int = 8000, limit: int = 20) -> List[Dict[str, Any]]:
    if lat is None or lon is None:
        return []

    filters = _hints_to_filters(kinds)
    if not filters:
        return []

    query = _build_overpass_query(lat, lon, radius, filters, limit=limit)

    # Try each Overpass server until one works
    res = None
    for url in OVERPASS_URLS:
        try:
            time.sleep(1)  # polite
            r = requests.post(url, data=query, headers=HEADERS, timeout=30)
            r.raise_for_status()
            res = r.json()

            # If this server returned valid data
            if "elements" in res and len(res["elements"]) > 0:
                break

        except Exception:
            continue

    # All servers failed or returned empty
    if not res or "elements" not in res:
        return []

    elements = res["elements"]
    pois = []

    for el in elements:
        tags = el.get("tags") or {}

        name = (
            tags.get("name")
            or tags.get("official_name")
            or tags.get("wikidata")
            or tags.get("tourism")
        )

        if el["type"] == "node":
            plat, plon = el.get("lat"), el.get("lon")
        else:
            center = el.get("center") or {}
            plat, plon = center.get("lat"), center.get("lon")

        if not name:
            name = tags.get("amenity") or tags.get("historic") or None

        if name and plat and plon:
            pois.append({
                "name": name,
                "lat": float(plat),
                "lon": float(plon),
                "tags": tags
            })

    # Dedupe
    unique = []
    seen = set()
    for p in pois:
        key = (p["name"].lower(), round(p["lat"], 4), round(p["lon"], 4))
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return unique[:limit]


def placeholder_place(activity_label: str, destination: str) -> Dict[str, Any]:
    """
    Simple friendly placeholder used when no real POI found.
    """
    pretty = activity_label.replace("_", " ").title()
    return {
        "name": f"{pretty} near {destination}",
        "lat": None,
        "lon": None,
        "tags": {"placeholder": "true", "activity": activity_label},
    }
