from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..core.database import get_db
from ..models import User, Claim
from ..schemas import ClaimResponse, TriggerCheckResponse
from ..api.dependencies import get_current_user
from ..services import ZeroTouchClaimService, ParametricTriggerService
from ..ai.fraud_detection import FraudDetectionEngine
from pydantic import BaseModel

class ClaimCreate(BaseModel):
    trigger_type: str
    description: str
    estimated_loss: float
    incident_date: str

router = APIRouter(prefix="/claims", tags=["Claims"])

@router.post("/check-triggers", response_model=TriggerCheckResponse)
def check_triggers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trigger_service = ParametricTriggerService(db)
    result = trigger_service.check_triggers(current_user)
    return result

@router.post("/submit")
def submit_claim(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trigger_service = ParametricTriggerService(db)
    trigger_data = trigger_service.check_triggers(current_user)
    
    if not trigger_data['triggered']:
        raise HTTPException(
            status_code=400,
            detail="No valid triggers detected. Cannot submit claim."
        )
    
    claim_service = ZeroTouchClaimService(db)
    result = claim_service.auto_process_claim(current_user.id, trigger_data)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result

@router.get("/my-claims", response_model=List[ClaimResponse])
def get_my_claims(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    claims = db.query(Claim).filter(
        Claim.user_id == current_user.id
    ).order_by(Claim.created_at.desc()).all()
    
    return claims

@router.get("/{claim_id}", response_model=ClaimResponse)
def get_claim(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if claim.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return claim

@router.post("/", response_model=ClaimResponse)
def create_claim(
    claim_data: ClaimCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new claim with AI fraud detection"""
    fraud_engine = FraudDetectionEngine()
    
    # Create claim with correct model fields
    new_claim = Claim(
        user_id=current_user.id,
        claim_type=claim_data.trigger_type,
        trigger_type=claim_data.trigger_type,
        estimated_loss=claim_data.estimated_loss,
        disruption_data={
            'description': claim_data.description,
            'incident_date': claim_data.incident_date
        },
        status="pending",
        fraud_score=0.0,
    )
    
    db.add(new_claim)
    db.flush()
    
    # Run fraud detection
    try:
        fraud_result = fraud_engine.analyze_claim(new_claim, current_user)
        new_claim.fraud_score = fraud_result['fraud_probability']
        
        # Auto-approve/reject based on fraud score
        if fraud_result['fraud_probability'] < 0.3:
            new_claim.status = "approved"
            new_claim.approved_amount = claim_data.estimated_loss
            new_claim.approval_reason = "Low fraud risk - auto-approved"
        elif fraud_result['fraud_probability'] > 0.7:
            new_claim.status = "rejected"
            new_claim.rejection_reason = "High fraud probability detected"
        else:
            new_claim.status = "pending"
            
    except Exception as e:
        print(f"Fraud detection error: {e}")
        new_claim.fraud_score = 0.5
    
    db.commit()
    db.refresh(new_claim)
    
    return new_claim

@router.get("/", response_model=List[ClaimResponse])
def get_all_claims(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    claims = db.query(Claim).offset(skip).limit(limit).order_by(Claim.created_at.desc()).all()
    return claims
