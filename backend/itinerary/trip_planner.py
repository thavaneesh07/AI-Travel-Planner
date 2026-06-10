from ..itinerary.itinerary_generator import generate_itinerary
from ..itinerary.budget_scorer import BudgetScorer
from ..maps.route_optimizer import RouteOptimizer
from datetime import datetime

class TripPlannerAgent:
    @staticmethod
    def generate_trip(entities: dict):
        raw_itinerary = generate_itinerary(
            destination=entities.get("destination"),
            start_date=entities.get("start_date"),
            end_date=entities.get("end_date"),
            interests=entities.get("interests", []),
            budget=entities.get("budget", 1000)
        )

        # Post-processing: Routing & Budgeting
        for day in raw_itinerary.get("days", []):
            activities = [day.get("morning"), day.get("afternoon"), day.get("evening")]
            day["route"] = RouteOptimizer.optimize(activities)

        days_count = len(raw_itinerary.get("days", []))
        budget_info = BudgetScorer.score(
            budget=entities.get("budget", 1000),
            currency=entities.get("currency", "USD"),
            days=days_count,
            travelers=entities.get("traveler_count", 1)
        )

        return {"itinerary": raw_itinerary, "budget_info": budget_info}