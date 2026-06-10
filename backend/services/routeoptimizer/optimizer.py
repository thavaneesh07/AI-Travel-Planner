import math
from typing import List, Dict, Any

class RouteOptimizer:
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0  # Earth radius in km
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    @staticmethod
    def optimize(activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid_acts = []
        invalid_acts = []
        for act in activities:
            if not act:
                continue
            coords = act.get("coordinates")
            if coords and isinstance(coords, dict) and coords.get("lat") is not None and coords.get("lng") is not None:
                valid_acts.append(act)
            else:
                invalid_acts.append(act)

        if len(valid_acts) <= 1:
            result = valid_acts + invalid_acts
            slots = ["morning", "afternoon", "evening"]
            for idx, act in enumerate(result):
                slot_idx = min(idx, len(slots) - 1)
                act["timeslot"] = slots[slot_idx]
                act["traveltonext"] = {
                    "mode": "walking",
                    "durationminutes": 0,
                    "distancekm": 0.0
                }
            return result

        ordered = []
        unvisited = valid_acts.copy()
        
        current = unvisited.pop(0)
        ordered.append(current)

        while unvisited:
            c_coords = current["coordinates"]
            best_idx = 0
            best_dist = float("inf")
            for idx, candidate in enumerate(unvisited):
                cand_coords = candidate["coordinates"]
                dist = RouteOptimizer.haversine_distance(
                    c_coords["lat"], c_coords["lng"],
                    cand_coords["lat"], cand_coords["lng"]
                )
                if dist < best_dist:
                    best_dist = dist
                    best_idx = idx
            
            next_node = unvisited.pop(best_idx)
            
            distance_km = best_dist
            mode = "walking" if distance_km < 1.5 else "driving"
            speed = 5.0 if mode == "walking" else 40.0
            duration_min = int((distance_km / speed) * 60)
            
            current["traveltonext"] = {
                "mode": mode,
                "durationminutes": max(5, duration_min),
                "distancekm": round(distance_km, 2)
            }
            
            ordered.append(next_node)
            current = next_node

        first_coords = ordered[0]["coordinates"]
        last_coords = ordered[-1]["coordinates"]
        return_dist = RouteOptimizer.haversine_distance(
            last_coords["lat"], last_coords["lng"],
            first_coords["lat"], first_coords["lng"]
        )
        return_mode = "walking" if return_dist < 1.5 else "driving"
        return_speed = 5.0 if return_mode == "walking" else 40.0
        return_duration = int((return_dist / return_speed) * 60)
        ordered[-1]["traveltonext"] = {
            "mode": return_mode,
            "durationminutes": max(5, return_duration),
            "distancekm": round(return_dist, 2)
        }

        slots = ["morning", "afternoon", "evening"]
        for idx, act in enumerate(ordered):
            slot_idx = min(idx, len(slots) - 1)
            act["timeslot"] = slots[slot_idx]

        return ordered + invalid_acts
