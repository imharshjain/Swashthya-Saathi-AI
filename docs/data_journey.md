# Swasthya Saathi AI - Data Journey & Privacy Lifecycle

---

## 1. Citizen Journey
1. **Input**: Citizen enters health concern in natural language (e.g., *"Mujhe 3 din se bukhar hai aur weakness bhi hai"*).
2. **Extraction**: System normalizes input into clinical symptom tokens (`fever`, `weakness`), duration (`3 days`), and context.
3. **Triage**: Clinical safety rule evaluates indicators $\rightarrow$ Risk level: `URGENT`.
4. **Provider Routing**: System matches specialty `General Medicine` and computes distance to verified Odisha facilities.
5. **Transparency**: Citizen views provider cards with mandatory freshness disclaimer (*"Current appointment availability requires provider confirmation"*).
6. **No PII Collected**: Citizen personal data (name, phone number, device info) is never requested or retained.

---

## 2. Department Analytics Journey
1. **Anonymized Ingestion**: Consultation event is logged with zero PII: `[timestamp, district, symptoms, risk_level, specialty, facility]`.
2. **Aggregation**: Data engine computes state-wide and district-level surveillance indicators.
3. **Surveillance Display**: Health Department officers view real-time disease trends and facility routing loads across all 30 districts of Odisha.
