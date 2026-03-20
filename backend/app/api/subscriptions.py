from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from ..core.database import get_db
from ..models import User, Subscription
from ..schemas import SubscriptionCreate, SubscriptionResponse
from ..api.dependencies import get_current_user
from ..ai import RiskIntelligenceEngine, DynamicPricingEngine

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

risk_engine = RiskIntelligenceEngine()
pricing_engine = DynamicPricingEngine()

@router.post("/", response_model=SubscriptionResponse)
def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    risk_features = {
        'rainfall_mm': 30,
        'temperature_c': 28,
        'aqi': 120,
        'traffic_congestion': 0.4,
        'flood_risk_score': 0.3,
        'historical_disruptions': 3,
        'zone_density': 0.7,
        'work_hours': current_user.work_hours_per_day,
        'avg_daily_earnings': current_user.avg_daily_earnings
    }
    
    risk_prediction = risk_engine.predict_risk(risk_features)
    
    user_data = {
        'zone': current_user.zone,
        'city': current_user.city,
        'work_hours_per_day': current_user.work_hours_per_day,
        'avg_daily_earnings': current_user.avg_daily_earnings,
        'trust_score': current_user.trust_score,
        'total_claims': current_user.total_claims
    }
    
    pricing_result = pricing_engine.calculate_weekly_premium(risk_prediction, user_data)
    
    subscription = Subscription(
        user_id=current_user.id,
        plan_type=subscription_data.plan_type,
        premium_amount=pricing_result['weekly_premium'],
        coverage_amount=pricing_result['coverage_amount'],
        risk_score=risk_prediction['risk_score'],
        risk_level=risk_prediction['risk_level'],
        predicted_loss=risk_prediction['predicted_loss'],
        status='active',
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=7),
        auto_renew=subscription_data.auto_renew,
        pricing_factors=pricing_result['pricing_factors']
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    return subscription

@router.get("/my-subscriptions", response_model=List[SubscriptionResponse])
def get_my_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).order_by(Subscription.created_at.desc()).all()
    
    return subscriptions

@router.get("/active", response_model=SubscriptionResponse)
def get_active_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == 'active',
        Subscription.end_date > datetime.now()
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    return subscription

@router.get("/calculate-premium")
def calculate_premium(
    current_user: User = Depends(get_current_user)
):
    risk_features = {
        'rainfall_mm': 30,
        'temperature_c': 28,
        'aqi': 120,
        'traffic_congestion': 0.4,
        'flood_risk_score': 0.3,
        'historical_disruptions': 3,
        'zone_density': 0.7,
        'work_hours': current_user.work_hours_per_day,
        'avg_daily_earnings': current_user.avg_daily_earnings
    }
    
    risk_prediction = risk_engine.predict_risk(risk_features)
    
    user_data = {
        'zone': current_user.zone,
        'city': current_user.city,
        'work_hours_per_day': current_user.work_hours_per_day,
        'avg_daily_earnings': current_user.avg_daily_earnings,
        'trust_score': current_user.trust_score,
        'total_claims': current_user.total_claims
    }
    
    pricing_result = pricing_engine.calculate_weekly_premium(risk_prediction, user_data)
    
    return {
        'risk_analysis': risk_prediction,
        'pricing': pricing_result
    }
