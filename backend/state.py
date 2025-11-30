"""
Tiny in-memory single-user state used by itinerary generator & chat assistant.
Stores itinerary, preferences, chat history and allows updates.
"""

_state = {
    "destination": None,
    "start_date": None,
    "end_date": None,
    "budget": None,
    "interests": [],
    "itinerary": None,
    "chat_history": [],     # NEW: used by ChatPanel -> postChat
}


def get_trip():
    """Return the entire state."""
    return _state


def set_trip(trip: dict):
    """Update state with new data (partial updates allowed)."""
    _state.update(trip)
    return _state


def save_chat_message(role: str, text: str):
    """
    Save a chat message (assistant or user).
    ChatPanel will call this indirectly through the /chat API.
    """
    _state.setdefault("chat_history", [])
    _state["chat_history"].append({"role": role, "text": text})


def clear_itinerary():
    """Reset itinerary only — used when user changes destination."""
    _state["itinerary"] = None


def update_itinerary(new_itinerary: dict):
    """
    Replace only the itinerary section.
    Chatbot uses this when user says:
    'Change my day 2 morning to Eiffel Tower'
    """
    _state["itinerary"] = new_itinerary
    return _state
