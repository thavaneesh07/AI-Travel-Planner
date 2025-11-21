# backend/api/groq_service.py
import os
import json
import requests
from typing import List, Dict, Any
from datetime import date

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.ai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

HEADERS = {"Content-Type": "application/json"}
if GROQ_API_KEY:
    HEADERS["Authorization"] = f"Bearer {GROQ_API_KEY}"


def _fallback_plan(days: int, interests: List[str]) -> List[Dict[str, Any]]:
    days = max(1, days)
    plan = []
    for d in range(1, days + 1):
        morning = "sightseeing"
        afternoon = "museum" if any("art" in i.lower() for i in interests) else "local_market"
        evening = "food_experience" if any("food" in i.lower() for i in interests) else "local_dinner"
        plan.append({"day": d, "morning": morning, "afternoon": afternoon, "evening": evening})
    return plan


def _parse_model_output(text: str) -> Any:
    txt = (text or "").strip()
    if not txt:
        raise ValueError("Empty model output")
    if txt.startswith("```"):
        idx = txt.find("\n")
        if idx != -1:
            txt = txt[idx + 1 :]
        txt = txt.rstrip("`").strip()
    return json.loads(txt)


def generate_activity_types(
    destination: str,
    start_date: str,
    end_date: str,
    interests: List[str],
    budget: float,
) -> List[Dict[str, Any]]:

    try:
        sd = date.fromisoformat(start_date)
        ed = date.fromisoformat(end_date)
        days = (ed - sd).days + 1
        if days < 1:
            days = 1
    except Exception:
        days = 3

    if not GROQ_API_KEY:
        return _fallback_plan(days, interests)

    system_instructions = (
        "You are a travel plan generator. Output JSON only. "
        "Return a JSON array of objects, one per day. Each object must have keys: "
        "'day' (int), 'morning' (short label), 'afternoon' (short label), 'evening' (short label). "
        "Use succinct machine-friendly labels like: museum, temple, park, beach, local_market, food_experience, shopping, sightseeing, historic_site."
    )

    user_prompt = (
        f"Destination: {destination}\n"
        f"Dates: {start_date} to {end_date}\n"
        f"Interests: {', '.join(interests) if interests else 'none'}\n"
        f"Budget: {budget}\n\n"
        f"Return a JSON array with {days} objects as described."
    )

    payload = {
        "input": f"{system_instructions}\n\n{user_prompt}",
        "max_output_tokens": 600,
        "temperature": 0.2,
    }

    url = f"{GROQ_API_URL}/models/{GROQ_MODEL}/generate"

    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        body = resp.json()
        text = None
        if "outputs" in body and isinstance(body["outputs"], list) and len(body["outputs"]) > 0:
            out = body["outputs"][0]
            if isinstance(out, dict) and "content" in out:
                content = out["content"]
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and "text" in c:
                            text = c["text"]
                            break
                elif isinstance(content, str):
                    text = content
        if not text:
            if "generations" in body and isinstance(body["generations"], list) and len(body["generations"]) > 0:
                gen = body["generations"][0]
                text = gen.get("text") or gen.get("content") or None
        if not text and isinstance(body, dict):
            text = json.dumps(body)

        parsed = _parse_model_output(text)
        if isinstance(parsed, list):
            return parsed
        else:
            return _fallback_plan(days, interests)
    except Exception:
        return _fallback_plan(days, interests)


def refine_itinerary_json(refine_input: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Accept a refine_input dict (see itinerary_generator) and return
    a list of polished day objects: {day, date, morning, afternoon, evening, notes}
    """
    # fallback if no API key
    if not GROQ_API_KEY:
        return [
            {
                "day": d.get("day"),
                "date": d.get("date"),
                "morning": d.get("morning"),
                "afternoon": d.get("afternoon"),
                "evening": d.get("evening"),
                "notes": ""
            }
            for d in refine_input.get("raw_days", [])
        ]

    system_instructions = (
        "You are an itinerary polishing assistant. Output JSON only. "
        "Given a list of days with raw place names, return a JSON array of objects. "
        "Each object must have keys: day (int), date (YYYY-MM-DD), morning (short blurb, max 45 words), "
        "afternoon (short blurb), evening (short blurb), notes (short tips). Do not output any extra text."
    )

    body_snippet = {
        "destination": refine_input.get("destination"),
        "start_date": refine_input.get("start_date"),
        "end_date": refine_input.get("end_date"),
        "budget": refine_input.get("budget"),
        "interests": refine_input.get("interests"),
        "raw_days": refine_input.get("raw_days", []),
    }

    user_prompt = f"Refine this itinerary:\n\n{json.dumps(body_snippet, ensure_ascii=False)}\n\nReturn JSON array only."

    payload = {
        "input": f"{system_instructions}\n\n{user_prompt}",
        "max_output_tokens": 1200,
        "temperature": 0.25,
    }

    url = f"{GROQ_API_URL}/models/{GROQ_MODEL}/generate"

    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=45)
        resp.raise_for_status()
        body = resp.json()

        text = None
        if "outputs" in body and isinstance(body["outputs"], list) and len(body["outputs"]) > 0:
            out = body["outputs"][0]
            if isinstance(out, dict) and "content" in out:
                content = out["content"]
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and "text" in c:
                            text = c["text"]
                            break
                elif isinstance(content, str):
                    text = content
        if not text:
            if "generations" in body and isinstance(body["generations"], list) and len(body["generations"]) > 0:
                gen = body["generations"][0]
                text = gen.get("text") or gen.get("content") or None
        if not text and isinstance(body, dict):
            text = json.dumps(body)

        parsed = _parse_model_output(text)
        if isinstance(parsed, list):
            return parsed
        else:
            raise ValueError("Refinement returned non-list")
    except Exception:
        # fallback structured output
        return [
            {
                "day": d.get("day"),
                "date": d.get("date"),
                "morning": d.get("morning"),
                "afternoon": d.get("afternoon"),
                "evening": d.get("evening"),
                "notes": ""
            }
            for d in refine_input.get("raw_days", [])
        ]
