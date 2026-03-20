from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..models import Claim, User, Subscription, DisruptionEvent, FraudLog, ActivityLog
from ..ai import FraudDetectionEngine
from .trigger_service import ParametricTriggerService
import time

class ZeroTouchClaimService:
    
    def __init__(self, db: Session):
        self.db = db
        self.fraud_engine = FraudDetectionEngine()
        self.trigger_service = ParametricTriggerService(db)
    
    def auto_process_claim(self, user_id: int, trigger_data: Dict) -> Dict:
        start_time = time.time()
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        active_subscription = self.db.query(Subscription).filter(
            and_(
                Subscription.user_id == user_id,
                Subscription.status == 'active',
                Subscription.end_date > datetime.now()
            )
        ).first()
        
        if not active_subscription:
            return {'success': False, 'error': 'No active subscription'}
        
        disruption_event = self.trigger_service.create_disruption_event(
            user.city, user.zone, trigger_data
        )
        
        estimated_loss = self.trigger_service.calculate_disruption_loss(
            user, disruption_event
        )
        
        claim = Claim(
            user_id=user_id,
            subscription_id=active_subscription.id,
            claim_type='parametric',
            trigger_type=trigger_data['triggers'][0]['type'],
            disruption_data=trigger_data,
            weather_data=trigger_data.get('weather_data', {}),
            traffic_data=trigger_data.get('traffic_data', {}),
            estimated_loss=estimated_loss,
            status='processing'
        )
        
        self.db.add(claim)
        self.db.commit()
        self.db.refresh(claim)
        
        fraud_result = self._run_fraud_screening(claim, user)
        
        claim.fraud_score = fraud_result['fraud_score']
        claim.fraud_flags = fraud_result['fraud_flags']
        claim.fraud_analysis = fraud_result['analysis']
        
        crowd_validation = self.trigger_service.validate_with_crowd(disruption_event.id)
        claim.crowd_validation_count = crowd_validation['crowd_reports']
        
        approval_decision = self._make_approval_decision(claim, fraud_result, crowd_validation)
        
        if approval_decision['approved']:
            claim.status = 'approved'
            claim.approved_amount = approval_decision['payout_amount']
            claim.auto_approved = True
            claim.approval_reason = approval_decision['reason']
            
            payout_result = self._process_payout(claim)
            claim.payout_status = payout_result['status']
            claim.payout_transaction_id = payout_result['transaction_id']
            claim.payout_timestamp = datetime.now()
            
            user.total_claims += 1
            user.approved_claims += 1
        else:
            claim.status = 'rejected'
            claim.rejection_reason = approval_decision['reason']
            user.total_claims += 1
            user.rejected_claims += 1
        
        processing_time = time.time() - start_time
        claim.processing_time_seconds = round(processing_time, 2)
        
        self.db.commit()
        self.db.refresh(claim)
        
        return {
            'success': True,
            'claim_id': claim.id,
            'status': claim.status,
            'approved': claim.status == 'approved',
            'approved_amount': claim.approved_amount,
            'estimated_loss': estimated_loss,
            'fraud_score': claim.fraud_score,
            'processing_time_seconds': claim.processing_time_seconds,
            'payout_transaction_id': claim.payout_transaction_id,
            'reason': claim.approval_reason or claim.rejection_reason
        }
    
    def _run_fraud_screening(self, claim: Claim, user: User) -> Dict:
        recent_logs = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user.id
        ).order_by(ActivityLog.timestamp.desc()).limit(20).all()
        
        activity_logs = [
            {
                'latitude': log.latitude,
                'longitude': log.longitude,
                'speed': log.speed,
                'timestamp': log.timestamp,
                'accelerometer_x': log.accelerometer_x,
                'accelerometer_y': log.accelerometer_y,
                'accelerometer_z': log.accelerometer_z
            }
            for log in recent_logs
        ]
        
        gps_data = {
            'latitude': claim.disruption_data.get('weather_data', {}).get('coordinates', {}).get('latitude'),
            'longitude': claim.disruption_data.get('weather_data', {}).get('coordinates', {}).get('longitude'),
            'accuracy': 15
        }
        
        gps_spoofing = self.fraud_engine.detect_gps_spoofing(gps_data, activity_logs)
        
        recent_claims = self.db.query(Claim).filter(
            and_(
                Claim.created_at >= datetime.now() - timedelta(hours=24),
                Claim.id != claim.id
            )
        ).limit(50).all()
        
        claim_data_list = [
            {
                'id': c.id,
                'estimated_loss': c.estimated_loss,
                'latitude': c.gps_data.get('latitude') if c.gps_data else 0,
                'longitude': c.gps_data.get('longitude') if c.gps_data else 0,
                'trigger_type': c.trigger_type,
                'disruption_data': c.disruption_data,
                'fraud_score': c.fraud_score or 0
            }
            for c in recent_claims
        ]
        
        current_claim_data = {
            'id': claim.id,
            'estimated_loss': claim.estimated_loss,
            'latitude': gps_data.get('latitude', 0),
            'longitude': gps_data.get('longitude', 0),
            'trigger_type': claim.trigger_type,
            'disruption_data': claim.disruption_data,
            'fraud_score': 0
        }
        
        fraud_ring = self.fraud_engine.detect_fraud_ring(current_claim_data, claim_data_list)
        
        user_trust_data = {
            'total_claims': user.total_claims,
            'approved_claims': user.approved_claims,
            'rejected_claims': user.rejected_claims,
            'activity_consistency': 0.8,
            'fraud_flags': len(self.db.query(FraudLog).filter(
                FraudLog.user_id == user.id,
                FraudLog.flagged == True
            ).all())
        }
        
        trust_score = self.fraud_engine.calculate_trust_score(user_trust_data)
        user.trust_score = trust_score
        
        combined_fraud_score = (
            gps_spoofing['score'] * 0.4 +
            fraud_ring['confidence'] * 0.4 +
            (1 - trust_score) * 0.2
        )
        
        fraud_flags = []
        fraud_flags.extend(gps_spoofing.get('flags', []))
        if fraud_ring['is_fraud_ring']:
            fraud_flags.append('FRAUD_RING_DETECTED')
        if trust_score < 0.5:
            fraud_flags.append('LOW_TRUST_SCORE')
        
        if combined_fraud_score > 0.7 or len(fraud_flags) > 2:
            fraud_log = FraudLog(
                user_id=user.id,
                claim_id=claim.id,
                fraud_type='combined',
                fraud_score=combined_fraud_score,
                risk_level='HIGH' if combined_fraud_score > 0.8 else 'MEDIUM',
                detection_method='multi_layer',
                gps_spoofing_score=gps_spoofing['score'],
                fraud_ring_score=fraud_ring['confidence'],
                evidence={
                    'gps_spoofing': gps_spoofing,
                    'fraud_ring': fraud_ring,
                    'trust_score': trust_score
                },
                flagged=True
            )
            self.db.add(fraud_log)
        
        return {
            'fraud_score': round(combined_fraud_score, 3),
            'fraud_flags': fraud_flags,
            'analysis': {
                'gps_spoofing': gps_spoofing,
                'fraud_ring': fraud_ring,
                'trust_score': round(trust_score, 3)
            }
        }
    
    def _make_approval_decision(self, claim: Claim, fraud_result: Dict, 
                               crowd_validation: Dict) -> Dict:
        fraud_score = fraud_result['fraud_score']
        fraud_flags = fraud_result['fraud_flags']
        
        if fraud_score > 0.8:
            return {
                'approved': False,
                'reason': 'High fraud probability detected',
                'payout_amount': 0
            }
        
        if 'FRAUD_RING_DETECTED' in fraud_flags:
            return {
                'approved': False,
                'reason': 'Coordinated fraud attack detected',
                'payout_amount': 0
            }
        
        if not crowd_validation['validated'] and fraud_score > 0.6:
            return {
                'approved': False,
                'reason': 'Insufficient crowd validation with elevated fraud risk',
                'payout_amount': 0
            }
        
        payout_amount = claim.estimated_loss
        
        if fraud_score > 0.5:
            payout_amount *= 0.7
        
        payout_amount = max(100, min(5000, payout_amount))
        
        return {
            'approved': True,
            'reason': f'Auto-approved - Fraud score: {fraud_score:.2f}, Crowd validated: {crowd_validation["validated"]}',
            'payout_amount': round(payout_amount, 2)
        }
    
    def _process_payout(self, claim: Claim) -> Dict:
        transaction_id = f"VTX{claim.id}{int(datetime.now().timestamp())}"
        
        return {
            'status': 'completed',
            'transaction_id': transaction_id,
            'timestamp': datetime.now().isoformat(),
            'message': f'Payout of ₹{claim.approved_amount} processed successfully'
        }
    
    def get_claim_details(self, claim_id: int) -> Optional[Dict]:
        claim = self.db.query(Claim).filter(Claim.id == claim_id).first()
        
        if not claim:
            return None
        
        return {
            'id': claim.id,
            'user_id': claim.user_id,
            'claim_type': claim.claim_type,
            'trigger_type': claim.trigger_type,
            'estimated_loss': claim.estimated_loss,
            'approved_amount': claim.approved_amount,
            'status': claim.status,
            'auto_approved': claim.auto_approved,
            'fraud_score': claim.fraud_score,
            'fraud_flags': claim.fraud_flags,
            'crowd_validation_count': claim.crowd_validation_count,
            'processing_time_seconds': claim.processing_time_seconds,
            'payout_status': claim.payout_status,
            'payout_transaction_id': claim.payout_transaction_id,
            'created_at': claim.created_at.isoformat(),
            'approval_reason': claim.approval_reason,
            'rejection_reason': claim.rejection_reason
        }
