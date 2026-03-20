from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    plan_type = Column(String, nullable=False)
    premium_amount = Column(Float, nullable=False)
    coverage_amount = Column(Float, default=5000.0)
    
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    predicted_loss = Column(Float, default=0.0)
    
    status = Column(String, default="active")
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    auto_renew = Column(Boolean, default=True)
    payment_method = Column(String, default="upi")
    transaction_id = Column(String, nullable=True)
    
    zone_risk_data = Column(JSON, default=dict)
    pricing_factors = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="subscriptions")
