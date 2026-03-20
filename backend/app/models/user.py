from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    
    role = Column(String, default="worker")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    city = Column(String, nullable=True)
    zone = Column(String, nullable=True)
    
    work_hours_per_day = Column(Float, default=8.0)
    avg_daily_earnings = Column(Float, default=500.0)
    delivery_platform = Column(String, nullable=True)
    
    trust_score = Column(Float, default=1.0)
    total_claims = Column(Integer, default=0)
    approved_claims = Column(Integer, default=0)
    rejected_claims = Column(Integer, default=0)
    
    device_id = Column(String, nullable=True)
    last_gps_update = Column(DateTime, nullable=True)
    gps_trajectory = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    subscriptions = relationship("Subscription", back_populates="user")
    claims = relationship("Claim", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")
