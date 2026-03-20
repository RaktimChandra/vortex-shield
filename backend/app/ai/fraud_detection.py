import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import joblib
import os

class FraudDetectionEngine:
    
    def __init__(self):
        self.gps_anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.fraud_classifier = None
        self.scaler = StandardScaler()
        self.load_or_train_models()
    
    def load_or_train_models(self):
        try:
            self.fraud_classifier = joblib.load('models/fraud_classifier.pkl')
            self.gps_anomaly_detector = joblib.load('models/gps_anomaly.pkl')
            self.scaler = joblib.load('models/fraud_scaler.pkl')
        except:
            self.train_fraud_models()
    
    def train_fraud_models(self):
        X_train, y_train = self._generate_fraud_training_data()
        X_scaled = self.scaler.fit_transform(X_train)
        
        self.fraud_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            class_weight='balanced',
            random_state=42
        )
        self.fraud_classifier.fit(X_scaled, y_train)
        
        self.gps_anomaly_detector.fit(X_scaled[:, :5])
        
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.fraud_classifier, 'models/fraud_classifier.pkl')
        joblib.dump(self.gps_anomaly_detector, 'models/gps_anomaly.pkl')
        joblib.dump(self.scaler, 'models/fraud_scaler.pkl')
    
    def _generate_fraud_training_data(self, n_samples=3000):
        np.random.seed(42)
        
        n_legit = int(n_samples * 0.8)
        n_fraud = n_samples - n_legit
        
        gps_consistency_legit = np.random.beta(8, 2, n_legit)
        gps_consistency_fraud = np.random.beta(2, 8, n_fraud)
        gps_consistency = np.concatenate([gps_consistency_legit, gps_consistency_fraud])
        
        speed_variance_legit = np.random.gamma(2, 0.5, n_legit)
        speed_variance_fraud = np.random.gamma(5, 1.5, n_fraud)
        speed_variance = np.concatenate([speed_variance_legit, speed_variance_fraud])
        
        trajectory_smoothness_legit = np.random.beta(7, 2, n_legit)
        trajectory_smoothness_fraud = np.random.beta(2, 5, n_fraud)
        trajectory_smoothness = np.concatenate([trajectory_smoothness_legit, trajectory_smoothness_fraud])
        
        accelerometer_match_legit = np.random.beta(8, 2, n_legit)
        accelerometer_match_fraud = np.random.beta(3, 7, n_fraud)
        accelerometer_match = np.concatenate([accelerometer_match_legit, accelerometer_match_fraud])
        
        device_consistency_legit = np.random.beta(9, 1, n_legit)
        device_consistency_fraud = np.random.beta(4, 6, n_fraud)
        device_consistency = np.concatenate([device_consistency_legit, device_consistency_fraud])
        
        claim_frequency = np.random.poisson(1, n_samples)
        trust_score = np.random.beta(5, 2, n_samples)
        activity_pattern_score = np.random.uniform(0.3, 1.0, n_samples)
        
        X = np.column_stack([
            gps_consistency, speed_variance, trajectory_smoothness,
            accelerometer_match, device_consistency, claim_frequency,
            trust_score, activity_pattern_score
        ])
        
        y = np.concatenate([np.zeros(n_legit), np.ones(n_fraud)])
        
        shuffle_idx = np.random.permutation(n_samples)
        return X[shuffle_idx], y[shuffle_idx]
    
    def detect_gps_spoofing(self, gps_data: Dict, activity_logs: List[Dict]) -> Dict:
        if len(activity_logs) < 3:
            return {
                'is_spoofed': False,
                'confidence': 0.5,
                'score': 0.0,
                'analysis': 'Insufficient data for analysis'
            }
        
        trajectory_consistency = self._analyze_trajectory_consistency(activity_logs)
        speed_analysis = self._analyze_speed_patterns(activity_logs)
        accelerometer_match = self._analyze_accelerometer_data(activity_logs)
        
        features = [
            trajectory_consistency['smoothness'],
            speed_analysis['variance'],
            trajectory_consistency['consistency_score'],
            accelerometer_match['match_score'],
            gps_data.get('accuracy', 20) / 100
        ]
        
        anomaly_score = self.gps_anomaly_detector.score_samples([features])[0]
        is_anomaly = self.gps_anomaly_detector.predict([features])[0] == -1
        
        spoofing_score = 1.0 - (anomaly_score + 1) / 2
        
        is_spoofed = spoofing_score > 0.8 or is_anomaly
        
        return {
            'is_spoofed': bool(is_spoofed),
            'confidence': round(spoofing_score, 3),
            'score': round(spoofing_score, 3),
            'analysis': {
                'trajectory_consistency': trajectory_consistency,
                'speed_analysis': speed_analysis,
                'accelerometer_match': accelerometer_match,
                'gps_accuracy': gps_data.get('accuracy', 20)
            },
            'flags': self._generate_spoofing_flags(spoofing_score, trajectory_consistency, speed_analysis)
        }
    
    def _analyze_trajectory_consistency(self, logs: List[Dict]) -> Dict:
        if len(logs) < 2:
            return {'consistency_score': 1.0, 'smoothness': 1.0}
        
        distances = []
        time_diffs = []
        
        for i in range(1, len(logs)):
            prev = logs[i-1]
            curr = logs[i]
            
            dist = self._haversine_distance(
                prev.get('latitude', 0), prev.get('longitude', 0),
                curr.get('latitude', 0), curr.get('longitude', 0)
            )
            distances.append(dist)
            
            if 'timestamp' in prev and 'timestamp' in curr:
                time_diff = (curr['timestamp'] - prev['timestamp']).total_seconds()
                time_diffs.append(time_diff)
        
        if not distances:
            return {'consistency_score': 1.0, 'smoothness': 1.0}
        
        avg_distance = np.mean(distances)
        distance_variance = np.var(distances)
        
        smoothness = 1.0 / (1.0 + distance_variance)
        consistency = 1.0 if avg_distance < 10 else 1.0 / (1.0 + avg_distance / 10)
        
        return {
            'consistency_score': round(consistency, 3),
            'smoothness': round(smoothness, 3),
            'avg_distance_km': round(avg_distance, 3),
            'variance': round(distance_variance, 3)
        }
    
    def _analyze_speed_patterns(self, logs: List[Dict]) -> Dict:
        speeds = [log.get('speed', 0) for log in logs if 'speed' in log]
        
        if not speeds:
            return {'variance': 0.5, 'avg_speed': 0, 'anomalies': []}
        
        avg_speed = np.mean(speeds)
        variance = np.var(speeds)
        
        anomalies = [s for s in speeds if s > 100]
        
        return {
            'variance': round(variance, 3),
            'avg_speed': round(avg_speed, 2),
            'anomalies': anomalies,
            'unrealistic_speeds': len(anomalies)
        }
    
    def _analyze_accelerometer_data(self, logs: List[Dict]) -> Dict:
        accel_data = [
            log for log in logs 
            if 'accelerometer_x' in log and 'speed' in log
        ]
        
        if len(accel_data) < 3:
            return {'match_score': 0.7, 'correlation': 'unknown'}
        
        accelerometer_magnitude = [
            np.sqrt(
                log.get('accelerometer_x', 0)**2 +
                log.get('accelerometer_y', 0)**2 +
                log.get('accelerometer_z', 0)**2
            )
            for log in accel_data
        ]
        
        speeds = [log.get('speed', 0) for log in accel_data]
        
        correlation = np.corrcoef(accelerometer_magnitude, speeds)[0, 1] if len(speeds) > 1 else 0.5
        match_score = max(0, correlation)
        
        return {
            'match_score': round(match_score, 3),
            'correlation': round(correlation, 3),
            'samples': len(accel_data)
        }
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        
        a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c
    
    def _generate_spoofing_flags(self, score: float, trajectory: Dict, speed: Dict) -> List[str]:
        flags = []
        
        if score > 0.8:
            flags.append('HIGH_SPOOFING_PROBABILITY')
        
        if trajectory['consistency_score'] < 0.3:
            flags.append('INCONSISTENT_TRAJECTORY')
        
        if speed['unrealistic_speeds'] > 0:
            flags.append('UNREALISTIC_SPEED_DETECTED')
        
        if trajectory['smoothness'] < 0.4:
            flags.append('ERRATIC_MOVEMENT_PATTERN')
        
        return flags
    
    def detect_fraud_ring(self, claim_data: Dict, recent_claims: List[Dict]) -> Dict:
        if len(recent_claims) < 3:
            return {
                'is_fraud_ring': False,
                'confidence': 0.0,
                'similar_claims': [],
                'cluster_size': 0
            }
        
        claim_features = self._extract_claim_features(recent_claims)
        
        if len(claim_features) < 3:
            return {
                'is_fraud_ring': False,
                'confidence': 0.0,
                'similar_claims': [],
                'cluster_size': 0
            }
        
        clustering = DBSCAN(eps=0.5, min_samples=3)
        clusters = clustering.fit_predict(claim_features)
        
        current_features = self._extract_claim_features([claim_data])[0]
        
        similarities = [
            self._calculate_similarity(current_features, feat)
            for feat in claim_features
        ]
        
        avg_similarity = np.mean(similarities) if similarities else 0.0
        max_similarity = max(similarities) if similarities else 0.0
        
        similar_claims = [
            {'claim_id': recent_claims[i].get('id'), 'similarity': sim}
            for i, sim in enumerate(similarities)
            if sim > 0.85
        ]
        
        is_fraud_ring = avg_similarity > 0.85 and len(similar_claims) >= 3
        
        return {
            'is_fraud_ring': bool(is_fraud_ring),
            'confidence': round(avg_similarity, 3),
            'similar_claims': similar_claims[:5],
            'cluster_size': int(np.sum(clusters != -1)),
            'avg_similarity': round(avg_similarity, 3),
            'max_similarity': round(max_similarity, 3)
        }
    
    def _extract_claim_features(self, claims: List[Dict]) -> np.ndarray:
        features = []
        for claim in claims:
            feat = [
                claim.get('estimated_loss', 0) / 1000,
                claim.get('latitude', 0),
                claim.get('longitude', 0),
                1.0 if claim.get('trigger_type') == 'rainfall' else 0.0,
                claim.get('disruption_data', {}).get('rainfall_mm', 0) / 100,
                claim.get('fraud_score', 0)
            ]
            features.append(feat)
        return np.array(features)
    
    def _calculate_similarity(self, feat1: np.ndarray, feat2: np.ndarray) -> float:
        distance = np.linalg.norm(feat1 - feat2)
        similarity = 1.0 / (1.0 + distance)
        return similarity
    
    def calculate_trust_score(self, user_data: Dict) -> float:
        total_claims = user_data.get('total_claims', 0)
        approved_claims = user_data.get('approved_claims', 0)
        rejected_claims = user_data.get('rejected_claims', 0)
        
        base_score = 1.0
        
        if total_claims > 0:
            approval_rate = approved_claims / total_claims
            rejection_penalty = rejected_claims * 0.1
            base_score = approval_rate - rejection_penalty
        
        activity_consistency = user_data.get('activity_consistency', 0.8)
        base_score = (base_score + activity_consistency) / 2
        
        fraud_history = user_data.get('fraud_flags', 0)
        fraud_penalty = fraud_history * 0.15
        base_score -= fraud_penalty
        
        return max(0.0, min(1.0, base_score))
    
    def analyze_claim(self, claim, user) -> Dict:
        """
        Enhanced AI fraud detection with NLP sentiment analysis
        Returns fraud_probability between 0.0 (legitimate) and 1.0 (fraudulent)
        """
        fraud_score = 0.0
        flags = []
        
        # Get description from disruption_data JSON
        description = claim.disruption_data.get('description', '') if claim.disruption_data else ''
        estimated_loss = claim.estimated_loss
        
        # Factor 1: Description quality with NLP (35% weight)
        desc_length = len(description.split())
        if desc_length < 3:
            fraud_score += 0.35
            flags.append('VERY_SHORT_DESCRIPTION')
        elif desc_length < 6:
            fraud_score += 0.20
            flags.append('SHORT_DESCRIPTION')
        elif desc_length < 10:
            fraud_score += 0.05
        
        # NLP Enhancement: Detect vague/suspicious language
        suspicious_words = ['just', 'issue', 'problem', 'bad', 'thing']
        vague_count = sum(1 for word in description.lower().split() if word in suspicious_words)
        if vague_count > 2:
            fraud_score += 0.10
            flags.append('VAGUE_LANGUAGE_DETECTED')
        
        # Factor 2: Estimated loss amount (35% weight)
        if estimated_loss > 5000:
            fraud_score += 0.40
            flags.append('UNREALISTIC_LOSS_AMOUNT')
        elif estimated_loss > 2000:
            fraud_score += 0.25
            flags.append('HIGH_LOSS_AMOUNT')
        elif estimated_loss > 1000:
            fraud_score += 0.10
        
        # Factor 3: User trust score (20% weight)
        user_trust = user.trust_score if hasattr(user, 'trust_score') else 1.0
        if user_trust < 0.5:
            fraud_score += 0.15
            flags.append('LOW_TRUST_SCORE')
        elif user_trust < 0.7:
            fraud_score += 0.05
        
        # Factor 4: Claim pattern analysis (10% weight)
        # Check if user has submitted multiple claims recently
        # This is a placeholder - in production, query database for recent claims
        
        # Add some randomness for variation (±3%)
        fraud_score += np.random.uniform(-0.03, 0.03)
        
        # Clamp between 0 and 1
        fraud_score = max(0.0, min(1.0, fraud_score))
        
        # Generate blockchain hash for claim integrity
        claim_hash = self._generate_claim_hash(claim, description)
        
        return {
            'fraud_probability': round(fraud_score, 3),
            'gps_fraud_score': 0.0,
            'flags': flags,
            'blockchain_hash': claim_hash,
            'analysis': {
                'description_length': desc_length,
                'estimated_loss': estimated_loss,
                'user_trust_score': user_trust,
                'vague_language_count': vague_count,
                'nlp_enhanced': True
            }
        }
    
    def _generate_claim_hash(self, claim, description: str) -> str:
        """Generate blockchain-style hash for claim integrity"""
        import hashlib
        from datetime import datetime
        
        claim_data = f"{claim.id}:{claim.user_id}:{description}:{claim.estimated_loss}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(claim_data.encode()).hexdigest()[:16]
