from fastapi import APIRouter
from pydantic import BaseModel
from groq import Groq
import os

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
        history = [
            {"role": m.role, "content": m.text}
            for m in request.messages
        ]

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=history
        )

        ai_text = response.choices[0].message.content

        return { "assistant": { "text": ai_text } }

    except Exception as e:
        print("Chat backend error:", e)
        return { "assistant": { "text": "Server error from backend. Try again later." } }
