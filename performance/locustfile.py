"""
Load Testing with Locust
Run: locust -f performance/locustfile.py --host=http://localhost:8000
"""
from locust import HttpUser, task, between
import random

class VortexUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login on start"""
        response = self.client.post("/auth/login", json={
            "email": "worker1@example.com",
            "password": "password123"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(3)
    def get_dashboard(self):
        """Get user dashboard"""
        if self.token:
            self.client.get("/users/me", headers=self.headers)
    
    @task(2)
    def check_triggers(self):
        """Check parametric triggers"""
        if self.token:
            self.client.post("/claims/check-triggers", headers=self.headers)
    
    @task(2)
    def get_analytics(self):
        """Get analytics dashboard"""
        if self.token:
            self.client.get("/analytics/dashboard", headers=self.headers)
    
    @task(1)
    def get_subscription(self):
        """Get active subscription"""
        if self.token:
            self.client.get("/subscriptions/active", headers=self.headers)
    
    @task(1)
    def get_claims(self):
        """Get user claims"""
        if self.token:
            self.client.get("/claims/my-claims", headers=self.headers)

class AdminUser(HttpUser):
    wait_time = between(2, 5)
    
    def on_start(self):
        """Admin login"""
        response = self.client.post("/auth/login", json={
            "email": "admin@vortex.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(2)
    def get_all_claims(self):
        """Get all claims (admin)"""
        if self.token:
            self.client.get("/claims/", headers=self.headers)
    
    @task(1)
    def get_admin_dashboard(self):
        """Get admin analytics"""
        if self.token:
            self.client.get("/analytics/admin-dashboard", headers=self.headers)

class UnauthorizedUser(HttpUser):
    wait_time = between(1, 2)
    
    @task
    def get_health(self):
        """Check health endpoint"""
        self.client.get("/health")
    
    @task
    def try_unauthorized(self):
        """Try unauthorized access"""
        self.client.get("/users/me")
