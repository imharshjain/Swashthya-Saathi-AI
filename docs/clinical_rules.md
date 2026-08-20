# Swasthya Saathi AI - Clinical Triage Protocol & Safety Rules

---

## 1. Triage Categories

| Risk Level | Target Response Time | Clinical Indicator Examples | Primary Citizen Guidance |
|---|---|---|---|
| **EMERGENCY** | Immediate (0 - 15 mins) | Severe chest pain, acute dyspnea / breathlessness, loss of consciousness, uncontrolled bleeding, sudden paralysis / stroke signs. | Seek immediate emergency department care. Dial **108** for ambulance dispatch. |
| **URGENT** | Prompt (< 24 hours) | High fever (> 101°F or > 3 days duration), persistent vomiting, severe abdominal pain, dehydration, multiple concurrent red flags. | Consult a doctor at nearest CHC, SDH, or District Headquarters Hospital. Dial **104** for advice. |
| **ROUTINE** | Standard (24 - 72 hours) | Mild cold, cough, sore throat, mild body ache, localized rash without systemic signs. | Visit local Primary Health Centre (PHC) / Health & Wellness Centre. |

---

## 2. Dynamic Modifier Rules

1. **Duration Upgrade**: If a citizen reports fever lasting $\ge 3\text{ days}$, triage is upgraded from ROUTINE to URGENT (`prolonged fever (> 3 days duration)`).
2. **Severity Upgrade**: If measured temperature is $\ge 101^\circ\text{F}$ or severity is tagged as `severe/extreme`, risk is escalated to URGENT.
3. **Multi-Symptom Accumulation**: If $\ge 3$ distinct concurrent symptoms are present without single red flags, the query is assigned URGENT review.

---

## 3. Disclaimers

> [!CAUTION]
> Swasthya Saathi AI is a technical prototype and does not constitute a certified medical device (SaMD) or clinical diagnostic system. It serves solely to provide information triage and guide citizens to appropriate healthcare resources.
