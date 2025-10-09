from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(title="AI Travel Planner - Phase 1")

class ParseReq(BaseModel):
    message: str

class ItinCreateReq(BaseModel):
    destination: str
    start_date: str
    end_date: str
    budget: float
    user_profile: Optional[str] = "solo"
    interests: List[str] = []

@app.post("/api/parse")
def parse(req: ParseReq):
    # placeholder: will be replaced in Phase 2
    return {
        "destination": "Paris",
        "start_date": "2025-10-01",
        "end_date": "2025-10-07",
        "budget": 1500,
        "user_profile": "solo",
        "interests": ["history","food"]
    }

@app.post("/api/itineraries")
def create_itinerary(req: ItinCreateReq):
    itin_id = "ITINERARY_ID_" + uuid.uuid4().hex[:8]
    return {"itinerary_id": itin_id, "status":"completed", "days": [
        {"day":1,"date":req.start_date,
         "morning":"Check-in at budget hotel near Montmartre",
         "afternoon":"Visit Eiffel Tower & Seine River cruise",
         "evening":"Dinner at Le Bouillon Pigalle",
         "estimated_cost":120}
    ]}

@app.get("/api/itineraries/{itinerary_id}")
def get_itinerary(itinerary_id: str):
    return {"itinerary_id": itinerary_id, "destination":"Paris", "days":[
        {"day":1,"date":"2025-10-01",
         "morning":"Sample","afternoon":"Sample","evening":"Sample",
         "estimated_cost":100}
    ], "total_estimated_cost":100}

