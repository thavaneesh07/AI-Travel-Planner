import math
from .geoapify_client import GeoapifyClient

class RouteOptimizer:
    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        R = 6371
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    @staticmethod
    def optimize(activities: list) -> list:
        valid_activities = [a for a in activities if a and isinstance(a, dict) and a.get("lat") is not None and a.get("lon") is not None]
        if len(valid_activities) <= 1:
            return valid_activities
            
        # Obtain distances via Geoapify Routing Matrix API
        matrix = GeoapifyClient.get_route_matrix(valid_activities, valid_activities)
        
        optimized = []
        unvisited = valid_activities.copy()
        
        # Begin with chronologically first activity
        current = unvisited.pop(0)
        optimized.append(current)
        
        while unvisited:
            current_idx = valid_activities.index(current)
            next_node = None
            
            if matrix and len(matrix) > current_idx:
                distances = matrix[current_idx]
                best_dist = float('inf')
                for candidate in unvisited:
                    cand_idx = valid_activities.index(candidate)
                    if len(distances) > cand_idx and distances[cand_idx].get("distance", float('inf')) < best_dist:
                        best_dist = distances[cand_idx]["distance"]
                        next_node = candidate
            
            if not next_node:
                next_node = min(unvisited, key=lambda x: RouteOptimizer.haversine_distance(
                    current["lat"], current["lon"], x["lat"], x["lon"]
                ))
            
            unvisited.remove(next_node)
            optimized.append(next_node)
            current = next_node

        return optimized