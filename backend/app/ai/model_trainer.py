"""
AI Model Training Module
Trains all AI/ML models with synthetic and real data
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
from datetime import datetime, timedelta
import random

class ModelTrainer:
    def __init__(self, model_dir="models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
    def generate_synthetic_risk_data(self, n_samples=10000):
        """Generate synthetic data for risk model training"""
        data = {
            'city': np.random.choice(['delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata'], n_samples),
            'zone': np.random.choice(['central', 'north', 'south', 'east', 'west'], n_samples),
            'hour': np.random.randint(0, 24, n_samples),
            'day_of_week': np.random.randint(0, 7, n_samples),
            'month': np.random.randint(1, 13, n_samples),
            'rainfall_mm': np.random.exponential(20, n_samples),
            'aqi': np.random.normal(150, 80, n_samples).clip(0, 500),
            'traffic_congestion': np.random.beta(2, 5, n_samples),
            'work_hours': np.random.uniform(4, 12, n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Generate risk scores based on features
        df['risk_score'] = (
            (df['rainfall_mm'] > 50).astype(int) * 0.3 +
            (df['aqi'] > 200).astype(int) * 0.25 +
            (df['traffic_congestion'] > 0.7).astype(int) * 0.2 +
            ((df['hour'] >= 18) | (df['hour'] <= 6)).astype(int) * 0.15 +
            (df['day_of_week'] >= 5).astype(int) * 0.1 +
            np.random.normal(0, 0.1, n_samples)
        ).clip(0, 1)
        
        df['risk_level'] = pd.cut(df['risk_score'], 
                                   bins=[0, 0.33, 0.66, 1.0], 
                                   labels=['LOW', 'MEDIUM', 'HIGH'])
        
        return df
    
    def generate_synthetic_fraud_data(self, n_samples=5000):
        """Generate synthetic data for fraud detection"""
        data = {
            'claim_amount': np.random.lognormal(5, 1, n_samples),
            'time_since_signup_days': np.random.exponential(180, n_samples),
            'claims_count': np.random.poisson(2, n_samples),
            'gps_accuracy': np.random.beta(8, 2, n_samples),
            'speed_kmph': np.random.gamma(2, 10, n_samples),
            'location_consistency': np.random.beta(7, 3, n_samples),
            'time_of_day': np.random.randint(0, 24, n_samples),
            'device_changes': np.random.poisson(0.5, n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Generate fraud labels based on suspicious patterns
        fraud_probability = (
            (df['claim_amount'] > df['claim_amount'].quantile(0.95)).astype(int) * 0.3 +
            (df['time_since_signup_days'] < 30).astype(int) * 0.2 +
            (df['claims_count'] > 5).astype(int) * 0.2 +
            (df['gps_accuracy'] < 0.5).astype(int) * 0.15 +
            (df['location_consistency'] < 0.5).astype(int) * 0.15 +
            np.random.normal(0, 0.1, n_samples)
        ).clip(0, 1)
        
        df['is_fraud'] = (fraud_probability > 0.5).astype(int)
        df['fraud_score'] = fraud_probability
        
        return df
    
    def train_risk_model(self):
        """Train risk prediction model"""
        print("Training Risk Intelligence Model...")
        
        # Generate training data
        df = self.generate_synthetic_risk_data(10000)
        
        # Encode categorical variables
        le_city = LabelEncoder()
        le_zone = LabelEncoder()
        
        df['city_encoded'] = le_city.fit_transform(df['city'])
        df['zone_encoded'] = le_zone.fit_transform(df['zone'])
        
        # Features
        feature_cols = ['city_encoded', 'zone_encoded', 'hour', 'day_of_week', 
                       'month', 'rainfall_mm', 'aqi', 'traffic_congestion', 'work_hours']
        X = df[feature_cols]
        y = df['risk_score']
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        
        # Evaluate
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        print(f"Risk Model - Train R²: {train_score:.4f}, Test R²: {test_score:.4f}")
        
        # Save model and encoders
        joblib.dump({
            'model': model,
            'city_encoder': le_city,
            'zone_encoder': le_zone,
            'feature_columns': feature_cols
        }, os.path.join(self.model_dir, 'risk_model.pkl'))
        
        print(f"Risk model saved to {self.model_dir}/risk_model.pkl")
        return model
    
    def train_fraud_model(self):
        """Train fraud detection model"""
        print("\nTraining Fraud Detection Model...")
        
        # Generate training data
        df = self.generate_synthetic_fraud_data(5000)
        
        # Features
        feature_cols = ['claim_amount', 'time_since_signup_days', 'claims_count',
                       'gps_accuracy', 'speed_kmph', 'location_consistency', 
                       'time_of_day', 'device_changes']
        X = df[feature_cols]
        y = df['is_fraud']
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, class_weight='balanced')
        model.fit(X_train, y_train)
        
        # Evaluate
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        print(f"Fraud Model - Train Accuracy: {train_score:.4f}, Test Accuracy: {test_score:.4f}")
        
        # Save model and scaler
        joblib.dump({
            'model': model,
            'scaler': scaler,
            'feature_columns': feature_cols
        }, os.path.join(self.model_dir, 'fraud_model.pkl'))
        
        print(f"Fraud model saved to {self.model_dir}/fraud_model.pkl")
        return model
    
    def train_pricing_model(self):
        """Train dynamic pricing model"""
        print("\nTraining Dynamic Pricing Model...")
        
        # Generate pricing data
        n_samples = 3000
        data = {
            'base_premium': np.random.uniform(30, 100, n_samples),
            'risk_score': np.random.beta(2, 5, n_samples),
            'trust_score': np.random.beta(5, 2, n_samples),
            'zone_multiplier': np.random.choice([0.8, 1.0, 1.2, 1.5], n_samples),
            'claims_history': np.random.poisson(2, n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Calculate optimal premium
        df['optimal_premium'] = (
            df['base_premium'] * 
            (1 + df['risk_score'] * 0.5) *
            (1 - (df['trust_score'] - 0.5) * 0.3) *
            df['zone_multiplier']
        ).clip(20, 150)
        
        # Features
        feature_cols = ['base_premium', 'risk_score', 'trust_score', 'zone_multiplier', 'claims_history']
        X = df[feature_cols]
        y = df['optimal_premium']
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model - using regressor for continuous premium values
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        
        # Evaluate
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        print(f"Pricing Model - Train R²: {train_score:.4f}, Test R²: {test_score:.4f}")
        
        # Save model
        joblib.dump({
            'model': model,
            'feature_columns': feature_cols
        }, os.path.join(self.model_dir, 'pricing_model.pkl'))
        
        print(f"Pricing model saved to {self.model_dir}/pricing_model.pkl")
        return model
    
    def train_all_models(self):
        """Train all AI/ML models"""
        print("=" * 60)
        print("VORTEX Shield 2.0 - AI Model Training")
        print("=" * 60)
        
        risk_model = self.train_risk_model()
        fraud_model = self.train_fraud_model()
        pricing_model = self.train_pricing_model()
        
        print("\n" + "=" * 60)
        print("All models trained successfully!")
        print(f"Models saved to: {os.path.abspath(self.model_dir)}")
        print("=" * 60)
        
        return {
            'risk_model': risk_model,
            'fraud_model': fraud_model,
            'pricing_model': pricing_model
        }

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.train_all_models()
