import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.main import app

client = TestClient(app)

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
print("Status Code:", res.status_code)
print("Response JSON:", res.json())
