"""
Swasthya Saathi AI - AI & NLP Symptom Extraction Service
Converts natural-language health queries into structured symptom representations.
Supports both OpenAI LLM extraction and resilient deterministic multilingual NLP fallback
(English, Hindi/Hinglish, and Odia transliterated phrases).
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Multilingual Symptom Lexicon (English, Hinglish, Odia transliterations)
SYMPTOM_LEXICON: Dict[str, List[str]] = {
    "difficulty breathing": [
        "difficulty breathing", "shortness of breath", "saans lene mein takleef",
        "sans lene me taklif", "damm ghutna", "nisswashe kasta", "breathlessness",
        "dyspnea", "gasping", "unable to breathe", "breath problem", "choking"
    ],
    "severe chest pain": [
        "severe chest pain", "chest pain", "chaati mein dard", "chhati dard",
        "chaati me dard", "chest tightness", "chest pressure", "chhati re jantrana",
        "heart pain", "crushing chest pain"
    ],
    "loss of consciousness": [
        "loss of consciousness", "fainting", "fainted", "behosh", "behoshi",
        "unconscious", "blacked out", "passed out", "gyana harana"
    ],
    "severe bleeding": [
        "severe bleeding", "khoon behna", "khoon nikalna", "rakta srava",
        "heavy bleeding", "profuse bleeding", "bleeding profusely"
    ],
    "high fever": [
        "high fever", "tez bukhar", "bahut tez bukhar", "adhika jwara",
        "high temp", "severe fever", "high temperature", "103 f", "104 f"
    ],
    "fever": [
        "fever", "bukhar", "bukhaar", "jwara", "jwar", "temperature",
        "tapa", "pyrexia", "feverish", "garam lagna"
    ],
    "weakness": [
        "weakness", "kamzori", "kamjori", "durbalata", "thakan",
        "tiredness", "fatigue", "lethargy", "exhaustion", "durbala"
    ],
    "persistent vomiting": [
        "persistent vomiting", "continuous vomiting", "bar bar ulti",
        "lagatar ulti", "ghana ghana banti"
    ],
    "vomiting": [
        "vomiting", "ulti", "banti", "nausea", "jee ghabrana",
        "vomit", "throwing up", "puking"
    ],
    "severe abdominal pain": [
        "severe abdominal pain", "severe stomach pain", "bahut tez pet dard",
        "pet me asahya dard", "severe cramps"
    ],
    "abdominal pain": [
        "abdominal pain", "stomach ache", "pet dard", "peta binda",
        "stomach pain", "peta dard", "tummy ache", "cramps", "belly pain"
    ],
    "dehydration": [
        "dehydration", "paani ki kami", "jala heenata", "dry mouth",
        "extreme thirst", "sukha padna"
    ],
    "cough": [
        "cough", "khasi", "khaasi", "kasha", "coughing", "dry cough", "balgam"
    ],
    "cold": [
        "cold", "sardi", "zukaam", "zukam", "thanda", "sneezing",
        "chheenk", "runny nose", "running nose", "blocked nose", "sinus"
    ],
    "headache": [
        "headache", "sir dard", "sar dard", "munda binda", "head pain",
        "matha dard", "migraine"
    ],
    "loose motions": [
        "loose motions", "diarrhea", "diarrhoea", "dast", "jhada",
        "pet kharab", "watery stools"
    ],
    "body ache": [
        "body ache", "body pain", "badan dard", "deha binda",
        "muscle pain", "joint pain", "angamardam", "gale mein dard", "sore throat"
    ],
    "dizziness": [
        "dizziness", "chakkar", "chakkar aana", "munda ghureiba", "lightheadedness"
    ],
    "skin rash": [
        "skin rash", "rash", "itching", "khujli", "khandu", "red spots",
        "allergy", "twacha infection", "rashes"
    ]
}


def rule_based_symptom_extraction(user_message: str) -> Dict[str, Any]:
    """
    High-accuracy deterministic multilingual symptom extractor.
    Extracts symptoms, duration, severity, and context from English, Hinglish, and transliterated Odia.
    """
    msg_lower = user_message.lower()
    extracted_symptoms: List[str] = []

    # 1. Match Symptoms via Lexicon
    # First test longer multi-word keys (e.g. severe chest pain before chest pain)
    sorted_lexicon = sorted(SYMPTOM_LEXICON.items(), key=lambda x: max(len(k) for k in x[1]), reverse=True)
    
    for canon_name, phrases in sorted_lexicon:
        matched = False
        for phrase in phrases:
            # Word-boundary aware or substring search for transliterations
            pattern = r'(?:\b|_)' + re.escape(phrase) + r'(?:\b|_)'
            if re.search(pattern, msg_lower) or phrase in msg_lower:
                matched = True
                break
        if matched:
            # If "high fever" is detected, don't duplicate with "fever" unless needed
            if canon_name == "fever" and "high fever" in extracted_symptoms:
                continue
            if canon_name == "vomiting" and "persistent vomiting" in extracted_symptoms:
                continue
            if canon_name == "abdominal pain" and "severe abdominal pain" in extracted_symptoms:
                continue
            if canon_name not in extracted_symptoms:
                extracted_symptoms.append(canon_name)

    # 2. Extract Duration
    duration = None
    duration_patterns = [
        r'(\d+\s*(?:to|-)\s*\d+\s*(?:days?|din|hours?|ghante|weeks?|hafte|months?|mahine))',
        r'(\d+\s*(?:days?|din|hours?|ghante|weeks?|hafte|months?|mahine))',
        r'((?:one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:days?|din|weeks?|months?))',
        r'((?:teen|do|ek|char|paanch|chhah|saat)\s*(?:din|hafte|mahine))',
        r'(since\s+(?:yesterday|morning|last\s+night|2\s+days|a\s+week))',
        r'(kal\s+se|aaj\s+se|subah\s+se|raat\s+se|parson\s+se)',
    ]
    for pat in duration_patterns:
        match = re.search(pat, msg_lower)
        if match:
            duration = match.group(1).strip()
            # Normalize common terms
            duration = duration.replace("din se", "days").replace("din", "days")
            duration = duration.replace("teen", "3").replace("do", "2").replace("ek", "1")
            break

    # 3. Extract Severity
    severity = None
    severity_patterns = [
        (r'(\b\d{2,3}(?:\.\d)?\s*(?:°\s*[fc]|f|c|degree|deg)\b)', "measured"),
        (r'\b(10[0-5](?:\.\d)?)\b', "measured"),
        (r'\b(severe|bahut tez|bohot zyada|bohot|bahut|asahya|critical|extreme|high)\b', "severe / high"),
        (r'\b(moderate|theek thaak|madhyam)\b', "moderate"),
        (r'\b(mild|halka|halka sa|little|slight|kam)\b', "mild"),
    ]
    for pat, label in severity_patterns:
        match = re.search(pat, msg_lower)
        if match:
            if label == "measured":
                val = match.group(1).strip()
                if "f" not in val.lower() and "c" not in val.lower() and "deg" not in val.lower():
                    severity = f"{val}°F"
                else:
                    severity = val
            else:
                severity = label
            break

    # 4. Additional Context
    additional_info = []
    if any(term in msg_lower for term in ["child", "bacha", "baby", "infant"]):
        additional_info.append("Patient demographic: Pediatric / Child")
    if any(term in msg_lower for term in ["elderly", "old age", "bujurg", "senior"]):
        additional_info.append("Patient demographic: Elderly")
    if any(term in msg_lower for term in ["pregnant", "garbhawati"]):
        additional_info.append("Patient condition: Pregnancy")
    if any(term in msg_lower for term in ["diabetes", "sugar", "bp", "hypertension"]):
        additional_info.append("Comorbidity noted")

    # Detect language / style
    is_hinglish_or_odia = any(
        word in msg_lower for word in [
            "mujhe", "hai", "aur", "bhi", "din", "se", "dard", "bukhar",
            "lagatar", "bohot", "bahut", "ulti", "takleef", "kamzori", "binda", "jwara"
        ]
    )
    detected_lang = "Hinglish / Regional" if is_hinglish_or_odia else "English"

    return {
        "symptoms": extracted_symptoms,
        "duration": duration,
        "severity": severity,
        "additional_information": additional_info,
        "language_detected": detected_lang,
        "extraction_method": "rule_based_nlp"
    }


def extract_symptoms(user_message: str) -> Dict[str, Any]:
    """
    Convert a citizen's natural-language health message into structured symptom information.
    Uses OpenAI LLM if configured and available; otherwise uses deterministic rule-based NLP.
    
    This function extracts information only. It does NOT diagnose a medical condition.
    """
    if not user_message or not user_message.strip():
        return {
            "symptoms": [],
            "duration": None,
            "severity": None,
            "additional_information": ["No message provided"],
            "language_detected": "Unknown",
            "extraction_method": "rule_based_nlp"
        }

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key.strip() and not api_key.startswith("your_"):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key.strip())
            
            prompt = f"""
You are a healthcare information extraction assistant for a government healthcare application (Swasthya Saathi AI, Odisha).

Extract only the health-related information explicitly present in the citizen's message.
Support English, Hindi/Hinglish (e.g., 'bukhar' -> fever, 'kamzori' -> weakness), and Odia transliterations.

CRITICAL SAFETY RULES:
- Do NOT diagnose the person.
- Do NOT invent symptoms not mentioned.
- Do NOT prescribe medicines.
- Do NOT make medical claims.

Return valid JSON with exactly these fields:
{{
    "symptoms": ["list of normalized symptom strings"],
    "duration": "duration string or null",
    "severity": "severity string or null",
    "additional_information": ["relevant context items"]
}}

Citizen message:
"{user_message}"
"""
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a structured healthcare information extraction assistant. Output only JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            raw_text = response.choices[0].message.content
            parsed = json.loads(raw_text)
            parsed["language_detected"] = "Multilingual (AI)"
            parsed["extraction_method"] = "llm"
            return parsed

        except Exception as e:
            logger.warning(f"OpenAI extraction failed or unavailable ({e}); falling back to deterministic NLP engine.")

    # Seamless deterministic fallback
    return rule_based_symptom_extraction(user_message)