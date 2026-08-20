# Swasthya Saathi AI - REST API Documentation

The FastAPI backend exposes RESTful endpoints for citizen triage, provider search, and departmental surveillance analytics.

---

## Base URL
`http://127.0.0.1:8000` (Local) / Configurable via `API_URL`

---

## Endpoints

### 1. System Health Probe
- **Method:** `GET`
- **Path:** `/health`
- **Response:**
  ```json
  {
    "status": "healthy",
    "service": "swasthya-saathi-ai-backend",
    "database": "connected",
    "ai_engine": "active"
  }
  ```

---

### 2. Unified Citizen Health Assistant Pipeline
- **Method:** `POST`
- **Path:** `/assistant`
- **Description:** Orchestrates end-to-end NLP symptom extraction, triage assessment, specialty matching, and provider recommendation.
- **Request Body:**
  ```json
  {
    "message": "Mujhe 3 din se bukhar hai aur weakness bhi hai.",
    "district": "Khordha",
    "user_latitude": 20.2961,
    "user_longitude": 85.8245
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "conversation_id": "conv-a1b2c3d4",
    "original_message": "Mujhe 3 din se bukhar hai aur weakness bhi hai.",
    "structured_symptoms": {
      "symptoms": ["fever", "weakness"],
      "duration": "3 days",
      "severity": null,
      "additional_information": [],
      "language_detected": "Hinglish / Regional",
      "extraction_method": "rule_based_nlp"
    },
    "triage_assessment": {
      "risk_level": "URGENT",
      "matched_indicators": ["prolonged fever (> 3 days duration)"],
      "recommended_action": "Your symptoms indicate a condition that should be evaluated promptly by a qualified medical professional (preferably within 24 hours)...",
      "clinical_disclaimer": "Swasthya Saathi AI provides preliminary triage guidance only and does not replace in-person clinical examination.",
      "emergency_contacts": [
        {
          "service": "Odisha State Health Helpline",
          "number": "104",
          "description": "Toll-free 24x7 medical information and health assistance"
        }
      ]
    },
    "recommended_specialty": "General Medicine",
    "providers": [
      {
        "doctor_id": "DOC_OD_001",
        "name": "Dr. Subhashree Mishra (Demo MD)",
        "speciality": "General Medicine",
        "facility": "Capital Hospital (PGIER)",
        "facility_type": "District Post-Graduate Institute",
        "district": "Khordha",
        "distance_km": 3.5,
        "consultation_fee": 0.0,
        "verified": true,
        "is_demo": true,
        "data_source": "DEMO_DATA",
        "verification_status": "demo_verified",
        "availability_status": "provider_confirmation_required",
        "last_updated": "2026-08-19T00:00:00Z"
      }
    ],
    "disclaimer": "Notice: This is an AI healthcare prototype for Odisha. It does not provide clinical diagnosis or prescriptions...",
    "data_provenance_notice": "All provider details are synthetic demo records (is_demo=true)..."
  }
  ```

---

### 3. Direct Symptom Extraction
- **Method:** `POST`
- **Path:** `/extract-symptoms`
- **Request Body:**
  ```json
  {
    "message": "I have severe chest pain and difficulty breathing."
  }
  ```

---

### 4. Direct Triage Assessment
- **Method:** `POST`
- **Path:** `/triage`
- **Request Body:**
  ```json
  {
    "symptoms": ["severe chest pain", "difficulty breathing"],
    "duration": "30 minutes",
    "severity": "severe"
  }
  ```

---

### 5. Provider Directory & Search
- **Method:** `GET`
- **Path:** `/doctors`
- **Query Parameters:**
  - `speciality`: string (e.g. `Cardiology`, `General Medicine`)
  - `district`: string (e.g. `Khordha`, `Cuttack`)
  - `max_fee`: float (e.g. `0` for free government care)

---

### 6. Provider Availability & Freshness Status
- **Method:** `GET`
- **Path:** `/availability/{provider_id}`
- **Response:**
  ```json
  {
    "doctor_id": "DOC_OD_001",
    "name": "Dr. Subhashree Mishra (Demo MD)",
    "speciality": "General Medicine",
    "facility": "Capital Hospital (PGIER)",
    "availability_status": "provider_confirmation_required",
    "provider_confirmation_required": true,
    "data_source": "DEMO_DATA",
    "last_updated": "2026-08-19T00:00:00Z",
    "is_demo": true,
    "notice": "Current appointment availability requires direct provider confirmation. Demo dataset record."
  }
  ```

---

### 7. Health Department Surveillance Dashboard
- **Method:** `GET`
- **Path:** `/admin/dashboard`
- **Response:** Aggregated KPIs, risk category breakdown, top reported symptoms, specialty demand, and district-wise surveillance table.
