from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/vortex_shield"
    SECRET_KEY: str = "vortex-shield-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # External API keys
    OPENWEATHER_API_KEY: Optional[str] = None
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"
    
    # AI Model paths
    RISK_MODEL_PATH: str = "models/risk_model.pkl"
    FRAUD_MODEL_PATH: str = "models/fraud_model.pkl"
    PRICING_MODEL_PATH: str = "models/pricing_model.pkl"
    
    # Thresholds
    RAINFALL_THRESHOLD_MM: float = 50.0
    AQI_THRESHOLD: int = 200
    TRAFFIC_JAM_THRESHOLD: float = 0.7
    CROWD_VALIDATION_MIN_USERS: int = 5
    
    GPS_SPOOFING_THRESHOLD: float = 0.8
    FRAUD_RING_SIMILARITY_THRESHOLD: float = 0.85
    MIN_TRUST_SCORE: float = 0.6
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@vortexshield.com"
    
    # Sentry and Environment
    SENTRY_DSN: str = ""
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
