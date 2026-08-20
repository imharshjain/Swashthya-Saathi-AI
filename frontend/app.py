"""
Swasthya Saathi AI - Streamlit Frontend Application
Dual-Sided Prototype: Citizen AI Health Assistant + Health Department Surveillance Dashboard
Target State: Odisha, India
"""

import os
import sys
import json
import requests
import pandas as pd
import streamlit as st

# Ensure backend package can be imported directly if needed
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.assistant_pipeline import process_health_query
from backend.database import get_admin_dashboard_metrics
from backend.doctor_service import load_doctors_dataset

# Configuration
API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Page Configuration
st.set_page_config(
    page_title="Swasthya Saathi AI - Odisha Health Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Odisha Districts List
ODISHA_DISTRICTS = [
    "Khordha (Bhubaneswar)", "Cuttack", "Puri", "Ganjam (Berhampur)",
    "Sambalpur", "Sundargarh (Rourkela)", "Balasore", "Koraput",
    "Mayurbhanj (Baripada)", "Angul", "Balangir", "Bargarh",
    "Bhadrak", "Deogarh", "Dhenkanal", "Gajapati", "Jharsuguda",
    "Jajpur", "Jagatsinghpur", "Kalahandi", "Kandhamal", "Kendrapara",
    "Kendujhar (Keonjhar)", "Malkangiri", "Nabarangpur", "Nayagarh",
    "Nuapada", "Rayagada", "Subarnapur (Sonepur)"
]


def execute_assistant_query(message: str, district: str) -> dict:
    """Execute assistant query via FastAPI backend with resilient in-process fallback."""
    clean_district = district.split("(")[0].strip()
    payload = {
        "message": message,
        "district": clean_district
    }
    
    # Try calling FastAPI backend HTTP endpoint
    try:
        resp = requests.post(f"{API_BASE_URL}/assistant", json=payload, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass

    # Direct in-process execution fallback
    return process_health_query(message=message, district=clean_district)


# -------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 0.5rem 0;'>
        <div style='font-size: 2.2rem;'>🏛️</div>
        <div style='font-weight: 800; font-size: 1.1rem; color: #0c2340;'>GOVERNMENT OF ODISHA</div>
        <div style='font-size: 0.8rem; color: #4a5568;'>Health & Family Welfare Department</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    portal_selection = st.radio(
        "Select Portal / ସେବା ବାଛନ୍ତୁ:",
        ["🩺 Citizen Health Assistant", "📊 Department Dashboard", "🏥 Odisha Healthcare Directory"],
        index=0
    )
    
    st.divider()
    
    st.markdown("### 🚨 Emergency Hotlines (Odisha)")
    st.markdown("""
    - **108**: Emergency Medical Ambulance (24x7)
    - **104**: State Health Advice Helpline
    - **112**: Unified Emergency Response
    - **AIIMS Casualty**: 0674-2476789
    - **SCB Cuttack Casualty**: 0671-2414080
    """)
    
    st.divider()
    st.markdown("""
    <div style='font-size: 0.75rem; color: #718096; text-align: center;'>
        <b>Swasthya Saathi AI Prototype v1.0</b><br>
        Built for demonstration & information triage.<br>
        <i>All provider slots are demo data.</i>
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------
# 1. CITIZEN HEALTH ASSISTANT PORTAL
# -------------------------------------------------------------
if portal_selection == "🩺 Citizen Health Assistant":
    # Header Banner
    st.markdown("""
    <div class="gov-header">
        <span class="gov-badge">Official Government Prototype • Odisha</span>
        <h1>ସ୍ୱାସ୍ଥ୍ୟ ସାଥୀ AI | SWASTHYA SAATHI AI</h1>
        <div class="subtitle">AI-Powered Health Assistance, Triage & Healthcare Routing for Citizens of Odisha</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Clinical Safety & Demo Data Disclaimer Bar
    st.markdown("""
    <div class="disclaimer-bar">
        ℹ️ <b>Citizen Notice:</b> Swasthya Saathi AI helps understand symptom urgency and routes you to healthcare facilities. 
        It does <b>NOT</b> provide medical diagnosis or prescriptions. For life-threatening emergencies, call <b>108</b> immediately. 
        Provider information shown is demo data (<code>is_demo=true</code>).
    </div>
    """, unsafe_allow_html=True)

    # Input Section
    col_dist, col_info = st.columns([1, 2])
    with col_dist:
        selected_district = st.selectbox(
            "📍 Select Your District in Odisha / ଆପଣଙ୍କ ଜିଲ୍ଲା:",
            ODISHA_DISTRICTS,
            index=0
        )
    with col_info:
        st.markdown("""
        <div style='padding-top: 1.8rem; font-size: 0.85rem; color: #4a5568;'>
            Location is used to calculate approximate travel distance to the nearest verified health facilities.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### Describe Your Health Concern / ଆପଣଙ୍କ ସ୍ୱାସ୍ଥ୍ୟ ସମସ୍ୟା ଜଣାନ୍ତୁ:")
    
    # Quick Example Prompts
    st.caption("Quick Demo Examples (Click to populate):")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    
    preset_query = ""
    if q_col1.button("🤒 Hinglish Fever (3 Days)"):
        preset_query = "Mujhe 3 din se bukhar hai aur weakness bhi hai."
    if q_col2.button("🚨 Emergency Chest Pain"):
        preset_query = "I have severe chest pain and difficulty breathing."
    if q_col3.button("🤧 Routine Cold & Cough"):
        preset_query = "I have mild cold and cough since yesterday."
    if q_col4.button("🤢 Urgent Vomiting & Pain"):
        preset_query = "Continuous vomiting and severe abdominal pain from morning."

    user_query = st.text_area(
        label="Citizen Complaint Input",
        value=preset_query if preset_query else st.session_state.get("user_query_input", ""),
        placeholder="Type in English or Hinglish (e.g., 'Mujhe 3 din se bukhar hai aur thakan lag rahi hai' or 'I have severe chest pain')...",
        height=100,
        label_visibility="collapsed",
        key="user_query_input_box"
    )

    btn_col1, btn_col2 = st.columns([1, 4])
    with btn_col1:
        submit_btn = st.button("🩺 Get Assistance / ସହାୟତା ପାଆନ୍ତୁ", type="primary", use_container_width=True)

    # Process Query
    if submit_btn and user_query.strip():
        with st.spinner("Analyzing symptoms and evaluating clinical risk thresholds..."):
            result = execute_assistant_query(user_query, selected_district)

        st.session_state["last_result"] = result

    # Render Result if available
    if "last_result" in st.session_state:
        res = st.session_state["last_result"]
        triage = res.get("triage_assessment", {})
        extraction = res.get("structured_symptoms", {})
        risk_level = triage.get("risk_level", "ROUTINE")
        specialty = res.get("recommended_specialty", "General Medicine")
        providers = res.get("providers", [])

        st.markdown("---")
        st.subheader("📋 Understanding Your Health Concern")

        # 1. Understanding Breakdown Card
        col_res1, col_res2 = st.columns([1, 1])
        with col_res1:
            st.markdown("""
            <div class="result-card">
                <h3>🔍 Extracted Health Information</h3>
            """, unsafe_allow_html=True)
            
            symptoms = extraction.get("symptoms", [])
            if symptoms:
                st.markdown("**Identified Symptoms:**")
                sym_chips = " ".join([f"<span class='meta-chip'>🩺 {s.title()}</span>" for s in symptoms])
                st.markdown(sym_chips, unsafe_allow_html=True)
            else:
                st.markdown("*No specific clinical symptoms recognized.*")
                
            st.markdown(f"**Reported Duration:** `{extraction.get('duration') or 'Not specified'}`")
            st.markdown(f"**Reported Severity:** `{extraction.get('severity') or 'Not specified'}`")
            st.markdown(f"**Language Detected:** `{extraction.get('language_detected', 'English / Hinglish')}`")
            st.markdown(f"**Extraction Engine:** `{extraction.get('extraction_method', 'rule_based_nlp')}`")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_res2:
            st.markdown("""
            <div class="result-card">
                <h3>🎯 Recommended Clinical Specialty</h3>
            """, unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 1.3rem; font-weight: 700; color: #0c2340;'>{specialty}</div>", unsafe_allow_html=True)
            st.markdown(f"**Target District:** `{selected_district}`")
            st.markdown(f"**Matching Facility Type:** `Government Tertiary / District Hospital / CHC`")
            st.markdown("</div>", unsafe_allow_html=True)

        # 2. Clinical Triage Banner
        st.subheader("⚖️ Clinical Risk & Triage Assessment")
        if risk_level == "EMERGENCY":
            st.markdown(f"""
            <div class="triage-banner-emergency">
                <div style="font-size: 1.3rem; font-weight: 800; margin-bottom: 0.5rem;">
                    🚨 RISK LEVEL: EMERGENCY / ଜରୁରୀକାଳୀନ
                </div>
                <div style="font-size: 1rem; margin-bottom: 0.75rem;">
                    <b>{triage.get('recommended_action')}</b>
                </div>
                <div><b>Triggered High-Risk Indicators:</b> {', '.join(triage.get('matched_indicators', []))}</div>
                <div style="margin-top: 0.75rem; font-size: 0.85rem; color: #742a2a;">
                    <i>{triage.get('clinical_disclaimer')}</i>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Emergency Call Action Buttons
            em_col1, em_col2, em_col3 = st.columns(3)
            with em_col1:
                st.link_button("📞 Call 108 (Odisha Ambulance)", "tel:108", type="primary", use_container_width=True)
            with em_col2:
                st.link_button("📞 Call 104 (Health Helpline)", "tel:104", use_container_width=True)
            with em_col3:
                st.link_button("📞 Call 112 (National Emergency)", "tel:112", use_container_width=True)

        elif risk_level == "URGENT":
            st.markdown(f"""
            <div class="triage-banner-urgent">
                <div style="font-size: 1.2rem; font-weight: 800; margin-bottom: 0.5rem;">
                    ⚠️ RISK LEVEL: URGENT / ଶୀଘ୍ର ଡାକ୍ତରୀ ପରାମର୍ଶ ଆବଶ୍ୟକ
                </div>
                <div style="font-size: 1rem; margin-bottom: 0.75rem;">
                    <b>{triage.get('recommended_action')}</b>
                </div>
                <div><b>Identified Indicators:</b> {', '.join(triage.get('matched_indicators', []))}</div>
                <div style="margin-top: 0.75rem; font-size: 0.85rem; color: #7b341e;">
                    <i>{triage.get('clinical_disclaimer')}</i>
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown(f"""
            <div class="triage-banner-routine">
                <div style="font-size: 1.2rem; font-weight: 800; margin-bottom: 0.5rem;">
                    ✅ RISK LEVEL: ROUTINE / ସାଧାରଣ ପରାମର୍ଶ
                </div>
                <div style="font-size: 1rem; margin-bottom: 0.75rem;">
                    <b>{triage.get('recommended_action')}</b>
                </div>
                <div style="margin-top: 0.75rem; font-size: 0.85rem; color: #2b6cb0;">
                    <i>{triage.get('clinical_disclaimer')}</i>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 3. Recommended Providers & Facilities
        st.subheader("🏥 Recommended Healthcare Providers & Facilities (Odisha)")
        st.markdown("""
        <div style='font-size: 0.85rem; color: #718096; margin-bottom: 1rem;'>
            Providers ranked by clinical specialty, proximity (distance in km from selected district), and verification.
        </div>
        """, unsafe_allow_html=True)

        if not providers:
            st.info("No matching providers found in the demo catalog for this specialty. Please consult your nearest District Headquarters Hospital (DHH) or CHC.")
        else:
            for idx, doc in enumerate(providers[:6], 1):
                fee_display = "Free (Government Facility)" if doc.get("consultation_fee", 0) == 0 else f"₹{doc.get('consultation_fee')}"
                dist_km = doc.get("distance_km", "N/A")
                
                with st.container():
                    st.markdown(f"""
                    <div class="provider-card">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <div class="doc-name">{idx}. {doc.get('name')}</div>
                                <div class="doc-spec">Specialty: {doc.get('speciality')} • {doc.get('facility')}</div>
                            </div>
                            <div>
                                <span class="meta-chip" style="background-color: #c6f6d5; color: #22543d;">✅ Demo Verified</span>
                            </div>
                        </div>
                        <div style="margin: 0.5rem 0;">
                            <span class="meta-chip">📍 Distance: ~{dist_km} km</span>
                            <span class="meta-chip">🏛️ {doc.get('facility_type', 'Hospital')}</span>
                            <span class="meta-chip">💰 Consultation Fee: {fee_display}</span>
                            <span class="meta-chip">🏷️ Source: {doc.get('data_source')}</span>
                        </div>
                        <div class="stale-freshness-notice">
                            ⚠️ <b>Availability Status:</b> {doc.get('availability_status').replace('_', ' ').title()}<br>
                            <i>Current appointment availability requires provider confirmation. Demo dataset record.</i>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander(f"ℹ️ View Facility & Contact Details for {doc.get('name')}"):
                        st.write(f"**Facility Address:** {doc.get('facility')}, {doc.get('district')}, Odisha")
                        st.write(f"**Helpline / Reception Contact:** `{doc.get('contact_phone', '104')}`")
                        st.write(f"**Coordinates:** Latitude {doc.get('latitude')}, Longitude {doc.get('longitude')}")
                        st.write(f"**Record Last Updated:** `{doc.get('last_updated')}`")
                        st.caption("Note: Live appointment booking APIs will be integrated with the State Hospital Management Information System (HMIS) / e-Hospital portal.")


# -------------------------------------------------------------
# 2. HEALTH DEPARTMENT / ADMIN DASHBOARD PORTAL
# -------------------------------------------------------------
elif portal_selection == "📊 Department Dashboard":
    st.markdown("""
    <div class="gov-header">
        <span class="gov-badge">Health Surveillance & Administration</span>
        <h1>ODISHA HEALTH DEPARTMENT DASHBOARD</h1>
        <div class="subtitle">State Public Health Surveillance, Symptom Trends & Healthcare Demand Analytics</div>
    </div>
    """, unsafe_allow_html=True)

    # Simulated Demo Authentication Notice
    st.info("🔒 **Access Control Notice:** Department surveillance dashboard requires authorized administrative credentials. For this demo prototype, access is automatically granted for review.")

    # Fetch aggregated metrics
    metrics = get_admin_dashboard_metrics()

    # KPI Metrics Row
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-num" style="color: #2b6cb0;">{metrics.get('total_consultations', 0)}</div>
            <div class="kpi-label">Total Consultations Logged</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-num" style="color: #c53030;">{metrics.get('emergency_count', 0)}</div>
            <div class="kpi-label">🚨 Emergency Cases (108 Routed)</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-num" style="color: #d69e2e;">{metrics.get('urgent_count', 0)}</div>
            <div class="kpi-label">⚠️ Urgent Cases (24h Review)</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-num" style="color: #2f855a;">{metrics.get('routine_count', 0)}</div>
            <div class="kpi-label">✅ Routine Consultations</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Analytics Charts Row 1
    chart_col1, chart_col2 = st.columns([1, 1])

    with chart_col1:
        st.markdown("### 📊 Clinical Risk Triage Breakdown")
        risk_df = pd.DataFrame([
            {"Risk Level": "Emergency", "Cases": metrics.get("emergency_count", 0)},
            {"Risk Level": "Urgent", "Cases": metrics.get("urgent_count", 0)},
            {"Risk Level": "Routine", "Cases": metrics.get("routine_count", 0)},
        ])
        st.bar_chart(risk_df.set_index("Risk Level"), color="#0c2340")

    with chart_col2:
        st.markdown("### 📈 Top Reported Symptoms in Odisha")
        top_syms = metrics.get("top_symptoms", [])
        if top_syms:
            sym_df = pd.DataFrame(top_syms)
            st.bar_chart(sym_df.set_index("symptom"), color="#0d5c75")
        else:
            st.info("No symptom trends recorded yet.")

    # Analytics Charts Row 2
    chart_col3, chart_col4 = st.columns([1, 1])

    with chart_col3:
        st.markdown("### 🩺 Specialty Demand Distribution")
        spec_demand = metrics.get("specialty_demand", [])
        if spec_demand:
            spec_df = pd.DataFrame(spec_demand)
            st.dataframe(spec_df, use_container_width=True, hide_index=True)
        else:
            st.info("No specialty demand records available.")

    with chart_col4:
        st.markdown("### 🏥 Top Routed Healthcare Facilities")
        fac_demand = metrics.get("facility_demand", [])
        if fac_demand:
            fac_df = pd.DataFrame(fac_demand)
            st.dataframe(fac_df, use_container_width=True, hide_index=True)
        else:
            st.info("No facility routing records available.")

    # District-wise Surveillance Table
    st.markdown("### 🗺️ District-Wise Health Surveillance (Odisha)")
    dist_trends = metrics.get("district_trends", [])
    if dist_trends:
        dist_df = pd.DataFrame(dist_trends)
        st.dataframe(dist_df, use_container_width=True, hide_index=True)

    # Privacy Guarantee & Recent Surveillance Feed
    st.markdown("### 🛡️ Anonymized Real-Time Surveillance Audit Stream")
    st.markdown("""
    <div style='font-size: 0.8rem; color: #718096; margin-bottom: 0.5rem;'>
        <b>Privacy Guarantee:</b> Zero Personally Identifiable Information (PII) is captured. Only anonymized clinical codes and districts are shown.
    </div>
    """, unsafe_allow_html=True)

    recent_logs = metrics.get("recent_consultations", [])
    if recent_logs:
        log_df = pd.DataFrame(recent_logs)
        st.dataframe(log_df, use_container_width=True, hide_index=True)


# -------------------------------------------------------------
# 3. ODISHA DIRECTORY & EMERGENCY TAB
# -------------------------------------------------------------
elif portal_selection == "🏥 Odisha Healthcare Directory":
    st.markdown("""
    <div class="gov-header">
        <span class="gov-badge">Health Facilities Directory</span>
        <h1>ODISHA HEALTHCARE FACILITIES & HOTLINES</h1>
        <div class="subtitle">Tertiary Medical Colleges, District Headquarters Hospitals & 24x7 Emergency Services</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🚨 24x7 Odisha Emergency Helplines")
    h_col1, h_col2, h_col3 = st.columns(3)
    with h_col1:
        st.markdown("""
        <div class="kpi-card" style="border-top: 4px solid #e53e3e;">
            <div class="kpi-num" style="color: #e53e3e;">108</div>
            <div class="kpi-label">Odisha Emergency Ambulance Service</div>
        </div>
        """, unsafe_allow_html=True)
    with h_col2:
        st.markdown("""
        <div class="kpi-card" style="border-top: 4px solid #dd6b20;">
            <div class="kpi-num" style="color: #dd6b20;">104</div>
            <div class="kpi-label">State Health Advice Helpline</div>
        </div>
        """, unsafe_allow_html=True)
    with h_col3:
        st.markdown("""
        <div class="kpi-card" style="border-top: 4px solid #3182ce;">
            <div class="kpi-num" style="color: #3182ce;">112</div>
            <div class="kpi-label">Unified Emergency Response Support</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🏥 Apex Medical Colleges & District Hospitals in Odisha")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fac_path = os.path.join(base_dir, "data", "facilities.json")
    if os.path.exists(fac_path):
        with open(fac_path, "r", encoding="utf-8") as f:
            facilities = json.load(f)
        fac_df = pd.DataFrame(facilities)
        st.dataframe(
            fac_df[["facility_id", "name", "type", "district", "city", "emergency_capable", "helpline"]],
            use_container_width=True,
            hide_index=True
        )
