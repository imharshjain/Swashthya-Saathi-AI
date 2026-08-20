"""
Swasthya Saathi AI - FastAPI Backend Application
Odisha State Health & Family Welfare AI Healthcare Assistant

Endpoints:
- GET  /                           : API Info & Health Status
- GET  /health                     : Readiness and liveness probe
- POST /assistant                  : Unified citizen pipeline (Extraction -> Triage -> Providers)
- POST /extract-symptoms           : Structured AI/NLP symptom extraction
- POST /triage                     : Clinical risk classification
- GET  /doctors                    : Search & filter healthcare providers
- GET  /doctors/{id}               : Provider details by ID
- GET  /facilities                 : Odisha healthcare facility directory
- GET  /availability/{provider_id} : Provider availability freshness status
- GET  /admin/dashboard            : Anonymized public health surveillance analytics
"""

import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas.health_schemas import (
    SymptomExtractionResult,
    CitizenMessage,
    TriageRequest,
    TriageResult,
    DoctorRecommendation,
    FacilityInfo,
    AssistantResponse,
    AdminDashboardMetrics,
    ProviderAvailabilityResponse,
)
from backend.ai_service import extract_symptoms
from backend.triage_engine import assess_triage
from backend.doctor_service import (
    load_doctors_dataset,
    recommend_doctors,
    get_provider_availability
)
from backend.services.assistant_pipeline import process_health_query
from backend.database import get_admin_dashboard_metrics

app = FastAPI(
    title="Swasthya Saathi AI",
    description="Odisha State Health & Family Welfare AI Healthcare Assistant API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Streamlit and web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["System"])
def home():
    """API Root endpoint."""
    return {
        "service": "Swasthya Saathi AI",
        "description": "AI-assisted healthcare platform for Odisha State Health & Family Welfare",
        "version": "1.0.0",
        "status": "operational",
        "state_context": "Odisha, India",
        "docs": "/docs"
    }


@app.get("/health", tags=["System"])
def health():
    """System health check probe."""
    return {
        "status": "healthy",
        "service": "swasthya-saathi-ai-backend",
        "database": "connected",
        "ai_engine": "active"
    }


@app.post(
    "/assistant",
    response_model=AssistantResponse,
    status_code=status.HTTP_200_OK,
    tags=["Citizen Assistant"]
)
def citizen_assistant_pipeline(request: CitizenMessage):
    """
    Unified citizen health assistant endpoint.
    Performs end-to-end NLP symptom extraction, deterministic clinical triage,
    specialty mapping, proximity-aware doctor recommendations, and anonymized surveillance logging.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Health concern message cannot be empty."
        )

    try:
        response_data = process_health_query(
            message=request.message,
            district=request.district,
            user_lat=request.user_latitude,
            user_lon=request.user_longitude
        )
        return response_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the health query: {str(e)}"
        )


@app.post(
    "/extract-symptoms",
    response_model=SymptomExtractionResult,
    tags=["AI Service"]
)
def extract_symptoms_api(request: CitizenMessage):
    """
    Extract structured symptoms, duration, severity, and context from natural language text.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty."
        )
    return extract_symptoms(request.message)


@app.post(
    "/triage",
    response_model=TriageResult,
    tags=["Triage Engine"]
)
def triage_api(request: TriageRequest):
    """
    Assess clinical urgency (EMERGENCY, URGENT, ROUTINE) based on deterministic clinical rules.
    """
    return assess_triage(
        symptoms=request.symptoms,
        duration=request.duration,
        severity=request.severity
    )


@app.get(
    "/doctors",
    response_model=List[DoctorRecommendation],
    tags=["Providers"]
)
def get_doctors_api(
    speciality: Optional[str] = Query(None, description="Filter by clinical specialty"),
    district: Optional[str] = Query(None, description="Filter by Odisha district"),
    max_fee: Optional[float] = Query(None, description="Maximum consultation fee")
):
    """
    Search and filter verified healthcare providers in Odisha with demo data provenance.
    """
    doctors = load_doctors_dataset()
    if speciality:
        doctors = recommend_doctors(doctors, speciality=speciality, user_location=district)
    if district:
        doctors = [d for d in doctors if d.get("district", "").lower() == district.lower()]
    if max_fee is not None:
        doctors = [d for d in doctors if d.get("consultation_fee", 0) <= max_fee]
    return doctors


@app.get(
    "/doctors/{doctor_id}",
    response_model=DoctorRecommendation,
    tags=["Providers"]
)
def get_doctor_by_id(doctor_id: str):
    """
    Retrieve specific provider details by doctor ID.
    """
    doctors = load_doctors_dataset()
    for doc in doctors:
        if doc.get("doctor_id") == doctor_id:
            return doc
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Provider with ID '{doctor_id}' was not found."
    )


@app.get(
    "/facilities",
    response_model=List[FacilityInfo],
    tags=["Facilities"]
)
def get_facilities_api(
    district: Optional[str] = Query(None, description="Filter by Odisha district")
):
    """
    Retrieve directory of Odisha healthcare facilities (AIIMS, SCB, DHHs, CHCs).
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", "facilities.json")
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        facilities = json.load(f)
    if district:
        facilities = [f for f in facilities if f.get("district", "").lower() == district.lower()]
    return facilities


@app.get(
    "/availability/{provider_id}",
    response_model=ProviderAvailabilityResponse,
    tags=["Providers"]
)
def get_availability_api(provider_id: str):
    """
    Check appointment availability and data freshness metadata for a provider.
    """
    return get_provider_availability(provider_id)


@app.get(
    "/admin/dashboard",
    response_model=AdminDashboardMetrics,
    tags=["Health Department Admin"]
)
def admin_dashboard_api():
    """
    Retrieve aggregated, privacy-conscious surveillance data for the Health Department dashboard.
    """
    return get_admin_dashboard_metrics()