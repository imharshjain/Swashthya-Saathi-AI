# Swasthya Saathi AI - AI & NLP Extraction Pipeline

---

## 1. Pipeline Design & Boundaries

```
[Citizen Health Complaint]
          │
          ▼
┌──────────────────────────────────────┐
│  AI / NLP Information Extraction     │
│  - Multilingual Token Matching       │
│  - Regex Duration & Severity Parser  │
│  - OpenAI LLM Mode (When Configured) │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  Structured Extraction Schema        │
│  - symptoms: List[str]               │
│  - duration: Optional[str]           │
│  - severity: Optional[str]           │
│  - context: List[str]                │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  Deterministic Clinical Triage       │
│  (Zero Generative Hallucinations)    │
└──────────────────────────────────────┘
```

---

## 2. Multilingual Support Matrix

The pipeline handles:
- **English**: `"I have severe chest pain and difficulty breathing."`
- **Hindi / Hinglish**: `"Mujhe 3 din se bukhar hai aur weakness bhi hai."`
- **Odia-Transliterated Phrases**: `"Munda binda"`, `"Peta dard"`, `"Nisswashe kasta"`, `"Ghana ghana banti"`.

---

## 3. Strict Safety Guardrails

- The AI is **strictly non-diagnostic**.
- It does **not** prescribe drugs, suggest dosages, or provide self-medication recommendations.
- Emergency triggers (chest pain, breathlessness, loss of consciousness) bypass all routine conversational flows to deliver immediate emergency assistance warnings and direct hotline links (108 / 104).
