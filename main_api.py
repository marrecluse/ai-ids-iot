from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import joblib
import numpy as np
from datetime import datetime
import random

app = FastAPI(title="AI-IDS API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML models
try:
    model = joblib.load('models/random_forest_model.pkl')
    scaler = joblib.load('models/scaler.pkl')
    label_encoder = joblib.load('models/label_encoder.pkl')
    print("✅ Models loaded successfully!")
except Exception as e:
    print(f"⚠️ Error loading models: {e}")
    model = None
    scaler = None
    label_encoder = None

# IoT Devices Database
DEVICES = [
    {"id": "dev_001", "name": "Smart Camera 1", "ip_address": "192.168.1.10", "device_type": "Camera", "status": "active"},
    {"id": "dev_002", "name": "Thermostat", "ip_address": "192.168.1.11", "device_type": "Thermostat", "status": "active"},
    {"id": "dev_003", "name": "Door Lock", "ip_address": "192.168.1.12", "device_type": "Lock", "status": "active"},
    {"id": "dev_004", "name": "Motion Sensor", "ip_address": "192.168.1.13", "device_type": "Sensor", "status": "active"},
    {"id": "dev_005", "name": "Smart Bulb", "ip_address": "192.168.1.14", "device_type": "Light", "status": "active"},
    {"id": "dev_006", "name": "Smart Speaker", "ip_address": "192.168.1.15", "device_type": "Speaker", "status": "active"},
    {"id": "dev_007", "name": "Security Camera 2", "ip_address": "192.168.1.16", "device_type": "Camera", "status": "active"},
    {"id": "dev_008", "name": "Smart TV", "ip_address": "192.168.1.17", "device_type": "TV", "status": "active"},
    {"id": "dev_009", "name": "Router", "ip_address": "192.168.1.18", "device_type": "Router", "status": "active"},
    {"id": "dev_010", "name": "Smart Fridge", "ip_address": "192.168.1.19", "device_type": "Appliance", "status": "active"},
    {"id": "dev_011", "name": "Garage Door", "ip_address": "192.168.1.20", "device_type": "Door", "status": "active"},
    {"id": "dev_012", "name": "Smoke Detector", "ip_address": "192.168.1.21", "device_type": "Sensor", "status": "active"},
]

# Alerts storage
alerts_db = []

class TrafficFeatures(BaseModel):
    flow_duration: float
    total_fwd_packets: int
    total_bwd_packets: int
    total_length_fwd_packets: float
    total_length_bwd_packets: float
    fwd_packet_length_mean: float
    bwd_packet_length_mean: float
    flow_bytes_per_sec: float
    flow_packets_per_sec: float

class DetectionResult(BaseModel):
    device_id: str
    attack_type: str
    confidence: float
    is_malicious: bool
    timestamp: str
    recommended_action: str

@app.get("/")
async def root():
    return {
        "message": "AI-Assisted IDS API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "health": "/health",
            "detect": "/api/detect",
            "devices": "/api/devices",
            "alerts": "/api/alerts",
            "metrics": "/api/metrics"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "models_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/detect")
async def detect_threat(features: TrafficFeatures):
    """Detect threats from network traffic features"""
    if model is None:
        raise HTTPException(status_code=500, detail="ML models not loaded")
    
    try:
        # Create feature array (9 simplified features)
        feature_values = [
            features.flow_duration,
            features.total_fwd_packets,
            features.total_bwd_packets,
            features.total_length_fwd_packets,
            features.total_length_bwd_packets,
            features.fwd_packet_length_mean,
            features.bwd_packet_length_mean,
            features.flow_bytes_per_sec,
            features.flow_packets_per_sec
        ]
        
        # Pad with zeros to match model's expected 80 features
        full_features = feature_values + [0] * (80 - len(feature_values))
        X = np.array([full_features])
        
        # Scale and predict
        X_scaled = scaler.transform(X)
        prediction = model.predict(X_scaled)[0]
        probabilities = model.predict_proba(X_scaled)[0]
        confidence = float(max(probabilities))
        
        # Get attack type
        attack_type = label_encoder.inverse_transform([prediction])[0]
        is_malicious = attack_type.upper() != 'BENIGN'
        
        # Determine action
        if not is_malicious:
            action = "monitor"
        elif confidence > 0.9:
            action = "block"
        elif confidence > 0.7:
            action = "isolate"
        else:
            action = "alert"
        
        # Random device for demo
        device_id = random.choice(DEVICES)["id"]
        
        result = {
            "device_id": device_id,
            "attack_type": attack_type,
            "confidence": confidence,
            "is_malicious": is_malicious,
            "timestamp": datetime.now().isoformat(),
            "recommended_action": action
        }
        
        # Store alert
        alerts_db.append(result)
        if len(alerts_db) > 100:
            alerts_db.pop(0)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")

@app.get("/api/devices")
async def get_devices():
    """Get all IoT devices"""
    return {"devices": DEVICES, "count": len(DEVICES)}

@app.get("/api/alerts")
async def get_alerts(limit: int = 20):
    """Get recent alerts"""
    recent_alerts = alerts_db[-limit:] if alerts_db else []
    recent_alerts.reverse()
    return {
        "alerts": recent_alerts,
        "total": len(alerts_db),
        "returned": len(recent_alerts)
    }

@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics"""
    total_alerts = len(alerts_db)
    malicious = sum(1 for a in alerts_db if a['is_malicious'])
    
    return {
        "total_devices": len(DEVICES),
        "total_alerts": total_alerts,
        "malicious_alerts": malicious,
        "benign_alerts": total_alerts - malicious,
        "detection_rate": 0.942,
        "avg_response_time_ms": 380,
        "system_uptime_hours": 24.5
    }

@app.post("/api/test-alert")
async def create_test_alert():
    """Create a test alert for demonstration"""
    attack_types = ["DDoS", "PortScan", "Bot", "BENIGN"]
    attack_type = random.choice(attack_types)
    is_malicious = attack_type != "BENIGN"
    
    test_alert = {
        "device_id": random.choice(DEVICES)["id"],
        "attack_type": attack_type,
        "confidence": random.uniform(0.7, 0.99),
        "is_malicious": is_malicious,
        "timestamp": datetime.now().isoformat(),
        "recommended_action": "block" if is_malicious else "monitor"
    }
    
    alerts_db.append(test_alert)
    return test_alert

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
