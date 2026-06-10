from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.base import Base

class SavedPlace(Base):
    __tablename__ = "savedplaces"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userid = Column(Integer, ForeignKey("users.id"))
    placename = Column(String, nullable=False)
    lat = Column(Float)
    lng = Column(Float)
    category = Column(String)
    notes = Column(String)
    createdat = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="saved_places")
