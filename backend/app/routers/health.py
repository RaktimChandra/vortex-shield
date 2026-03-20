from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from ..core.database import get_db
import time
import os

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "VORTEX Shield 2.0",
        "version": "2.0.0"
    }

@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check - verifies all dependencies are available"""
    checks = {
        "database": False,
        "models_loaded": False,
        "config_valid": False
    }
    
    try:
        # Check database connection
        start = time.time()
        db.execute(text("SELECT 1"))
        db_latency = (time.time() - start) * 1000
        checks["database"] = True
        checks["database_latency_ms"] = round(db_latency, 2)
    except Exception as e:
        checks["database_error"] = str(e)
    
    try:
        # Check if ML models directory exists and has model files
        import os
        models_dir = os.path.join(os.path.dirname(__file__), "..", "..", "models")
        model_files = ["risk_model.pkl", "fraud_model.pkl", "pricing_model.pkl"]
        models_exist = os.path.exists(models_dir) and any(
            os.path.exists(os.path.join(models_dir, f)) for f in model_files
        )
        checks["models_loaded"] = models_exist
    except Exception as e:
        checks["models_error"] = str(e)
        checks["models_loaded"] = False
    
    try:
        # Check configuration
        checks["config_valid"] = bool(os.getenv("SECRET_KEY"))
    except Exception as e:
        checks["config_error"] = str(e)
    
    all_healthy = all([
        checks["database"],
        checks["models_loaded"],
        checks["config_valid"]
    ])
    
    if not all_healthy:
        raise HTTPException(status_code=503, detail={
            "status": "not_ready",
            "checks": checks
        })
    
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }

@router.get("/live")
async def liveness_check():
    """Liveness check - basic process health"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time()
    }

@router.get("/metrics")
async def metrics(db: Session = Depends(get_db)):
    """System metrics endpoint"""
    try:
        # Database metrics
        result = db.execute(text("""
            SELECT 
                (SELECT COUNT(*) FROM users) as total_users,
                (SELECT COUNT(*) FROM subscriptions WHERE status = 'active') as active_subscriptions,
                (SELECT COUNT(*) FROM claims) as total_claims,
                (SELECT COUNT(*) FROM claims WHERE status = 'approved') as approved_claims
        """))
        row = result.fetchone()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "total_users": row[0] if row else 0,
                "active_subscriptions": row[1] if row else 0,
                "total_claims": row[2] if row else 0,
                "approved_claims": row[3] if row else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
