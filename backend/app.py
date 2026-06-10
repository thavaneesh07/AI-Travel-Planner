from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Routers
from .routes import suggestions, hotels, chat

# Local modules
from .nlp.nlp_parser import parse_user_query
from .itinerary.itinerary_generator import generate_itinerary
from .api.weather_service import get_weather_forecast

app = FastAPI(title="AI Travel Planner - Phase 3")

# Include routes
app.include_router(suggestions.router, prefix="/api")
app.include_router(hotels.router, prefix="/api")
app.include_router(chat.router)  # Chat is not inside /api on purpose


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- MODELS ----------
class ParseReq(BaseModel):
    message: str


class PlanReq(BaseModel):
    message: str


# ---------- ENDPOINTS ----------
@app.post("/api/parse")
def parse(req: ParseReq):
    if not req.message:
        raise HTTPException(400, "Missing message")
    return parse_user_query(req.message)


@app.post("/api/plan")
def plan_trip(req: PlanReq):
    parsed = parse_user_query(req.message)

    if not parsed.get("destination"):
        raise HTTPException(422, "Destination not detected")

    itinerary = generate_itinerary(
        destination=parsed["destination"],
        start_date=parsed["start_date"],
        end_date=parsed["end_date"],
        interests=parsed.get("interests", []),
        budget=parsed.get("budget", 1000),
    )

    return {
        "parsed_query": parsed,
        "generated_itinerary": itinerary,
        "hotels": [],  # Filled later
    }


@app.get("/api/weather/{city}")
def get_weather(city: str):
    return {"city": city, "forecast": get_weather_forecast(city)}
