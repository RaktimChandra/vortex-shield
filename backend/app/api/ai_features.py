from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import numpy as np
import hashlib
from datetime import datetime
from typing import List, Dict
import random

router = APIRouter(prefix="/ai", tags=["AI Features"])

# ========================================
# 1. FREE COMPUTER VISION (Simple Rules)
# ========================================

class ImageAnalysisResponse(BaseModel):
    detected_objects: List[str]
    confidence: float
    weather_verified: bool
    authenticity_score: float

@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_claim_image(file: UploadFile = File(...)):
    """
    FREE Computer Vision - Simple image verification
    Uses basic heuristics (no GPU/paid models needed)
    """
    # Read image bytes
    contents = await file.read()
    file_size = len(contents)
    
    # Simple heuristics based on file properties
    is_large = file_size > 500000  # > 500KB likely detailed photo
    is_small = file_size < 50000   # < 50KB likely screenshot/fake
    
    # Mock object detection (in production, use Hugging Face Inference API - FREE)
    detected = []
    confidence = 0.0
    
    if is_large:
        detected = ["rain", "wet_surface", "outdoor"]
        confidence = 0.85
        weather_verified = True
    elif is_small:
        detected = ["screenshot", "edited_image"]
        confidence = 0.45
        weather_verified = False
    else:
        detected = ["unclear_image"]
        confidence = 0.60
        weather_verified = False
    
    authenticity_score = confidence * (1.0 if is_large else 0.5)
    
    return ImageAnalysisResponse(
        detected_objects=detected,
        confidence=round(confidence, 2),
        weather_verified=weather_verified,
        authenticity_score=round(authenticity_score, 2)
    )


# ========================================
# 2. LSTM PREDICTION (Simulated)
# ========================================

class LSTMPredictionRequest(BaseModel):
    historical_data: List[float]
    predict_steps: int = 7

class LSTMPredictionResponse(BaseModel):
    predictions: List[float]
    confidence_intervals: List[Dict[str, float]]
    trend: str

@router.post("/predict-disruptions", response_model=LSTMPredictionResponse)
def predict_disruptions(request: LSTMPredictionRequest):
    """
    LSTM-based disruption prediction (simulated)
    Predicts future disruption probability for next N days
    """
    historical = request.historical_data
    n_steps = request.predict_steps
    
    # Simple LSTM simulation using moving average + noise
    if len(historical) < 3:
        raise HTTPException(status_code=400, detail="Need at least 3 historical data points")
    
    # Calculate trend
    recent_avg = sum(historical[-3:]) / 3
    overall_avg = sum(historical) / len(historical)
    trend = "increasing" if recent_avg > overall_avg else "decreasing"
    
    # Generate predictions with trend
    predictions = []
    confidence_intervals = []
    
    base = historical[-1]
    for i in range(n_steps):
        # Add trend + randomness
        noise = random.uniform(-0.05, 0.05)
        trend_factor = 0.02 if trend == "increasing" else -0.02
        
        pred = base + (trend_factor * (i + 1)) + noise
        pred = max(0.0, min(1.0, pred))  # Clamp between 0 and 1
        
        predictions.append(round(pred, 3))
        confidence_intervals.append({
            "lower": round(max(0, pred - 0.1), 3),
            "upper": round(min(1, pred + 0.1), 3)
        })
    
    return LSTMPredictionResponse(
        predictions=predictions,
        confidence_intervals=confidence_intervals,
        trend=trend
    )


# ========================================
# 3. REINFORCEMENT LEARNING PRICING
# ========================================

class RLPricingRequest(BaseModel):
    user_risk_score: float
    market_demand: float
    claims_history: int
    work_hours: int

class RLPricingResponse(BaseModel):
    optimal_premium: float
    expected_profit: float
    action_taken: str
    q_values: Dict[str, float]

@router.post("/rl-pricing", response_model=RLPricingResponse)
def reinforcement_learning_pricing(request: RLPricingRequest):
    """
    RL-based dynamic pricing (Q-learning simulation)
    Optimizes premium based on risk, demand, and history
    """
    # State representation
    risk = request.user_risk_score
    demand = request.market_demand
    claims = request.claims_history
    hours = request.work_hours
    
    # Q-learning simulation (simplified)
    # Actions: low_price, medium_price, high_price
    base_premium = 50  # Base weekly premium
    
    # Q-values for each action (learned values)
    q_values = {
        "low_price": base_premium * 0.8 * (1 + demand * 0.2),
        "medium_price": base_premium * 1.0 * (1 + demand * 0.3),
        "high_price": base_premium * 1.2 * (1 + risk * 0.4)
    }
    
    # Select action with highest Q-value
    best_action = max(q_values, key=q_values.get)
    optimal_premium = q_values[best_action]
    
    # Calculate expected profit
    coverage = hours * 150  # ₹150 per hour coverage
    expected_loss = risk * coverage * 0.3
    expected_profit = optimal_premium - expected_loss
    
    return RLPricingResponse(
        optimal_premium=round(optimal_premium, 2),
        expected_profit=round(expected_profit, 2),
        action_taken=best_action,
        q_values={k: round(v, 2) for k, v in q_values.items()}
    )


# ========================================
# 4. FREE CHATBOT (Rule-based, no API)
# ========================================

class ChatRequest(BaseModel):
    message: str
    context: str = "general"

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float

@router.post("/chatbot", response_model=ChatResponse)
def chatbot_interaction(request: ChatRequest):
    """
    FREE Rule-based chatbot (no OpenAI/LLM API cost)
    Handles common insurance queries
    """
    message = request.message.lower()
    
    # Intent classification (rule-based)
    intents = {
        "claim_filing": ["claim", "report", "submit", "file", "loss"],
        "status_check": ["status", "where", "pending", "approved"],
        "coverage": ["cover", "protection", "insure", "policy"],
        "fraud": ["fraud", "fake", "reject", "deny"],
        "help": ["help", "how", "what", "support"],
    }
    
    detected_intent = "general"
    for intent, keywords in intents.items():
        if any(kw in message for kw in keywords):
            detected_intent = intent
            break
    
    # Generate response based on intent
    responses = {
        "claim_filing": "To file a claim, click the '+ Report' button on the Claims page. Fill in the disruption type, description, and estimated loss. Our AI will analyze it instantly!",
        "status_check": "You can check your claim status on the Claims page. Approved claims show a green badge, pending claims are yellow, and rejected ones are red. Check the fraud score for details.",
        "coverage": "VORTEX Shield is 100% FREE! You get full coverage for weather disruptions, platform outages, and traffic delays. No subscription needed - all features are unlocked!",
        "fraud": "Our AI fraud detection analyzes description quality, loss amount, and your trust score. Claims with fraud score below 30% are auto-approved. Above 70% are rejected. Between 30-70% need manual review.",
        "help": "I can help you with: filing claims, checking claim status, understanding coverage, fraud detection info, and general support. What would you like to know?",
        "general": "Hello! I'm your VORTEX Shield AI assistant. I can help you with claims, coverage questions, and platform support. How can I assist you today?"
    }
    
    response_text = responses.get(detected_intent, responses["general"])
    confidence = 0.9 if detected_intent != "general" else 0.7
    
    return ChatResponse(
        response=response_text,
        intent=detected_intent,
        confidence=confidence
    )
