## 📊 Progress Tracker – Phase 2 & 3

| Team Member | Role                 | Completed ✅                     | In Progress 🔄                   | Upcoming 🎯                | Overall Progress |
|------------|--------------------|---------------------------------|---------------------------------|----------------------------|-----------------|
| Brunda     | NLP / AI Engineer  | NLP parser development, dataset generation, evaluation (79% accuracy) | Support backend API integration, assist frontend testing | Phase 3 integration & refinement | 90% |
| Backend Dev| Backend Developer  | FastAPI setup, SQLite DB, basic endpoints | API integration with NLP parser, itinerary generator | Connect frontend, weather & POI APIs | 50% |
| Frontend   | Frontend Developer | React/Tailwind setup, mock UI, components scaffolding | Connect chatbot → `/api/parse` → `/api/itineraries` | Full dashboard + charts + timeline | 40% |

---

### 🗓 Visual Progress Overview

```mermaid
gantt
    title AI Travel Planner – Phase 2 & 3 Progress
    dateFormat  YYYY-MM-DD
    axisFormat  %b %d

    section Phase 1: MVP & Setup
    Completed               :done,    phase1, 2025-09-01, 2025-09-15

    section Phase 2: NLP + Data Layer
    Parser Dev              :done,    phase2_parser, 2025-09-16, 2025-10-10
    Dataset Evaluation      :done,    phase2_eval,   2025-10-01, 2025-10-10

    section Phase 3: Backend & Frontend
    Backend API Integration :active,  phase3_backend, 2025-10-11, 2025-10-25
    Itinerary Generator     :active,  phase3_itinerary, 2025-10-15, 2025-10-30
    Frontend Integration    :crit,    phase3_frontend, 2025-10-20, 2025-11-05
