import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class DigitalTwinSimulator:
    
    def __init__(self):
        self.city_models = self._initialize_city_models()
    
    def _initialize_city_models(self) -> Dict:
        return {
            'Delhi': {
                'zones': ['South Delhi', 'North Delhi', 'East Delhi', 'West Delhi', 'Central Delhi'],
                'avg_workers_per_zone': 500,
                'avg_hourly_deliveries': 3,
                'avg_earnings_per_delivery': 50,
                'flood_prone_zones': ['East Delhi', 'North Delhi'],
                'traffic_prone_zones': ['Central Delhi', 'South Delhi']
            },
            'Mumbai': {
                'zones': ['Andheri', 'Bandra', 'Dadar', 'Malad', 'Borivali'],
                'avg_workers_per_zone': 600,
                'avg_hourly_deliveries': 4,
                'avg_earnings_per_delivery': 60,
                'flood_prone_zones': ['Andheri', 'Malad'],
                'traffic_prone_zones': ['Bandra', 'Dadar']
            },
            'Bangalore': {
                'zones': ['Whitefield', 'Koramangala', 'Indiranagar', 'Marathahalli', 'Electronic City'],
                'avg_workers_per_zone': 450,
                'avg_hourly_deliveries': 3.5,
                'avg_earnings_per_delivery': 55,
                'flood_prone_zones': ['Marathahalli'],
                'traffic_prone_zones': ['Whitefield', 'Electronic City', 'Marathahalli']
            }
        }
    
    def simulate_disruption_impact(self, city: str, disruption_type: str, 
                                   disruption_data: Dict) -> Dict:
        if city not in self.city_models:
            city = 'Delhi'
        
        city_model = self.city_models[city]
        
        affected_zones = self._identify_affected_zones(city, disruption_type, disruption_data)
        
        total_impact = {
            'city': city,
            'disruption_type': disruption_type,
            'affected_zones': affected_zones,
            'total_workers_affected': 0,
            'total_estimated_loss': 0,
            'zone_impacts': [],
            'duration_hours': disruption_data.get('duration_hours', 4),
            'severity': self._calculate_severity(disruption_type, disruption_data)
        }
        
        for zone_name in affected_zones:
            zone_impact = self._simulate_zone_impact(
                city_model, zone_name, disruption_type, disruption_data
            )
            total_impact['zone_impacts'].append(zone_impact)
            total_impact['total_workers_affected'] += zone_impact['workers_affected']
            total_impact['total_estimated_loss'] += zone_impact['total_loss']
        
        total_impact['avg_loss_per_worker'] = (
            total_impact['total_estimated_loss'] / total_impact['total_workers_affected']
            if total_impact['total_workers_affected'] > 0 else 0
        )
        
        total_impact['recommendations'] = self._generate_simulation_recommendations(total_impact)
        
        return total_impact
    
    def _identify_affected_zones(self, city: str, disruption_type: str, 
                                 disruption_data: Dict) -> List[str]:
        city_model = self.city_models[city]
        all_zones = city_model['zones']
        
        if disruption_type == 'rainfall':
            rainfall_mm = disruption_data.get('rainfall_mm', 0)
            if rainfall_mm > 80:
                return all_zones
            elif rainfall_mm > 50:
                return city_model['flood_prone_zones'] + [all_zones[0]]
            else:
                return city_model['flood_prone_zones']
        
        elif disruption_type == 'traffic':
            congestion = disruption_data.get('congestion_level', 0.5)
            if congestion > 0.8:
                return all_zones
            else:
                return city_model['traffic_prone_zones']
        
        elif disruption_type == 'air_quality':
            aqi = disruption_data.get('aqi', 100)
            if aqi > 300:
                return all_zones
            else:
                return all_zones[:3]
        
        else:
            return all_zones[:2]
    
    def _simulate_zone_impact(self, city_model: Dict, zone: str, 
                             disruption_type: str, disruption_data: Dict) -> Dict:
        workers_in_zone = city_model['avg_workers_per_zone']
        hourly_deliveries = city_model['avg_hourly_deliveries']
        earnings_per_delivery = city_model['avg_earnings_per_delivery']
        duration_hours = disruption_data.get('duration_hours', 4)
        
        if disruption_type == 'rainfall':
            rainfall_mm = disruption_data.get('rainfall_mm', 0)
            if rainfall_mm > 80:
                activity_reduction = 0.8
            elif rainfall_mm > 50:
                activity_reduction = 0.5
            else:
                activity_reduction = 0.3
        elif disruption_type == 'traffic':
            congestion = disruption_data.get('congestion_level', 0.5)
            activity_reduction = congestion * 0.6
        elif disruption_type == 'air_quality':
            aqi = disruption_data.get('aqi', 100)
            if aqi > 300:
                activity_reduction = 0.7
            elif aqi > 200:
                activity_reduction = 0.4
            else:
                activity_reduction = 0.2
        else:
            activity_reduction = 0.3
        
        workers_affected = int(workers_in_zone * activity_reduction)
        
        deliveries_lost_per_worker = hourly_deliveries * duration_hours * activity_reduction
        loss_per_worker = deliveries_lost_per_worker * earnings_per_delivery
        total_loss = workers_affected * loss_per_worker
        
        return {
            'zone': zone,
            'workers_affected': workers_affected,
            'activity_reduction_percentage': round(activity_reduction * 100, 1),
            'deliveries_lost_per_worker': round(deliveries_lost_per_worker, 2),
            'loss_per_worker': round(loss_per_worker, 2),
            'total_loss': round(total_loss, 2),
            'duration_hours': duration_hours
        }
    
    def _calculate_severity(self, disruption_type: str, data: Dict) -> str:
        if disruption_type == 'rainfall':
            rainfall = data.get('rainfall_mm', 0)
            if rainfall > 80:
                return 'CRITICAL'
            elif rainfall > 50:
                return 'HIGH'
            else:
                return 'MEDIUM'
        
        elif disruption_type == 'traffic':
            congestion = data.get('congestion_level', 0.5)
            if congestion > 0.8:
                return 'HIGH'
            elif congestion > 0.6:
                return 'MEDIUM'
            else:
                return 'LOW'
        
        elif disruption_type == 'air_quality':
            aqi = data.get('aqi', 100)
            if aqi > 300:
                return 'CRITICAL'
            elif aqi > 200:
                return 'HIGH'
            else:
                return 'MEDIUM'
        
        return 'MEDIUM'
    
    def _generate_simulation_recommendations(self, impact: Dict) -> List[str]:
        recommendations = []
        
        severity = impact['severity']
        workers_affected = impact['total_workers_affected']
        avg_loss = impact['avg_loss_per_worker']
        
        if severity in ['CRITICAL', 'HIGH']:
            recommendations.append(f"Deploy emergency support for {workers_affected} affected workers")
            recommendations.append("Activate automatic claim processing")
            recommendations.append("Send real-time alerts to workers in affected zones")
        
        if avg_loss > 500:
            recommendations.append("Consider increasing coverage limits for affected areas")
        
        if workers_affected > 1000:
            recommendations.append("Coordinate with delivery platforms for workforce redistribution")
        
        recommendations.append(f"Estimated total payout: ₹{impact['total_estimated_loss']:,.2f}")
        
        return recommendations
    
    def predict_future_disruptions(self, city: str, days_ahead: int = 7) -> List[Dict]:
        predictions = []
        
        current_date = datetime.now()
        
        for day in range(days_ahead):
            prediction_date = current_date + timedelta(days=day)
            
            rainfall_prob = np.random.random()
            traffic_prob = 0.6 if prediction_date.weekday() < 5 else 0.3
            
            disruptions = []
            
            if rainfall_prob > 0.7:
                disruptions.append({
                    'type': 'rainfall',
                    'probability': round(rainfall_prob, 2),
                    'expected_rainfall_mm': round(np.random.uniform(30, 100), 1),
                    'expected_duration_hours': round(np.random.uniform(2, 6), 1)
                })
            
            if traffic_prob > 0.5:
                disruptions.append({
                    'type': 'traffic',
                    'probability': round(traffic_prob, 2),
                    'expected_congestion': round(np.random.uniform(0.5, 0.9), 2),
                    'peak_hours': ['8-10 AM', '6-9 PM']
                })
            
            if len(disruptions) > 0:
                predictions.append({
                    'date': prediction_date.strftime('%Y-%m-%d'),
                    'day_of_week': prediction_date.strftime('%A'),
                    'disruptions': disruptions,
                    'overall_risk': 'HIGH' if len(disruptions) > 1 else 'MEDIUM'
                })
        
        return predictions
    
    def simulate_market_crash_scenario(self, city: str, coordinated_claims: int) -> Dict:
        legitimate_ratio = 0.3
        fraudulent_ratio = 0.7
        
        legitimate_claims = int(coordinated_claims * legitimate_ratio)
        fraudulent_claims = int(coordinated_claims * fraudulent_ratio)
        
        avg_payout = 1000
        total_exposure = coordinated_claims * avg_payout
        
        fraud_detection_rate = 0.95
        detected_fraud = int(fraudulent_claims * fraud_detection_rate)
        undetected_fraud = fraudulent_claims - detected_fraud
        
        actual_payout = (legitimate_claims + undetected_fraud) * avg_payout
        blocked_payout = detected_fraud * avg_payout
        
        return {
            'scenario': 'Market Crash Attack',
            'total_claims': coordinated_claims,
            'legitimate_claims': legitimate_claims,
            'fraudulent_claims': fraudulent_claims,
            'fraud_detection_rate': round(fraud_detection_rate * 100, 1),
            'detected_fraud': detected_fraud,
            'undetected_fraud': undetected_fraud,
            'total_exposure': round(total_exposure, 2),
            'actual_payout': round(actual_payout, 2),
            'blocked_payout': round(blocked_payout, 2),
            'savings_percentage': round((blocked_payout / total_exposure) * 100, 1),
            'system_resilience': 'HIGH' if fraud_detection_rate > 0.9 else 'MEDIUM'
        }
