from sqlalchemy import Column, Integer, String, Float, Date, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    trips = relationship("Trip", back_populates="owner", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    saved_places = relationship("SavedPlace", back_populates="user", cascade="all, delete-orphan")

class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    destination = Column(String, index=True, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    budget = Column(Float)
    currency = Column(String, default="USD")
    interests = Column(JSON)          # List of strings
    itinerary_data = Column(JSON)     # The generated complete itinerary
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="trips")
    days = relationship("TripDay", back_populates="trip", cascade="all, delete-orphan")
    budget_info = relationship("Budget", back_populates="trip", uselist=False, cascade="all, delete-orphan")

class TripDay(Base):
    __tablename__ = "trip_days"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    day_number = Column(Integer)
    date = Column(Date)
    estimated_cost = Column(Float, default=0.0)

    trip = relationship("Trip", back_populates="days")
    activities = relationship("Activity", back_populates="day", cascade="all, delete-orphan")

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("trip_days.id"))
    time_slot = Column(String) # morning, afternoon, evening
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    estimated_cost = Column(Float, default=0.0)

    day = relationship("TripDay", back_populates="activities")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    state_data = Column(JSON) 
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_sessions")

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), unique=True)
    total_score = Column(Float)
    comfort_level = Column(String)
    allocation = Column(JSON)

    trip = relationship("Trip", back_populates="budget_info")

class SavedPlace(Base):
    __tablename__ = "saved_places"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    category = Column(String)

    user = relationship("User", back_populates="saved_places")