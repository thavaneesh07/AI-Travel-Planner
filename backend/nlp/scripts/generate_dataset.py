import json
import random
from datetime import datetime, timedelta

# --- Define random data pools ---
destinations = ["Paris", "Tokyo", "Bali", "New York", "London", "Rome", "Sydney", "Dubai", "Bangkok", "Cape Town"]
profiles = ["solo", "couple", "family", "friends"]
accommodations = ["hotel", "Airbnb", "hostel", "resort", "villa"]
interests_pool = [
    "food", "art", "history", "adventure", "shopping", "beaches",
    "hiking", "culture", "nightlife", "photography", "relaxation", "wildlife"
]

# --- Generate random travel dates ---
def random_dates():
    start = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 300))
    duration = random.randint(3, 10)
    end = start + timedelta(days=duration)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"), duration

# --- Group size based on profile ---
def group_size(profile):
    if profile == "solo":
        return 1
    elif profile == "couple":
        return 2
    elif profile == "family":
        return random.randint(3, 5)
    else:  # friends
        return random.randint(2, 6)

# --- Generate one synthetic query ---
def generate_query():
    destination = random.choice(destinations)
    start_date, end_date, duration = random_dates()
    budget = random.choice([800, 1200, 1500, 2000, 2500, 3000, 5000])
    profile = random.choice(profiles)
    people = group_size(profile)
    accommodation = random.choice(accommodations)
    interests = random.sample(interests_pool, k=random.randint(1, 3))

    # Create natural-sounding query
    query_templates = [
        f"Plan a {profile} trip to {destination} from {start_date} to {end_date} staying in a {accommodation}, budget ${budget}, interested in {', '.join(interests)}.",
        f"{profile.capitalize()} vacation to {destination} ({start_date}–{end_date}) with ${budget} for {people} people, prefer {accommodation}, focusing on {', '.join(interests)}.",
        f"Looking for a {duration}-day {profile} getaway to {destination}, around ${budget}, staying at a {accommodation}, mainly for {', '.join(interests)}."
    ]
    query = random.choice(query_templates)

    # Define output format
    output = {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "trip_duration": duration,
        "budget": budget,
        "user_profile": profile,
        "group_size": people,
        "accommodation": accommodation,
        "interests": interests
    }

    return {"query": query, "output": output}

# --- Generate dataset ---
def main(n=300):
    data = [generate_query() for _ in range(n)]
    with open("backend/nlp/data/sample_queries.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Generated {n} enhanced queries in backend/nlp/data/sample_queries.json")

if __name__ == "__main__":
    main(300)
