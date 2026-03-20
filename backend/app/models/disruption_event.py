from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from datetime import datetime
from ..core.database import Base

class DisruptionEvent(Base):
    __tablename__ = "disruption_events"
    
    id = Column(Integer, primary_key=True, index=True)
    
    event_type = Column(String, nullable=False, index=True)
    severity = Column(String, nullable=False)
    
    city = Column(String, nullable=False, index=True)
    zone = Column(String, nullable=True, index=True)
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    radius_km = Column(Float, default=5.0)
    
    weather_data = Column(JSON, default=dict)
    traffic_data = Column(JSON, default=dict)
    aqi_data = Column(JSON, default=dict)
    
    rainfall_mm = Column(Float, default=0.0)
    temperature_c = Column(Float, nullable=True)
    aqi_value = Column(Integer, nullable=True)
    traffic_congestion = Column(Float, default=0.0)
    
    affected_users_count = Column(Integer, default=0)
    claims_triggered = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    validated = Column(Boolean, default=False)
    crowd_reports = Column(Integer, default=0)
    
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    duration_hours = Column(Float, nullable=True)
    
    estimated_impact = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
