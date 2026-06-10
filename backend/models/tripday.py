from sqlalchemy import Column, Integer, Date, Float, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from ..database.base import Base

class TripDay(Base):
    __tablename__ = "tripdays"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tripid = Column(Integer, ForeignKey("trips.id"))
    day_number = Column(Integer, nullable=False)
    date = Column(Date)
    theme = Column(String)
    estimated_cost = Column(Float, default=0.0)
    weatherjson = Column(JSON)
    routejson = Column(JSON)

    trip = relationship("Trip", back_populates="days")
    activities = relationship("Activity", back_populates="day", cascade="all, delete-orphan")
