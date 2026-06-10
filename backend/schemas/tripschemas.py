from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ActivitySchema(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    coordinates: Dict[str, float]
    estimateddurationminutes: Optional[int] = 90
    estimatedcost: Optional[float] = 0.0
    currency: Optional[str] = "USD"
    openinghours: Optional[str] = None
    bookingnotes: Optional[str] = None

class TripUpdateDayRequest(BaseModel):
    tripid: int
    day: int
    activities: List[ActivitySchema]
