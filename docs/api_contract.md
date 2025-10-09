# 🧠 AI Travel Planner – API Contract Specification
*Version 1.0 — For Phase 2 & 3 Development*

## 🌍 Overview
This document defines the **API request and response formats** for all services in the AI Travel Planner MVP.  
All endpoints use:
- **Base URL:** `http://127.0.0.1:8000/api/`
- **Content-Type:** `application/json`
- **Authentication:** none (for MVP)
- **Status Codes:**  
  - `200 OK` → success  
  - `400 Bad Request` → invalid input  
  - `404 Not Found` → missing resource  
  - `500 Internal Server Error` → unexpected error  

## 🔹 1. `/api/parse` — NLP Parsing Endpoint
**Purpose:** Takes a natural-language travel query and returns structured data placeholders.

**Method:** `POST`  
**URL:** `/api/parse`

### 🧾 Request Body:
```json
{ "message": "Plan a solo trip to Paris from October 1st to 7th 2025 with a budget of 1500 interested in history and food" }
```

### ✅ Response (Example):
```json
{
  "destination": "Paris",
  "start_date": "2025-10-01",
  "end_date": "2025-10-07",
  "budget": 1500,
  "user_profile": "solo",
  "interests": ["history", "food"]
}
```

## 🔹 2. `/api/itineraries` — Itinerary Generation Endpoint
**Purpose:** Generates a detailed multi-day itinerary using user preferences.

**Method:** `POST`  
**URL:** `/api/itineraries`

### 🧾 Request Body:
```json
{
  "destination": "Paris",
  "start_date": "2025-10-01",
  "end_date": "2025-10-07",
  "budget": 1500,
  "user_profile": "solo",
  "interests": ["history", "food"]
}
```

### ✅ Response (Example):
```json
{
  "itinerary_id": "ITIN_12345",
  "destination": "Paris",
  "days": [
    {
      "day": 1,
      "date": "2025-10-01",
      "morning": "Arrive and check into hotel near Montmartre",
      "afternoon": "Visit Eiffel Tower & enjoy Seine cruise",
      "evening": "Dinner at Le Bouillon Pigalle",
      "estimated_cost": 120
    },
    {
      "day": 2,
      "date": "2025-10-02",
      "morning": "Explore the Louvre Museum",
      "afternoon": "Lunch at local bistro, walk around Latin Quarter",
      "evening": "Attend a street music event",
      "estimated_cost": 110
    }
  ],
  "total_estimated_cost": 800,
  "status": "completed"
}
```

## 🔹 3. `/api/itineraries/{id}` — Fetch Specific Itinerary
**Purpose:** Retrieve a saved itinerary by ID.

**Method:** `GET`  
**URL:** `/api/itineraries/{id}`

### ✅ Response:
```json
{
  "itinerary_id": "ITIN_12345",
  "destination": "Paris",
  "days": [...],
  "total_estimated_cost": 800
}
```

## 🔹 4. `/api/weather` — Weather Forecast (optional)
**Purpose:** Returns 7-day forecast for a given destination.

**Method:** `GET`  
**URL:** `/api/weather?destination=Paris&start_date=2025-10-01`

### ✅ Response (Example):
```json
{
  "destination": "Paris",
  "forecast": [
    { "date": "2025-10-01", "temp": 20, "condition": "Cloudy" },
    { "date": "2025-10-02", "temp": 18, "condition": "Sunny" }
  ]
}
```

## 🔹 5. `/api/places/search` — Local Activities by Interest (optional)
**Purpose:** Return attractions or restaurants based on user interests.

**Method:** `GET`  
**URL:** `/api/places/search?destination=Paris&interest=food`

### ✅ Response (Example):
```json
{
  "destination": "Paris",
  "interest": "food",
  "results": [
    {
      "name": "Le Bouillon Pigalle",
      "category": "Restaurant",
      "rating": 4.5,
      "description": "Affordable French cuisine near Montmartre"
    },
    {
      "name": "Marché des Enfants Rouges",
      "category": "Market",
      "rating": 4.3,
      "description": "Historic covered market with diverse food stalls"
    }
  ]
}
```

## 📦 Data Models (Backend Reference)

### **Itinerary**
| Field | Type | Description |
|--------|------|-------------|
| id | string | unique ID |
| destination | string | travel destination |
| start_date | date | trip start |
| end_date | date | trip end |
| budget | integer | budget value |
| user_profile | string | solo/family/couple |
| interests | array[string] | list of interests |

### **ItineraryDay**
| Field | Type | Description |
|--------|------|-------------|
| itinerary_id | string | foreign key |
| day | integer | day number |
| date | date | exact date |
| morning | string | morning plan |
| afternoon | string | afternoon plan |
| evening | string | evening plan |
| estimated_cost | integer | optional cost |

## 🧩 Testing Strategy
| API | Testing Tool | Expected Result |
|------|----------------|----------------|
| `/api/parse` | pytest or Postman | Correctly parsed placeholders |
| `/api/itineraries` | Postman / Swagger | Returns multi-day itinerary |
| `/api/weather` | Mock test | Returns mock forecast |
| `/api/places/search` | Mock test | Returns list of attractions |

## ✅ Usage
- **Brunda (NLP):** build parser to match `/api/parse` schema  
- **Backend dev:** build endpoints & DB models as per contract  
- **Frontend dev:** connect UI components using these structures  
