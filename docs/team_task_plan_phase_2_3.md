# 🧠 AI Travel Planner – Phase 2 & 3 Work Allocation

Team size: 3 members\
Duration: \~4–6 weeks

---

## 👩‍💻 Brunda – AI / NLP Engineer 

### 🎯 Primary Goal:

Make the chatbot *understand* travel-related user messages and convert them into structured placeholders to generate itineraries automatically.

---

### 🧩 Phase 2 — NLP + Data Layer

#### 1. Setup NLP Environment

- Install dependencies:
  ```bash
  pip install spacy dateparser regex pandas
  python -m spacy download en_core_web_sm
  ```
- Folder: `/backend/nlp/`
  - Create `nlp_parser.py`
  - Create `data/` subfolder for datasets

---

#### 2. Build NLP Parser

**File:** `/backend/nlp/nlp_parser.py`

**Modules to include:**

- Tokenization using spaCy
- Named Entity Recognition (location, dates, money)
- Regex for budget detection (`\$?\d+`)
- Date extraction using `dateparser`
- Interest extraction via keyword lists (`["food", "history", "adventure", ...]`)

**Expected function:**

```python
def parse_user_query(query: str) -> dict:
    """
    Extracts destination, dates, budget, profile, and interests from user input.
    """
    return {
        "destination": DESTINATION,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "budget": BUDGET,
        "user_profile": USER_PROFILE,
        "interests": INTERESTS
    }
```

---

#### 3. Create Synthetic Dataset

**File:** `/backend/nlp/sample_queries.json`

- 200–300 examples of user queries with structured outputs.
- Format:

```json
[
  {
    "query": "Plan a solo trip to Paris from October 1st to 7th, budget 1500, interested in food and history",
    "output": {
      "destination": "Paris",
      "start_date": "2025-10-01",
      "end_date": "2025-10-07",
      "budget": 1500,
      "user_profile": "solo",
      "interests": ["food", "history"]
    }
  }
]
```

---

#### 4. Evaluate NLP Parser

**File:** `/backend/nlp/evaluate_parser.ipynb`

- Load `sample_queries.json`
- Compare extracted vs expected fields
- Compute **precision, recall, and F1-score**
- Goal: ≥80% accuracy across fields

---

#### 5. Integrate with Backend

- Edit `app.py` `/api/parse` route to call:
  ```python
  from nlp.nlp_parser import parse_user_query
  ```
- Replace dummy data with actual parsed output.

---

#### ✅ Phase 2 Completion Criteria

- `nlp_parser.py` working end-to-end
- At least 80% accuracy on test dataset
- `/api/parse` returns structured placeholders from real text

---

### ⚙️ Phase 3 — Smart Itinerary Logic

#### 1. Extend Itinerary Builder

**File:** `/backend/itinerary_generator.py`

- Function:
  ```python
  def generate_itinerary(destination, start_date, end_date, budget, interests):
  ```
- Auto-split days → morning/afternoon/evening slots
- Placeholder logic for activities
- Estimate cost per activity and total

---

#### 2. Add Weather Integration (optional)

**File:** `/backend/api/weather.py`

- Use OpenWeather API (mock or free API key)
- Connect to `/api/weather` endpoint

---

#### 3. Testing

- Add pytest tests for `nlp_parser.py` and `itinerary_generator.py`

#### ✅ Phase 3 Completion Criteria

- `/api/itineraries` generates full day-by-day itineraries
- Weather data optional but structured
- NLP + itinerary fully connected

---

## ⚙️ Member 2 – Backend Developer

### 🎯 Primary Goal:

Build and maintain the backend that connects NLP → itinerary generation → frontend APIs.

---

### 🧩 Phase 2 — Backend Foundation

#### 1. Organize Project Structure

**Folders:**

```
/backend/
  app.py
  /routers/
  /models/
  /database/
  /nlp/
```

---

#### 2. Setup Database (SQLite / SQLAlchemy)

**File:** `/backend/database/models.py`

```python
class Itinerary(Base):
    id = Column(Integer, primary_key=True)
    destination = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    budget = Column(Integer)
    interests = Column(String)
```

**File:** `/backend/database/crud.py`

- CRUD methods for creating and fetching itineraries.

---

#### 3. Create API Routes

**Folder:** `/backend/routers/`

- `/api/parse` → connects to Brunda’s NLP parser
- `/api/itineraries` → creates itinerary
- `/api/itineraries/{id}` → fetch itinerary by ID

---

#### 4. Testing

- Add `pytest` for endpoints
- Example test:

```python
def test_parse_endpoint(client):
    response = client.post("/api/parse", json={"message": "Trip to Paris"})
    assert response.status_code == 200
```

---

#### ✅ Phase 2 Completion Criteria

- Working DB and endpoints
- Can receive NLP output and save itineraries

---

### ⚙️ Phase 3 — API Expansion + Deployment

#### 1. Extend Itinerary API

- Integrate with `itinerary_generator.py`
- Store per-day activity data in DB

#### 2. Add Weather & Places Endpoints

- `/api/weather` — pulls forecast
- `/api/places/search` — returns activities by interest

#### 3. Docker Setup

**File:** `Dockerfile`

- Base image: `python:3.10`
- Copy backend, install deps, expose port 8000

#### 4. CI/CD

**File:** `.github/workflows/backend.yml`

- Run tests on push
- Build and deploy to cloud (Render/Heroku)

#### ✅ Phase 3 Completion Criteria

- All endpoints functional
- Deployed Docker container working
- CI pipeline green

---

## 💻 Member 3 – Frontend Developer

### 🎯 Primary Goal:

Design and build a clean, responsive UI with chatbot interaction and travel visualizations.

---

### 🧩 Phase 2 — Frontend Foundation

#### 1. Setup React + Tailwind

```bash
npx create-react-app frontend
cd frontend
npm install axios recharts react-leaflet framer-motion
```

**Files:**

```
/frontend/
  /components/
  /pages/
  /services/
```

---

#### 2. Create Chatbot UI

**File:** `/frontend/components/Chatbot.jsx`

- Text input for user queries
- Send message → `POST /api/parse`
- Display structured output

---

#### 3. Display Basic Itinerary

**File:** `/frontend/pages/ItineraryPage.jsx`

- Fetch `/api/itineraries`
- Display each day in a simple card

---

#### ✅ Phase 2 Completion Criteria

- Chatbot sends queries and displays parsed output
- Itinerary page fetches mock itinerary

---

### ⚙️ Phase 3 — Visualizations & Integration

#### 1. Interactive Map

**Component:** `/frontend/components/MapView.jsx`

- Display markers for key activities

#### 2. Timeline View

**Component:** `/frontend/components/Timeline.jsx`

- Show day-wise itinerary (Morning → Evening)

#### 3. Budget Chart

**Component:** `/frontend/components/BudgetChart.jsx`

- Pie or Bar chart via Recharts
- Input: itinerary cost breakdown

#### 4. Weather Chart

**Component:** `/frontend/components/WeatherChart.jsx`

- Connect to `/api/weather`

#### 5. Trip Dashboard

**Page:** `/frontend/pages/Dashboard.jsx`

- Combine all visuals + trip summary

---

#### ✅ Phase 3 Completion Criteria

- Fully functional UI (chatbot → itinerary → visuals)
- All charts/maps rendering live data
- Responsive & styled with Tailwind

---

# 📦 Integration Plan

| Order | Action                                                 | Owner             |
| ----- | ------------------------------------------------------ | ----------------- |
| 1     | Brunda finalizes `nlp_parser.py`                       | Brunda            |
| 2     | Backend connects parser output to itinerary builder    | Member 2          |
| 3     | Frontend connects to `/api/parse` + `/api/itineraries` | Member 3          |
| 4     | All test locally                                       | All               |
| 5     | Merge + Dockerize                                      | Member 2          |
| 6     | UI refinement + documentation                          | Member 3 & Brunda |

---

# ✅ Acceptance Criteria (Phase 2 + 3 Combined)

| Requirement   | Description                                                                                            |
| ------------- | ------------------------------------------------------------------------------------------------------ |
| Chatbot Input | Understands messages like “Plan a solo trip to Paris Oct 1–7, budget 1500, interested in food and art” |
| NLP Output    | Extracts correct placeholders                                                                          |
| Backend       | Generates structured day-wise itinerary                                                                |
| Database      | Stores itineraries + activities                                                                        |
| Frontend      | Displays itinerary, map, charts, timeline                                                              |
| Integration   | End-to-end flow from text → visualization                                                              |
| Deployment    | Docker container runs backend + frontend                                                               |

