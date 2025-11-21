# backend/state.py

_trip_state = {
    "destination": None,
    "start_date": None,
    "end_date": None,
    "itinerary": [],
    "interests": [],
    "budget": 1000.0,
}

def get_trip():
    return _trip_state

def set_trip(data):
    global _trip_state
    _trip_state.update(data)
