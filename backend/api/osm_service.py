# backend/api/osm_service.py
import requests
import time
from typing import List, Dict, Any, Optional

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
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


def search_pois(lat: float, lon: float, kinds: List[str], radius: int = 3000, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search OSM (Overpass) for POIs around lat/lon.
    `kinds` is a list of friendly hints (e.g. ["museum","tourism","viewpoint"])
    Returns list of dicts: {name, lat, lon, tags}
    """
    if lat is None or lon is None:
        return []

    filters = _hints_to_filters(kinds)
    if not filters:
        return []

    query = _build_overpass_query(lat, lon, radius, filters, limit=limit)
    try:
        r = requests.post(OVERPASS_URL, data=query.encode("utf-8"), headers=HEADERS, timeout=25)
        r.raise_for_status()
        res = r.json()
    except Exception:
        # on any failure, return empty to force fallback
        return []

    elements = res.get("elements", [])
    pois = []
    for el in elements:
        name = None
        tags = el.get("tags") or {}
        # prefer 'name' tag
        name = tags.get("name") or tags.get("official_name") or tags.get("wikidata") or tags.get("tourism") or None
        # compute lat/lon: node has lat/lon, way/relation often have 'center'
        if el.get("type") == "node":
            plat = el.get("lat")
            plon = el.get("lon")
        else:
            center = el.get("center") or {}
            plat = center.get("lat")
            plon = center.get("lon")
        if not name:
            # if no name, try to build from tags (small fallback)
            name = tags.get("amenity") or tags.get("tourism") or tags.get("historic") or None
        if name and plat and plon:
            pois.append({"name": name, "lat": float(plat), "lon": float(plon), "tags": tags})
    # Simple dedupe by name + coords
    seen = set()
    unique = []
    for p in pois:
        key = (p["name"], round(p["lat"], 5), round(p["lon"], 5))
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
