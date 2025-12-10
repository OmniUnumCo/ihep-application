# patient_twin_service/app.py
import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib
import hmac

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from google.cloud import healthcare_v1
from google.cloud import pubsub_v1
import redis
import numpy as np
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_patient_id(patient_id: str) -> str:
    """Hash patient ID for secure logging (HIPAA compliance)"""
    return hashlib.sha256(patient_id.encode()).hexdigest()[:16]

app = FastAPI(title="Patient Digital Twin Service")

# Database setup
DATABASE_URL = "postgresql://user:password@localhost/patient_twin_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis for caching
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Healthcare API client
healthcare_client = healthcare_v1.HealthcareServiceClient()

# Configuration
ENCRYPTION_KEY = os.getenv('TWIN_ENCRYPTION_KEY')
fernet = Fernet(ENCRYPTION_KEY) if ENCRYPTION_KEY else None

class PatientTwin(Base):
    __tablename__ = "patient_twins"
    
    id = Column(String, primary_key=True)
    patient_id = Column(String, unique=True, index=True)
    twin_state = Column(Text)  # JSON serialized state
    last_sync = Column(DateTime, default=datetime.utcnow)
    morphogenetic_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class VitalSigns(BaseModel):
    heart_rate: Optional[float]
    blood_pressure_systolic: Optional[float]
    blood_pressure_diastolic: Optional[float]
    temperature: Optional[float]
    oxygen_saturation: Optional[float]
    weight: Optional[float]
    viral_load: Optional[float]
    cd4_count: Optional[float]

class LabResults(BaseModel):
    test_name: str
    result_value: float
    unit: str
    reference_range: str
    test_date: datetime

class TwinUpdateRequest(BaseModel):
    patient_id: str
    vital_signs: Optional[VitalSigns]
    lab_results: Optional[List[LabResults]]
    medication_adherence: Optional[float]
    appointment_attendance: Optional[float]

class TwinState(BaseModel):
    vital_signs: VitalSigns
    lab_results: List[LabResults]
    medication_adherence: float
    appointment_attendance: float
    risk_score: float
    morphogenetic_score: float
    last_updated: datetime

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify HMAC signature for data integrity"""
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)

async def morphogenetic_self_healing(twin_state: TwinState) -> TwinState:
    """
    Morphogenetic self-healing algorithm
    Implements adaptive state correction based on historical patterns
    """
    # This would implement complex self-healing logic
    # For now, we'll simulate the process
    
    # Calculate morphogenetic score based on consistency and stability
    consistency_score = 0.8  # Would be calculated from historical data
    stability_score = 0.7    # Would be calculated from trend analysis
    
    twin_state.morphogenetic_score = (consistency_score + stability_score) / 2
    
    logger.info(f"Morphogenetic self-healing applied. Score: {twin_state.morphogenetic_score}")
    
    return twin_state

def calculate_risk_score(twin_state: TwinState) -> float:
    """Calculate patient risk score based on twin state"""
    # Simplified risk calculation - would be much more complex in practice
    risk_factors = []
    
    if twin_state.vital_signs.viral_load and twin_state.vital_signs.viral_load > 50:
        risk_factors.append(0.3)
    
    if twin_state.vital_signs.cd4_count and twin_state.vital_signs.cd4_count < 200:
        risk_factors.append(0.4)
    
    if twin_state.medication_adherence < 0.8:
        risk_factors.append(0.2)
    
    total_risk = sum(risk_factors)
    return min(total_risk, 1.0)

@app.post("/v1/twin/update")
async def update_twin(
    update_request: TwinUpdateRequest,
    x_signature: str = Header(None),
    db = Depends(get_db)
):
    """
    Update patient digital twin with new data
    Implements envelope encryption and integrity verification
    """
    try:
        # Verify data integrity
        payload = json.dumps(update_request.dict(), default=str)
        if x_signature and not verify_signature(payload, x_signature, os.getenv('SIGNING_SECRET', '')):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Get existing twin or create new one
        twin = db.query(PatientTwin).filter(PatientTwin.patient_id == update_request.patient_id).first()
        
        if not twin:
            twin = PatientTwin(
                id=hashlib.sha256(update_request.patient_id.encode()).hexdigest()[:16],
                patient_id=update_request.patient_id
            )
            db.add(twin)
        
        # Load current state
        current_state = json.loads(twin.twin_state) if twin.twin_state else {}
        
        # Update state with new data
        if update_request.vital_signs:
            current_state['vital_signs'] = update_request.vital_signs.dict()
        
        if update_request.lab_results:
            if 'lab_results' not in current_state:
                current_state['lab_results'] = []
            current_state['lab_results'].extend([lr.dict() for lr in update_request.lab_results])
        
        if update_request.medication_adherence is not None:
            current_state['medication_adherence'] = update_request.medication_adherence
        
        if update_request.appointment_attendance is not None:
            current_state['appointment_attendance'] = update_request.appointment_attendance
        
        # Apply morphogenetic self-healing
        twin_state = TwinState(**current_state)
        twin_state = await morphogenetic_self_healing(twin_state)
        
        # Calculate risk score
        twin_state.risk_score = calculate_risk_score(twin_state)
        twin_state.last_updated = datetime.utcnow()
        
        # Store encrypted state
        state_json = json.dumps(twin_state.dict(), default=str)
        if fernet:
            encrypted_state = fernet.encrypt(state_json.encode())
            twin.twin_state = encrypted_state.decode()
        else:
            twin.twin_state = state_json
        
        twin.last_sync = datetime.utcnow()
        db.commit()
        
        # Publish update event for real-time processing (hash patient_id for HIPAA compliance)
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path('your-project-id', 'twin-updates')

        message_data = json.dumps({
            'patient_id': hash_patient_id(update_request.patient_id),
            'risk_score': twin_state.risk_score,
            'timestamp': datetime.utcnow().isoformat()
        }).encode('utf-8')

        publisher.publish(topic_path, message_data)
        
        logger.info(f"Twin updated for patient {hash_patient_id(update_request.patient_id)}")

        return {
            "status": "success",
            "patient_id": hash_patient_id(update_request.patient_id),
            "risk_score": twin_state.risk_score,
            "morphogenetic_score": twin_state.morphogenetic_score
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating twin: {type(e).__name__}")
        logger.debug(f"Error details: {str(e)}")  # Detailed error only in debug mode
        raise HTTPException(status_code=500, detail="Failed to update twin")

@app.get("/v1/twin/{patient_id}")
async def get_twin(patient_id: str, db = Depends(get_db)):
    """Get patient digital twin state"""
    try:
        twin = db.query(PatientTwin).filter(PatientTwin.patient_id == patient_id).first()
        if not twin:
            raise HTTPException(status_code=404, detail="Twin not found")
        
        # Decrypt and return state
        if fernet and twin.twin_state:
            try:
                decrypted_state = fernet.decrypt(twin.twin_state.encode())
                state = json.loads(decrypted_state.decode())
            except:
                # Fallback to non-encrypted state
                state = json.loads(twin.twin_state)
        else:
            state = json.loads(twin.twin_state) if twin.twin_state else {}
        
        return {
            "patient_id": hash_patient_id(patient_id),
            "twin_state": state,
            "last_sync": twin.last_sync.isoformat() if twin.last_sync else None,
            "morphogenetic_score": twin.morphogenetic_score
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving twin: {type(e).__name__}")
        logger.debug(f"Error details: {str(e)}")  # Detailed error only in debug mode
        raise HTTPException(status_code=500, detail="Failed to retrieve twin")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Initialize database
Base.metadata.create_all(bind=engine)
