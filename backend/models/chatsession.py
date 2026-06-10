from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.base import Base

class ChatSession(Base):
    __tablename__ = "chatsessions"
    
    id = Column(String, primary_key=True, index=True) # UUID string
    userid = Column(Integer, ForeignKey("users.id"))
    tripid = Column(Integer, ForeignKey("trips.id"), nullable=True)
    messagesjson = Column(JSON)          # List of chat messages
    planningstatejson = Column(JSON)     # Structured planning context
    createdat = Column(DateTime, default=datetime.utcnow)
    updatedat = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="chat_sessions")
