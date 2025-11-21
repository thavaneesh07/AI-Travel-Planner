import requests
from functools import lru_cache
import time

OSM_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "TravelPlanner/1.0 (student-project)"}


class OSMService:
    def __init__(self, sleep_time=1.1):
        self.sleep_time = sleep_time

    # -----------------------------
    # Geocoding: City → Coordinates
    # -----------------------------
    @lru_cache(maxsize=64)
    def geocode_city(self, city_name: str):
        params = {
            "q": city_name,
            "format": "json",
            "limit": 1
        }

        r = requests.get(OSM_NOMINATIM_URL, params=params, headers=HEADERS)

        if r.status_code != 200:
            raise Exception(f"Nominatim geocode failed: {r.status_code}")

        data = r.json()
        if not data:
            raise Exception(f"City '{city_name}' not found")

        return {
            "lat": float(data[0]["lat"]),
            "lon": float(data[0]["lon"])
        }

    # ------------------------------------
    # Search POIs Near Coordinates via OSM
    # ------------------------------------
    def search_pois(self, lat: float, lon: float, radius: int = 3000, tags=None):
        """
        tags example: ["tourism", "amenity", "leisure"]
        """

        if not tags:
            tags = ["tourism", "amenity"]

        overpass_query = f"""
        [out:json];
        (
            {"".join([f'node["{tag}"](around:{radius},{lat},{lon}); way["{tag}"](around:{radius},{lat},{lon}); ' for tag in tags])}
        );
        out center;
        """

        # Rate-limit safe
        time.sleep(self.sleep_time)

        r = requests.post(OVERPASS_API_URL, data=overpass_query, headers=HEADERS)

        if r.status_code != 200:
            raise Exception(f"Overpass API failed: {r.status_code}")

        data = r.json()
        results = []

        for el in data.get("elements", []):
            tags = el.get("tags", {})
            name = tags.get("name")

            if not name:
                continue

            # unified lat/lon for nodes, ways
            center = el.get("center") or el
            lat_res = center.get("lat")
            lon_res = center.get("lon")

            results.append({
                "name": name,
                "category": tags,
                "lat": lat_res,
                "lon": lon_res
            })

        return results


osm_service = OSMService()
