"""
Swasthya Saathi AI - Health Schemas
Pydantic schemas for request and response validation across the application.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class SymptomExtractionResult(BaseModel):
    """Structured extraction of citizen-reported health information."""
    symptoms: List[str] = Field(
        default_factory=list,
        description="Normalized list of symptoms reported by the citizen"
    )
    duration: Optional[str] = Field(
        default=None,
        description="Duration of symptoms if mentioned (e.g. '3 days')"
    )
    severity: Optional[str] = Field(
        default=None,
        description="Subjective or objective severity if mentioned (e.g. 'mild', '101 F', 'severe')"
    )
    additional_information: List[str] = Field(
        default_factory=list,
        description="Relevant additional context (e.g. age, prior history, body location)"
    )
    language_detected: Optional[str] = Field(
        default="English / Hinglish",
        description="Language or dialect detected"
    )
    extraction_method: str = Field(
        default="rule_based_nlp",
        description="Method used for extraction: 'llm' or 'rule_based_nlp'"
    )


class SymptomRequest(BaseModel):
    """Legacy or direct list input for symptom extraction."""
    symptoms: List[str] = Field(..., description="List of raw symptom strings")


class CitizenMessage(BaseModel):
    """Natural language message submitted by a citizen."""
    message: str = Field(..., min_length=1, description="Natural language health concern")
    district: Optional[str] = Field(default="Khordha", description="Citizen's current Odisha district")
    user_latitude: Optional[float] = Field(default=20.2961, description="User latitude (default: Bhubaneswar)")
    user_longitude: Optional[float] = Field(default=85.8245, description="User longitude (default: Bhubaneswar)")


class TriageRequest(BaseModel):
    """Input payload for clinical triage assessment."""
    symptoms: List[str] = Field(..., description="List of extracted symptoms")
    duration: Optional[str] = Field(default=None, description="Reported duration")
    severity: Optional[str] = Field(default=None, description="Reported severity")


class EmergencyContact(BaseModel):
    """Emergency helpline information for Odisha."""
    service: str
    number: str
    description: str


class TriageResult(BaseModel):
    """Deterministic clinical risk assessment result."""
    risk_level: Literal["EMERGENCY", "URGENT", "ROUTINE"] = Field(
        ...,
        description="Triage risk category"
    )
    matched_indicators: List[str] = Field(
        default_factory=list,
        description="Predefined risk triggers matched by the triage engine"
    )
    recommended_action: str = Field(
        ...,
        description="Next step guidance for the citizen"
    )
    clinical_disclaimer: str = Field(
        default="Swasthya Saathi AI provides information triage only and does not diagnose conditions or prescribe medications. In an emergency, immediately seek professional emergency medical assistance.",
        description="Mandatory clinical safety disclaimer"
    )
    emergency_contacts: Optional[List[EmergencyContact]] = Field(
        default=None,
        description="Emergency contacts displayed for high-risk triage levels"
    )


class DoctorRecommendation(BaseModel):
    """Structured healthcare provider recommendation card."""
    doctor_id: str
    name: str
    speciality: str
    facility: str
    facility_type: str = "Government Tertiary Hospital"
    district: str
    latitude: float
    longitude: float
    distance_km: Optional[float] = None
    consultation_fee: float = 0.0
    verified: bool = True
    is_demo: bool = True
    data_source: str = "DEMO_DATA"
    verification_status: str = "demo_verified"
    availability_status: str = "provider_confirmation_required"
    last_updated: str = "2026-08-19T00:00:00Z"
    next_slot: Optional[str] = None
    contact_phone: Optional[str] = "104 (Health Helpline)"


class FacilityInfo(BaseModel):
    """Healthcare facility details in Odisha."""
    facility_id: str
    name: str
    type: str
    district: str
    latitude: float
    longitude: float
    emergency_capable: bool = True
    helpline: str = "108 / 104"
    is_demo: bool = True
    data_source: str = "DEMO_DATA"


class AssistantResponse(BaseModel):
    """Unified full-stack response for the citizen assistant."""
    conversation_id: str
    original_message: str
    structured_symptoms: SymptomExtractionResult
    triage_assessment: TriageResult
    recommended_specialty: str
    providers: List[DoctorRecommendation]
    disclaimer: str = (
        "Notice: This is an AI healthcare prototype for Odisha. "
        "It does not provide clinical diagnosis or prescriptions. "
        "Provider information is demo data and must be verified before consultation."
    )
    data_provenance_notice: str = (
        "All provider details are synthetic demo records (is_demo=true). "
        "Current appointment availability requires provider confirmation."
    )


class ProviderAvailabilityResponse(BaseModel):
    """Detailed freshness and availability status for a provider."""
    doctor_id: str
    name: str
    speciality: str
    facility: str
    availability_status: str
    provider_confirmation_required: bool
    data_source: str
    last_updated: str
    is_demo: bool
    notice: str


class AdminDashboardMetrics(BaseModel):
    """Aggregated surveillance and utilization metrics for the Health Department."""
    total_consultations: int
    emergency_count: int
    urgent_count: int
    routine_count: int
    top_symptoms: List[Dict[str, Any]]
    specialty_demand: List[Dict[str, Any]]
    district_trends: List[Dict[str, Any]]
    facility_demand: List[Dict[str, Any]]
    recent_consultations: List[Dict[str, Any]]
    data_freshness_summary: Dict[str, Any]
