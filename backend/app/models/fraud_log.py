from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Text
from datetime import datetime
from ..core.database import Base

class FraudLog(Base):
    __tablename__ = "fraud_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=True)
    
    fraud_type = Column(String, nullable=False, index=True)
    fraud_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    
    detection_method = Column(String, nullable=False)
    
    gps_spoofing_score = Column(Float, default=0.0)
    fraud_ring_score = Column(Float, default=0.0)
    behavioral_anomaly_score = Column(Float, default=0.0)
    
    evidence = Column(JSON, default=dict)
    gps_analysis = Column(JSON, default=dict)
    cluster_analysis = Column(JSON, default=dict)
    pattern_analysis = Column(JSON, default=dict)
    
    similar_users = Column(JSON, default=list)
    similar_claims = Column(JSON, default=list)
    
    action_taken = Column(String, nullable=True)
    flagged = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
