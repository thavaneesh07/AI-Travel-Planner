import os
import json
from typing import Dict, Any
import redis

# In-memory fallback if Redis is not configured
_SESSIONS = {}

class ConversationManager:
    _redis_client = None
    
    @classmethod
    def _get_redis(cls):
        if cls._redis_client is None:
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                try:
                    cls._redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
                except Exception as e:
                    print(f"[Redis connection error]: {e}")
        return cls._redis_client
    
    @staticmethod
    def get_state(session_id: str) -> Dict[str, Any]:
        r = ConversationManager._get_redis()
        if r:
            try:
                data = r.get(f"session:{session_id}")
                if data: return json.loads(data)
            except: pass
            
        return _SESSIONS.get(session_id, {"entities": {}})

    @staticmethod
    def update_state(session_id: str, new_entities: Dict[str, Any]) -> Dict[str, Any]:
        state = ConversationManager.get_state(session_id)
        if not new_entities:
            return state
            
        for k, v in new_entities.items():
            if v is not None and v != "":
                state["entities"][k] = v
                
        r = ConversationManager._get_redis()
        if r:
            try:
                r.setex(f"session:{session_id}", 86400, json.dumps(state)) # Expire in 24h
            except: pass
            
        _SESSIONS[session_id] = state
        return state

    @staticmethod
    def get_missing_fields(state: Dict[str, Any]) -> list:
        required = ["destination", "start_date", "end_date", "budget", "traveler_count"]
        entities = state.get("entities", {})
        return [field for field in required if not entities.get(field)]