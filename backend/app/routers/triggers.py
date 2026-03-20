"""
Parametric Triggers API Router
Real-time trigger checking and management
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models import User
from ..api.dependencies import get_current_user
from ..services.weather_service import WeatherService

router = APIRouter(prefix="/triggers", tags=["Triggers"])

@router.get("/check")
def check_triggers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    demo: bool = True  # Set to True for demo/showcase mode
):
    """Check if any parametric triggers are activated using REAL weather API"""
    
    # Get real weather data for user's location (Mumbai default)
    weather_service = WeatherService()
    weather_data = weather_service.get_current_weather(
        latitude=19.0760,  # Mumbai coordinates
        longitude=72.8777
    )
    
    triggers_activated = []
    triggers_data = []
    
    # DEMO MODE: Simulate active triggers for showcase
    if demo:
        # Simulated heavy rainfall trigger
        triggers_activated.append('weather')
        triggers_data.append({
            'type': 'weather',
            'status': 'triggered',
            'location': 'Andheri West, Mumbai',
            'conditions': {
                'rainfall_mm': 65,  # Simulated heavy rain
                'temperature': 28,
                'wind_speed': 45
            },
            'triggered': True,
            'severity': 'high'
        })
        
        # Simulated pollution trigger
        triggers_activated.append('pollution')
        triggers_data.append({
            'type': 'pollution',
            'status': 'triggered',
            'location': 'Mumbai',
            'conditions': {
                'aqi': 420,  # Severe pollution
                'pollutant': 'PM2.5'
            },
            'triggered': True,
            'severity': 'high'
        })
        
        # Platform outage trigger
        triggers_activated.append('platform')
        triggers_data.append({
            'type': 'platform',
            'status': 'triggered',
            'location': 'Swiggy Mumbai',
            'conditions': {
                'downtime_hours': 3.5,
                'uptime': 85.2
            },
            'triggered': True,
            'severity': 'medium'
        })
        
        # Traffic congestion (monitoring, not triggered)
        triggers_data.append({
            'type': 'traffic',
            'status': 'monitoring',
            'location': 'Mumbai',
            'conditions': {'congestion': 55},
            'triggered': False,
            'severity': 'medium'
        })
    else:
        # REAL MODE: Use actual weather data
        rainfall = weather_data.get('rainfall_mm', 0)
        if rainfall >= 40:
            triggers_activated.append('weather')
            triggers_data.append({
                'type': 'weather',
                'status': 'triggered',
                'location': 'Mumbai',
                'conditions': {
                    'rainfall_mm': rainfall,
                    'temperature': weather_data.get('temperature_c'),
                    'wind_speed': weather_data.get('wind_speed_kmh')
                },
                'triggered': True,
                'severity': 'high' if rainfall >= 80 else 'medium'
            })
        else:
            triggers_data.append({
                'type': 'weather',
                'status': 'monitoring',
                'location': 'Mumbai',
                'conditions': {
                    'rainfall_mm': rainfall,
                    'temperature': weather_data.get('temperature_c'),
                    'wind_speed': weather_data.get('wind_speed_kmh')
                },
                'triggered': False,
                'severity': 'low'
            })
        
        # Platform status (mock for now)
        triggers_data.append({
            'type': 'platform',
            'status': 'monitoring',
            'location': 'All platforms',
            'conditions': {'uptime': 99.5},
            'triggered': False,
            'severity': 'low'
        })
        
        # Traffic (mock for now)
        triggers_data.append({
            'type': 'traffic',
            'status': 'monitoring',
            'location': 'Mumbai',
            'conditions': {'congestion': 35},
            'triggered': False,
            'severity': 'low'
        })
    
    return {
        "triggered": len(triggers_activated) > 0,
        "triggers_activated": triggers_activated,
        "triggers_data": triggers_data,
        "weather_api_used": "Open-Meteo (FREE)" if not demo else "DEMO MODE",
        "message": f"{len(triggers_activated)} trigger(s) activated" if triggers_activated else "No triggers activated - conditions normal",
        "demo_mode": demo
    }

@router.get("/history")
def get_trigger_history(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical trigger events"""
    # This would query DisruptionEvent model
    from ..models import DisruptionEvent
    events = db.query(DisruptionEvent).filter(
        DisruptionEvent.city == current_user.city,
        DisruptionEvent.zone == current_user.zone
    ).order_by(DisruptionEvent.detected_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            'id': e.id,
            'trigger_type': e.trigger_type,
            'severity': e.severity,
            'detected_at': e.detected_at.isoformat(),
            'weather_conditions': e.weather_conditions,
            'affected_users': e.affected_users_count
        }
        for e in events
    ]

@router.get("/active")
def get_active_triggers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get currently active triggers in user's zone"""
    from ..models import DisruptionEvent
    from datetime import datetime, timedelta
    
    # Get events from last 24 hours
    recent_events = db.query(DisruptionEvent).filter(
        DisruptionEvent.city == current_user.city,
        DisruptionEvent.zone == current_user.zone,
        DisruptionEvent.detected_at >= datetime.utcnow() - timedelta(hours=24)
    ).all()
    
    return {
        'active_count': len(recent_events),
        'events': [
            {
                'type': e.trigger_type,
                'severity': e.severity,
                'detected_at': e.detected_at.isoformat()
            }
            for e in recent_events
        ]
    }
