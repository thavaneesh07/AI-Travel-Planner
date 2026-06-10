from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import re

from ..ai.intent_engine import TravelIntentEngine
from ..state.conversation_manager import ConversationManager
from ..agents.travel_assistant import TravelAssistantAgent
from ..agents.trip_planner import TripPlannerAgent

router = APIRouter()

class GenerateRequest(BaseModel):
    session_id: str
    message: str
    history: Optional[List[Dict[str, str]]] = []

@router.post("/generate")
def generate_endpoint(request: GenerateRequest):
    try:
        state = ConversationManager.get_state(request.session_id)
        analysis = TravelIntentEngine.analyze(request.message, state)
        intent = analysis.get("intent", "travel_question")

        if intent == "non_travel":
            return {
                "status": "success",
                "intent": intent,
                "answer": "I am an AI Travel Assistant. I can help you plan trips, discover destinations, and answer travel-related logistics. How can I help with your travels today?"
            }

        if intent == "travel_question":
            answer = TravelAssistantAgent.answer(request.message, request.history)
            return {"status": "success", "intent": intent, "answer": answer}

        if intent == "plan_trip":
            updated_state = ConversationManager.update_state(request.session_id, analysis.get("entities", {}))
            missing = ConversationManager.get_missing_fields(updated_state)

            if missing:
                fallback_q = f"Could you tell me a bit more? I still need to know: {', '.join(missing)}."
                question = analysis.get("question") or fallback_q
                return {
                    "status": "needs_more_info",
                    "intent": intent,
                    "missing_fields": missing,
                    "question": question
                }
            else:
                trip_data = TripPlannerAgent.generate_trip(updated_state["entities"])
                return {"status": "success", "intent": intent, "trip": trip_data}

        if intent == "modify_trip":
            from ..api.ollama_service import _call_ollama
            from ..state import get_trip, set_trip
            from ..itinerary.itinerary_generator import apply_itinerary_modification
            
            prompt = f"User wants to modify their itinerary. Extract the change as JSON. User: '{request.message}'. Format exactly like this: {{ \"day1\": {{ \"morning\": \"New Place Name\" }} }}"
            raw = _call_ollama(prompt)
            changes = {}
            try:
                m = re.search(r"\{.*\}", raw, re.S)
                if m: changes = json.loads(m.group(0))
            except: pass
            
            trip = get_trip()
            if trip and trip.get("itinerary") and changes:
                updated_itinerary = apply_itinerary_modification(trip["itinerary"], changes)
                trip["itinerary"] = updated_itinerary
                set_trip(trip)
                return {
                    "status": "success", 
                    "intent": intent, 
                    "answer": "I have successfully updated your itinerary.", 
                    "trip": {"itinerary": updated_itinerary}
                }
            return {"status": "success", "intent": intent, "answer": "I couldn't process the exact modification from your request. Could you specify which day and time slot to change (e.g., 'Change day 2 morning to the Louvre')?"}

        return {"status": "error", "message": "Unknown intent."}

    except Exception as e:
        print(f"[Generate API Error]: {e}")
        return {"status": "error", "message": "An internal error occurred."}