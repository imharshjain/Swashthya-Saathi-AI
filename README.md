# ସ୍ୱାସ୍ଥ୍ୟ ସାଥୀ AI | SWASTHYA SAATHI AI
### Odisha State Health & Family Welfare AI Healthcare Assistant

---

## 1. Project Overview & Vision

**Swasthya Saathi AI** is a dual-sided, government-oriented AI healthcare prototype developed for the state of **Odisha, India**. 

The system assists citizens by extracting health concerns from natural-language messages (English & Hinglish), evaluating clinical urgency through deterministic safety rules, and routing patients to appropriate healthcare providers across Odisha (e.g. AIIMS Bhubaneswar, SCB Medical College Cuttack, Capital Hospital, District Headquarters Hospitals, CHCs).

Simultaneously, the platform provides the **Odisha Health & Family Welfare Department** with aggregated, privacy-preserving real-time public health surveillance insights without collecting or storing personally identifiable information.

---

## 2. Key Capabilities & Safety Architecture

1. **AI & Multilingual NLP Symptom Extraction**:
   - Converts conversational complaints (e.g., *"Mujhe 3 din se bukhar hai aur weakness bhi hai."*) into structured clinical representations (`symptoms`, `duration`, `severity`).
   - Supports online OpenAI LLM extraction and resilient offline deterministic NLP fallback.
2. **Deterministic Clinical Triage**:
   - Classifies queries into **EMERGENCY**, **URGENT**, or **ROUTINE**.
   - Immediate high-risk triggers (severe chest pain, breathlessness, loss of consciousness) prompt direct emergency routing (Odisha **108** Ambulance and **104** Helpline).
   - **Zero AI Diagnosis or Prescription**: Never diagnoses conditions or prescribes medications.
3. **Location-Aware Provider Recommendation**:
   - Ranks verified Odisha healthcare facilities using Haversine distance from the citizen's district.
   - Enforces data transparency: All demo records are tagged with `data_source="DEMO_DATA"` and `is_demo=true`.
   - Explicit freshness notice: *"Current appointment availability requires provider confirmation."*
4. **Health Department Surveillance Dashboard**:
   - Real-time aggregated KPIs (total consultations, emergency cases, urgent cases, routine cases).
   - Visualizations for risk triage distribution, top reported symptoms in Odisha, specialty demand, and district-wise surveillance.
5. **Zero-PII Privacy-by-Design**:
   - No names, phone numbers, email addresses, or IP addresses are stored.

---

## 3. Technology Stack

- **Backend**: Python 3.10+, FastAPI, Pydantic v2, Uvicorn
- **AI/NLP**: OpenAI API (optional) + Deterministic Multilingual Lexicon & Regex Engine
- **Frontend**: Streamlit, Pandas, Custom Government CSS
- **Database**: SQLite with anonymized surveillance schemas
- **Testing**: Python `unittest` suite (34 automated tests)

---

## 4. Project Structure

```
swasthya-saathi-ai/
├── backend/
│   ├── main.py                     # FastAPI REST API endpoints & CORS
│   ├── ai_service.py               # AI & Multilingual NLP symptom extractor
│   ├── triage_engine.py            # Deterministic clinical safety rules
│   ├── doctor_service.py           # Provider matching & distance ranking
│   ├── database.py                 # SQLite persistence (Zero PII)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── health_schemas.py       # Pydantic request/response models
│   └── services/
│       ├── __init__.py
│       └── assistant_pipeline.py   # Unified Query -> Triage -> Doctor pipeline
├── data/
│   ├── doctors.json                # Synthetic demo Odisha provider dataset
│   ├── facilities.json             # Odisha tertiary/district hospital directory
│   ├── specialities.json           # Clinical specialty mapping definitions
│   └── test_cases.json             # Multi-scenario test fixtures
├── frontend/
│   ├── app.py                      # Dual-sided Streamlit UI (Citizen + Admin)
│   └── styles.css                  # Odisha Government Theme styling
├── docs/
│   ├── architecture.md             # System architecture & component design
│   ├── api.md                      # REST API documentation & sample payloads
│   ├── data_model.md               # Data entities & provenance models
│   ├── ai_pipeline.md              # NLP prompt engineering & safety rules
│   ├── clinical_rules.md           # Triage matrices & escalation thresholds
│   ├── deployment.md               # Local and production deployment guide
│   ├── data_journey.md             # Citizen & Department data journeys
│   └── mvp_scope.md                # Scope and production roadmap
├── tests/
│   ├── __init__.py
│   ├── test_ai_service.py          # Multilingual NLP & schema tests
│   ├── test_triage.py              # Clinical rule triage tests
│   ├── test_doctor_service.py      # Provider ranking & freshness tests
│   ├── test_api.py                 # FastAPI integration tests
│   └── test_dashboard.py           # Aggregation & zero-PII tests
├── requirements.txt
└── README.md
```

---

## 5. Quickstart & Local Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Automated Test Suite
```bash
python -m unittest discover -s "tests" -p "test_*.py" -v
```

### 3. Start FastAPI Backend (Port 8000)
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Documentation: `http://127.0.0.1:8000/docs`
- Health Probe: `http://127.0.0.1:8000/health`

### 4. Start Streamlit Frontend (Port 8501)
```bash
streamlit run frontend/app.py --server.port 8501
```
- Open browser at `http://localhost:8501`

---

## 6. Demo Scenarios to Test

1. **Hinglish Urgent Case**:
   - Input: `"Mujhe 3 din se bukhar hai aur weakness bhi hai."`
   - Result: Structured extraction (`fever`, `weakness`, `3 days`), Triage: `URGENT` (prolonged fever > 3 days), Specialty: `General Medicine`, Provider: Capital Hospital / AIIMS Bhubaneswar.
2. **Emergency Danger Signs**:
   - Input: `"I have severe chest pain and difficulty breathing."`
   - Result: Triage: `EMERGENCY`, Specialty: `Emergency Medicine`, Direct click-to-dial `108 Ambulance` and `104 Helpline`.
3. **Routine Care**:
   - Input: `"I have mild cold and cough since yesterday."`
   - Result: Triage: `ROUTINE`, Guidance: Primary Health Centre / Wellness Centre.
4. **Department Surveillance**:
   - Switch to **Department Dashboard** in the sidebar to review live aggregated charts and disease trends across Odisha districts.
