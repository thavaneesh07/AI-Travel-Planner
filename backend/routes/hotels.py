from fastapi import APIRouter
from pydantic import BaseModel
import random
import os
import json
import httpx

from ..utils.hotel_ranker import rank_hotels

router = APIRouter()


class HotelRequest(BaseModel):
    destination: str
    budget: float
    interests: list = []


# -------------------------------
# Load fallback hotels JSON
# -------------------------------
def load_fallback_hotels(city: str):
    path = os.path.join(os.path.dirname(__file__), "..", "api", "fallback_hotels.json")
    path = os.path.abspath(path)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(city, [])
    except:
        return []


# -------------------------------
# /hotels Route — Fallback ONLY
# -------------------------------
@router.post("/hotels")
async def get_hotels(request: HotelRequest):
    dest = request.destination

    # -------------------------------
    # 1. Load fallback hotels
    # -------------------------------
    fallback_hotels = load_fallback_hotels(dest)
    if not fallback_hotels:
        return {"hotels": []}

    # Shuffle for variety
    random.shuffle(fallback_hotels)

    # -------------------------------
    # 2. Geocode city to get base coords
    # -------------------------------
    try:
        async with httpx.AsyncClient() as client:
            geo_url = f"https://nominatim.openstreetmap.org/search?format=json&q={dest}&limit=1"
            geo_res = await client.get(geo_url, timeout=10)
            geo_data = geo_res.json()

        if geo_data:
            city_lat = float(geo_data[0]["lat"])
            city_lon = float(geo_data[0]["lon"])
        else:
            # Default coordinates fallback if geocode fails
            city_lat, city_lon = 0.0, 0.0

    except:
        city_lat, city_lon = 0.0, 0.0

    # -------------------------------
    # 3. Build hotel objects with map coords
    # -------------------------------
    hotels = []

    for h in fallback_hotels:
        # generate random offset within ~1 km
        lat_offset = random.uniform(-0.01, 0.01)
        lon_offset = random.uniform(-0.01, 0.01)

        hotel_obj = {
            "name": h["name"],
            "rating": h.get("rating"),
            "price_per_night": h.get("price_per_night"),
            "address": h.get("address"),
            "latitude": city_lat + lat_offset,
            "longitude": city_lon + lon_offset,
        }

        # Add booking URLs only if present
        if "booking_urls" in h and isinstance(h["booking_urls"], dict):
            hotel_obj["booking_urls"] = h["booking_urls"]

        hotels.append(hotel_obj)

    # -------------------------------
    # ⭐ 4. AI Ranking
    # -------------------------------
    ranked = rank_hotels(
        hotels,
        request.budget,
        request.interests
    )

    return {"hotels": ranked}
