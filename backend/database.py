"""
Swasthya Saathi AI - Database & Anonymized Analytics Layer
SQLite-backed persistence layer strictly adhering to privacy-by-design.

PRIVACY & ETHICS GUARANTEE:
No citizen names, phone numbers, device IDs, or personally identifiable information (PII)
are stored in this database. Only aggregated symptom codes, risk categories, and district
surveillance indicators are logged for public health department insights.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "swasthya_saathi.db")


def get_db_connection() -> sqlite3.Connection:
    """Create a connection to the SQLite database with row factory."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables and seed representative baseline surveillance records."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create consultation_logs table (Anonymized surveillance data)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consultation_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        district TEXT NOT NULL,
        language_detected TEXT,
        symptoms_json TEXT NOT NULL,
        risk_level TEXT NOT NULL,
        matched_indicators_json TEXT,
        recommended_specialty TEXT NOT NULL,
        matched_facility TEXT,
        extraction_method TEXT
    )
    """)

    # Seed baseline surveillance records if table is empty
    cursor.execute("SELECT COUNT(*) FROM consultation_logs")
    count = cursor.fetchone()[0]

    if count == 0:
        base_time = datetime.now(timezone.utc)
        sample_records = [
            ("conv-001", (base_time - timedelta(hours=36)).isoformat(), "Khordha", "Hinglish / Regional", ["fever", "weakness"], "URGENT", ["prolonged fever (> 3 days duration)"], "General Medicine", "Capital Hospital (PGIER)", "rule_based_nlp"),
            ("conv-002", (base_time - timedelta(hours=30)).isoformat(), "Cuttack", "English", ["severe chest pain"], "EMERGENCY", ["severe chest pain"], "Emergency Medicine", "SCB Medical College Casualty", "rule_based_nlp"),
            ("conv-003", (base_time - timedelta(hours=28)).isoformat(), "Khordha", "English", ["cold", "cough"], "ROUTINE", [], "General Medicine", "Capital Hospital (PGIER)", "rule_based_nlp"),
            ("conv-004", (base_time - timedelta(hours=24)).isoformat(), "Puri", "Hinglish / Regional", ["persistent vomiting", "abdominal pain"], "URGENT", ["persistent vomiting"], "Gastroenterology", "District Headquarters Hospital (DHH) Puri", "rule_based_nlp"),
            ("conv-005", (base_time - timedelta(hours=20)).isoformat(), "Sambalpur", "English", ["difficulty breathing"], "EMERGENCY", ["difficulty breathing"], "Emergency Medicine", "VIMSAR Burla", "rule_based_nlp"),
            ("conv-006", (base_time - timedelta(hours=18)).isoformat(), "Ganjam", "Hinglish / Regional", ["fever", "body ache"], "ROUTINE", [], "General Medicine", "MKCG Medical College & Hospital", "rule_based_nlp"),
            ("conv-007", (base_time - timedelta(hours=14)).isoformat(), "Sundargarh", "English", ["joint pain", "knee pain"], "ROUTINE", [], "Orthopedics", "Rourkela Government Hospital (RGH)", "rule_based_nlp"),
            ("conv-008", (base_time - timedelta(hours=10)).isoformat(), "Balasore", "English", ["skin rash", "itching"], "ROUTINE", [], "Dermatology", "District Headquarters Hospital Balasore", "rule_based_nlp"),
            ("conv-009", (base_time - timedelta(hours=6)).isoformat(), "Khordha", "Hinglish / Regional", ["fever", "cough", "weakness"], "URGENT", ["multiple concurrent symptoms requiring physician review"], "General Medicine", "AIIMS Bhubaneswar", "rule_based_nlp"),
            ("conv-010", (base_time - timedelta(hours=2)).isoformat(), "Cuttack", "English", ["loss of consciousness"], "EMERGENCY", ["loss of consciousness"], "Emergency Medicine", "SCB Medical College Casualty", "rule_based_nlp"),
        ]

        cursor.executemany("""
        INSERT INTO consultation_logs (
            conversation_id, timestamp, district, language_detected,
            symptoms_json, risk_level, matched_indicators_json,
            recommended_specialty, matched_facility, extraction_method
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (
                r[0], r[1], r[2], r[3],
                json.dumps(r[4]), r[5], json.dumps(r[6]),
                r[7], r[8], r[9]
            ) for r in sample_records
        ])

    conn.commit()
    conn.close()


def log_consultation(
    conversation_id: str,
    district: str,
    language_detected: str,
    symptoms: List[str],
    risk_level: str,
    matched_indicators: List[str],
    recommended_specialty: str,
    matched_facility: Optional[str] = None,
    extraction_method: str = "rule_based_nlp"
):
    """
    Log an anonymized consultation record for public health trend aggregation.
    No personal identifiers are ever stored.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO consultation_logs (
            conversation_id, timestamp, district, language_detected,
            symptoms_json, risk_level, matched_indicators_json,
            recommended_specialty, matched_facility, extraction_method
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            conversation_id,
            datetime.now(timezone.utc).isoformat(),
            district,
            language_detected,
            json.dumps(symptoms),
            risk_level,
            json.dumps(matched_indicators),
            recommended_specialty,
            matched_facility or "Local Health Facility",
            extraction_method
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging anonymized consultation: {e}")


def get_admin_dashboard_metrics() -> Dict[str, Any]:
    """
    Aggregate anonymized surveillance records across Odisha districts
    for the Health Department / Admin dashboard.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total counts
    cursor.execute("SELECT COUNT(*) FROM consultation_logs")
    total_consultations = cursor.fetchone()[0]

    # Risk level breakdown
    cursor.execute("SELECT risk_level, COUNT(*) FROM consultation_logs GROUP BY risk_level")
    risk_counts = {row[0]: row[1] for row in cursor.fetchall()}
    emergency_count = risk_counts.get("EMERGENCY", 0)
    urgent_count = risk_counts.get("URGENT", 0)
    routine_count = risk_counts.get("ROUTINE", 0)

    # Top symptoms
    cursor.execute("SELECT symptoms_json FROM consultation_logs")
    symptom_frequency: Dict[str, int] = {}
    for row in cursor.fetchall():
        try:
            s_list = json.loads(row[0])
            for sym in s_list:
                symptom_frequency[sym] = symptom_frequency.get(sym, 0) + 1
        except Exception:
            continue

    top_symptoms = [
        {"symptom": k.title(), "count": v}
        for k, v in sorted(symptom_frequency.items(), key=lambda x: x[1], reverse=True)[:8]
    ]

    # Specialty demand
    cursor.execute("""
    SELECT recommended_specialty, COUNT(*) as cnt
    FROM consultation_logs
    GROUP BY recommended_specialty
    ORDER BY cnt DESC
    LIMIT 6
    """)
    specialty_demand = [
        {"specialty": row[0], "count": row[1]}
        for row in cursor.fetchall()
    ]

    # District-wise distribution
    cursor.execute("""
    SELECT district,
           COUNT(*) as total,
           SUM(CASE WHEN risk_level = 'EMERGENCY' THEN 1 ELSE 0 END) as emergency_cases,
           SUM(CASE WHEN risk_level = 'URGENT' THEN 1 ELSE 0 END) as urgent_cases,
           SUM(CASE WHEN risk_level = 'ROUTINE' THEN 1 ELSE 0 END) as routine_cases
    FROM consultation_logs
    GROUP BY district
    ORDER BY total DESC
    """)
    district_trends = [
        {
            "district": row[0],
            "total_queries": row[1],
            "emergency_cases": row[2],
            "urgent_cases": row[3],
            "routine_cases": row[4]
        }
        for row in cursor.fetchall()
    ]

    # Facility demand
    cursor.execute("""
    SELECT matched_facility, COUNT(*) as cnt
    FROM consultation_logs
    WHERE matched_facility IS NOT NULL
    GROUP BY matched_facility
    ORDER BY cnt DESC
    LIMIT 5
    """)
    facility_demand = [
        {"facility": row[0], "routed_queries": row[1]}
        for row in cursor.fetchall()
    ]

    # Recent anonymized consultations
    cursor.execute("""
    SELECT conversation_id, timestamp, district, risk_level,
           symptoms_json, recommended_specialty, extraction_method
    FROM consultation_logs
    ORDER BY id DESC
    LIMIT 15
    """)
    recent_consultations = []
    for row in cursor.fetchall():
        try:
            s_list = json.loads(row[4])
        except Exception:
            s_list = []
        recent_consultations.append({
            "conversation_id": row[0],
            "timestamp": row[1][:19].replace("T", " "),
            "district": row[2],
            "risk_level": row[3],
            "symptoms": s_list,
            "recommended_specialty": row[5],
            "extraction_method": row[6]
        })

    conn.close()

    return {
        "total_consultations": total_consultations,
        "emergency_count": emergency_count,
        "urgent_count": urgent_count,
        "routine_count": routine_count,
        "top_symptoms": top_symptoms,
        "specialty_demand": specialty_demand,
        "district_trends": district_trends,
        "facility_demand": facility_demand,
        "recent_consultations": recent_consultations,
        "data_freshness_summary": {
            "catalog_status": "DEMO_DATA_VALIDATED",
            "last_synced": datetime.now(timezone.utc).isoformat()[:19] + "Z",
            "live_hospital_integration": "pending_nhm_api_gateway"
        }
    }


# Initialize DB on module load
init_db()
