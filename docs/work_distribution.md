# AI Travel Planner – Phase 2 Work Distribution & Parallel Development Plan

Excellent question — and it shows you’re thinking like a **real project lead** 👏

Here’s the best way to handle it:

You **don’t** need to do everything sequentially; you can **parallelize** a lot of the work **if you define clear interfaces (APIs + data formats)** early.

---

## ⚙️ Recommended Workflow: Parallel Development Plan

| Role                   | Can Start Right Away? | Depends On                                          | Notes                                                                                                     |
| ---------------------- | ------------------- | -------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| **Brunda (NLP)**       | ✅ Yes               | None                                               | Produce structured JSON output from user queries. Backend can mock this until NLP is done.               |
| **Backend Developer**  | ✅ Yes               | Needs expected NLP output format (JSON keys)      | Can already build `/api/parse`, `/api/itineraries`, and DB structure using dummy data.                   |
| **Frontend Developer** | ✅ Yes               | Needs backend API schema                            | Can build chatbot UI and itinerary display using mock JSON responses from Postman or sample files.        |

---

## 🧩 Step-by-Step Plan (How to Work in Parallel)

### Step 1 — Define Common API Contract (Now)

Before you all start coding, agree on:

- `/api/parse` → what JSON looks like (input/output)  
- `/api/itineraries` → what itinerary JSON looks like (day-wise)  
- `/api/itineraries/{id}` → structure for detailed itinerary  

Example everyone can use:

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
      "morning": "Visit the Louvre Museum",
      "afternoon": "Eiffel Tower and River Cruise",
      "evening": "Dinner near Montmartre",
      "estimated_cost": 120
    }
  ],
  "total_estimated_cost": 120
}
```

> Once this is shared, **everyone can start coding independently.**

---

### Step 2 — Work Independently with Mock Data

- **NLP (Brunda)**  
  Build and test `nlp_parser.py` locally. Save test outputs in `sample_outputs/parse_result.json`.  

- **Backend Developer**  
  - Build `/api/parse` using mock JSON before NLP parser is ready.  
  - Example:  
    ```python
    from sample_outputs.parse_result import mock_parse_output
    ```
  - Later replace with:  
    ```python
    from nlp.nlp_parser import parse_user_query
    ```

- **Frontend Developer**  
  - Mock backend responses in `api.js` using dummy JSON.  
  - Build and style UI without waiting for real data.  
  - Later switch mock URL → real FastAPI endpoint.

---

### Step 3 — Integration (Once NLP is Ready)

1. Give backend your function:
    ```python
    from nlp.nlp_parser import parse_user_query
    ```
2. Backend replaces dummy logic with real parser.  
3. Frontend connects to `/api/parse` and `/api/itineraries`.  

> This step should take just a day of integration and debugging.

---

### Step 4 — Testing Together

- **Backend** tests APIs using Postman or pytest.  
- **Frontend** tests API responses and UI flow.  
- **NLP** tests edge cases in user queries.  

---

## ✅ Summary Timeline

| Phase           | Who Works               | Dependencies                | Outcome                                      |
| ---------------- | ---------------------- | --------------------------- | -------------------------------------------- |
| Phase 2 Start    | All three in parallel   | Shared JSON schema          | Independent coding using mock data          |
| Mid Phase 2      | NLP finalizes parser    | Backend preps integration   | Minimal merge conflicts                      |
| Phase 3          | Backend + Frontend      | Real parser + itinerary     | Full flow working                             |
| Integration      | All together            | End-to-end testing          | Chatbot → NLP → itinerary → UI visualization |

---

## 💡 Pro Tips

- Keep **one shared “data contract” file**, e.g., `docs/api_contract.md`, to ensure everyone’s code will plug together perfectly.  
- Use `.md` format for version control, collaboration, and live updates.  
- Optional: generate PDF for stakeholders who prefer a read-only format.

---

> With this plan, your team can **start coding in parallel immediately**, avoid bottlenecks, and integrate quickly once NLP outputs are ready.

