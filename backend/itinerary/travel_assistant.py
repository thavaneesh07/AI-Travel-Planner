from ..api.ollama_service import _call_ollama

class TravelAssistantAgent:
    @staticmethod
    def answer(message: str, history: list) -> str:
        prompt = (
            "You are an expert travel assistant. Answer the user's travel question clearly and concisely.\n"
            "Do not attempt to generate a full itinerary, just provide the advice requested.\n\n"
            f"User: {message}\n"
        )
        return _call_ollama(prompt)