import numpy as np
from typing import Dict, Tuple
from datetime import datetime, timedelta

class DynamicPricingEngine:
    
    def __init__(self):
        self.base_premium_low = 39.0
        self.base_premium_medium = 59.0
        self.base_premium_high = 79.0
        self.coverage_amount = 5000.0
    
    def calculate_weekly_premium(self, risk_data: Dict, user_data: Dict) -> Dict:
        risk_level = risk_data.get('risk_level', 'MEDIUM')
        risk_score = risk_data.get('risk_score', 0.5)
        predicted_loss = risk_data.get('predicted_loss', 0)
        
        if risk_level == 'LOW':
            base_premium = self.base_premium_low
        elif risk_level == 'MEDIUM':
            base_premium = self.base_premium_medium
        else:
            base_premium = self.base_premium_high
        
        zone_multiplier = self._calculate_zone_multiplier(user_data)
        work_hours_multiplier = self._calculate_work_hours_multiplier(user_data)
        trust_multiplier = self._calculate_trust_multiplier(user_data)
        seasonal_multiplier = self._calculate_seasonal_multiplier()
        
        total_multiplier = (
            zone_multiplier * 0.3 +
            work_hours_multiplier * 0.2 +
            trust_multiplier * 0.2 +
            seasonal_multiplier * 0.3
        )
        
        adjusted_premium = base_premium * (1 + total_multiplier)
        
        final_premium = max(29.0, min(99.0, adjusted_premium))
        
        expected_loss_ratio = predicted_loss / self.coverage_amount if self.coverage_amount > 0 else 0
        
        return {
            'weekly_premium': round(final_premium, 2),
            'base_premium': round(base_premium, 2),
            'risk_level': risk_level,
            'coverage_amount': self.coverage_amount,
            'pricing_factors': {
                'zone_multiplier': round(zone_multiplier, 3),
                'work_hours_multiplier': round(work_hours_multiplier, 3),
                'trust_multiplier': round(trust_multiplier, 3),
                'seasonal_multiplier': round(seasonal_multiplier, 3),
                'total_adjustment': round(total_multiplier, 3)
            },
            'expected_loss_ratio': round(expected_loss_ratio, 3),
            'recommended_coverage': self._recommend_coverage(user_data),
            'discount_eligible': self._check_discount_eligibility(user_data),
            'pricing_explanation': self._generate_pricing_explanation(
                risk_level, final_premium, base_premium, total_multiplier
            )
        }
    
    def _calculate_zone_multiplier(self, user_data: Dict) -> float:
        zone = user_data.get('zone', '')
        city = user_data.get('city', '')
        
        high_risk_zones = ['Andheri', 'Malad', 'East Delhi', 'Marathahalli']
        medium_risk_zones = ['Bandra', 'Dadar', 'North Delhi', 'Koramangala']
        
        if zone in high_risk_zones:
            return 0.3
        elif zone in medium_risk_zones:
            return 0.15
        else:
            return 0.0
    
    def _calculate_work_hours_multiplier(self, user_data: Dict) -> float:
        work_hours = user_data.get('work_hours_per_day', 8.0)
        
        if work_hours > 10:
            return 0.2
        elif work_hours > 8:
            return 0.1
        else:
            return 0.0
    
    def _calculate_trust_multiplier(self, user_data: Dict) -> float:
        trust_score = user_data.get('trust_score', 1.0)
        
        if trust_score > 0.9:
            return -0.15
        elif trust_score > 0.7:
            return -0.05
        elif trust_score < 0.5:
            return 0.25
        else:
            return 0.0
    
    def _calculate_seasonal_multiplier(self) -> float:
        current_month = datetime.now().month
        
        monsoon_months = [6, 7, 8, 9]
        winter_months = [12, 1, 2]
        
        if current_month in monsoon_months:
            return 0.25
        elif current_month in winter_months:
            return -0.1
        else:
            return 0.0
    
    def _recommend_coverage(self, user_data: Dict) -> float:
        avg_earnings = user_data.get('avg_daily_earnings', 500)
        work_hours = user_data.get('work_hours_per_day', 8)
        
        weekly_earnings = avg_earnings * 7
        recommended = min(weekly_earnings * 0.3, 5000)
        
        return round(recommended, 2)
    
    def _check_discount_eligibility(self, user_data: Dict) -> Dict:
        trust_score = user_data.get('trust_score', 1.0)
        total_claims = user_data.get('total_claims', 0)
        
        discounts = []
        total_discount = 0.0
        
        if trust_score > 0.9 and total_claims > 0:
            discounts.append({'type': 'high_trust', 'amount': 5.0, 'description': 'High trust score bonus'})
            total_discount += 5.0
        
        if total_claims == 0:
            discounts.append({'type': 'no_claims', 'amount': 3.0, 'description': 'No claims bonus'})
            total_discount += 3.0
        
        return {
            'eligible': len(discounts) > 0,
            'discounts': discounts,
            'total_discount': round(total_discount, 2)
        }
    
    def _generate_pricing_explanation(self, risk_level: str, final: float, base: float, adjustment: float) -> str:
        if adjustment > 0:
            return f"Premium adjusted +{adjustment*100:.1f}% from base ₹{base} to ₹{final} due to {risk_level.lower()} risk factors"
        elif adjustment < 0:
            return f"Premium discounted {abs(adjustment)*100:.1f}% from base ₹{base} to ₹{final} due to favorable conditions"
        else:
            return f"Standard premium of ₹{final} for {risk_level.lower()} risk profile"
    
    def calculate_loss_coverage(self, actual_loss: float, subscription_data: Dict) -> Dict:
        coverage_amount = subscription_data.get('coverage_amount', 5000.0)
        premium_paid = subscription_data.get('premium_amount', 0)
        
        coverage_percentage = min(100, (actual_loss / coverage_amount) * 100) if coverage_amount > 0 else 0
        
        approved_amount = min(actual_loss, coverage_amount)
        
        deductible = 0.0
        if actual_loss < 100:
            deductible = 50.0
            approved_amount = max(0, approved_amount - deductible)
        
        return {
            'actual_loss': round(actual_loss, 2),
            'coverage_amount': coverage_amount,
            'approved_payout': round(approved_amount, 2),
            'deductible': deductible,
            'coverage_percentage': round(coverage_percentage, 2),
            'roi': round((approved_amount / premium_paid) if premium_paid > 0 else 0, 2)
        }
    
    def simulate_monthly_cost(self, weekly_premium: float, risk_level: str) -> Dict:
        weeks_per_month = 4.33
        monthly_cost = weekly_premium * weeks_per_month
        yearly_cost = monthly_cost * 12
        
        expected_claims_per_year = {
            'LOW': 1,
            'MEDIUM': 2,
            'HIGH': 4
        }.get(risk_level, 2)
        
        avg_payout = {
            'LOW': 500,
            'MEDIUM': 1000,
            'HIGH': 1500
        }.get(risk_level, 1000)
        
        expected_benefit = expected_claims_per_year * avg_payout
        net_benefit = expected_benefit - yearly_cost
        
        return {
            'weekly_premium': round(weekly_premium, 2),
            'monthly_cost': round(monthly_cost, 2),
            'yearly_cost': round(yearly_cost, 2),
            'expected_annual_benefit': round(expected_benefit, 2),
            'net_annual_benefit': round(net_benefit, 2),
            'break_even_claims': max(1, int(yearly_cost / avg_payout))
        }
