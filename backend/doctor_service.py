"""
Swasthya Saathi AI - Doctor Recommendation Service
Filters and ranks healthcare providers based on clinical specialty,
geographic proximity (Odisha context), verification, and consultation fee.

CRITICAL SAFETY & REALISM RULE:
All demo provider records are synthetic (is_demo=true, data_source='DEMO_DATA').
Real-time availability is explicitly labelled as requiring provider confirmation.
"""

import json
import math
import os
from typing import List, Dict, Any, Optional, Tuple

# Default reference coordinates: Master Canteen / Central Bhubaneswar, Odisha
DEFAULT_ODISHA_LAT = 20.2961
DEFAULT_ODISHA_LON = 85.8245

DISTRICT_COORDINATES: Dict[str, Tuple[float, float]] = {
    "khordha": (20.2961, 85.8245),
    "bhubaneswar": (20.2961, 85.8245),
    "cuttack": (20.4625, 85.8828),
    "puri": (19.8135, 85.8312),
    "ganjam": (19.3149, 84.7941),
    "berhampur": (19.3149, 84.7941),
    "sambalpur": (21.4669, 83.9812),
    "burla": (21.4983, 83.8741),
    "sundargarh": (22.2604, 84.8536),
    "rourkela": (22.2289, 84.8573),
    "balasore": (21.4934, 86.9135),
    "koraput": (18.8135, 82.7123),
    "mayurbhanj": (21.9287, 86.7329)
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance in kilometers between two points."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)


def load_doctors_dataset() -> List[Dict[str, Any]]:
    """Load synthetic demo doctors dataset from data/doctors.json."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", "doctors.json")
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def map_symptoms_to_specialty(
    symptoms: List[str],
    risk_level: str = "ROUTINE",
    additional_info: Optional[List[str]] = None
) -> str:
    """
    Map extracted symptoms and risk assessment to the most appropriate clinical specialty.
    """
    if risk_level == "EMERGENCY":
        return "Emergency Medicine"

    norm_symptoms = [s.strip().lower() for s in symptoms if s]

    # Pediatric check
    if additional_info and any("pediatric" in str(info).lower() or "child" in str(info).lower() for info in additional_info):
        return "Pediatrics"

    # Specialty mapping heuristics
    for sym in norm_symptoms:
        if any(term in sym for term in ["chest pain", "tightness", "palpitation"]):
            return "Cardiology"
        if any(term in sym for term in ["breathing", "breathlessness", "asthma", "cough", "wheez"]):
            return "Pulmonology"
        if any(term in sym for term in ["abdominal pain", "vomit", "vomiting", "loose motions", "diarrhea", "stomach", "acidity"]):
            return "Gastroenterology"
        if any(term in sym for term in ["rash", "itching", "skin", "allergy"]):
            return "Dermatology"
        if any(term in sym for term in ["joint", "knee", "bone", "back pain", "fracture", "sprain"]):
            return "Orthopedics"
        if any(term in sym for term in ["consciousness", "faint", "seizure", "paralysis", "migraine"]):
            return "Neurology"

    return "General Medicine"


def recommend_doctors(
    doctors: List[Dict[str, Any]],
    speciality: str,
    user_location: Any = None
) -> List[Dict[str, Any]]:
    """
    Filter and rank healthcare providers by specialty, proximity, verification, and fee.
    
    Args:
        doctors: List of provider dictionaries.
        speciality: Required medical specialty.
        user_location: Tuple of (lat, lon), dict {'latitude': ..., 'longitude': ...}, or district name string.
    
    Returns:
        Ranked list of provider recommendation dictionaries with distance and freshness metadata.
    """
    # 1. Parse user coordinates
    user_lat = DEFAULT_ODISHA_LAT
    user_lon = DEFAULT_ODISHA_LON

    if isinstance(user_location, (tuple, list)) and len(user_location) >= 2:
        user_lat, user_lon = float(user_location[0]), float(user_location[1])
    elif isinstance(user_location, dict):
        user_lat = float(user_location.get("latitude", DEFAULT_ODISHA_LAT))
        user_lon = float(user_location.get("longitude", DEFAULT_ODISHA_LON))
    elif isinstance(user_location, str):
        dist_key = user_location.strip().lower()
        if dist_key in DISTRICT_COORDINATES:
            user_lat, user_lon = DISTRICT_COORDINATES[dist_key]

    # 2. Filter and rank matching providers
    matched = []
    speciality_norm = speciality.strip().lower()

    for doctor in doctors:
        # Require verified flag
        if not doctor.get("verified", False):
            continue

        doc_spec = doctor.get("speciality", "").strip().lower()
        # Exact match or General Medicine fallback for non-emergency if specialty has few doctors
        is_exact = doc_spec == speciality_norm
        is_gen_fallback = (doc_spec == "general medicine" and speciality_norm != "emergency medicine")

        if not (is_exact or is_gen_fallback):
            continue

        doc_copy = dict(doctor)
        doc_lat = doc_copy.get("latitude", DEFAULT_ODISHA_LAT)
        doc_lon = doc_copy.get("longitude", DEFAULT_ODISHA_LON)
        doc_copy["distance_km"] = haversine_distance(user_lat, user_lon, doc_lat, doc_lon)

        # Enforce demo data transparency
        doc_copy["is_demo"] = True
        doc_copy["data_source"] = "DEMO_DATA"
        doc_copy["verification_status"] = "demo_verified"
        doc_copy["availability_status"] = "provider_confirmation_required"
        doc_copy["last_updated"] = doc_copy.get("last_updated", "2026-08-19T00:00:00Z")

        # Flag specialty exact match weight (0 = exact match, 1 = general fallback)
        doc_copy["_spec_match_rank"] = 0 if is_exact else 1

        matched.append(doc_copy)

    # 3. Sort: First exact specialty match, then proximity (distance), then consultation fee
    matched.sort(
        key=lambda d: (
            d.get("_spec_match_rank", 0),
            d.get("distance_km", 9999),
            d.get("consultation_fee", 0)
        )
    )

    # Clean internal sort keys
    for doc in matched:
        doc.pop("_spec_match_rank", None)

    return matched


def get_provider_availability(doctor_id: str) -> Dict[str, Any]:
    """
    Retrieve provider availability metadata with strict freshness transparency.
    """
    doctors = load_doctors_dataset()
    for doc in doctors:
        if doc.get("doctor_id") == doctor_id:
            return {
                "doctor_id": doc["doctor_id"],
                "name": doc["name"],
                "speciality": doc["speciality"],
                "facility": doc["facility"],
                "availability_status": "provider_confirmation_required",
                "provider_confirmation_required": True,
                "data_source": "DEMO_DATA",
                "last_updated": doc.get("last_updated", "2026-08-19T00:00:00Z"),
                "is_demo": True,
                "notice": "Current appointment availability requires direct provider confirmation. Demo dataset record."
            }
    return {
        "doctor_id": doctor_id,
        "availability_status": "provider_not_found",
        "provider_confirmation_required": True,
        "data_source": "DEMO_DATA",
        "last_updated": "2026-08-19T00:00:00Z",
        "is_demo": True,
        "notice": "Provider ID not found in demo catalog."
    }