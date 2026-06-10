from ..ai.ollamaclient import OllamaClient
from ..ai.promptregistry import PROMPTS

class TravelAssistantAgent:
    @staticmethod
    def answer(message: str, history: list, itinerary: dict = None, intent: str = "travelquestion") -> str:
        if intent in ("non_travel", "nontravel"):
            prompt = (
                "You are a helpful AI travel assistant. The user has asked a general question outside travel: \"{message}\"\n"
                "Answer their question politely and clearly. You do not need to block them, but try to relate it back to travel or mention you are happy to help with their travel plans as well.\n"
                "Response:"
            ).format(message=message)
            response = OllamaClient.call_ollama(prompt)
            if response:
                return response
            return PROMPTS["nontravelredirect"]

        history_str = ""
        if history:
            history_str = "\n".join([f"{h.get('role', 'user')}: {h.get('text', '') or h.get('content', '')}" for h in history[-5:]])

        itinerary_context = "No active itinerary planned yet."
        if itinerary:
            dest = itinerary.get("destination", "Unknown")
            days_str = []
            for day in itinerary.get("days", []):
                day_num = day.get("day", "?")
                theme = day.get("theme", "")
                theme_part = f" ({theme})" if theme else ""
                acts = []
                for act in day.get("activities", []):
                    time_slot = act.get("timeslot") or act.get("time_slot") or ""
                    slot_part = f"[{time_slot}] " if time_slot else ""
                    desc = act.get("description", "")
                    desc_part = f" - {desc}" if desc else ""
                    acts.append(f"  - {slot_part}{act.get('name')}{desc_part}")
                acts_str = "\n".join(acts)
                days_str.append(f"Day {day_num}{theme_part}:\n{acts_str}")
            itinerary_context = f"Destination: {dest}\n" + "\n".join(days_str)

        prompt = PROMPTS["travelassistantresponse"].format(
            message=message,
            chat_history=history_str,
            itinerary_context=itinerary_context
        )
        response = OllamaClient.call_ollama(prompt)
        
        if not response:
            return "I am here to help you with any travel recommendations or details for your upcoming journeys! Could you clarify your question?"
        return response
