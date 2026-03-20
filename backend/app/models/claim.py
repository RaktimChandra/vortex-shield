from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class Claim(Base):
    __tablename__ = "claims"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    
    claim_type = Column(String, nullable=False)
    trigger_type = Column(String, nullable=False)
    
    disruption_data = Column(JSON, default=dict)
    weather_data = Column(JSON, default=dict)
    traffic_data = Column(JSON, default=dict)
    
    estimated_loss = Column(Float, nullable=False)
    approved_amount = Column(Float, default=0.0)
    
    status = Column(String, default="pending")
    auto_approved = Column(Boolean, default=False)
    
    fraud_score = Column(Float, default=0.0)
    fraud_flags = Column(JSON, default=list)
    fraud_analysis = Column(JSON, default=dict)
    
    crowd_validation_count = Column(Integer, default=0)
    crowd_validation_users = Column(JSON, default=list)
    
    gps_data = Column(JSON, default=dict)
    sensor_data = Column(JSON, default=dict)
    
    processing_time_seconds = Column(Float, default=0.0)
    approval_reason = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    payout_status = Column(String, default="pending")
    payout_transaction_id = Column(String, nullable=True)
    payout_timestamp = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="claims")
