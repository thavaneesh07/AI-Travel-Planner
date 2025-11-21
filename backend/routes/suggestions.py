# backend/routes/suggestions.py
# backend/routes/suggestions.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import random

router = APIRouter()

class SuggestionRequest(BaseModel):
    destination: Optional[str] = None
    budget: Optional[float] = 0.0
    total_estimated_cost: Optional[float] = 0.0
    interests: Optional[List[str]] = []
    weather_forecast: Optional[List[str]] = []


@router.post("/suggestions")
async def get_suggestions(request: SuggestionRequest):
    print("🪄 Incoming request:", request.model_dump())
    try:
        # 🌍 Basic data extraction
        destination = request.destination
        budget = request.budget
        spent = request.total_estimated_cost
        interests = request.interests or []
        weather = request.weather_forecast or []

        suggestions = []

        # 💸 Budget insight
        if spent > budget:
            suggestions.append(
                f"⚠️ You’re going over budget by ${spent - budget:.2f}. Try cheaper stays or transport options in {destination}."
            )
        elif spent < budget * 0.8:
            suggestions.append(
                f"🎉 You’re well within your budget! Consider upgrading hotels or adding a premium experience in {destination}."
            )
        else:
            suggestions.append(
                f"💰 Your spending aligns well with your planned budget for {destination}."
            )

        # 🌦️ Weather-based tip
        if any("rain" in w.lower() for w in weather):
            suggestions.append(
                "🌧 It might rain during your trip — pack an umbrella and plan some indoor activities."
            )
        elif any("sun" in w.lower() or "clear" in w.lower() for w in weather):
            suggestions.append(
                "☀️ Great weather ahead — plan outdoor adventures or sightseeing!"
            )

        # 🎨 Interest-based tips
        if "food" in [i.lower() for i in interests]:
            suggestions.append(
                f"🍽 Don’t miss trying local specialties in {destination} — search for top-rated restaurants nearby."
            )
        if "art" in [i.lower() for i in interests]:
            suggestions.append(
                f"🎨 Since you love art, check out local galleries or street murals in {destination}."
            )
        if "nature" in [i.lower() for i in interests]:
            suggestions.append(
                f"🌿 Explore nature trails or nearby parks around {destination} for peaceful experiences."
            )
        if "history" in [i.lower() for i in interests]:
            suggestions.append(
                f"🏛 Visit a local museum or heritage site — {destination} has a rich history worth seeing!"
            )

        # 🧠 Random travel wisdom
        wisdom = [
            "🧳 Pack light and keep essentials handy.",
            "💡 Learn a few local phrases — locals always appreciate it!",
            "🚶 Walk whenever possible — you’ll discover hidden gems.",
            "📸 Capture small moments, not just landmarks.",
        ]
        suggestions.append(random.choice(wisdom))

        return {"suggestions": suggestions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
