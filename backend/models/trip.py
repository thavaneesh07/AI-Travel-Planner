from sqlalchemy import Column, Integer, String, Date, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.base import Base

class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userid = Column(Integer, ForeignKey("users.id"))
    destination = Column(String, index=True, nullable=False)
    country = Column(String, nullable=True)
    startdate = Column(Date)
    enddate = Column(Date)
    travelercount = Column(Integer, default=1)
    travelertype = Column(String, default="solo")
    interests = Column(JSON)          # List of strings
    status = Column(String, default="planning")
    createdat = Column(DateTime, default=datetime.utcnow)
    updatedat = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="trips")
    days = relationship("TripDay", back_populates="trip", cascade="all, delete-orphan")
    budget_info = relationship("Budget", back_populates="trip", uselist=False, cascade="all, delete-orphan")
