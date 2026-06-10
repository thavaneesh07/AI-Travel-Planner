from typing import Dict, Any, List
import logging

logger = logging.getLogger("budget_scorer")

BUDGETALLOCATIONRATIOS = {
    "accommodation": 0.35,
    "food": 0.20,
    "transportation": 0.15,
    "activities": 0.20,
    "emergencybuffer": 0.10
}

# Average daily cost estimate per destination in USD
DESTINATION_COST_ESTIMATES = {
    "tokyo": 180.0,
    "paris": 220.0,
    "london": 230.0,
    "new york": 250.0,
    "goa": 70.0,
    "bali": 80.0,
    "rome": 170.0,
    "dubai": 210.0,
    "sydney": 190.0,
    "switzerland": 260.0
}

EXCHANGE_RATES_TO_1_USD = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.78,
    "INR": 83.5,
    "JPY": 156.0,
    "CAD": 1.37,
    "AUD": 1.50,
    "CHF": 0.89,
    "CNY": 7.25,
    "SGD": 1.35,
    "NZD": 1.63,
    "KRW": 1375.0,
    "AED": 3.67,
    "ZAR": 18.5,
    "RUB": 89.0,
    "TRY": 32.5,
    "BRL": 5.3,
    "HKD": 7.8,
    "MXN": 18.2,
    "DKK": 6.9,
    "PLN": 4.0,
    "TWD": 32.3,
    "THB": 36.5,
    "SEK": 10.5,
    "NOK": 10.6,
    "MYR": 4.70,
    "IDR": 16000.0,
    "PHP": 58.5,
    "VND": 25400.0,
    "ILS": 3.75,
}

class BudgetScorer:
    @staticmethod
    def score(budget: float, currency: str, days: int, travelers: int, destination: str) -> Dict[str, Any]:
        dest_key = destination.lower().strip()
        daily_cost_estimate = 120.0  # Default fallback
        
        for k, v in DESTINATION_COST_ESTIMATES.items():
            if k in dest_key:
                daily_cost_estimate = v
                break

        total_days = max(1, days)
        total_travelers = max(1, travelers)
        daily_budget = budget / total_days
        daily_budget_per_person = daily_budget / total_travelers

        # Convert daily budget per person to USD for accurate scoring
        curr_upper = currency.upper().strip()
        rate = EXCHANGE_RATES_TO_1_USD.get(curr_upper, 1.0)
        daily_budget_per_person_usd = daily_budget_per_person / rate

        # Score calculation: 1.0 ratio = 5.0 score, 2.0 ratio = 10.0 score
        base_score = (daily_budget_per_person_usd / daily_cost_estimate) * 5.0
        score = round(min(10.0, max(0.1, base_score)), 1)

        # Comfort level
        if score >= 8.0:
            comfort_level = "Comfortable"
        elif score >= 5.0:
            comfort_level = "Moderate"
        elif score >= 3.0:
            comfort_level = "Budget"
        else:
            comfort_level = "Very Tight"

        # Allocation
        allocations = {}
        for key, ratio in BUDGETALLOCATIONRATIOS.items():
            allocations[key] = round(budget * ratio, 2)

        # Warnings
        warnings = []
        if comfort_level == "Very Tight":
            warnings.append(f"Your daily budget ({currency} {daily_budget_per_person:.2f}) is very tight for {destination}. Consider increasing your budget.")
        elif comfort_level == "Budget":
            warnings.append(f"Budget accommodation and dining choices will be necessary for this trip in {destination}.")
        
        if daily_budget_per_person < (daily_cost_estimate * 0.4):
            warnings.append("Accommodation budget may be tight for central hotels.")

        return {
            "score": score,
            "comfortlevel": comfort_level,
            "dailybudget": round(daily_budget, 2),
            "currency": currency,
            "tripdurationdays": total_days,
            "allocation": allocations,
            "warnings": warnings
        }
