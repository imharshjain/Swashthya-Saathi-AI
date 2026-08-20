"""
Swasthya Saathi AI - Clinical Triage Engine
Deterministic clinical safety rule engine for initial risk classification.

Target: Odisha State Health Ecosystem
Categories:
1. EMERGENCY - Immediate life-threatening signs (Prompts 108 Ambulance / Emergency Dept)
2. URGENT    - Potentially serious symptoms requiring prompt medical consultation (within 24 hours)
3. ROUTINE   - Non-critical, self-limiting symptoms suitable for standard outpatient consultation

SAFETY NOTICE:
This is a rule-based triage assessment tool for demonstration and routing purposes.
It does NOT diagnose medical conditions or provide clinical treatment plans.
"""

from typing import List, Dict, Any, Optional

# Core Emergency Indicators (Preserved and Expanded)
EMERGENCY_SYMPTOMS = {
    "difficulty breathing",
    "severe chest pain",
    "loss of consciousness",
    "severe bleeding",
    "sudden paralysis",
    "stroke symptoms",
    "choking",
    "cyanosis",
    "anaphylaxis"
}

# Core Urgent Indicators (Preserved and Expanded)
URGENT_SYMPTOMS = {
    "high fever",
    "persistent vomiting",
    "severe abdominal pain",
    "dehydration",
    "loose motions",
    "acute rash with fever",
    "deep wound",
    "persistent dizziness"
}

# Emergency contacts for Odisha
ODISHA_EMERGENCY_CONTACTS = [
    {
        "service": "Odisha Emergency Medical Ambulance",
        "number": "108",
        "description": "24x7 Free emergency ambulance dispatch across all 30 districts of Odisha"
    },
    {
        "service": "Odisha State Health Helpline",
        "number": "104",
        "description": "Toll-free 24x7 medical information and health assistance"
    },
    {
        "service": "National Emergency Response Support",
        "number": "112",
        "description": "Unified national emergency number"
    }
]


def assess_triage(
    symptoms: List[str],
    duration: Optional[str] = None,
    severity: Optional[str] = None
) -> Dict[str, Any]:
    """
    Deterministic rule-based clinical risk assessment engine.
    
    Evaluates extracted symptoms, reported duration, and severity against
    predefined clinical risk thresholds.
    """
    if not symptoms:
        return {
            "risk_level": "ROUTINE",
            "matched_indicators": [],
            "recommended_action": "No specific symptoms were identified. If you feel unwell, consult a qualified medical doctor at your nearest Primary Health Centre (PHC) or Community Health Centre (CHC).",
            "clinical_disclaimer": "Swasthya Saathi AI provides health information and triage guidance only. It does not provide medical diagnosis or prescriptions.",
            "emergency_contacts": None
        }

    normalized_symptoms = [symptom.strip().lower() for symptom in symptoms if symptom]

    matched_emergency = set()
    matched_urgent = set()

    # 1. Evaluate Emergency Indicators (exact or token/phrase matching)
    for sym in normalized_symptoms:
        # Check against emergency set
        for emer_rule in EMERGENCY_SYMPTOMS:
            if emer_rule == sym or emer_rule in sym or sym in emer_rule:
                # Disambiguate simple "pain" or generic terms
                if sym == "pain" or sym == "fever":
                    continue
                matched_emergency.add(emer_rule)

    # 2. Evaluate Urgent Indicators
    for sym in normalized_symptoms:
        for urg_rule in URGENT_SYMPTOMS:
            if urg_rule == sym or urg_rule in sym or sym in urg_rule:
                if sym == "fever" and "high fever" not in sym:
                    continue
                matched_urgent.add(urg_rule)

    # 3. Contextual modifiers (Duration & Severity upgrades)
    # High fever criteria: e.g. fever with measured temp >= 101°F or duration >= 3 days
    if "fever" in normalized_symptoms and "high fever" not in matched_urgent:
        if severity and any(val in severity.lower() for val in ["severe", "high", "101", "102", "103", "104"]):
            matched_urgent.add("high fever (elevated temperature/severity)")
        elif duration and any(d in duration.lower() for d in ["3 days", "4 days", "5 days", "week", "hafte", "din se", "3 din"]):
            matched_urgent.add("prolonged fever (> 3 days duration)")

    # Multiple concurrent symptoms upgrade
    if len(normalized_symptoms) >= 3 and not matched_emergency and not matched_urgent:
        matched_urgent.add("multiple concurrent symptoms requiring physician review")

    # 4. Triage Determination
    if matched_emergency:
        return {
            "risk_level": "EMERGENCY",
            "matched_indicators": sorted(list(matched_emergency)),
            "recommended_action": "Your reported symptoms may require immediate emergency medical evaluation. Please contact emergency medical services or proceed immediately to the nearest Emergency / Casualty Department (e.g., AIIMS Bhubaneswar, SCB Medical College Cuttack, or your District Headquarters Hospital).",
            "clinical_disclaimer": "CRITICAL: Swasthya Saathi AI is not a certified diagnostic system. For life-threatening emergencies, call 108 immediately.",
            "emergency_contacts": ODISHA_EMERGENCY_CONTACTS
        }

    if matched_urgent:
        return {
            "risk_level": "URGENT",
            "matched_indicators": sorted(list(matched_urgent)),
            "recommended_action": "Your symptoms indicate a condition that should be evaluated promptly by a qualified medical professional (preferably within 24 hours). Please consult a doctor at your nearest Sub-Divisional Hospital (SDH), Community Health Centre (CHC), or District Hospital.",
            "clinical_disclaimer": "Swasthya Saathi AI provides preliminary triage guidance only and does not replace in-person clinical examination.",
            "emergency_contacts": [ODISHA_EMERGENCY_CONTACTS[1]]  # 104 helpline
        }

    # ROUTINE
    return {
        "risk_level": "ROUTINE",
        "matched_indicators": [],
        "recommended_action": "Your symptoms appear suitable for a standard routine consultation. Schedule an appointment or visit your local Primary Health Centre (PHC) / Wellness Centre for clinical guidance.",
        "clinical_disclaimer": "Swasthya Saathi AI provides information triage only and does not diagnose conditions or prescribe medications. Always consult a licensed healthcare provider for medical care.",
        "emergency_contacts": None
    }