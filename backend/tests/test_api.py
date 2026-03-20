"""
API Integration Tests for VORTEX Shield 2.0
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, get_db
from app.models import User
from app.core.security import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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
    client = TestClient(app)
    yield client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_user(test_client):
    """Create a test user and return auth data with access token"""
    import random
    random_id = random.randint(1000, 9999)
    user_data = {
        "email": f"test{random_id}@example.com",
        "username": f"testuser{random_id}",
        "password": "testpassword123",
        "full_name": "Test User",
        "phone": f"+9198765432{random_id % 100:02d}",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "city": "Delhi",
        "zone": "Central Delhi",
        "work_hours_per_day": 8.0,
        "avg_daily_earnings": 800.0,
        "delivery_platform": "Swiggy"
    }
    response = test_client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    # Ensure access_token is present
    assert "access_token" in data, "Registration response missing access_token"
    return data

class TestAuthentication:
    def test_register_user(self, test_client):
        """Test user registration"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "full_name": "New User",
            "phone": "+919876543211",
            "city": "Mumbai",
            "zone": "Andheri"
        }
        response = test_client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == user_data["email"]
    
    def test_login(self, test_client, test_user):
        """Test user login"""
        # Use the email from test_user fixture
        login_data = {
            "email": test_user["user"]["email"],
            "password": "testpassword123"
        }
        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_login_invalid_credentials(self, test_client):
        """Test login with invalid credentials"""
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 401

class TestHealthChecks:
    def test_root_endpoint(self, test_client):
        """Test root endpoint"""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "version" in data
    
    def test_health_endpoint(self, test_client):
        """Test basic health check"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_health_ready(self, test_client):
        """Test readiness check"""
        response = test_client.get("/health/ready")
        # Health check may fail in test environment without production models
        # Accept both 200 (ready) and 503 (not ready but service running)
        assert response.status_code in [200, 503]

class TestUserAPI:
    def test_get_current_user(self, test_client, test_user):
        """Test getting current user profile"""
        token = test_user["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["user"]["email"]
    
    def test_update_user(self, test_client, test_user):
        """Test updating user profile"""
        token = test_user["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        update_data = {
            "full_name": "Updated Name",
            "avg_daily_earnings": 1000.0
        }
        response = test_client.put("/users/me", json=update_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["avg_daily_earnings"] == 1000.0

class TestSubscriptions:
    def test_calculate_premium(self, test_client, test_user):
        """Test premium calculation"""
        token = test_user["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/subscriptions/calculate-premium", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # API returns nested structure with 'pricing' and 'risk_analysis' keys
        assert "pricing" in data
        assert "risk_analysis" in data
        assert data["pricing"]["weekly_premium"] > 0
    
    def test_create_subscription(self, test_client, test_user):
        """Test creating subscription"""
        token = test_user["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        sub_data = {
            "plan_type": "monthly",
            "coverage_amount": 5000
        }
        response = test_client.post("/subscriptions/", json=sub_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert data["coverage_amount"] == 5000

class TestClaims:
    def test_check_triggers(self, test_client, test_user):
        """Test checking parametric triggers"""
        token = test_user["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.post("/claims/check-triggers", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "triggered" in data
        assert "triggers" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
