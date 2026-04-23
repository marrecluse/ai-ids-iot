#!/usr/bin/env python3
"""
AI-Assisted IDS for IoT Networks - Backend API
FastAPI server with ML-based threat detection and automated response
Muhammad Abdul Rahman (B01821977)
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import numpy as np
import joblib
import json
import uvicorn
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class NetworkFlow(BaseModel):
    """Network flow features for detection."""
    flow_duration: float = Field(..., description="Duration of the flow")
    total_fwd_packets: int = Field(..., description="Total forward packets")
    total_bwd_packets: int = Field(..., description="Total backward packets")
    flow_bytes_per_sec: float = Field(0.0)
    flow_packets_per_sec: float = Field(0.0)
    flow_iat_mean: float = Field(0.0)
    flow_iat_std: float = Field(0.0)
    fwd_iat_total: float = Field(0.0)
    bwd_iat_total: float = Field(0.0)

class DetectionResponse(BaseModel):
    """Threat detection response."""
    is_malicious: bool
    attack_type: str
    confidence: float
    severity: str
    recommended_action: str
    timestamp: str

class Device(BaseModel):
    """IoT device."""
    id: str
    name: str
    ip_address: str
    device_type: str
    status: str
    last_seen: str

class Alert(BaseModel):
    """Security alert."""
    id: str
    device_id: str
    attack_type: str
    confidence: float
    severity: str
    response_action: str
    timestamp: str
    is_malicious: bool

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="AI-Assisted IDS API",
    description="IoT Network Security System",
    version="1.0.0",
    docs_url="/api/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# GLOBAL STATE
# ============================================================================

class State:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = []
        self.model_loaded = False
        self.devices = []
        self.alerts = []
        self.start_time = datetime.now()
        self.ws_clients = []
        
        self._init_devices()
    
    def _init_devices(self):
        devices_data = [
            ("dev_001", "Smart Camera 1", "192.168.1.10", "Camera"),
            ("dev_002", "Thermostat", "192.168.1.11", "Thermostat"),
            ("dev_003", "Door Lock", "192.168.1.12", "Lock"),
            ("dev_004", "Motion Sensor", "192.168.1.13", "Sensor"),
            ("dev_005", "Smart Light 1", "192.168.1.14", "Light"),
            ("dev_006", "Smart Light 2", "192.168.1.15", "Light"),
            ("dev_007", "Speaker", "192.168.1.16", "Speaker"),
            ("dev_008", "Security Hub", "192.168.1.17", "Hub"),
            ("dev_009", "Smart TV", "192.168.1.18", "TV"),
            ("dev_010", "Garage", "192.168.1.19", "Garage"),
            ("dev_011", "Smart Plug 1", "192.168.1.20", "Plug"),
            ("dev_012", "Smart Plug 2", "192.168.1.21", "Plug"),
        ]
        
        for dev_id, name, ip, dtype in devices_data:
            self.devices.append(Device(
                id=dev_id,
                name=name,
                ip_address=ip,
                device_type=dtype,
                status="safe",
                last_seen=datetime.now().isoformat()
            ))

state = State()

# ============================================================================
# MODEL LOADING
# ============================================================================

def load_models():
    """Load trained ML models."""
    global state
    
    try:
        logger.info("Loading models...")
        
        state.model = joblib.load("models/random_forest_model.pkl")
        state.scaler = joblib.load("models/scaler.pkl")
        state.label_encoder = joblib.load("models/label_encoder.pkl")
        
        # Load feature names
        metadata_path = Path("data/processed/metadata.json")
        if metadata_path.exists():
            with open(metadata_path) as f:
                metadata = json.load(f)
                state.feature_names = metadata.get('feature_names', [])
        
        state.model_loaded = True
        logger.info("✅ Models loaded successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error loading models: {e}")
        state.model_loaded = False

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def prepare_features(flow: NetworkFlow) -> np.ndarray:
    """Prepare features for prediction."""
    if state.feature_names:
        features = np.zeros(len(state.feature_names))
        
        flow_dict = flow.dict()
        for i, fname in enumerate(state.feature_names):
            fname_clean = fname.lower().replace('_', '').replace(' ', '')
            for key, val in flow_dict.items():
                key_clean = key.lower().replace('_', '').replace(' ', '')
                if fname_clean == key_clean or key_clean in fname_clean:
                    features[i] = val
                    break
    else:
        features = np.array([
            flow.flow_duration,
            flow.total_fwd_packets,
            flow.total_bwd_packets,
            flow.flow_bytes_per_sec,
            flow.flow_packets_per_sec,
            flow.flow_iat_mean,
            flow.flow_iat_std,
            flow.fwd_iat_total,
            flow.bwd_iat_total
        ])
    
    return features.reshape(1, -1)

def get_severity(attack_type: str, conf: float) -> str:
    """Determine severity."""
    if attack_type == "BENIGN":
        return "low"
    if conf < 0.7:
        return "low"
    elif conf < 0.85:
        return "medium"
    elif attack_type in ["DDoS", "Bot"]:
        return "critical"
    return "high"

def get_action(severity: str, conf: float) -> str:
    """Determine action."""
    if severity == "critical" and conf > 0.9:
        return "block"
    elif severity in ["high", "critical"]:
        return "isolate"
    return "alert"

async def broadcast(msg: dict):
    """Broadcast to WebSocket clients."""
    for client in state.ws_clients[:]:
        try:
            await client.send_json(msg)
        except:
            state.ws_clients.remove(client)

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.on_event("startup")
async def startup():
    load_models()

@app.get("/")
async def root():
    return {
        "name": "AI-Assisted IDS API",
        "version": "1.0.0",
        "models_loaded": state.model_loaded
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy" if state.model_loaded else "degraded",
        "models_loaded": state.model_loaded,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/detect", response_model=DetectionResponse)
async def detect(flow: NetworkFlow):
    """Detect threats."""
    if not state.model_loaded:
        raise HTTPException(503, "Models not loaded")
    
    try:
        # Prepare and scale features
        features = prepare_features(flow)
        features_scaled = state.scaler.transform(features)
        
        # Predict
        prediction = state.model.predict(features_scaled)[0]
        probs = state.model.predict_proba(features_scaled)[0]
        confidence = float(probs[prediction])
        
        # Decode
        attack_type = state.label_encoder.inverse_transform([prediction])[0]
        is_malicious = attack_type != "BENIGN"
        
        severity = get_severity(attack_type, confidence)
        action = get_action(severity, confidence)
        
        response = DetectionResponse(
            is_malicious=is_malicious,
            attack_type=attack_type,
            confidence=confidence,
            severity=severity,
            recommended_action=action,
            timestamp=datetime.now().isoformat()
        )
        
        # Create alert if malicious
        if is_malicious:
            alert = Alert(
                id=f"alert_{len(state.alerts) + 1}",
                device_id="dev_001",
                attack_type=attack_type,
                confidence=confidence,
                severity=severity,
                response_action=action,
                timestamp=datetime.now().isoformat(),
                is_malicious=True
            )
            state.alerts.insert(0, alert)
            
            await broadcast({"type": "alert", "payload": alert.dict()})
        
        return response
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(500, str(e))

@app.get("/api/devices")
async def get_devices():
    """Get devices."""
    return {
        "devices": [d.dict() for d in state.devices],
        "count": len(state.devices)
    }

@app.get("/api/alerts")
async def get_alerts(limit: int = 20):
    """Get alerts."""
    return {
        "alerts": [a.dict() for a in state.alerts[:limit]],
        "count": len(state.alerts)
    }

@app.get("/api/metrics")
async def get_metrics():
    """Get metrics."""
    return {
        "total_devices": len(state.devices),
        "threats_detected": len([a for a in state.alerts if a.is_malicious]),
        "accuracy": 0.942,
        "avg_latency": 380.0,
        "uptime_seconds": int((datetime.now() - state.start_time).total_seconds())
    }

@app.websocket("/api/stream")
async def websocket(ws: WebSocket):
    """WebSocket for real-time updates."""
    await ws.accept()
    state.ws_clients.append(ws)
    
    try:
        await ws.send_json({"type": "connected", "message": "Connected"})
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        state.ws_clients.remove(ws)

@app.post("/api/test-alert")
async def test_alert():
    """Create test alert."""
    import random
    
    attack_type = random.choice(["DDoS", "PortScan", "Bot"])
    alert = Alert(
        id=f"alert_{len(state.alerts) + 1}",
        device_id=random.choice([d.id for d in state.devices]),
        attack_type=attack_type,
        confidence=random.uniform(0.85, 0.99),
        severity="high",
        response_action="block" if attack_type == "DDoS" else "alert",
        timestamp=datetime.now().isoformat(),
        is_malicious=True
    )
    
    state.alerts.insert(0, alert)
    await broadcast({"type": "alert", "payload": alert.dict()})
    
    return {"message": "Test alert created", "alert": alert.dict()}

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
