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

# Fallback deterministic planner
def _fallback_plan(days: int, interests: List[str]) -> List[Dict[str, Any]]:
    days = max(1, days)
    plan = []
    for d in range(1, days + 1):
        morning = "sightseeing"
        afternoon = "museum" if any("art" in i.lower() for i in interests) else "local_market"
        evening = "food_experience" if any("food" in i.lower() for i in interests) else "local_dinner"
        plan.append({"day": d, "morning": morning, "afternoon": afternoon, "evening": evening})
    return plan


def _parse_model_output(text: str) -> List[Dict[str, Any]]:
    """
    Attempts to parse JSON from model output. Strips code fences if present.
    Returns list of day dicts on success, otherwise raises ValueError.
    """
    txt = text.strip()
    if txt.startswith("```"):
        # remove fencing
        # find first newline after opening ```
        idx = txt.find("\n")
        if idx != -1:
            txt = txt[idx + 1 :]
        txt = txt.rstrip("`").strip()
    # try JSON load
    return json.loads(txt)


def generate_activity_types(
    destination: str,
    start_date: str,
    end_date: str,
    interests: List[str],
    budget: float,
) -> List[Dict[str, Any]]:
    """
    Produces activity-level labels (morning/afternoon/evening) per day via Groq model.
    If Groq is not configured or call fails, falls back to deterministic planner.
    """

    # compute days
    try:
        sd = date.fromisoformat(start_date)
        ed = date.fromisoformat(end_date)
        days = (ed - sd).days + 1
        if days < 1:
            days = 1
    except Exception:
        days = 3

    # If no GROQ key, fallback
    if not GROQ_API_KEY:
        return _fallback_plan(days, interests)

    # Build a compact instruction asking for JSON array only
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
        # model output location may differ per Groq API; try common shapes:
        # - body["outputs"][0]["content"]
        # - body["generations"][0]["text"]
        text = None
        if "outputs" in body and isinstance(body["outputs"], list) and len(body["outputs"]) > 0:
            # try to concatenate content entries if present
            out = body["outputs"][0]
            if isinstance(out, dict) and "content" in out:
                # sometimes content can be list of dicts with text
                content = out["content"]
                if isinstance(content, list):
                    # find first text block
                    for c in content:
                        if isinstance(c, dict) and "text" in c:
                            text = c["text"]
                            break
                elif isinstance(content, str):
                    text = content
        if not text:
            # try alternative keys
            if "generations" in body and isinstance(body["generations"], list) and len(body["generations"]) > 0:
                gen = body["generations"][0]
                text = gen.get("text") or gen.get("content") or None
        if not text and isinstance(body, dict):
            # fallback: stringify any 'output' field
            text = json.dumps(body)
        # parse JSON from text
        parsed = _parse_model_output(text)
        if isinstance(parsed, list):
            return parsed
        else:
            return _fallback_plan(days, interests)
    except Exception:
        # any failure -> deterministic fallback
        return _fallback_plan(days, interests)
