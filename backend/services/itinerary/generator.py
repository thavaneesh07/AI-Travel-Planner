import json
import re
import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
from ...ai.ollamaclient import OllamaClient
from ...ai.promptregistry import PROMPTS
from ...services.maps.geocoding import GeocodingService
from ...services.maps.places import PlacesService
from ...api.osm_service import load_local_fallback_spots

class ItineraryGenerator:
    @staticmethod
    async def generate_itinerary(
        destination: str,
        country: str,
        start_date: str,
        end_date: str,
        interests: List[str],
        budget: float,
        currency: str,
        travelers: int,
        traveler_type: str
    ) -> Dict[str, Any]:
        
        prompt = PROMPTS["itinerarygeneration"].format(
            destination=destination,
            country=country,
            startdate=start_date,
            enddate=end_date,
            interests=interests,
            budget=budget,
            currency=currency,
            travelercount=travelers,
            travelertype=traveler_type
        )
        
        raw_res = OllamaClient.call_ollama(prompt)
        parsed = {}
        
        try:
            m = re.search(r"\{.*\}", raw_res, re.S)
            if m:
                parsed = json.loads(m.group(0))
        except Exception:
            pass

        days_list = parsed.get("days", [])
        if not days_list:
            days_list = await ItineraryGenerator._generate_fallback_days(
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                interests=interests,
                budget=budget,
                currency=currency
            )
        else:
            for day in days_list:
                for act in day.get("activities", []):
                    coords = act.get("coordinates")
                    if not coords or coords.get("lat") is None:
                        geo = await GeocodingService.geocode(f"{act['name']} in {destination}")
                        if geo:
                            act["coordinates"] = {"lat": geo["lat"], "lng": geo["lng"]}
                        else:
                            base_lat, base_lng = await ItineraryGenerator._get_destination_coords(destination)
                            act["coordinates"] = {
                                "lat": base_lat + random.uniform(-0.02, 0.02),
                                "lng": base_lng + random.uniform(-0.02, 0.02)
                            }
                    if act.get("estimatedcost") is None:
                        act["estimatedcost"] = 10.0
                    if act.get("currency") is None:
                        act["currency"] = currency
                    if act.get("estimateddurationminutes") is None:
                        act["estimateddurationminutes"] = 90

        for day in days_list:
            day_cost = sum([float(act.get("estimatedcost") or 0.0) for act in day.get("activities", [])])
            day["estimatedcost"] = round(day_cost, 2)

        return {
            "tripid": None,
            "destination": destination,
            "country": country,
            "startdate": start_date,
            "enddate": end_date,
            "travelercount": travelers,
            "travelertype": traveler_type,
            "interests": interests,
            "days": days_list
        }

    @staticmethod
    async def _get_destination_coords(destination: str) -> tuple:
        geo = await GeocodingService.geocode(destination)
        if geo:
            return geo["lat"], geo["lng"]
        
        seed_text = f"{destination}|center"
        seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16)
        rng = random.Random(seed)
        lat = 20 + rng.random() * 25
        lon = 60 + rng.random() * 60
        return float(lat), float(lon)

    @staticmethod
    async def _generate_fallback_days(
        destination: str,
        start_date: str,
        end_date: str,
        interests: List[str],
        budget: float,
        currency: str
    ) -> List[Dict[str, Any]]:
        
        try:
            sd = datetime.fromisoformat(start_date).date()
            ed = datetime.fromisoformat(end_date).date()
            days_count = max(1, (ed - sd).days + 1)
        except:
            sd = datetime.utcnow().date()
            days_count = 3

        base_lat, base_lng = await ItineraryGenerator._get_destination_coords(destination)

        places = await PlacesService.search_places(base_lat, base_lng, interests)
        if not places:
            spots = []
            for category in ["sightseeing", "food_experience", "relaxation"]:
                spots.extend(load_local_fallback_spots(destination, category))
            
            for s in spots:
                places.append({
                    "name": s["name"],
                    "coordinates": {
                        "lat": base_lat + random.uniform(-0.015, 0.015),
                        "lng": base_lng + random.uniform(-0.015, 0.015)
                    },
                    "category": "tourism.attraction",
                    "openinghours": None
                })

        if not places:
            for idx in range(10):
                places.append({
                    "name": f"Landmark {idx + 1} in {destination}",
                    "coordinates": {
                        "lat": base_lat + random.uniform(-0.01, 0.01),
                        "lng": base_lng + random.uniform(-0.01, 0.01)
                    },
                    "category": "tourism.attraction",
                    "openinghours": None
                })

        days = []
        place_idx = 0
        
        for i in range(days_count):
            day_date = (sd + timedelta(days=i)).isoformat()
            day_activities = []
            
            p_morning = places[place_idx % len(places)]
            day_activities.append({
                "name": p_morning["name"],
                "category": "attraction",
                "description": f"Explore the beautiful {p_morning['name']}.",
                "coordinates": p_morning["coordinates"],
                "estimateddurationminutes": 120,
                "estimatedcost": round(budget / days_count * 0.08, 2),
                "currency": currency,
                "openinghours": p_morning["openinghours"],
                "bookingnotes": None
            })
            place_idx += 1

            p_lunch = places[place_idx % len(places)]
            day_activities.append({
                "name": f"Local Restaurant near {p_lunch['name']}",
                "category": "restaurant",
                "description": "Stop by a cozy dining spot for lunch.",
                "coordinates": p_lunch["coordinates"],
                "estimateddurationminutes": 60,
                "estimatedcost": round(budget / days_count * 0.1, 2),
                "currency": currency,
                "openinghours": None,
                "bookingnotes": None
            })
            place_idx += 1

            p_afternoon = places[place_idx % len(places)]
            day_activities.append({
                "name": p_afternoon["name"],
                "category": "attraction",
                "description": f"Visit {p_afternoon['name']}.",
                "coordinates": p_afternoon["coordinates"],
                "estimateddurationminutes": 120,
                "estimatedcost": round(budget / days_count * 0.08, 2),
                "currency": currency,
                "openinghours": p_afternoon["openinghours"],
                "bookingnotes": None
            })
            place_idx += 1

            days.append({
                "day": i + 1,
                "date": day_date,
                "theme": f"Discovering {destination} Day {i + 1}",
                "activities": day_activities
            })

        return days

generate_itinerary = ItineraryGenerator.generate_itinerary
