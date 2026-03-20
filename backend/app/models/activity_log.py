from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    
    speed = Column(Float, nullable=True)
    heading = Column(Float, nullable=True)
    altitude = Column(Float, nullable=True)
    
    is_active = Column(Boolean, default=True)
    activity_type = Column(String, nullable=True)
    
    accelerometer_x = Column(Float, nullable=True)
    accelerometer_y = Column(Float, nullable=True)
    accelerometer_z = Column(Float, nullable=True)
    
    device_id = Column(String, nullable=True)
    app_version = Column(String, nullable=True)
    
    weather_conditions = Column(JSON, default=dict)
    traffic_conditions = Column(JSON, default=dict)
    
    fraud_indicators = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="activity_logs")
