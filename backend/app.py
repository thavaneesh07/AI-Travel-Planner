from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from fastapi.middleware.cors import CORSMiddleware
from routes import suggestions,hotels




# ✅ Import local modules
from nlp.nlp_parser import parse_user_query
from itinerary.itinerary_generator import generate_itinerary   # <-- make sure file is inside backend/itinerary/
from api.weather_service import get_weather_forecast            # <-- make sure file is inside backend/api/

app = FastAPI(title="AI Travel Planner - Phase 3")
app.include_router(suggestions.router)
app.include_router(hotels.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or ["*"] for easier dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- Request Models ---
class ParseReq(BaseModel):
    message: str

class ItinCreateReq(BaseModel):
    destination: str
    start_date: str
    end_date: str
    budget: float
    user_profile: Optional[str] = "solo"
    interests: List[str] = []

# --- 1️⃣ NLP Parser Endpoint ---
@app.post("/api/parse")
def parse(req: ParseReq):
    """Parse user natural language message into structured travel details."""
    if not req.message:
        raise HTTPException(status_code=400, detail="Missing 'message' field")

    result = parse_user_query(req.message)
    if not result:
        raise HTTPException(status_code=422, detail="Could not extract data from message")
    return result


# --- 2️⃣ Create Itinerary ---
@app.post("/api/itineraries")
def create_itinerary(req: ItinCreateReq):
    """Generate a dynamic day-by-day itinerary using AI logic."""
    itinerary = generate_itinerary(
        destination=req.destination,
        start_date=req.start_date,
        end_date=req.end_date,
        budget=req.budget,
        interests=req.interests
    )
    return itinerary


# --- 3️⃣ Combined Planner (NLP + Itinerary) ---
class PlanReq(BaseModel):
    message: str

@app.post("/api/plan")
def plan_trip(req: PlanReq):
    """Combine NLP parsing + itinerary generation."""
    parsed = parse_user_query(req.message)

    if not parsed.get("destination"):
        return {"error": "Destination not detected. Please specify your destination."}

    itinerary = generate_itinerary(
        destination=parsed.get("destination"),
        start_date=parsed.get("start_date"),
        end_date=parsed.get("end_date"),
        budget=parsed.get("budget", 1000),
        interests=parsed.get("interests", [])
    )

    return {"parsed_query": parsed, "generated_itinerary": itinerary}


# --- 4️⃣ Weather API ---
@app.get("/api/weather/{city}")
def get_weather(city: str):
    """Fetch mock or live weather forecast for a city."""
    forecast = get_weather_forecast(city)
    return {"city": city, "forecast": forecast}


# --- 5️⃣ (Optional) Get Itinerary by ID ---
@app.get("/api/itineraries/{itinerary_id}")
def get_itinerary(itinerary_id: str):
    return {
        "itinerary_id": itinerary_id,
        "destination": "Paris",
        "days": [
            {
                "day": 1,
                "date": "2025-10-01",
                "morning": "Sample",
                "afternoon": "Sample",
                "evening": "Sample",
                "estimated_cost": 100,
            }
        ],
        "total_estimated_cost": 100,
    }
