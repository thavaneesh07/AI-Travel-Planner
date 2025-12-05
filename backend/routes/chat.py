from fastapi import APIRouter
from pydantic import BaseModel
from groq import Groq
import os
import json

from state import get_trip, set_trip, save_chat_message, update_itinerary

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    text: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


@router.post("/chat")
def chat(request: ChatRequest):
    try:
        trip = get_trip()

        # Save user message
        last_user_msg = request.messages[-1]
        save_chat_message("user", last_user_msg.text)

        # ---------- SYSTEM PROMPT ----------
        system_prompt = {
            "role": "system",
            "content": (
                "You are an AI travel assistant.\n\n"
                "IMPORTANT RULES:\n"
                "- ONLY return JSON when the user EXPLICITLY asks to edit, change, modify, update, swap, or regenerate the itinerary.\n"
                "- For normal conversation, DO NOT output JSON.\n"
                "- When JSON is needed, output ONLY the JSON object with NO extra text.\n\n"
                "Correct JSON example:\n"
                "{ \"action\": \"modify_itinerary\", \"changes\": { \"day2\": {\"afternoon\": \"Dubai Mall\"} } }\n\n"
                f"Current trip data: {trip}"
            )
        }

        history = [system_prompt] + [
            {"role": m.role, "content": m.text}
            for m in request.messages
        ]

        # ---------- LLM RESPONSE ----------
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=history
        )

        ai_text = response.choices[0].message.content.strip()
        save_chat_message("assistant", ai_text)

        # ---------- STABLE JSON EXTRACTION ----------
        action_data = None
        try:
            # Attempt to extract the last {...} block from the message
            json_candidates = []
            for line in ai_text.split("\n"):
                line = line.strip()
                if line.startswith("{") and line.endswith("}"):
                    json_candidates.append(line)

            if json_candidates:
                parsed = json.loads(json_candidates[-1])
                if parsed.get("action"):
                    action_data = parsed

        except Exception:
            action_data = None

        # ---------- PROCESS MODIFY ITINERARY ----------
        if action_data and action_data.get("action") == "modify_itinerary":
            raw_changes = action_data.get("changes", {})
            fixed_changes = {}

            for key, value in raw_changes.items():

                # Format: itinerary.days.3.morning.name
                if key.startswith("itinerary.days"):
                    parts = key.split(".")  # ["itinerary", "days", "3", "morning", "name"]
                    day_num = int(parts[2]) + 1  # convert index → day number
                    slot = parts[3]              # morning/afternoon/evening
                    fixed_changes.setdefault(f"day{day_num}", {})
                    fixed_changes[f"day{day_num}"][slot] = value

                # Already clean: day4: {...}
                elif key.startswith("day"):
                    fixed_changes[key] = value

            action_data["changes"] = fixed_changes

            # -------- Apply local backend update --------
            itinerary = trip.get("itinerary")
            if itinerary:
                for day_key, slot_updates in fixed_changes.items():
                    idx = int(day_key.replace("day", "")) - 1

                    if 0 <= idx < len(itinerary["days"]):
                        for slot, new_name in slot_updates.items():
                            if slot in ("morning", "afternoon", "evening"):
                                if isinstance(itinerary["days"][idx][slot], dict):
                                    itinerary["days"][idx][slot]["name"] = new_name
                                else:
                                    itinerary["days"][idx][slot] = {"name": new_name}

                update_itinerary(itinerary)

        # ---------- CLEAN RESPONSE ----------
        return {
            "assistant": {
                "text": ai_text,
                "action": action_data.get("action") if action_data else None,
                "changes": action_data.get("changes") if action_data else None,
            }
        }

    except Exception as e:
        print("Chat backend error:", e)
        return {"assistant": {"text": "Server error from backend."}}
