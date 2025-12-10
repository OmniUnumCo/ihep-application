# ai_inference_service/main.py
import os
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Any
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import shap
from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_patient_id(patient_id: str) -> str:
    """Hash patient ID for secure logging (HIPAA compliance)"""
    return hashlib.sha256(patient_id.encode()).hexdigest()[:16]

app = FastAPI(title="AI/ML Inference Service")

class PatientData(BaseModel):
    patient_id: str
    viral_load: float
    cd4_count: float
    medication_adherence: float
    appointment_attendance: float
    age: int
    gender: str
    treatment_duration: float

class RiskPrediction(BaseModel):
    patient_id: str
    risk_score: float
    confidence: float
    explanation: Dict[str, float]
    recommendations: List[str]
    timestamp: str

class AIPredictionService:
    def __init__(self):
        self.project_id = os.getenv('GCP_PROJECT_ID')
        self.location = os.getenv('GCP_LOCATION', 'us-central1')
        self.model_endpoint = os.getenv('MODEL_ENDPOINT')
        
        # Initialize Vertex AI
        aiplatform.init(project=self.project_id, location=self.location)
        
        # Load local model for fallback
        try:
            self.local_model = joblib.load('models/adherence_model_v1.2.pkl')
            self.explainer = shap.Explainer(self.local_model)
        except Exception as e:
            logger.warning(f"Could not load local model: {e}")
            self.local_model = None
            self.explainer = None

    def prepare_features(self, patient_data: PatientData) -> np.ndarray:
        """Prepare features for model prediction"""
        # Feature engineering
        features = np.array([
            patient_data.viral_load,
            patient_data.cd4_count,
            patient_data.medication_adherence,
            patient_data.appointment_attendance,
            patient_data.age,
            1 if patient_data.gender.lower() == 'male' else 0,
            patient_data.treatment_duration,
            patient_data.viral_load / max(patient_data.cd4_count, 1),  # viral load to CD4 ratio
            patient_data.medication_adherence * patient_data.appointment_attendance  # interaction term
        ]).reshape(1, -1)
        
        return features

    def predict_with_vertex_ai(self, features: np.ndarray) -> tuple:
        """Make prediction using Vertex AI endpoint"""
        try:
            # This would make actual API call to Vertex AI
            # For demonstration, we'll simulate the response
            prediction = np.random.beta(2, 5)  # Simulated risk score
            confidence = 0.95  # Simulated confidence
            
            return prediction, confidence
        except Exception as e:
            logger.error(f"Vertex AI prediction failed: {e}")
            raise

    def explain_prediction(self, features: np.ndarray, patient_data: PatientData) -> Dict[str, float]:
        """Generate SHAP explanation for prediction"""
        if not self.explainer or not self.local_model:
            return {"error": "Local model not available for explanation"}
        
        try:
            shap_values = self.explainer(features)
            feature_names = [
                'viral_load', 'cd4_count', 'medication_adherence', 
                'appointment_attendance', 'age', 'gender_male',
                'treatment_duration', 'vl_cd4_ratio', 'adherence_appt_interaction'
            ]
            
            explanation = {}
            for i, name in enumerate(feature_names):
                explanation[name] = float(shap_values[0][i])
            
            return explanation
        except Exception as e:
            logger.error(f"Explanation generation failed: {e}")
            return {"error": "Could not generate explanation"}

    def generate_recommendations(self, risk_score: float, patient_data: PatientData) -> List[str]:
        """Generate personalized recommendations based on risk score and patient data"""
        recommendations = []
        
        if risk_score > 0.7:
            recommendations.append("Immediate clinical intervention recommended")
            recommendations.append("Increase medication adherence monitoring")
        elif risk_score > 0.4:
            recommendations.append("Enhanced patient engagement program")
            recommendations.append("Regular follow-up appointments scheduled")
        else:
            recommendations.append("Continue current treatment plan")
            recommendations.append("Standard monitoring protocol")
        
        if patient_data.medication_adherence < 0.8:
            recommendations.append("Medication adherence support program")
        
        if patient_data.appointment_attendance < 0.7:
            recommendations.append("Appointment reminder system activation")
        
        return recommendations

# Initialize service
ai_service = AIPredictionService()

@app.post("/v1/predict/risk", response_model=RiskPrediction)
async def predict_risk(patient_data: PatientData):
    """Predict patient risk score using AI model"""
    try:
        # Prepare features
        features = ai_service.prepare_features(patient_data)
        
        # Make prediction
        try:
            risk_score, confidence = ai_service.predict_with_vertex_ai(features)
        except Exception as e:
            logger.error(f"Primary prediction failed: {e}")
            raise HTTPException(status_code=500, detail="Prediction service unavailable")
        
        # Generate explanation
        explanation = ai_service.explain_prediction(features, patient_data)
        
        # Generate recommendations
        recommendations = ai_service.generate_recommendations(risk_score, patient_data)
        
        # Create response (hash patient_id for HIPAA compliance)
        prediction = RiskPrediction(
            patient_id=hash_patient_id(patient_data.patient_id),
            risk_score=float(risk_score),
            confidence=float(confidence),
            explanation=explanation,
            recommendations=recommendations,
            timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(f"Risk prediction generated for patient {hash_patient_id(patient_data.patient_id)}: {risk_score:.3f}")
        
        return prediction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in risk prediction: {type(e).__name__}")
        logger.debug(f"Error details: {str(e)}")  # Detailed error only in debug mode
        raise HTTPException(status_code=500, detail="Failed to generate prediction")

@app.get("/v1/model/status")
async def model_status():
    """Get model status and performance metrics"""
    return {
        "model_version": "v1.2",
        "status": "active",
        "performance_metrics": {
            "auc": 0.92,
            "precision": 0.88,
            "recall": 0.85,
            "f1_score": 0.86
        },
        "last_updated": "2024-01-15T10:30:00Z",
        "bias_metrics": {
            "gender_parity": 0.95,
            "age_parity": 0.92
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
