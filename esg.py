import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# ------------------------
# CONFIG
# ------------------------
st.set_page_config(page_title="AI ESG Carbon System", layout="wide")

# Secure API key from Streamlit Secrets
genai.configure(api_key=st.secrets["AIzaSyA8QixFJLKvcj7UMLYRtsKGm5RE92oMtdQ"])
model = genai.GenerativeModel("gemini-1.5-flash")

# ------------------------
# SESSION CONTROL
# ------------------------
if "started" not in st.session_state:
    st.session_state.started = False

st.title("AI-Assisted Carbon Footprint & ESG Assessment System")

if not st.session_state.started:
    st.write("This sustainability assessment takes approximately 1–2 minutes.")
    if st.button("Start Assessment"):
        st.session_state.started = True
    st.stop()

# ------------------------
# QUESTIONNAIRE
# ------------------------
st.header("📋 Sustainability Questionnaire")

industry_type = st.selectbox(
    "Industry Type",
    ["Manufacturing", "Textile", "Food Processing", "Chemical", "Other"]
)

electricity = st.number_input("Monthly Electricity Usage (kWh)", min_value=0.0)
solar = st.number_input("Solar Energy Usage (kWh)", min_value=0.0)
diesel = st.number_input("Monthly Diesel Consumption (litres)", min_value=0.0)
lpg = st.number_input("Monthly LPG Usage (kg)", min_value=0.0)
production = st.number_input("Monthly Production Output (units)", min_value=1.0)

worker_safety = st.selectbox(
    "Worker Safety Standards",
    ["Excellent", "Good", "Average", "Poor"]
)

compliance = st.selectbox(
    "Regulatory Compliance",
    ["Fully Compliant", "Partially Compliant", "Non-Compliant"]
)

# ------------------------
# GENERATE REPORT
# ------------------------
if st.button("Generate Assessment Report"):

    if solar > electricity:
        st.error("Solar energy cannot exceed total electricity usage.")
        st.stop()

    # Emission Factors
    EF_ELECTRICITY = 0.82
    EF_DIESEL = 2.68
    EF_LPG = 1.51

    grid_electricity = electricity - solar

    electricity_emission = grid_electricity * EF_ELECTRICITY
    diesel_emission = diesel * EF_DIESEL
    lpg_emission = lpg * EF_LPG

    scope1 = diesel_emission + lpg_emission
    scope2 = electricity_emission
    total = scope1 + scope2

    emission_per_unit = total / production
    renewable_percentage = (solar / electricity * 100) if electricity > 0 else 0

    # ESG Scoring
    E_score = 85 if emission_per_unit < 5 else 65 if emission_per_unit < 10 else 40

    S_score = {
        "Excellent": 90,
        "Good": 75,
        "Average": 60,
        "Poor": 40
    }[worker_safety]

    G_score = {
        "Fully Compliant": 85,
        "Partially Compliant": 60,
        "Non-Compliant": 35
    }[compliance]

    ESG = (E_score * 0.4) + (S_score * 0.3) + (G_score * 0.3)

    # ------------------------
    # RESULTS
    # ------------------------
    st.header("📊 Emission Results")

    st.write(f"Scope 1 Emissions: {scope1:.2f} kg CO₂")
    st.write(f"Scope 2 Emissions: {scope2:.2f} kg CO₂")
    st.write(f"Total Emissions: {total:.2f} kg CO₂")
    st.write(f"Emission per Unit: {emission_per_unit:.2f} kg CO₂/unit")
    st.write(f"Renewable Energy Usage: {renewable_percentage:.2f}%")
    st.write(f"Final ESG Score: {ESG:.2f} / 100")

    df = pd.DataFrame({
        "Source": ["Diesel", "LPG", "Grid Electricity"],
        "Emissions": [diesel_emission, lpg_emission, electricity_emission]
    })

    fig = px.pie(df, names="Source", values="Emissions",
                 title="Emission Distribution by Source")
    st.plotly_chart(fig)

    # ------------------------
    # AI ANALYSIS
    # ------------------------
    st.header("🤖 AI Sustainability Analysis")

    prompt = f"""
    You are a sustainability consultant.

    Industry Type: {industry_type}
    Total Emissions: {total:.2f} kg CO2
    Emission per Unit: {emission_per_unit:.2f} kg CO2/unit
    Renewable Energy Usage: {renewable_percentage:.2f}%
    ESG Score: {ESG:.2f}

    Provide:
    1. Carbon footprint analysis
    2. ESG interpretation
    3. Risk level (Low/Medium/High)
    4. 5 practical improvement suggestions
    5. Long-term sustainability strategy
    """

    try:
        with st.spinner("Generating AI insights..."):
            response = model.generate_content(prompt)
        st.write(response.text)
    except Exception as e:

        st.error(f"AI Error: {str(e)}")
