"""
Database Initialization Script
Creates tables, indexes, and sample data for development
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.database import engine, Base
from app.models import User, Subscription, Claim, ActivityLog, DisruptionEvent, FraudLog
from app.core.security import get_password_hash
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")

def create_indexes():
    """Create database indexes from SQL file"""
    print("Creating database indexes...")
    indexes_sql = os.path.join(os.path.dirname(__file__), '../models/indexes.sql')
    
    if os.path.exists(indexes_sql):
        with open(indexes_sql, 'r') as f:
            sql_content = f.read()
        
        with engine.connect() as conn:
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            for statement in statements:
                try:
                    conn.execute(statement)
                except Exception as e:
                    print(f"Index creation warning: {e}")
        
        print("✅ Indexes created successfully")
    else:
        print("⚠️  Indexes SQL file not found")

def create_sample_users(session: Session):
    """Create sample users for testing"""
    print("Creating sample users...")
    
    # Admin user
    admin = User(
        email="admin@vortex.com",
        username="admin",
        full_name="Admin User",
        phone="+919876543210",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_active=True,
        is_verified=True,
        city="Delhi",
        zone="Central Delhi",
        work_hours_per_day=8.0,
        avg_daily_earnings=1000.0,
        trust_score=1.0
    )
    session.add(admin)
    
    # Sample workers
    cities = ['Delhi', 'Mumbai', 'Bangalore']
    zones = {
        'Delhi': ['South Delhi', 'North Delhi', 'Central Delhi'],
        'Mumbai': ['Andheri', 'Bandra', 'Malad'],
        'Bangalore': ['Whitefield', 'Koramangala', 'Indiranagar']
    }
    
    for i in range(10):
        city = random.choice(cities)
        zone = random.choice(zones[city])
        
        user = User(
            email=f"worker{i+1}@example.com",
            username=f"worker{i+1}",
            full_name=f"Worker {i+1}",
            phone=f"+9198765432{10+i}",
            hashed_password=get_password_hash("password123"),
            role="worker",
            is_active=True,
            is_verified=True,
            city=city,
            zone=zone,
            work_hours_per_day=random.uniform(6, 10),
            avg_daily_earnings=random.uniform(400, 900),
            delivery_platform=random.choice(['Zomato', 'Swiggy', 'Uber Eats']),
            trust_score=random.uniform(0.7, 1.0)
        )
        session.add(user)
    
    session.commit()
    print("✅ Sample users created")

def create_sample_subscriptions(session: Session):
    """Create sample subscriptions"""
    print("Creating sample subscriptions...")
    
    users = session.query(User).filter(User.role == 'worker').all()
    
    for user in users[:7]:  # 7 out of 10 users have subscriptions
        subscription = Subscription(
            user_id=user.id,
            plan_type='monthly',
            coverage_amount=5000.0,
            premium_amount=random.uniform(50, 150),
            status='active',
            start_date=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            end_date=datetime.utcnow() + timedelta(days=random.randint(1, 30))
        )
        session.add(subscription)
    
    session.commit()
    print("✅ Sample subscriptions created")

def main():
    """Main initialization function"""
    print("=" * 60)
    print("VORTEX Shield 2.0 - Database Initialization")
    print("=" * 60)
    
    # Create tables
    create_tables()
    
    # Create indexes
    create_indexes()
    
    # Create sample data
    with Session(engine) as session:
        # Check if admin already exists
        existing_admin = session.query(User).filter(User.username == 'admin').first()
        
        if not existing_admin:
            create_sample_users(session)
            create_sample_subscriptions(session)
            print("\n✅ Sample data created for development")
        else:
            print("\n⚠️  Database already has data, skipping sample data creation")
    
    print("\n" + "=" * 60)
    print("Database initialization complete!")
    print("=" * 60)
    print("\nDefault Credentials:")
    print("  Email: admin@vortex.com")
    print("  Password: admin123")
    print("\n  Worker Email: worker1@example.com")
    print("  Worker Password: password123")
    print("=" * 60)

if __name__ == "__main__":
    main()
