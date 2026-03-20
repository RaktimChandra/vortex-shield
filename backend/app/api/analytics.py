from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict
from ..core.database import get_db
from ..models import User, Claim, Subscription, DisruptionEvent, FraudLog
from ..api.dependencies import get_current_user
from ..ai import DigitalTwinSimulator

router = APIRouter(prefix="/analytics", tags=["Analytics"])

digital_twin = DigitalTwinSimulator()

@router.get("/dashboard")
def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total_claims = db.query(func.count(Claim.id)).filter(
        Claim.user_id == current_user.id
    ).scalar()
    
    approved_claims = db.query(func.count(Claim.id)).filter(
        Claim.user_id == current_user.id,
        Claim.status == 'approved'
    ).scalar()
    
    total_payout = db.query(func.sum(Claim.approved_amount)).filter(
        Claim.user_id == current_user.id,
        Claim.status == 'approved'
    ).scalar() or 0
    
    active_subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == 'active'
    ).first()
    
    recent_claims = db.query(Claim).filter(
        Claim.user_id == current_user.id
    ).order_by(Claim.created_at.desc()).limit(5).all()
    
    return {
        'total_claims': total_claims,
        'approved_claims': approved_claims,
        'rejected_claims': total_claims - approved_claims,
        'approval_rate': round((approved_claims / total_claims * 100) if total_claims > 0 else 0, 1),
        'total_payout': round(total_payout, 2),
        'trust_score': round(current_user.trust_score, 2),
        'active_coverage': active_subscription.coverage_amount if active_subscription else 0,
        'risk_level': active_subscription.risk_level if active_subscription else 'UNKNOWN',
        'recent_claims': [
            {
                'id': claim.id,
                'amount': claim.approved_amount,
                'status': claim.status,
                'date': claim.created_at.isoformat()
            }
            for claim in recent_claims
        ]
    }

@router.get("/admin-dashboard")
def get_admin_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not authorized")
    
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    
    total_claims = db.query(func.count(Claim.id)).scalar()
    pending_claims = db.query(func.count(Claim.id)).filter(Claim.status == 'pending').scalar()
    approved_claims = db.query(func.count(Claim.id)).filter(Claim.status == 'approved').scalar()
    rejected_claims = db.query(func.count(Claim.id)).filter(Claim.status == 'rejected').scalar()
    
    total_payout = db.query(func.sum(Claim.approved_amount)).filter(
        Claim.status == 'approved'
    ).scalar() or 0
    
    fraud_alerts = db.query(func.count(FraudLog.id)).filter(
        FraudLog.flagged == True,
        FraudLog.created_at >= datetime.now() - timedelta(days=7)
    ).scalar()
    
    avg_processing_time = db.query(func.avg(Claim.processing_time_seconds)).scalar() or 0
    
    recent_disruptions = db.query(DisruptionEvent).filter(
        DisruptionEvent.is_active == True
    ).order_by(DisruptionEvent.created_at.desc()).limit(5).all()
    
    return {
        'total_users': total_users,
        'active_users': active_users,
        'total_claims': total_claims,
        'pending_claims': pending_claims,
        'approved_claims': approved_claims,
        'rejected_claims': rejected_claims,
        'approval_rate': round((approved_claims / total_claims * 100) if total_claims > 0 else 0, 1),
        'total_payout': round(total_payout, 2),
        'fraud_alerts': fraud_alerts,
        'avg_processing_time_seconds': round(avg_processing_time, 2),
        'recent_disruptions': [
            {
                'id': event.id,
                'type': event.event_type,
                'severity': event.severity,
                'city': event.city,
                'zone': event.zone,
                'affected_users': event.affected_users_count,
                'claims_triggered': event.claims_triggered
            }
            for event in recent_disruptions
        ]
    }

@router.get("/simulate-disruption")
def simulate_disruption(
    city: str = "Delhi",
    disruption_type: str = "rainfall",
    current_user: User = Depends(get_current_user)
):
    disruption_data = {
        'rainfall_mm': 75 if disruption_type == 'rainfall' else 0,
        'aqi': 250 if disruption_type == 'air_quality' else 100,
        'congestion_level': 0.85 if disruption_type == 'traffic' else 0.3,
        'duration_hours': 4
    }
    
    simulation = digital_twin.simulate_disruption_impact(
        city, disruption_type, disruption_data
    )
    
    return simulation

@router.get("/predict-disruptions")
def predict_disruptions(
    city: str = "Delhi",
    days: int = 7
):
    predictions = digital_twin.predict_future_disruptions(city, days)
    return {
        'city': city,
        'days_ahead': days,
        'predictions': predictions
    }

@router.get("/fraud-stats")
def get_fraud_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not authorized")
    
    total_fraud_logs = db.query(func.count(FraudLog.id)).scalar()
    flagged_fraud = db.query(func.count(FraudLog.id)).filter(FraudLog.flagged == True).scalar()
    
    fraud_by_type = db.query(
        FraudLog.fraud_type,
        func.count(FraudLog.id)
    ).group_by(FraudLog.fraud_type).all()
    
    return {
        'total_fraud_logs': total_fraud_logs,
        'flagged_cases': flagged_fraud,
        'detection_rate': round((flagged_fraud / total_fraud_logs * 100) if total_fraud_logs > 0 else 0, 1),
        'fraud_by_type': [
            {'type': fraud_type, 'count': count}
            for fraud_type, count in fraud_by_type
        ]
    }
