# 🧭 AI Travel Planner – Phase 2 & 3 Team Plan (Updated)

**Team Size:** 3 members

**Current Status (as of now):**
- ✅ Phase 1: Requirements & MVP – Completed
- ✅ Phase 2: NLP + Data Layer – Completed by Brunda (accuracy: 79%)
- 🔜 Phase 3: Backend & Frontend Integration – In progress

---

## 👩‍💻 Brunda – AI / NLP Engineer

### 🎯 Primary Goal
Make the chatbot *understand* travel-related messages and convert them into structured placeholders to generate itineraries automatically.

---

## 🧩 Phase 2 — NLP + Data Layer ✅ (Completed)

### 1. NLP Environment Setup
- Installed: `spacy`, `dateparser`, `regex`, `pandas`
- Downloaded: `en_core_web_sm`
- Folder structure:
  ```
  /backend/nlp/
    ├── nlp_parser.py
    ├── evaluate_parser.py
    ├── evaluate_parser_detailed.py
    └── data/
  ```

### 2. NLP Parser Development
- Created `nlp_parser.py` with:
  - spaCy for NER (destination, locations)
  - Regex + dateparser for dates and budget
  - Keyword lists for `interests`, `accommodation`, `profile`
- Enhanced version includes trip duration, group size inference, and budget normalization.

### 3. Synthetic Dataset Generation
- Created using **Enhanced Synthetic Dataset Generator** and **Simple Query Paraphraser**.
- Output files:
  ```
  backend/nlp/data/sample_queries.json
  backend/nlp/data/sample_queries_augmented.json
  ```
- Dataset size: 900 examples (300 × 3 augmentations)

### 4. Parser Evaluation
- Evaluated using `evaluate_parser.py`
- Results:
  ```
  destination:    100%
  start_date:     38.67%
  end_date:       38.00%
  trip_duration:  42.00%
  budget:         100%
  user_profile:   100%
  group_size:     90.67%
  accommodation:  100%
  interests:      100%
  Overall Accuracy: 78.81%
  ```
- Logged mismatches in `parser_mismatches.csv` for date improvements (Phase 6 refinement).

### ✅ Completion Criteria (Met)
- NLP parser functional end-to-end
- Accuracy ≥ 75%
- Structured placeholders integrated and test-ready for backend API

---

## ⚙️ Phase 3 — Smart Itinerary Logic (In Progress)

### 🔹 Brunda (Support Role)
- Provide `parse_user_query()` to backend team
- Assist backend testing `/api/parse`
- Help verify chatbot → NLP → Itinerary flow after integration

### 🔹 Backend Developer

#### 🎯 Primary Goal
Build and maintain backend connecting NLP → itinerary generation → frontend APIs.

#### 1. Setup FastAPI Backend
**Files:**
```
/backend/
  ├── app.py
  ├── routers/
  ├── models/
  ├── database/
  └── nlp/
```

#### 2. Database Setup (SQLite + SQLAlchemy)
```python
class Itinerary(Base):
    id = Column(Integer, primary_key=True)
    destination = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    budget = Column(Integer)
    interests = Column(String)
```

#### 3. API Endpoints
| Endpoint | Method | Description |
|-----------|--------|-------------|
| `/api/parse` | POST | Calls Brunda's NLP parser |
| `/api/itineraries` | POST | Generates itinerary using placeholders |
| `/api/itineraries/{id}` | GET | Fetch itinerary by ID |

#### 4. Itinerary Generation
**File:** `/backend/itinerary_generator.py`
```python
def generate_itinerary(destination, start_date, end_date, budget, interests):
    # Generate placeholder day-by-day itinerary
```
- Includes morning/afternoon/evening plan + estimated cost per day

#### 5. Optional Integrations
- `/api/weather` using OpenWeather API
- `/api/places/search` for interest-based POIs

#### 6. Docker & CI/CD
- Create `Dockerfile` (Python 3.10 base)
- CI pipeline via `.github/workflows/backend.yml`
- Deploy to Render / Heroku

#### ✅ Completion Criteria
- All endpoints functional and tested
- Docker container runs backend
- CI pipeline green

---

### 🔹 Frontend Developer

#### 🎯 Primary Goal
Build a clean, responsive UI with chatbot interface and interactive visualizations.

#### 1. Setup React + Tailwind Environment
```bash
npx create-react-app frontend
cd frontend
npm install axios recharts react-leaflet framer-motion
```

#### 2. Chatbot UI Component
**File:** `/frontend/components/Chatbot.jsx`
- Textbox for user input
- Sends `POST /api/parse`
- Displays itinerary cards

#### 3. Visualizations
| Feature | Library | Component |
|----------|----------|------------|
| Interactive Map | Leaflet | `MapView.jsx` |
| Timeline | React timeline | `Timeline.jsx` |
| Budget Chart | Recharts | `BudgetChart.jsx` |
| Weather Forecast | Recharts / OpenWeather | `WeatherChart.jsx` |

#### 4. Dashboard
**File:** `/frontend/pages/Dashboard.jsx`
- Combine itinerary, charts, weather, and summary

#### ✅ Completion Criteria
- Chatbot → Itinerary → Visualization flow complete
- Responsive, minimal, Tailwind-styled UI

---

# 🔄 Parallel Development Plan (Phase 2 → 3)

| Role | Can Start Immediately? | Depends On | Notes |
|------|--------------------------|-------------|-------|
| Brunda (NLP) | ✅ Done | None | Completed and shared `parse_user_query()` |
| Backend Developer | ✅ Yes | Needs NLP output format | Can mock until NLP integrated |
| Frontend Developer | ✅ Yes | Needs API schema | Can use dummy JSON responses |

### API Contract Example
```json
// POST /api/parse response
{
  "destination": "Paris",
  "start_date": "2025-10-01",
  "end_date": "2025-10-07",
  "budget": 1500,
  "user_profile": "solo",
  "interests": ["history", "food"]
}

// POST /api/itineraries response
{
  "itinerary_id": "abc123",
  "days": [
    {
      "day": 1,
      "date": "2025-10-01",
      "morning": "Visit Louvre Museum",
      "afternoon": "Eiffel Tower & River Cruise",
      "evening": "Dinner near Montmartre",
      "estimated_cost": 120
    }
  ],
  "total_estimated_cost": 120
}
```

### Integration Flow
1. **Backend** imports Brunda’s parser:  
   ```python
   from nlp.nlp_parser import parse_user_query
   ```
2. **Frontend** connects chatbot to `/api/parse` → `/api/itineraries`.
3. Test locally before Dockerizing.

---

# ✅ Combined Acceptance Criteria (Phase 2 + 3)

| Requirement | Description |
|--------------|-------------|
| Chatbot Input | Understands queries like “Plan a solo trip to Paris Oct 1–7, budget 1500, interested in food and art.” |
| NLP Output | Extracts placeholders accurately (≥75%) |
| Backend | Generates structured day-wise itinerary |
| Database | Stores itineraries + activities |
| Frontend | Displays itinerary, map, charts, timeline |
| Integration | End-to-end flow working |
| Deployment | Docker + Cloud-hosted container |

---

# 🧩 Next Steps
- Backend developer begins integration (Phase 3 Step 1)
- Brunda supports API testing with sample queries
- Frontend developer prepares chatbot + mock visualizations
- Team sync for final integration demo

---

**📁 Commit Path:** `docs/phase2_phase3_team_plan.md`

> This file now serves as the single source of truth for Phases 2 and 3 progress, ownership, and API alignment.




