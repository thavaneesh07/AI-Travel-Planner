import sys
from pathlib import Path
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.main import app

client = TestClient(app)

def test_parse_endpoint():
    res = client.post(
        "/api/parse",
        json={"message": "Going to Paris Oct 1 to Oct 7 2025, budget 1500, solo, history/food"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["destination"] == "Paris"
    assert data["budget"] == 1500

def test_create_itinerary():
    payload = {
        "message": "Plan a trip to Paris Oct 1 to Oct 7 2025, budget 1500, solo, history/food"
    }
    res = client.post("/api/plan", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "generated_itinerary" in data
    assert isinstance(data["generated_itinerary"]["days"], list)

def test_chatbot_with_context():
    payload = {
        "message": "What is my activity on Day 1 morning?",
        "sessionid": "test-session-123",
        "planningstate": {"entities": {}},
        "history": [
            {"role": "user", "text": "Can you show me my trip?"},
            {"role": "assistant", "text": "Sure, here is your trip details."}
        ],
        "itinerary": {
            "destination": "Paris",
            "days": [
                {
                    "day": 1,
                    "theme": "Museum Day",
                    "activities": [
                        {
                            "name": "Louvre Museum",
                            "timeslot": "morning",
                            "description": "Visit the famous art museum."
                        }
                    ]
                }
            ]
        }
    }
    res = client.post("/api/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "answer" in data
    assert "louvre" in data["answer"].lower()

def test_planning_session_country_reply():
    payload = {
        "message": "India",
        "sessionid": "test-session-456",
        "planningstate": {
            "entities": {
                "destination": "Manglore",
                "country": None,
                "startdate": "2026-10-01",
                "enddate": "2026-10-05",
                "budget": 1500,
                "currency": "USD",
                "travelercount": 1,
                "travelertype": "solo",
                "interests": ["beaches"]
            }
        }
    }
    res = client.post("/api/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["intent"] == "plantrip"
    assert "trip" in data
    assert data["trip"]["destination"] == "Manglore"
    assert data["trip"]["country"] == "India"
