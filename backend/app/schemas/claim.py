from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class ClaimResponse(BaseModel):
    id: int
    user_id: int
    claim_type: str
    trigger_type: str
    estimated_loss: float
    approved_amount: float
    status: str
    auto_approved: bool
    fraud_score: float
    fraud_flags: List[str]
    crowd_validation_count: int
    processing_time_seconds: float
    payout_status: str
    payout_transaction_id: Optional[str]
    approval_reason: Optional[str]
    rejection_reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class TriggerCheckResponse(BaseModel):
    triggered: bool
    trigger_count: int
    triggers: List[Dict]
    weather_data: Dict
    aqi_data: Dict
    traffic_data: Dict
