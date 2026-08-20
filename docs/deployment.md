# Swasthya Saathi AI - Deployment & Operations Guide

---

## 1. Local Development Setup

### Prerequisites
- Python 3.10+
- Virtual Environment

### Installation
```bash
cd "AI ASSISTANT UNEECOPS/swasthya-saathi-ai"
pip install -r requirements.txt
```

### Environment Variables
Configure `.env` (optional for local testing; default offline NLP works without API keys):
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
API_URL=http://127.0.0.1:8000
```

---

## 2. Running the System

### Start FastAPI Backend
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Start Streamlit Frontend
```bash
streamlit run frontend/app.py --server.port 8501
```

---

## 3. Production Deployment Architecture

```
Internet / Citizen
       │
       ▼
[ Cloudflare / Reverse Proxy (SSL Termination) ]
       │
       ├─────────────────────────────────────────┐
       ▼                                         ▼
[ Streamlit UI Service ]                 [ FastAPI API Gateway ]
(Port 8501, Stateless)                  (Gunicorn + Uvicorn Workers, Port 8000)
                                                 │
                                                 ▼
                                        [ SQLite / PostgreSQL DB ]
```
