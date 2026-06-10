import json
import re
from typing import Dict, Any
from ..api.ollama_service import _call_ollama

class TravelIntentEngine:
    REQUIRED_FIELDS = ["destination", "start_date", "end_date", "budget", "traveler_count"]

    @staticmethod
    def analyze(message: str, current_state: Dict[str, Any] = None) -> Dict[str, Any]:
        current_state = current_state or {}
        
        prompt = f"""
        You are a highly precise Travel Intent Engine. Analyze the user's message and determine the intent.
        Intents: plan_trip, modify_trip, travel_question, non_travel.
        
        Current known trip state:
        {json.dumps(current_state, indent=2)}
        
        User Message: "{message}"
        
        Output ONLY valid JSON matching this schema:
        {{
            "intent": "plan_trip|modify_trip|travel_question|non_travel",
            "confidence": 0.95,
            "entities": {{
                "destination": "string or null",
                "start_date": "YYYY-MM-DD or null",
                "end_date": "YYYY-MM-DD or null",
                "budget": "number or null",
                "currency": "string or null",
                "traveler_count": "number or null",
                "interests": ["string"]
            }},
            "missing_fields": ["array of missing required fields based on the current state"],
            "question": "If missing fields, ask a natural, friendly follow-up question here to get them."
        }}
        """
        
        raw = _call_ollama(prompt)
        return TravelIntentEngine._parse_json(raw)

    @staticmethod
    def _parse_json(raw: str) -> Dict[str, Any]:
        try:
            m = re.search(r"\{.*\}", raw, re.S)
            if m:
                return json.loads(m.group(0))
        except Exception as e:
            print(f"[IntentEngine] Parsing failed: {e}")
            
        return {"intent": "travel_question", "confidence": 0.0, "entities": {}, "missing_fields": []}