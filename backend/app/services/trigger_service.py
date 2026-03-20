from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import DisruptionEvent, User, Claim
from .weather_service import WeatherService
from ..core.config import settings

class ParametricTriggerService:
    
    def __init__(self, db: Session):
        self.db = db
        self.weather_service = WeatherService(settings.OPENWEATHER_API_KEY)
    
    def check_triggers(self, user: User) -> Dict:
        if not user.latitude or not user.longitude:
            return {
                'triggered': False,
                'reason': 'Location not available'
            }
        
        weather_data = self.weather_service.get_current_weather(
            user.latitude, user.longitude
        )
        
        aqi_data = self.weather_service.get_air_quality(
            user.latitude, user.longitude
        )
        
        traffic_data = self.weather_service.get_traffic_data(
            user.latitude, user.longitude
        )
        
        triggers = []
        
        rainfall_mm = weather_data.get('rainfall_mm', 0)
        if rainfall_mm >= settings.RAINFALL_THRESHOLD_MM:
            triggers.append({
                'type': 'rainfall',
                'severity': 'HIGH' if rainfall_mm > 80 else 'MEDIUM',
                'value': rainfall_mm,
                'threshold': settings.RAINFALL_THRESHOLD_MM,
                'description': f'Heavy rainfall detected: {rainfall_mm}mm'
            })
        
        aqi = aqi_data.get('aqi', 0)
        if aqi >= settings.AQI_THRESHOLD:
            triggers.append({
                'type': 'air_quality',
                'severity': 'HIGH' if aqi > 300 else 'MEDIUM',
                'value': aqi,
                'threshold': settings.AQI_THRESHOLD,
                'description': f'Poor air quality: AQI {aqi}'
            })
        
        traffic_congestion = traffic_data.get('congestion_level', 0)
        if traffic_congestion >= settings.TRAFFIC_JAM_THRESHOLD:
            triggers.append({
                'type': 'traffic',
                'severity': 'HIGH' if traffic_congestion > 0.85 else 'MEDIUM',
                'value': traffic_congestion,
                'threshold': settings.TRAFFIC_JAM_THRESHOLD,
                'description': f'Heavy traffic congestion: {traffic_congestion*100:.0f}%'
            })
        
        triggered = len(triggers) > 0
        
        return {
            'triggered': triggered,
            'trigger_count': len(triggers),
            'triggers': triggers,
            'weather_data': weather_data,
            'aqi_data': aqi_data,
            'traffic_data': traffic_data,
            'timestamp': datetime.now().isoformat()
        }
    
    def create_disruption_event(self, city: str, zone: str, 
                               trigger_data: Dict) -> DisruptionEvent:
        trigger = trigger_data['triggers'][0] if trigger_data['triggers'] else {}
        
        event = DisruptionEvent(
            event_type=trigger.get('type', 'unknown'),
            severity=trigger.get('severity', 'MEDIUM'),
            city=city,
            zone=zone,
            weather_data=trigger_data.get('weather_data', {}),
            traffic_data=trigger_data.get('traffic_data', {}),
            aqi_data=trigger_data.get('aqi_data', {}),
            rainfall_mm=trigger_data.get('weather_data', {}).get('rainfall_mm', 0),
            temperature_c=trigger_data.get('weather_data', {}).get('temperature_c'),
            aqi_value=trigger_data.get('aqi_data', {}).get('aqi'),
            traffic_congestion=trigger_data.get('traffic_data', {}).get('congestion_level', 0),
            is_active=True,
            validated=False,
            start_time=datetime.now()
        )
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        return event
    
    def validate_with_crowd(self, event_id: int) -> Dict:
        event = self.db.query(DisruptionEvent).filter(
            DisruptionEvent.id == event_id
        ).first()
        
        if not event:
            return {'validated': False, 'reason': 'Event not found'}
        
        affected_users = self.db.query(User).filter(
            User.city == event.city,
            User.zone == event.zone,
            User.is_active == True
        ).all()
        
        inactive_users = []
        for user in affected_users[:20]:
            if user.last_gps_update:
                time_diff = (datetime.now() - user.last_gps_update).total_seconds()
                if time_diff > 1800:
                    inactive_users.append(user.id)
        
        crowd_reports = len(inactive_users)
        event.crowd_reports = crowd_reports
        
        if crowd_reports >= settings.CROWD_VALIDATION_MIN_USERS:
            event.validated = True
            validation_status = 'VALIDATED'
        else:
            validation_status = 'PENDING'
        
        self.db.commit()
        
        return {
            'validated': event.validated,
            'validation_status': validation_status,
            'crowd_reports': crowd_reports,
            'required_reports': settings.CROWD_VALIDATION_MIN_USERS,
            'affected_users': len(affected_users),
            'inactive_users': len(inactive_users)
        }
    
    def calculate_disruption_loss(self, user: User, disruption_event: DisruptionEvent, 
                                 duration_hours: float = 4.0) -> float:
        hourly_earnings = user.avg_daily_earnings / user.work_hours_per_day
        
        if disruption_event.event_type == 'rainfall':
            if disruption_event.rainfall_mm > 80:
                loss_percentage = 0.8
            elif disruption_event.rainfall_mm > 50:
                loss_percentage = 0.5
            else:
                loss_percentage = 0.3
        
        elif disruption_event.event_type == 'air_quality':
            if disruption_event.aqi_value > 300:
                loss_percentage = 0.7
            elif disruption_event.aqi_value > 200:
                loss_percentage = 0.4
            else:
                loss_percentage = 0.2
        
        elif disruption_event.event_type == 'traffic':
            loss_percentage = disruption_event.traffic_congestion * 0.6
        
        else:
            loss_percentage = 0.3
        
        estimated_loss = hourly_earnings * duration_hours * loss_percentage
        
        max_coverage = 5000.0
        estimated_loss = min(estimated_loss, max_coverage)
        
        return round(estimated_loss, 2)
