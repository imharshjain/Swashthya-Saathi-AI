# Swasthya Saathi AI - MVP Scope & Production Roadmap

---

## 1. Prototype Capabilities (Delivered)
- Natural language symptom extraction in English and Hindi/Hinglish.
- Deterministic clinical risk classification (EMERGENCY, URGENT, ROUTINE).
- Odisha-specific provider recommendations with Haversine distance calculations.
- Data freshness stamping (`availability_status="provider_confirmation_required"`).
- Dual-sided interface (Citizen Portal & Health Department Dashboard).
- Privacy-by-design SQLite surveillance persistence (Zero PII).
- Automated test suite with 100% pass rate.

---

## 2. Production Integration Roadmap
1. **Hospital Management Information System (HMIS / e-Hospital)**: Replace synthetic provider catalog with live National Health Mission (NHM) and State HMIS provider directories.
2. **Real-Time Appointment Slot Booking**: Integrate ABHA (Ayushman Bharat Health Account) and ORS (Online Registration System) slot booking gateways.
3. **Multi-Dialect Odia Voice Engine**: Add Odia speech-to-text (STT) and text-to-speech (TTS) for rural voice interfaces.
4. **State Disease Surveillance Network (IDSP)**: Stream aggregated anonymized epidemiological data directly into the Integrated Disease Surveillance Programme.