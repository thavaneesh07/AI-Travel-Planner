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

        # ---------- FIXED SYSTEM PROMPT ----------
        system_prompt = {
            "role": "system",
            "content": (
                "You are an AI travel assistant.\n\n"
                "IMPORTANT RULES:\n"
                "- ONLY return JSON when the user EXPLICITLY asks to edit, change, modify, update, swap, or regenerate the itinerary.\n"
                "- For greetings or normal conversation, DO NOT output JSON. Just reply naturally.\n"
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

        # LLM response
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=history
        )

        ai_text = response.choices[0].message.content.strip()
        save_chat_message("assistant", ai_text)

        action_data = None

        # ---------- FIXED JSON EXTRACTION ----------
        if ai_text.startswith("{") and ai_text.endswith("}"):
            try:
                parsed = json.loads(ai_text)
                if parsed.get("action"):
                    action_data = parsed
            except:
                action_data = None

        # ---------- PROCESS JSON ACTION ----------
        if action_data and action_data.get("action") == "modify_itinerary":
            raw_changes = action_data.get("changes", {})
            fixed_changes = {}

            for key, value in raw_changes.items():
                parts = key.split(".")
                if len(parts) >= 4:
                    day_num = int(parts[2]) + 1
                    slot = parts[3]
                    fixed_changes.setdefault(f"day{day_num}", {})
                    fixed_changes[f"day{day_num}"][slot] = value
                else:
                    fixed_changes[key] = value

            action_data["changes"] = fixed_changes

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

        # ---------- RETURN CLEAN RESPONSE ----------
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
