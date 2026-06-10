# AI Travel Planner - Technical Documentation

This document provides a comprehensive architectural and technical breakdown of the **AI Travel Planner** project, designed to be used as a reference script or fed into ChatGPT for interview preparation.

## 1. Project Synopsis
**AI Travel Planner** is an intelligent, full-stack web application that acts as a personal travel assistant. It leverages Natural Language Processing (NLP) to understand user requests, interfaces with an AI service (like Ollama) to dynamically generate personalized travel itineraries, fetches real-time weather, and presents the data through a rich, interactive, and responsive user interface.

## 2. Architecture & Tech Stack

### Backend (Python / FastAPI)
- **Framework**: **FastAPI** for high-performance, asynchronous REST APIs.
- **Validation**: **Pydantic** models (e.g., `ParseReq`, `PlanReq`) to validate incoming JSON requests.
- **ORM/Database**: **SQLAlchemy** connected to a SQLite (`travel_planner.db`) or PostgreSQL database. Models include `User`, `Trip`, `TripDay`, `Activity`, `SavedPlace`, and `ChatSession`.
- **AI/NLP Integration**: 
  - NLP parsing to extract entities (destination, dates, budget, interests).
  - Integrates with external LLM APIs (e.g., Ollama) to generate structured travel plans (`generate_travel_itinerary_json`).
- **External Services**:
  - **Open-Meteo API** (or similar) for weather forecasting, with robust fallback JSON data when offline.
  - **Geoapify/OSM** for geocoding and fetching localized Points of Interest (POIs).

### Frontend (React / Vite)
- **Framework**: **React 19** with **Vite** for fast HMR and optimized builds.
- **Styling**: **Tailwind CSS** coupled with **Framer Motion** for premium, smooth micro-animations and responsive layouts.
- **State Management**: **Zustand** for efficient, lightweight client-side state without the boilerplate of Redux.
- **Mapping**: **Leaflet** & **React-Leaflet** for plotting interactive maps of generated itineraries.
- **Data Visualization**: **Recharts** for visualizing budget breakdowns or travel stats.
- **HTTP Client**: **Axios** to communicate with the FastAPI backend.

## 3. Key Systems & Workflows

### 3.1. Natural Language Query Parsing (`/api/parse`)
When a user submits a query like _"Plan a 3-day trip to Tokyo for under $1500 focusing on food and anime"_, the system hits the `/api/parse` endpoint.
- **Mechanism**: The backend runs the text through an NLP engine (`nlp_parser.py`) which extracts structured parameters: `destination`, `start_date`, `end_date`, `budget`, and a list of `interests`.

### 3.2. Itinerary Generation Engine (`/api/plan`)
The core logic resides in `itinerary_generator.py`. 
1. **AI Call**: It attempts to query the LLM to get a structured JSON itinerary with activities mapped to `morning`, `afternoon`, and `evening`.
2. **Fallback Logic**: If the AI fails or hallucinates, it uses a deterministic fallback generator (`generate_activity_types`). It calculates a deterministic pseudo-center for the destination to ensure the map still renders points if geocoding fails.
3. **Budget Constraints**: The budget is divided proportionally across the days and time slots (`morning: 0.25, afternoon: 0.35, evening: 0.40`).
4. **Contextual Additions**: The engine automatically suggests nearby coffee shops for each slot using deterministic offsets.
5. **Modification API**: The `apply_itinerary_modification` function allows the user to dynamically edit specific slots (e.g., changing Tuesday morning from "Eiffel Tower" to "Louvre Museum").

### 3.3. Weather Service
The system normalizes weather data (`get_weather_forecast`). It handles various data structures returned by the Open-Meteo API (dict vs list) and normalizes it to a standard `{ temp, desc }` format. If the API rate limits, a fallback dataset is loaded.

### 3.4. Frontend View Management
The `App.jsx` uses a custom view-router approach based on local state (`currentView` switching between `planner`, `login`, `register`, and `saved-trips`). An `ErrorBoundary` wraps the entire application to gracefully handle UI crashes.

## 4. Notable Engineering Practices
- **Graceful Degradation**: The backend is heavily fortified with `try/except` blocks. If the LLM is down, it uses fallback local data. If the geocoding fails, it uses deterministic random coordinates. If weather fails, it uses historical fallback data. This ensures the UI never breaks.
- **Deterministic Randomness**: `itinerary_generator.py` uses `hashlib.sha256` and a seeded randomizer (`_seeded_rng`) to ensure that generating an itinerary for "Paris" on a specific date will reliably produce the same fallback coordinates, avoiding jumpy map markers on page reloads.
- **Component Segregation**: The frontend is properly modularized into `pages`, `components`, `hooks`, `services`, and `state`.

## 5. Potential Interview Talking Points
If asked about the project in an interview, you can highlight:
1. **How did you handle LLM hallucinations or downtime?**
   _Answer: I implemented a robust fallback system. If the AI response times out or returns malformed JSON, the backend seamlessly switches to a deterministic local POI generator that still respects the user's budget and timeframe._
2. **How is state managed on the frontend?**
   _Answer: I chose Zustand over Redux. It significantly reduces boilerplate and provides a very clean Hook-based API for sharing itinerary data across the mapping component, the sidebar, and the budget charts._
3. **How do you handle geocoding for unknown places?**
   _Answer: To prevent the map from crashing, I implemented a seeded pseudo-random coordinate generator. It hashes the destination name to pick a stable latitude/longitude on the globe, and adds micro-offsets for morning/afternoon/evening slots._

---
*Feel free to feed this document directly into ChatGPT and ask it to generate mock interview questions for a Full Stack / AI Engineering role based on this architecture.*
