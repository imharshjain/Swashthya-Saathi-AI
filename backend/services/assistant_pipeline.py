"""
Swasthya Saathi AI - Unified Assistant Pipeline Service
Coordinates the end-to-end Citizen query flow:
Natural Language -> AI Symptom Extraction -> Clinical Triage -> Provider Recommendation -> Anonymized Logging
"""

import uuid
from typing import Dict, Any, Optional
from backend.ai_service import extract_symptoms
from backend.triage_engine import assess_triage
from backend.doctor_service import (
    load_doctors_dataset,
    recommend_doctors,
    map_symptoms_to_specialty
)
from backend.database import log_consultation


def process_health_query(
    message: str,
    district: Optional[str] = "Khordha",
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None
) -> Dict[str, Any]:
    """
    End-to-end orchestration pipeline for citizen health queries.
    
    1. Receive citizen natural language input.
    2. Extract structured symptoms, duration, and severity via AI / NLP.
    3. Evaluate clinical risk through the deterministic triage engine.
    4. Map condition to an appropriate healthcare specialty.
    5. Search and rank verified healthcare providers in Odisha with distance calculation.
    6. Log an anonymized surveillance record in SQLite (Zero PII).
    7. Return a unified, structured response.
    """
    conversation_id = f"conv-{uuid.uuid4().hex[:8]}"

    # Step 1: AI / NLP Symptom Extraction
    extraction = extract_symptoms(message)
    symptoms = extraction.get("symptoms", [])
    duration = extraction.get("duration")
    severity = extraction.get("severity")
    additional_info = extraction.get("additional_information", [])
    lang_detected = extraction.get("language_detected", "English / Hinglish")
    method = extraction.get("extraction_method", "rule_based_nlp")

    # Step 2: Clinical Triage Assessment
    triage = assess_triage(symptoms, duration=duration, severity=severity)
    risk_level = triage.get("risk_level", "ROUTINE")
    matched_indicators = triage.get("matched_indicators", [])

    # Step 3: Specialty Mapping
    specialty = map_symptoms_to_specialty(
        symptoms=symptoms,
        risk_level=risk_level,
        additional_info=additional_info
    )

    # Step 4: Doctor / Facility Recommendation & Ranking
    location_arg = (user_lat, user_lon) if (user_lat is not None and user_lon is not None) else (district or "Khordha")
    doctors_data = load_doctors_dataset()
    providers = recommend_doctors(
        doctors=doctors_data,
        speciality=specialty,
        user_location=location_arg
    )

    top_facility = providers[0]["facility"] if providers else "Local Health Facility"

    # Step 5: Privacy-Preserving Surveillance Logging (Zero PII)
    log_consultation(
        conversation_id=conversation_id,
        district=district or "Khordha",
        language_detected=lang_detected,
        symptoms=symptoms,
        risk_level=risk_level,
        matched_indicators=matched_indicators,
        recommended_specialty=specialty,
        matched_facility=top_facility,
        extraction_method=method
    )

    # Step 6: Construct Unified Response
    return {
        "conversation_id": conversation_id,
        "original_message": message,
        "structured_symptoms": extraction,
        "triage_assessment": triage,
        "recommended_specialty": specialty,
        "providers": providers,
        "disclaimer": (
            "Notice: This is an AI healthcare prototype for Odisha. "
            "It does not provide clinical diagnosis or prescriptions. "
            "Provider information is demo data and must be verified before consultation."
        ),
        "data_provenance_notice": (
            "All provider details are synthetic demo records (is_demo=true). "
            "Current appointment availability requires provider confirmation."
        )
    }
