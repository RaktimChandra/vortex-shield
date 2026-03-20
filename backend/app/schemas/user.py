from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    phone: str

class UserCreate(UserBase):
    password: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    zone: Optional[str] = None
    work_hours_per_day: float = 8.0
    avg_daily_earnings: float = 500.0
    delivery_platform: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    zone: Optional[str] = None
    work_hours_per_day: Optional[float] = None
    avg_daily_earnings: Optional[float] = None

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    is_verified: bool
    latitude: Optional[float]
    longitude: Optional[float]
    city: Optional[str]
    zone: Optional[str]
    work_hours_per_day: float
    avg_daily_earnings: float
    trust_score: float
    total_claims: int
    approved_claims: int
    rejected_claims: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
