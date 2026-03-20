from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class SubscriptionCreate(BaseModel):
    plan_type: str
    auto_renew: bool = True

class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_type: str
    premium_amount: float
    coverage_amount: float
    risk_score: float
    risk_level: str
    predicted_loss: float
    status: str
    start_date: datetime
    end_date: datetime
    auto_renew: bool
    pricing_factors: Dict
    created_at: datetime
    
    class Config:
        from_attributes = True
