# Swasthya Saathi AI - Data Model & Provenance Architecture

---

## 1. Core Data Entities

### A. Provider Record (`DoctorRecommendation`)
| Field | Type | Description | Mandatory Demo Value |
|---|---|---|---|
| `doctor_id` | String | Unique provider identifier | `DOC_OD_XXX` |
| `name` | String | Provider name with credential annotation | Synthetic demo doctor |
| `speciality` | String | Clinical specialty | e.g. `General Medicine` |
| `facility` | String | Affiliated health facility | e.g. `AIIMS Bhubaneswar` |
| `facility_type`| String | Category of institution | `District Hospital / CHC / Tertiary` |
| `district` | String | Odisha District | `Khordha / Cuttack / Puri...` |
| `latitude` | Float | Facility geo-latitude | Decimal degrees |
| `longitude` | Float | Facility geo-longitude | Decimal degrees |
| `distance_km` | Float | Great-circle distance from user | Dynamically calculated |
| `consultation_fee` | Float | Out-of-pocket fee in INR | `0.0` (Govt) or nominal fee |
| `verified` | Boolean | Verification flag | `True` |
| `is_demo` | Boolean | Synthetic record flag | `True` (Mandatory) |
| `data_source` | String | Data origin provenance | `"DEMO_DATA"` |
| `verification_status` | String | Verification classification | `"demo_verified"` |
| `availability_status` | String | Booking availability indicator | `"provider_confirmation_required"` |
| `last_updated` | String | ISO8601 Timestamp | `"2026-08-19T00:00:00Z"` |

---

## 2. Privacy-Preserving Surveillance Data Model

```sql
CREATE TABLE consultation_logs (
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
);
```

### Zero PII Policy:
No citizen names, telephone numbers, Aadhaar numbers, IP addresses, or location coordinates are stored in the database.
