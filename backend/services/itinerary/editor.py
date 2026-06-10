import json
import re
from typing import Dict, Any
from ...ai.ollamaclient import OllamaClient
from ...ai.promptregistry import PROMPTS
from ...services.routeoptimizer.optimizer import RouteOptimizer
from ...services.maps.geocoding import GeocodingService

class ItineraryEditor:
    @staticmethod
    async def parse_edit_query(message: str) -> Dict[str, Any]:
        prompt = PROMPTS["chateditparse"].format(message=message)
        res = OllamaClient.call_ollama(prompt)
        
        try:
            m = re.search(r"\{.*\}", res, re.S)
            if m:
                return json.loads(m.group(0))
        except:
            pass
        return {}

    @staticmethod
    async def apply_edit(itinerary: Dict[str, Any], operation: Dict[str, Any]) -> Dict[str, Any]:
        op = operation.get("operation")
        day_num = operation.get("day")
        timeslot = operation.get("timeslot", "morning")
        target = operation.get("target")

        if not op or not day_num:
            return itinerary

        days = itinerary.get("days", [])
        day_idx = int(day_num) - 1
        if day_idx < 0 or day_idx >= len(days):
            return itinerary

        target_day = days[day_idx]
        activities = target_day.get("activities", [])

        if op == "replaceactivity" and target:
            dest = itinerary.get("destination", "")
            geo = await GeocodingService.geocode(f"{target} in {dest}")
            new_act = {
                "name": target,
                "category": "attraction",
                "description": f"Visit the iconic {target}.",
                "coordinates": {"lat": geo.get("lat", 0.0), "lng": geo.get("lng", 0.0)},
                "estimateddurationminutes": 90,
                "estimatedcost": 15.00,
                "currency": itinerary.get("currency", "USD"),
                "openinghours": None,
                "bookingnotes": None,
                "timeslot": timeslot
            }
            
            replaced = False
            for idx, act in enumerate(activities):
                if act.get("timeslot") == timeslot:
                    activities[idx] = new_act
                    replaced = True
                    break
            if not replaced:
                activities.append(new_act)

        elif op == "addactivity" and target:
            dest = itinerary.get("destination", "")
            geo = await GeocodingService.geocode(f"{target} in {dest}")
            new_act = {
                "name": target,
                "category": "attraction",
                "description": f"Enjoy visiting {target}.",
                "coordinates": {"lat": geo.get("lat", 0.0), "lng": geo.get("lng", 0.0)},
                "estimateddurationminutes": 90,
                "estimatedcost": 15.00,
                "currency": itinerary.get("currency", "USD"),
                "openinghours": None,
                "bookingnotes": None,
                "timeslot": timeslot
            }
            activities.append(new_act)

        elif op == "removeactivity":
            target_day["activities"] = [act for act in activities if act.get("timeslot") != timeslot]

        target_day["activities"] = RouteOptimizer.optimize(target_day["activities"])
        target_day["route"] = [{"lat": act["coordinates"]["lat"], "lng": act["coordinates"]["lng"], "label": act["name"]} for act in target_day["activities"]]
        target_day["estimatedcost"] = round(sum([float(act.get("estimatedcost", 0.0)) for act in target_day["activities"]]), 2)
        
        itinerary["total_estimated_cost"] = round(sum([day.get("estimatedcost", 0.0) for day in days]), 2)

        return itinerary
