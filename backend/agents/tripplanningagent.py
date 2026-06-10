import json
from typing import Dict, Any, List
from ..ai.ollamaclient import OllamaClient
from ..ai.promptregistry import PROMPTS
from ..services.itinerary.generator import generate_itinerary
from ..services.routeoptimizer.optimizer import RouteOptimizer
from ..services.budget.budgetscorer import BudgetScorer
from ..services.weather.weatherservice import WeatherService

REQUIREDTRIPFIELDS = [
    "destination",
    "country",
    "startdate",
    "enddate",
    "travelercount",
    "travelertype",
    "budget",
    "currency",
    "interests"
]

class TripPlanningAgent:
    @staticmethod
    def get_missing_fields(entities: Dict[str, Any]) -> List[str]:
        missing = []
        for field in REQUIREDTRIPFIELDS:
            val = entities.get(field)
            if val is None or val == "" or val == []:
                missing.append(field)
        return missing

    @staticmethod
    async def handle_conversation(session_state: Dict[str, Any], new_entities: Dict[str, Any], message: str) -> Dict[str, Any]:
        if "entities" not in session_state:
            session_state["entities"] = {f: None for f in REQUIREDTRIPFIELDS}
            session_state["entities"]["interests"] = []

        # Merge and support corrections
        for k, v in new_entities.items():
            if v is not None and v != "" and v != []:
                session_state["entities"][k] = v

        # Missing required details
        missing = TripPlanningAgent.get_missing_fields(session_state["entities"])
        
        if missing:
            field_to_ask = missing[0]
            question_prompt = PROMPTS["followupquestion"].format(
                missing_fields=missing,
                current_state=json.dumps(session_state["entities"])
            )
            question = OllamaClient.call_ollama(question_prompt)
            if not question:
                friendly_names = {
                    "destination": "Where would you like to travel to?",
                    "country": "Which country is that destination located in?",
                    "startdate": "When do you plan to start your trip? (format YYYY-MM-DD)",
                    "enddate": "When will your trip end? (format YYYY-MM-DD)",
                    "travelercount": "How many travelers will be going?",
                    "travelertype": "What type of trip is it? (solo, couple, family, group)",
                    "budget": "What is your budget for the trip?",
                    "currency": "Which currency will you use? (USD, EUR, GBP, etc.)",
                    "interests": "What are your interests? (e.g. food, art, nature, history, relaxation)"
                }
                question = friendly_names.get(field_to_ask, f"Could you provide your {field_to_ask}?")

            return {
                "status": "needsmoreinfo",
                "missingfields": missing,
                "question": question,
                "planningstate": session_state
            }
        else:
            trip_data = await TripPlanningAgent.generate_trip(session_state["entities"])
            return {
                "status": "success",
                "trip": trip_data["itinerary"],
                "budget": trip_data["budget_info"],
                "routesummary": trip_data["route_summary"]
            }

    @staticmethod
    async def generate_trip(entities: Dict[str, Any]) -> Dict[str, Any]:
        destination = entities.get("destination")
        country = entities.get("country")
        start_date = entities.get("startdate")
        end_date = entities.get("enddate")
        interests = entities.get("interests", [])
        budget = float(entities.get("budget", 1000.0))
        currency = entities.get("currency", "USD")
        travelers = int(entities.get("travelercount", 1))
        traveler_type = entities.get("travelertype", "solo")

        # 1. Generate Itinerary
        raw_itinerary = await generate_itinerary(
            destination=destination,
            country=country,
            start_date=start_date,
            end_date=end_date,
            interests=interests,
            budget=budget,
            currency=currency,
            travelers=travelers,
            traveler_type=traveler_type
        )

        # 2. Heuristically Optimize Routes per day
        for day in raw_itinerary.get("days", []):
            activities = day.get("activities", [])
            day["activities"] = RouteOptimizer.optimize(activities)
            day["route"] = [{"lat": act["coordinates"]["lat"], "lng": act["coordinates"]["lng"], "label": act["name"]} for act in day["activities"]]

        # 3. Budget Scoring
        days_count = len(raw_itinerary.get("days", []))
        budget_info = BudgetScorer.score(
            budget=budget,
            currency=currency,
            days=days_count,
            travelers=travelers,
            destination=destination
        )

        # 4. Attach Weather
        lat, lng = destination_lat_lon_fallback(destination)
        for day in raw_itinerary.get("days", []):
            day_date = day.get("date")
            day["weather"] = await WeatherService.get_weather_for_date(destination, lat, lng, day_date)

        route_summary = {
            "total_distance_km": sum([day.get("route_distance_km", 0.0) for day in raw_itinerary.get("days", [])]),
            "optimized": True,
            "routing_method": "Heuristic nearest-neighbor with time windows"
        }

        return {
            "itinerary": raw_itinerary,
            "budget_info": budget_info,
            "route_summary": route_summary
        }

def destination_lat_lon_fallback(destination: str):
    import hashlib
    seed_text = f"{destination}|center"
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16)
    import random
    rng = random.Random(seed)
    lat = 20 + rng.random() * 25
    lon = 60 + rng.random() * 60
    return float(lat), float(lon)
