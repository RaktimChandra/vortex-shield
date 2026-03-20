import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import joblib
import os

class RiskIntelligenceEngine:
    
    def __init__(self):
        self.risk_model = None
        self.loss_predictor = None
        self.scaler = StandardScaler()
        self.load_or_train_models()
    
    def load_or_train_models(self):
        try:
            self.risk_model = joblib.load('models/risk_classifier.pkl')
            self.loss_predictor = joblib.load('models/loss_predictor.pkl')
            self.scaler = joblib.load('models/scaler.pkl')
        except:
            self.train_initial_models()
    
    def train_initial_models(self):
        X_train, y_risk, y_loss = self._generate_synthetic_training_data()
        
        X_scaled = self.scaler.fit_transform(X_train)
        
        self.risk_model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        self.risk_model.fit(X_scaled, y_risk)
        
        self.loss_predictor = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.loss_predictor.fit(X_scaled, y_loss)
        
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.risk_model, 'models/risk_classifier.pkl')
        joblib.dump(self.loss_predictor, 'models/loss_predictor.pkl')
        joblib.dump(self.scaler, 'models/scaler.pkl')
    
    def _generate_synthetic_training_data(self, n_samples=5000):
        np.random.seed(42)
        
        rainfall = np.random.exponential(20, n_samples)
        temperature = np.random.normal(30, 8, n_samples)
        aqi = np.random.gamma(2, 50, n_samples)
        traffic_congestion = np.random.beta(2, 5, n_samples)
        
        flood_risk = np.random.uniform(0, 1, n_samples)
        historical_disruptions = np.random.poisson(3, n_samples)
        zone_density = np.random.uniform(0.3, 1.0, n_samples)
        work_hours = np.random.uniform(6, 12, n_samples)
        avg_earnings = np.random.normal(500, 150, n_samples)
        
        X = np.column_stack([
            rainfall, temperature, aqi, traffic_congestion,
            flood_risk, historical_disruptions, zone_density,
            work_hours, avg_earnings
        ])
        
        risk_score = (
            (rainfall > 50) * 0.3 +
            (aqi > 200) * 0.25 +
            (traffic_congestion > 0.7) * 0.2 +
            flood_risk * 0.15 +
            (historical_disruptions > 5) * 0.1
        )
        
        y_risk = np.where(risk_score < 0.3, 0, np.where(risk_score < 0.6, 1, 2))
        
        income_loss = (
            rainfall * 5 +
            (aqi - 100) * 0.5 +
            traffic_congestion * 300 +
            flood_risk * 400 +
            historical_disruptions * 50
        )
        income_loss = np.clip(income_loss, 0, avg_earnings * 0.3)
        y_loss = income_loss
        
        return X, y_risk, y_loss
    
    def predict_risk(self, features: Dict) -> Dict:
        feature_vector = self._extract_features(features)
        feature_scaled = self.scaler.transform([feature_vector])
        
        risk_level_code = self.risk_model.predict(feature_scaled)[0]
        risk_proba = self.risk_model.predict_proba(feature_scaled)[0]
        
        predicted_loss = self.loss_predictor.predict(feature_scaled)[0]
        
        risk_levels = ["LOW", "MEDIUM", "HIGH"]
        risk_level = risk_levels[risk_level_code]
        
        risk_score = float(risk_proba[risk_level_code])
        
        disruption_probability = self._calculate_disruption_probability(features)
        
        return {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 3),
            "predicted_loss": round(predicted_loss, 2),
            "disruption_probability": round(disruption_probability, 3),
            "risk_factors": self._analyze_risk_factors(features),
            "recommendations": self._generate_recommendations(risk_level, features)
        }
    
    def _extract_features(self, data: Dict) -> List[float]:
        return [
            data.get('rainfall_mm', 0),
            data.get('temperature_c', 30),
            data.get('aqi', 100),
            data.get('traffic_congestion', 0.3),
            data.get('flood_risk_score', 0.2),
            data.get('historical_disruptions', 2),
            data.get('zone_density', 0.7),
            data.get('work_hours', 8),
            data.get('avg_daily_earnings', 500)
        ]
    
    def _calculate_disruption_probability(self, features: Dict) -> float:
        rainfall = features.get('rainfall_mm', 0)
        aqi = features.get('aqi', 100)
        traffic = features.get('traffic_congestion', 0.3)
        
        prob = 0.0
        if rainfall > 50:
            prob += 0.4
        elif rainfall > 30:
            prob += 0.2
        
        if aqi > 200:
            prob += 0.3
        elif aqi > 150:
            prob += 0.15
        
        if traffic > 0.7:
            prob += 0.3
        elif traffic > 0.5:
            prob += 0.15
        
        return min(prob, 0.95)
    
    def _analyze_risk_factors(self, features: Dict) -> Dict:
        factors = {}
        
        rainfall = features.get('rainfall_mm', 0)
        if rainfall > 50:
            factors['heavy_rain'] = {'severity': 'high', 'impact': 'High rainfall expected'}
        elif rainfall > 30:
            factors['moderate_rain'] = {'severity': 'medium', 'impact': 'Moderate rainfall'}
        
        aqi = features.get('aqi', 100)
        if aqi > 200:
            factors['poor_air_quality'] = {'severity': 'high', 'impact': 'Hazardous air quality'}
        elif aqi > 150:
            factors['moderate_aqi'] = {'severity': 'medium', 'impact': 'Unhealthy air quality'}
        
        traffic = features.get('traffic_congestion', 0.3)
        if traffic > 0.7:
            factors['heavy_traffic'] = {'severity': 'high', 'impact': 'Severe traffic congestion'}
        
        flood_risk = features.get('flood_risk_score', 0)
        if flood_risk > 0.7:
            factors['flood_risk'] = {'severity': 'high', 'impact': 'High flood risk zone'}
        
        return factors
    
    def _generate_recommendations(self, risk_level: str, features: Dict) -> List[str]:
        recommendations = []
        
        if risk_level == "HIGH":
            recommendations.append("Consider taking break during peak disruption hours")
            recommendations.append("Monitor weather updates closely")
            recommendations.append("Ensure insurance coverage is active")
        elif risk_level == "MEDIUM":
            recommendations.append("Stay updated on weather conditions")
            recommendations.append("Plan routes carefully")
        else:
            recommendations.append("Normal working conditions expected")
        
        return recommendations
    
    def calculate_zone_risk(self, city: str, zone: str) -> Dict:
        zone_risks = {
            'Delhi': {
                'South Delhi': 0.3,
                'North Delhi': 0.5,
                'East Delhi': 0.6,
                'West Delhi': 0.4,
                'Central Delhi': 0.35
            },
            'Mumbai': {
                'Andheri': 0.7,
                'Bandra': 0.5,
                'Dadar': 0.6,
                'Malad': 0.65,
                'Borivali': 0.55
            },
            'Bangalore': {
                'Whitefield': 0.4,
                'Koramangala': 0.45,
                'Indiranagar': 0.4,
                'Marathahalli': 0.6,
                'Electronic City': 0.5
            }
        }
        
        base_risk = zone_risks.get(city, {}).get(zone, 0.5)
        
        return {
            'zone': zone,
            'city': city,
            'base_risk_score': base_risk,
            'flood_prone': base_risk > 0.6,
            'traffic_prone': base_risk > 0.5,
            'historical_disruptions': int(base_risk * 10)
        }
