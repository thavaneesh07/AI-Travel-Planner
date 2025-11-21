# backend/routes/itinerary.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any

from itinerary.itinerary_generator import generate_itinerary

router = APIRouter()

# ----------- Request Model -----------

class ItineraryRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    interests: Optional[List[str]] = []
    budget: Optional[float] = 1000.0


# ----------- Route -----------

@router.post("/generate-itinerary")
def generate_itinerary_route(req: ItineraryRequest) -> Any:
    try:
        itinerary = generate_itinerary(
            destination=req.destination,
            start_date=req.start_date,
            end_date=req.end_date,
            interests=req.interests or [],
            budget=req.budget or 1000.0,
        )
        return {"status": "success", "itinerary": itinerary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
