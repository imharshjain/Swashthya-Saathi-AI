# Swasthya Saathi AI - System Architecture
**Target State:** Odisha, India  
**Ecosystem:** Odisha State Health & Family Welfare Department

---

## 1. Architectural Overview

Swasthya Saathi AI is architected as a **dual-sided, modular, privacy-preserving healthcare platform** that bridges citizen self-triage with health system navigation and administrative disease surveillance.

```
+-----------------------------------------------------------------------------------+
|                                  CITIZEN PORTAL                                   |
|                     (Streamlit UI / Web / Mobile Interface)                       |
+-----------------------------------------------------------------------------------+
                                         |
                                         | HTTP / REST (POST /assistant)
                                         v
+-----------------------------------------------------------------------------------+
|                                FASTAPI BACKEND                                    |
|  - CORS & Request Validation (Pydantic Schemas)                                   |
|  - Unified Pipeline Orchestrator (process_health_query)                           |
+-----------------------------------------------------------------------------------+
       |                               |                              |
       v                               v                              v
+--------------------+      +--------------------+         +--------------------+
|   AI/NLP SERVICE   |      |   TRIAGE ENGINE    |         |   DOCTOR SERVICE   |
| - OpenAI LLM Model |      | - Deterministic    |         | - Specialty Map    |
| - Multilingual     | ---> |   Safety Rules     | ------> | - Haversine Dist   |
|   Rule Engine      |      | - Risk Levels:     |         | - Ranking & Fee    |
|   (Eng/Hinglish)   |      |   EMERGENCY/URGENT |         | - Freshness Stamping
+--------------------+      +--------------------+         +--------------------+
                                       |
                                       v
                     +------------------------------------+
                     |    SQLITE SURVEILLANCE DATABASE    |
                     |  - Anonymized Consultation Logs    |
                     |  - Zero PII (Privacy by Design)    |
                     +------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
|                         HEALTH DEPARTMENT ADMIN DASHBOARD                         |
|             (Real-Time Disease Surveillance & Healthcare Demand)                  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Core Subsystems

### A. AI & Multilingual NLP Extraction Layer (`backend/ai_service.py`)
- **Dual-Mode Resilient Architecture**:
  - **Online Mode**: Invokes OpenAI Chat Completions API with structured JSON output when `OPENAI_API_KEY` is present.
  - **Offline/Fallback Mode**: Deterministic multilingual rule engine parsing English, Hindi/Hinglish, and Odia transliterations.
- **Safety Guarantee**: Information extraction only. Strictly forbids diagnosis, prescription, or clinical speculation.

### B. Deterministic Clinical Triage Engine (`backend/triage_engine.py`)
- Clinical safety layer decoupled from generative AI hallucinations.
- Predefined indicator matrices for:
  1. **EMERGENCY**: Immediate danger signs (severe chest pain, difficulty breathing, unconsciousness). Activates Odisha 108 Ambulance and 104 helpline.
  2. **URGENT**: Potential high-risk progression (persistent vomiting, prolonged fever > 3 days, severe abdominal pain).
  3. **ROUTINE**: Self-limiting conditions suited for Primary Health Centres (PHCs).

### C. Provider Recommendation & Distance Engine (`backend/doctor_service.py`)
- Location-aware search across 30 Odisha districts.
- Calculates Haversine distance from citizen coordinates.
- Enforces data provenance (`is_demo=true`, `data_source="DEMO_DATA"`).
- Explicit freshness status: *"Current appointment availability requires provider confirmation."*

### D. Privacy-Preserving Surveillance Database (`backend/database.py`)
- SQLite storage logging anonymized consultation events.
- Strictly captures: `[timestamp, district, language_detected, symptoms_json, risk_level, recommended_specialty, matched_facility]`.
- Absolutely **no PII** (no names, phone numbers, IP addresses, or home addresses).
