import sys
from pathlib import Path

# Ensure 'backend' folder is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent  # points to 'backend'
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Now we can safely import app
from app import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_parse_endpoint():
    res = client.post(
        "/api/parse",
        json={"message":"Going to Paris Oct 1 to Oct 7 2025, budget 1500, solo, history/food"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["destination"] == "Paris"
    assert data["budget"] == 1500

def test_create_itinerary():
    payload = {
        "destination":"Paris",
        "start_date":"2025-10-01",
        "end_date":"2025-10-07",
        "budget":1500,
        "interests":["history","food"]
    }
    res = client.post("/api/itineraries", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "itinerary_id" in data
    assert isinstance(data["days"], list)
