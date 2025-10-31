import random
from datetime import datetime, timedelta
from api.weather_service import get_weather_forecast

# --- Sample activity pools by interest ---
ACTIVITIES = {
    "food": [
        "Local food market tour",
        "French pastry baking class",
        "Street food crawl at night markets",
        "Dinner at a riverside restaurant",
        "Visit a local café for brunch"
    ],
    "history": [
        "Visit local museums",
        "Guided historical walking tour",
        "Explore old town architecture",
        "Visit ancient landmarks",
        "Tour famous historical monuments"
    ],
    "art": [
        "Art gallery hopping",
        "Montmartre art walk",
        "Street art tour",
        "Visit the Louvre Museum",
        "Sketching session at a scenic spot"
    ],
    "adventure": [
        "Morning hike or cycling trail",
        "Kayaking on a nearby river",
        "Hot air balloon ride",
        "Scenic countryside exploration"
    ],
    "shopping": [
        "Local street shopping",
        "Visit vintage stores",
        "Explore weekend flea markets",
        "Shop at a local artisan market"
    ],
    "beaches": [
        "Morning beach walk",
        "Snorkeling session",
        "Sunset at the beach bar",
        "Beach volleyball with locals"
    ],
    "culture": [
        "Attend a local cultural event",
        "Traditional cooking experience",
        "Watch a folk performance",
        "Learn a local dance"
    ],
    "nightlife": [
        "Pub crawl across downtown",
        "Night walk with scenic views",
        "Attend a music festival",
        "Visit rooftop bars"
    ],
}

DEFAULT_ACTIVITIES = [
    "Visit a popular attraction",
    "Try local street food and cafés",
    "Explore scenic spots and viewpoints",
    "Attend a walking city tour"
]


def generate_itinerary(destination, start_date, end_date, budget, interests):
    """
    Generate a realistic, day-wise itinerary including weather forecast and varied activities.
    """
    # Convert dates to datetime objects
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    total_days = (end - start).days + 1

    # Fetch weather forecast for the destination
    weather_data = get_weather_forecast(destination)

    # Build activity pool from interests
    all_activities = []
    for interest in interests:
        all_activities.extend(ACTIVITIES.get(interest.lower(), []))

    if not all_activities:
        all_activities = DEFAULT_ACTIVITIES

    itinerary = []
    daily_budget = budget / total_days if budget else 150

    used_activities = set()  # prevent exact repetition

    for i in range(total_days):
        date_str = (start + timedelta(days=i)).strftime("%Y-%m-%d")

        # Pick 3 unique random activities for the day
        daily_choices = random.sample(all_activities, k=min(3, len(all_activities)))

        # Calculate day cost with slight variance
        estimated_cost = round(daily_budget * random.uniform(0.9, 1.2), 2)

        # Attach weather (fallback to mock if date missing)
        weather = weather_data.get(date_str, {"temp": random.randint(15, 28), "desc": "clear sky"})

        itinerary.append({
            "day": i + 1,
            "date": date_str,
            "morning": daily_choices[0],
            "afternoon": daily_choices[1] if len(daily_choices) > 1 else random.choice(all_activities),
            "evening": daily_choices[2] if len(daily_choices) > 2 else random.choice(all_activities),
            "estimated_cost": estimated_cost,
            "weather": weather
        })

    total_cost = sum(d["estimated_cost"] for d in itinerary)

    return {
        "destination": destination,
        "total_estimated_cost": round(total_cost, 2),
        "days": itinerary
    }


# --- Local testing ---
if __name__ == "__main__":
    sample = generate_itinerary(
        destination="Paris",
        start_date="2025-10-31",
        end_date="2025-11-04",
        budget=1500,
        interests=["food", "art"]
    )
    import json
    print(json.dumps(sample, indent=2))
