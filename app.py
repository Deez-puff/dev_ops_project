import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from database import init_db
from auth import register_patient, login_patient
from vitals import (record_vitals, get_vitals_df, check_vital,
                    needs_doctor, suggest_medicine_change, IDEAL_RANGES)
from certificate import generate_certificate

# Initialize database
init_db()

# Page config
st.set_page_config(
    page_title="Vitals AI",
    page_icon="🏥",
    layout="wide"
)

# Green and white styling
st.markdown("""
    <style>
    body { background-color: white; color: black; }
    .stApp { background-color: white; }
    .stButton>button {
        background-color: #006400;
        color: white;
        border-radius: 5px;
        padding: 8px 20px;
        font-size: 16px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #228B22;
        color: white;
    }
    .alert-box {
        padding: 12px;
        border: 1.5px solid #006400;
        border-radius: 6px;
        margin: 6px 0;
        font-size: 15px;
        background-color: #f0fff0;
        color: black;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 16px;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "patient" not in st.session_state:
    st.session_state.patient = None

# ─── LOGIN / REGISTER PAGE ───────────────────────────────
def show_auth_page():
    st.title("🏥 Vitals AI")
    st.subheader("Your Personal Health Monitoring System")
    st.write("Track your vitals, get health insights and download your health report.")
    st.write("---")

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        st.subheader("Login to Your Account")
        email = st.text_input("Email Address", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if not email or not password:
                st.warning("Please fill in all fields.")
            else:
                success, result = login_patient(email, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.patient = result
                    st.success("Login successful! Welcome back.")
                    st.rerun()
                else:
                    st.warning(result)

    with tab2:
        st.subheader("Create a New Account")
        col1, col2 = st.columns(2)
        with col1:
            name     = st.text_input("Full Name")
            age      = st.number_input("Age", min_value=1, max_value=120, value=25)
            sex      = st.selectbox("Sex", ["Male", "Female", "Other"])
            phone    = st.text_input("Phone Number")
        with col2:
            email_r    = st.text_input("Email Address", key="reg_email")
            password_r = st.text_input(
                "Password (min 8 chars, 1 uppercase, 1 number)",
                type="password", key="reg_pass"
            )
            address = st.text_area("Address")

        if st.button("Create Account"):
            if not all([name, age, sex, phone, email_r, password_r, address]):
                st.warning("Please fill in all fields.")
            else:
                success, result = register_patient(
                    name, age, sex, phone, email_r, password_r, address)
                if success:
                    st.success(f"✅ Account created successfully!")
                    st.info(f"Your unique Patient ID is: **{result}** — Please save this!")
                else:
                    st.warning(result)
# ─── MAIN DASHBOARD ──────────────────────────────────────
def show_dashboard():
    patient    = st.session_state.patient
    patient_id = patient[0]
    name       = patient[1]

    st.title(f"Welcome, {name} 👋")
    st.write(f"**Patient ID:** {patient_id}")
    st.write("---")

    page = st.sidebar.radio("Go to", [
        "📋 Enter Vitals",
        "📊 Dashboard",
        "🗃️ History",
        "📄 Health Certificate",
        "🗑️ Delete My Records",
        "🚪 Logout"
    ])

    if page == "📋 Enter Vitals":
        show_enter_vitals(patient_id)
    elif page == "📊 Dashboard":
        show_graphs(patient_id)
    elif page == "🗃️ History":
        show_history(patient_id)
    elif page == "📄 Health Certificate":
        show_certificate(patient)
    elif page == "🗑️ Delete My Records":
        show_delete(patient_id)
    elif page == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.patient   = None
        st.rerun()


# ─── ENTER VITALS PAGE ───────────────────────────────────
def show_enter_vitals(patient_id):
    st.subheader("📋 Enter Your Vitals Today")
    st.write("Fill in your current readings below and click Save & Analyse.")
    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        heart_rate   = st.number_input("Heart Rate (bpm)",
                                        min_value=30, max_value=250, value=75)
        spo2         = st.number_input("Oxygen Level - SpO2 (%)",
                                        min_value=50, max_value=100, value=98)
        temperature  = st.number_input("Body Temperature (°F)",
                                        min_value=90.0, max_value=110.0, value=98.6)
    with col2:
        bp_systolic  = st.number_input("Blood Pressure - Upper Number (mmHg)",
                                        min_value=50, max_value=250, value=120)
        bp_diastolic = st.number_input("Blood Pressure - Lower Number (mmHg)",
                                        min_value=30, max_value=150, value=80)
        medicines    = st.text_area(
            "Medicines you are currently taking (comma separated)",
            placeholder="e.g. Paracetamol, Amlodipine"
        )

    if st.button("Save & Analyse"):
        record_vitals(patient_id, heart_rate, spo2, temperature,
                      bp_systolic, bp_diastolic, medicines)
        st.write("---")
        st.subheader("📊 Your Results")

        alerts = [
            check_vital("heart_rate",   heart_rate),
            check_vital("spo2",         spo2),
            check_vital("temperature",  temperature),
            check_vital("bp_systolic",  bp_systolic),
            check_vital("bp_diastolic", bp_diastolic),
        ]

        for status, msg in alerts:
            st.markdown(
                f'<div class="alert-box">{msg}</div>',
                unsafe_allow_html=True
            )

        st.write("---")
        st.subheader("💊 Medicine Suggestions")
        suggestions = suggest_medicine_change(medicines, alerts)
        for s in suggestions:
            st.write(s)

        st.write("---")
        if needs_doctor(alerts):
            st.warning("🚨 You have multiple abnormal readings. "
                       "Please see a doctor as soon as possible.")
        else:
            st.success("✅ Overall health looks good. "
                       "Keep monitoring regularly!")


# ─── GRAPHS PAGE ─────────────────────────────────────────
def show_graphs(patient_id):
    st.subheader("📊 Your Health Trends")
    st.write("The grey shaded area shows the ideal/normal range for each vital.")
    st.write("---")
    df = get_vitals_df(patient_id)

    if df is None or df.empty:
        st.info("No vitals recorded yet. Please enter your vitals first.")
        return

    vitals_to_plot = {
        "heart_rate":   ("Heart Rate (bpm)", 60, 100),
        "spo2":         ("Oxygen Level % (SpO2)", 95, 100),
        "temperature":  ("Body Temperature (°F)", 97.0, 99.5),
        "bp_systolic":  ("Blood Pressure - Upper (mmHg)", 90, 120),
        "bp_diastolic": ("Blood Pressure - Lower (mmHg)", 60, 80),
    }

    for key, (label, low, high) in vitals_to_plot.items():
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df["date"], y=df[key],
            mode="lines+markers",
            name="Your Reading",
            line=dict(color="#006400", width=2),
            marker=dict(size=8, color="#006400")
        ))

        fig.add_hrect(
            y0=low, y1=high,
            fillcolor="lightgreen", opacity=0.2,
            line_width=0,
            annotation_text="Ideal Range",
            annotation_position="top left"
        )

        fig.update_layout(
            title=label,
            xaxis_title="Date",
            yaxis_title=label,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="black", size=13),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)


# ─── HISTORY PAGE ────────────────────────────────────────
def show_history(patient_id):
    st.subheader("🗃️ Your Past Records")
    st.write("---")
    df = get_vitals_df(patient_id)

    if df is None or df.empty:
        st.info("No records found yet. Please enter your vitals first.")
        return

    st.write("### All Records")
    display_df = df[[
        "date", "heart_rate", "spo2",
        "temperature", "bp_systolic", "bp_diastolic", "medicines"
    ]].copy()
    display_df.columns = [
        "Date", "Heart Rate", "SpO2 %",
        "Temperature", "BP Upper", "BP Lower", "Medicines"
    ]
    st.dataframe(display_df, use_container_width=True)

    st.write("---")
    st.write("### Before & After Medication Comparison")
    if len(df) >= 2:
        first  = df.iloc[0]
        latest = df.iloc[-1]
        compare_data = {
            "Vital": [
                "Heart Rate", "SpO2 %",
                "Temperature", "BP Upper", "BP Lower"
            ],
            "First Reading": [
                first["heart_rate"], first["spo2"],
                first["temperature"], first["bp_systolic"],
                first["bp_diastolic"]
            ],
            "Latest Reading": [
                latest["heart_rate"], latest["spo2"],
                latest["temperature"], latest["bp_systolic"],
                latest["bp_diastolic"]
            ],
        }
        compare_df = pd.DataFrame(compare_data)
        st.dataframe(compare_df, use_container_width=True)
    else:
        st.info("Enter at least 2 readings to see before & after comparison.")


# ─── CERTIFICATE PAGE ────────────────────────────────────
def show_certificate(patient):
    st.subheader("📄 Download Your Health Report")
    st.write("Your health report will be generated as a PDF file.")
    st.write("---")
    patient_id = patient[0]
    df = get_vitals_df(patient_id)

    if df is None or df.empty:
        st.info("Please enter your vitals first before generating a report.")
        return

    latest = df.iloc[-1]
    alerts = [
        check_vital("heart_rate",   latest["heart_rate"]),
        check_vital("spo2",         latest["spo2"]),
        check_vital("temperature",  latest["temperature"]),
        check_vital("bp_systolic",  latest["bp_systolic"]),
        check_vital("bp_diastolic", latest["bp_diastolic"]),
    ]
    suggestions = suggest_medicine_change(latest["medicines"], alerts)

    if st.button("Generate Health Report PDF"):
        filename = generate_certificate(patient, df, alerts, suggestions)
        with open(filename, "rb") as f:
            st.download_button(
                label="📥 Download Your Report",
                data=f,
                file_name=f"{patient_id}_health_report.pdf",
                mime="application/pdf"
            )
        st.success("✅ Your report is ready! Click the button above to download.")


# ─── DELETE RECORDS PAGE ─────────────────────────────────
def show_delete(patient_id):
    st.subheader("🗑️ Delete Your Records")
    st.write("You can delete all your vital records or your entire account.")
    st.write("---")

    st.write("### Delete All Vital Records")
    st.write("This will delete all your health readings but keep your account.")
    entered_id = st.text_input("Enter your Patient ID to confirm")
    if st.button("Delete All My Vital Records"):
        if entered_id == patient_id:
            from database import delete_vitals
            delete_vitals(patient_id)
            st.success("✅ All your vital records have been deleted successfully.")
        else:
            st.warning("⚠️ Patient ID does not match. Please try again.")

    st.write("---")
    st.write("### Delete Entire Account")
    st.write("⚠️ This will permanently delete your account and all data.")
    entered_id2 = st.text_input("Enter your Patient ID to confirm account deletion",
                                 key="del_account")
    if st.button("Delete My Account Permanently"):
        if entered_id2 == patient_id:
            from database import delete_patient
            delete_patient(patient_id)
            st.success("✅ Your account has been deleted.")
            st.session_state.logged_in = False
            st.session_state.patient   = None
            st.rerun()
        else:
            st.warning("⚠️ Patient ID does not match. Please try again.")


# ─── MAIN APP ────────────────────────────────────────────
if st.session_state.logged_in:
    show_dashboard()
else:
    show_auth_page()