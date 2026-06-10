from pydantic import BaseModel

class ChatEditRequest(BaseModel):
    tripid: int
    message: str
