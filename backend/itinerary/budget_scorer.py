class BudgetScorer:
    @staticmethod
    def score(budget: float, currency: str, days: int, travelers: int) -> dict:
        try:
            daily_per_person = float(budget) / max(1, days) / max(1, travelers)
        except Exception:
            daily_per_person = 0

        comfort = "Budget"
        if daily_per_person > 150: comfort = "Moderate"
        if daily_per_person > 350: comfort = "Luxury"

        return {
            "score": round(min(10.0, daily_per_person / 30.0), 1),
            "comfort_level": comfort,
            "daily_budget_per_person": round(daily_per_person, 2),
            "allocation": {
                "accommodation": round(budget * 0.4, 2),
                "food": round(budget * 0.25, 2),
                "transportation": round(budget * 0.15, 2),
                "activities": round(budget * 0.15, 2),
                "emergency_buffer": round(budget * 0.05, 2)
            }
        }