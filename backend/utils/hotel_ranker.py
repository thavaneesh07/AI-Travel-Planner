# backend/utils/hotel_ranker.py

import math

def normalize(value, min_val, max_val):
    """Normalize any value into 0–1 range safely."""
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)


def score_hotel(hotel, user_budget, interests=None):
    """
    Calculate a 0–100 score for a hotel.
    Uses:
      - rating (weight 40%)
      - price fit (weight 35%)
      - interest match (weight 25%)
    """
    rating = hotel.get("rating", 0)
    price = hotel.get("price_per_night", 0)

    # --- 📌 1. Rating Score (0–1)
    rating_score = normalize(rating, 3.0, 5.0)

    # --- 💸 2. Budget Fit Score (0–1)
    if user_budget <= 0:
        budget_score = 0.5
    else:
        if price > user_budget:
            # price above budget → penalty
            budget_score = max(0, 1 - (price - user_budget) / user_budget)
        else:
            # price below budget → reward
            budget_score = 1.0

    # --- 🎯 3. Interest Match Score (0–1)
    hotel_features = hotel.get("name", "").lower()
    interests = interests or []

    matches = 0
    for interest in interests:
        if interest.lower() in hotel_features:
            matches += 1

    interest_score = matches / len(interests) if interests else 0.5

    # --- 🎯 FINAL WEIGHTED SCORE (0–100)
    final_score = (
        rating_score * 0.40 +
        budget_score * 0.35 +
        interest_score * 0.25
    ) * 100

    return round(final_score, 2)


def rank_hotels(hotels, user_budget, interests=None):
    """Add score + explanation for each hotel, then return sorted list."""
    ranked = []

    for h in hotels:
        s = score_hotel(h, user_budget, interests)

        explanation = []

        # Explanation parts
        if h["rating"] >= 4.5:
            explanation.append("Excellent rating ⭐")
        elif h["rating"] >= 4.0:
            explanation.append("Good rating 👍")

        if h["price_per_night"] <= user_budget:
            explanation.append("Matches your budget 💸")
        else:
            explanation.append("Slightly above your budget")

        interest_text = (
            ", ".join(interests) if interests else "general preference"
        )
        explanation.append(f"Suitable for {interest_text}")

        h_with_score = {
            **h,
            "score": s,
            "reason": " | ".join(explanation),
        }
        ranked.append(h_with_score)

    # Sort highest → lowest
    ranked.sort(key=lambda x: x["score"], reverse=True)

    return ranked
