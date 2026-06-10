from sqlalchemy import Column, Integer, Float, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from ..database.base import Base

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tripid = Column(Integer, ForeignKey("trips.id"), unique=True)
    totalbudget = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    total_score = Column(Float, default=0.0)
    comfort_level = Column(String)
    allocationjson = Column(JSON)
    warningsjson = Column(JSON)

    trip = relationship("Trip", back_populates="budget_info")
