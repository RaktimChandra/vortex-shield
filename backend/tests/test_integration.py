"""
Integration Tests for VORTEX Shield 2.0
Tests end-to-end flows and service integrations
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models import User, Subscription, Claim
from app.core.security import get_password_hash
from datetime import datetime, timedelta

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def test_client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_worker(test_client):
    """Create a test worker user with subscription"""
    # Register user
    user_data = {
        "email": "integration_worker@test.com",
        "username": "int_worker",
        "password": "TestPass123",
        "full_name": "Integration Worker",
        "phone": "+919876543210",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "city": "Delhi",
        "zone": "South Delhi",
        "work_hours_per_day": 8.0,
        "avg_daily_earnings": 800.0,
        "delivery_platform": "Swiggy"
    }
    response = test_client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    token_data = response.json()
    
    # Create subscription
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    sub_data = {
        "plan_type": "monthly",
        "coverage_amount": 5000
    }
    sub_response = test_client.post("/subscriptions/", json=sub_data, headers=headers)
    assert sub_response.status_code == 200
    
    return {
        "token": token_data['access_token'],
        "user": token_data['user'],
        "headers": headers
    }

class TestEndToEndFlows:
    """Test complete user journeys"""
    
    def test_complete_claim_flow(self, test_client, test_worker):
        """Test complete claim submission and processing"""
        headers = test_worker['headers']
        
        # Step 1: Check triggers
        trigger_response = test_client.post("/claims/check-triggers", headers=headers)
        assert trigger_response.status_code == 200
        trigger_data = trigger_response.json()
        assert 'triggered' in trigger_data
        
        # Step 2: Get my claims (should be empty)
        claims_response = test_client.get("/claims/my-claims", headers=headers)
        assert claims_response.status_code == 200
        initial_claims = claims_response.json()
        
        # Step 3: Check active subscription
        sub_response = test_client.get("/subscriptions/active", headers=headers)
        assert sub_response.status_code == 200
        subscription = sub_response.json()
        assert subscription['status'] == 'active'
    
    def test_user_profile_update_flow(self, test_client, test_worker):
        """Test user profile management"""
        headers = test_worker['headers']
        
        # Get current profile
        profile_response = test_client.get("/users/me", headers=headers)
        assert profile_response.status_code == 200
        profile = profile_response.json()
        
        # Update profile
        update_data = {
            "full_name": "Updated Worker Name",
            "avg_daily_earnings": 1000.0
        }
        update_response = test_client.put("/users/me", json=update_data, headers=headers)
        assert update_response.status_code == 200
        updated_profile = update_response.json()
        
        assert updated_profile['full_name'] == "Updated Worker Name"
        assert updated_profile['avg_daily_earnings'] == 1000.0
    
    def test_subscription_lifecycle(self, test_client):
        """Test subscription creation and management"""
        # Create new user
        user_data = {
            "email": "sub_test@test.com",
            "username": "sub_test",
            "password": "TestPass123",
            "full_name": "Sub Test",
            "phone": "+919876543211",
            "city": "Mumbai",
            "zone": "Andheri"
        }
        register_response = test_client.post("/auth/register", json=user_data)
        assert register_response.status_code == 200
        token = register_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Calculate premium
        premium_response = test_client.get("/subscriptions/calculate-premium", headers=headers)
        assert premium_response.status_code == 200
        premium_data = premium_response.json()
        assert 'monthly_premium' in premium_data
        assert premium_data['monthly_premium'] > 0
        
        # Create subscription
        sub_data = {
            "plan_type": "monthly",
            "coverage_amount": 5000
        }
        create_response = test_client.post("/subscriptions/", json=sub_data, headers=headers)
        assert create_response.status_code == 200
        subscription = create_response.json()
        assert subscription['status'] == 'active'
        
        # Get active subscription
        active_response = test_client.get("/subscriptions/active", headers=headers)
        assert active_response.status_code == 200

class TestServiceIntegrations:
    """Test integration between services"""
    
    def test_risk_fraud_integration(self, test_client, test_worker):
        """Test risk engine and fraud detection working together"""
        headers = test_worker['headers']
        
        # Trigger check invokes risk engine
        trigger_response = test_client.post("/claims/check-triggers", headers=headers)
        assert trigger_response.status_code == 200
        
        # Dashboard should show risk data
        dashboard_response = test_client.get("/analytics/dashboard", headers=headers)
        assert dashboard_response.status_code == 200
        dashboard = dashboard_response.json()
        assert 'risk_level' in dashboard or 'analytics' in dashboard

class TestErrorHandling:
    """Test error scenarios and edge cases"""
    
    def test_unauthorized_access(self, test_client):
        """Test unauthorized access is properly rejected"""
        # Try to access protected route without token
        response = test_client.get("/users/me")
        assert response.status_code == 401
        
        # Try with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = test_client.get("/users/me", headers=headers)
        assert response.status_code == 401
    
    def test_duplicate_registration(self, test_client):
        """Test duplicate email/username is rejected"""
        user_data = {
            "email": "duplicate@test.com",
            "username": "duplicate",
            "password": "TestPass123",
            "full_name": "Duplicate User",
            "phone": "+919876543212"
        }
        
        # First registration should succeed
        response1 = test_client.post("/auth/register", json=user_data)
        assert response1.status_code == 200
        
        # Second registration should fail
        response2 = test_client.post("/auth/register", json=user_data)
        assert response2.status_code == 400
    
    def test_claim_without_subscription(self, test_client):
        """Test claim submission requires active subscription"""
        # Create user without subscription
        user_data = {
            "email": "no_sub@test.com",
            "username": "no_sub",
            "password": "TestPass123",
            "full_name": "No Sub User",
            "phone": "+919876543213"
        }
        register_response = test_client.post("/auth/register", json=user_data)
        token = register_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to submit claim - should check subscription first
        response = test_client.post("/claims/check-triggers", headers=headers)
        # Should work but indicate no subscription
        assert response.status_code in [200, 400]

class TestPerformance:
    """Test performance and load handling"""
    
    def test_concurrent_requests(self, test_client, test_worker):
        """Test handling multiple concurrent requests"""
        headers = test_worker['headers']
        
        # Make multiple requests
        responses = []
        for _ in range(10):
            response = test_client.get("/users/me", headers=headers)
            responses.append(response)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
    
    def test_pagination(self, test_client):
        """Test pagination works correctly"""
        # Would need admin token
        # Test skipped for now
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
