"""
WebSocket Routes for Real-time Features
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import verify_token
from .connection_manager import manager
import json

router = APIRouter()

@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time updates
    Token is passed as path parameter for WebSocket authentication
    """
    # Verify token
    payload = verify_token(token)
    if not payload:
        await websocket.close(code=1008)  # Policy violation
        return
    
    user_id = int(payload.get("sub"))
    user_email = payload.get("email")
    
    # Get user from database
    from ..models import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        await websocket.close(code=1008)
        return
    
    is_admin = user.role == "admin"
    
    # Connect
    await manager.connect(websocket, user_id, is_admin)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to VORTEX Shield real-time updates",
            "user_id": user_id,
            "is_admin": is_admin
        })
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif message.get("type") == "subscribe_zone":
                # User wants zone-specific updates
                await websocket.send_json({
                    "type": "subscribed",
                    "zone": user.zone,
                    "city": user.city
                })
            
            elif message.get("type") == "request_risk_update":
                # Real-time risk calculation
                from ..ai import RiskIntelligenceEngine
                from ..services import ParametricTriggerService
                
                risk_engine = RiskIntelligenceEngine()
                trigger_service = ParametricTriggerService(db)
                
                # Get current conditions
                weather_data = trigger_service.get_weather_data(user.city)
                
                risk_data = risk_engine.predict_risk({
                    'rainfall_mm': weather_data.get('rainfall', 0),
                    'temperature_c': weather_data.get('temperature', 30),
                    'aqi': weather_data.get('aqi', 100),
                    'traffic_congestion': 0.5,
                    'flood_risk_score': 0.3,
                    'historical_disruptions': 2,
                    'zone_density': 0.7,
                    'work_hours': user.work_hours_per_day,
                    'avg_daily_earnings': user.avg_daily_earnings
                })
                
                await manager.send_risk_update(user_id, risk_data)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id, is_admin)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id, is_admin)

@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return {
        "active_users": manager.get_active_users_count(),
        "active_admins": manager.get_active_admins_count(),
        "total_connections": manager.get_active_users_count() + manager.get_active_admins_count()
    }
