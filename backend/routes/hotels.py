# backend/routes/hotels.py
from fastapi import APIRouter
from pydantic import BaseModel
import httpx
import random
from utils.hotel_ranker import rank_hotels   # ✅ Correct import

router = APIRouter()

class HotelRequest(BaseModel):
    destination: str
    budget: float
    interests: list = []

@router.post("/hotels")
async def get_hotels(request: HotelRequest):
    dest = request.destination

    hotels = [
        {
            "name": f"{dest} Grand Palace Hotel",
            "rating": 4.6,
            "price_per_night": 120,
            "address": f"Central area, {dest}"
        },
        {
            "name": f"{dest} Comfort Suites",
            "rating": 4.2,
            "price_per_night": 90,
            "address": f"Near main station, {dest}"
        },
        {
            "name": f"{dest} Budget Inn",
            "rating": 3.9,
            "price_per_night": 60,
            "address": f"Affordable zone, {dest}"
        },
    ]

    async with httpx.AsyncClient() as client:
        city_url = f"https://nominatim.openstreetmap.org/search?format=json&q={dest}"
        city_response = await client.get(city_url, timeout=10)
        city_data = city_response.json()

        if city_data:
            city_lat = float(city_data[0]["lat"])
            city_lon = float(city_data[0]["lon"])
        else:
            city_lat, city_lon = 35.6764, 139.6500

        # Geocode each hotel
        for hotel in hotels:
            query = f"{hotel['name']}, {dest}"
            url = f"https://nominatim.openstreetmap.org/search?format=json&q={query}"

            try:
                geores = await client.get(url, timeout=10)
                data = geores.json()

                if data:
                    hotel["latitude"] = float(data[0]["lat"])
                    hotel["longitude"] = float(data[0]["lon"])
                else:
                    hotel["latitude"] = city_lat + random.uniform(-0.01, 0.01)
                    hotel["longitude"] = city_lon + random.uniform(-0.01, 0.01)

            except:
                hotel["latitude"] = city_lat + random.uniform(-0.01, 0.01)
                hotel["longitude"] = city_lon + random.uniform(-0.01, 0.01)

    # ⭐ AI-Powered Ranking (score + explanation + sorting)
    ranked_hotels = rank_hotels(
        hotels,
        request.budget,
        request.interests
    )

    return {"hotels": ranked_hotels}
