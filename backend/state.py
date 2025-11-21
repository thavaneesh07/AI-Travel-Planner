# backend/state.py
"""
Tiny in-memory single-user state used by itinerary generator while developing.
You can replace with a DB or file-based persistence later.
"""
_state = {
    "itinerary": None,
    "budget": None,
    "destination": None,
}

def get_trip():
    return _state

def set_trip(trip: dict):
    _state.update(trip)
    return _state
