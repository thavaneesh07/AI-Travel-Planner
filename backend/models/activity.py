from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..database.base import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tripdayid = Column(Integer, ForeignKey("tripdays.id"))
    time_slot = Column(String)
    name = Column(String, nullable=False)
    category = Column(String) # attraction | restaurant | hotel | transport
    description = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    durationminutes = Column(Integer, default=90)
    estimatedcost = Column(Float, default=0.0)
    openinghours = Column(String)
    bookingnotes = Column(String)
    sequenceorder = Column(Integer)
    traveltonextjson = Column(JSON)

    day = relationship("TripDay", back_populates="activities")
