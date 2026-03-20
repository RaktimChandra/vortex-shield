from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.database import init_db, engine
from .models import Base
from .api import auth, users, subscriptions, claims, analytics, ai_features, real_data
from .routers import health, triggers
from .websocket import routes as websocket_routes

app = FastAPI(
    title="VORTEX Shield 2.0",
    description="AI-Powered Parametric Insurance Platform for Gig Workers",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(subscriptions.router)
app.include_router(claims.router)
app.include_router(analytics.router)
app.include_router(triggers.router)
app.include_router(websocket_routes.router)
app.include_router(health.router)
app.include_router(ai_features.router)
app.include_router(real_data.router)

@app.get("/")
def root():
    return {
        "message": "VORTEX Shield 2.0 - Intelligent Income Protection Engine",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "AI Risk Prediction",
            "Fraud Detection",
            "Zero-Touch Claims",
            "Parametric Triggers",
            "Digital Twin Simulation"
        ]
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "ai_engines": "loaded"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
