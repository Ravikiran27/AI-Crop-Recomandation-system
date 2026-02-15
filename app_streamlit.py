
# Load model with caching
import streamlit as st
import pandas as pd
import joblib
import numpy as np
import sqlite3
from pandas.api.types import CategoricalDtype
import importlib
import hashlib
from farmer_db import get_db_connection

# Load model with caching
@st.cache_resource
def load_model():
    try:
        model = joblib.load('models/crop_recommendation_model.pkl')
        encoder = joblib.load('models/label_encoder.pkl')
        return model, encoder, True
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None, None, False
import joblib
import numpy as np
import sqlite3
from pandas.api.types import CategoricalDtype
import importlib
import hashlib
from farmer_db import get_db_connection

st.set_page_config(
    page_title="Crop Recommendation Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dashboard UI
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .dashboard-card {
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        padding: 30px;
        margin-bottom: 20px;
    }
    .dashboard-title {
        color: #2e7d32;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .dashboard-subtitle {
        color: #1976d2;
        font-size: 18px;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# Feature engineering function
def feature_engineer(data):
    data['NPK'] = (data['N'] + data['P'] + data['K']) / 3
    data['THI'] = data['temperature'] * data['humidity'] / 100
    data['rainfall_level'] = pd.cut(data['rainfall'],
                              bins=[0, 50, 100, 200, 300],
                              labels=['Low', 'Medium', 'High', 'Very High'])
    def ph_category(p):
        if p < 5.5:
            return 'Acidic'
        elif p <= 7.5:
            return 'Neutral'
        else:
            return 'Alkaline'
    data['ph_category'] = data['ph'].apply(ph_category)
    ph_order = CategoricalDtype(categories=["Acidic", "Neutral", "Alkaline"], ordered=True)
    data["ph_category"] = data["ph_category"].astype(ph_order)
    data['temp_rain_interaction'] = data['temperature'] * data['rainfall']
    data['ph_rain_interaction'] = data['ph'] * data['rainfall']
    return data


# --- AUTHENTICATION & DASHBOARD ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def signup_farmer(name, contact, password, location="", crops_grown="", notes=""):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM farmers WHERE contact=?", (contact,))
    if c.fetchone():
        conn.close()
        return False, "Contact already registered. Please sign in."
    c.execute("INSERT INTO farmers (name, contact, password, location, crops_grown, notes) VALUES (?, ?, ?, ?, ?, ?)",
              (name, contact, hash_password(password), location, crops_grown, notes))
    conn.commit()
    conn.close()
    return True, "Signup successful! Please sign in."

def signin_farmer(contact, password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name FROM farmers WHERE contact=? AND password=?", (contact, hash_password(password)))
    row = c.fetchone()
    conn.close()
    if row:
        return True, row[1], row[0]
    return False, None, None

if "farmer_logged_in" not in st.session_state:
    st.session_state["farmer_logged_in"] = False
    st.session_state["farmer_name"] = ""
    st.session_state["farmer_id"] = None

if not st.session_state["farmer_logged_in"]:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='dashboard-title'>Farmer Sign In</div>", unsafe_allow_html=True)
    with st.form("signin_form"):
        contact = st.text_input("Contact")
        password = st.text_input("Password", type="password")
        signin_submit = st.form_submit_button("Sign In")
        signin_error = ""
        if signin_submit:
            ok, name, fid = signin_farmer(contact, password)
            if ok:
                st.session_state["farmer_logged_in"] = True
                st.session_state["farmer_name"] = name
                st.session_state["farmer_id"] = fid
                st.rerun()
            else:
                signin_error = "Invalid contact or password."
        if signin_error:
            st.error(signin_error)
    st.markdown("---", unsafe_allow_html=True)
    st.markdown("<div class='dashboard-title'>New Farmer? Sign Up</div>", unsafe_allow_html=True)
    with st.form("signup_form"):
        name = st.text_input("Name")
        contact = st.text_input("Contact (unique)")
        password = st.text_input("Password", type="password")
        location = st.text_input("Location (optional)")
        crops_grown = st.text_input("Crops Grown (optional)")
        notes = st.text_area("Notes (optional)")
        signup_submit = st.form_submit_button("Sign Up")
        signup_msg = ""
        if signup_submit:
            ok, msg = signup_farmer(name, contact, password, location, crops_grown, notes)
            if ok:
                signup_msg = msg
            else:
                st.error(msg)
        if signup_msg:
            st.success(signup_msg)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='dashboard-title'>Welcome, {st.session_state['farmer_name']}!</div>", unsafe_allow_html=True)
    st.markdown("<div class='dashboard-subtitle'>Select a feature from the dashboard below:</div>", unsafe_allow_html=True)
    dashboard_page = st.sidebar.selectbox(
        "Dashboard Navigation",
        ["Crop Recommendation", "Chatbot", "Logout"]
    )
    if dashboard_page == "Crop Recommendation":
        # Load the model
        model, encoder, model_loaded = load_model()
        st.markdown("<h1 style='text-align: center;'>🌾 AI-Powered Crop Recommendation System</h1>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle' style='text-align: center;'>Get intelligent crop recommendations based on soil and climate conditions</p>", unsafe_allow_html=True)
        if not model_loaded:
            st.error("⚠️ Model files not found! Please run the training notebook first to generate the model files.")
            st.info("📝 Run all cells in 'predict-crop-recommendation-accucarcy-99-55.ipynb' to create the model.")
            st.stop()
        preset = st.session_state.get('preset', {})
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("### 🌱 Soil Nutrients")
            N = st.slider('**Nitrogen (N)** - Ratio of Nitrogen in soil', min_value=0, max_value=140, value=preset.get('N', 90), help="Nitrogen content in kg/ha")
            P = st.slider('**Phosphorus (P)** - Ratio of Phosphorus in soil', min_value=5, max_value=145, value=preset.get('P', 42), help="Phosphorus content in kg/ha")
            K = st.slider('**Potassium (K)** - Ratio of Potassium in soil', min_value=5, max_value=205, value=preset.get('K', 43), help="Potassium content in kg/ha")
            ph = st.slider('**pH Level** - Soil acidity/alkalinity', min_value=3.5, max_value=9.9, value=preset.get('ph', 6.5), step=0.1, help="pH scale (3.5-9.9)")
            if ph < 5.5:
                ph_cat = "🔴 Acidic"
            elif ph <= 7.5:
                ph_cat = "🟢 Neutral"
            else:
                ph_cat = "🔵 Alkaline"
            st.info(f"Soil Type: {ph_cat}")
        with col2:
            st.markdown("### 🌤️ Climate Conditions")
            temperature = st.slider('**Temperature** - Average temperature', min_value=8.0, max_value=44.0, value=preset.get('temp', 20.8), step=0.1, help="Temperature in Celsius")
            humidity = st.slider('**Humidity** - Relative humidity', min_value=14.0, max_value=100.0, value=preset.get('humidity', 82.0), step=0.1, help="Relative humidity in percentage")
            rainfall = st.slider('**Rainfall** - Annual rainfall', min_value=20.0, max_value=300.0, value=preset.get('rainfall', 202.9), step=0.1, help="Rainfall in mm")
            if rainfall < 50:
                rain_cat = "💧 Low"
            elif rainfall < 100:
                rain_cat = "💧💧 Medium"
            elif rainfall < 200:
                rain_cat = "💧💧💧 High"
            else:
                rain_cat = "💧💧💧💧 Very High"
            st.info(f"Rainfall Level: {rain_cat}")
        st.markdown("---")
        if st.button('🔍 Get Crop Recommendation', use_container_width=True):
            input_data = pd.DataFrame({
                'N': [N], 'P': [P], 'K': [K],
                'temperature': [temperature], 'humidity': [humidity],
                'ph': [ph], 'rainfall': [rainfall]
            })
            input_data_fe = feature_engineer(input_data.copy())
            with st.spinner('🤔 Analyzing soil and climate data...'):
                prediction = model.predict(input_data_fe)
                predicted_crop = encoder.inverse_transform(prediction)[0]
                proba = model.predict_proba(input_data_fe)[0]
                confidence = proba.max() * 100
                top_5_idx = proba.argsort()[-5:][::-1]
            st.markdown(f"""
                <div class='recommendation-box'>
                    <h2 style='color: white; margin: 0;'>🎯 Recommended Crop</h2>
                    <div class='crop-name'>{predicted_crop.upper()}</div>
                    <div class='confidence-text'>Confidence: {confidence:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("### 📊 Top 5 Crop Recommendations")
            cols = st.columns(5)
            for idx, col in enumerate(cols):
                if idx < len(top_5_idx):
                    crop_idx = top_5_idx[idx]
                    crop = encoder.classes_[crop_idx]
                    prob = proba[crop_idx] * 100
                    with col:
                        st.markdown(f"""
                            <div style='text-align: center; padding: 15px; background-color: #f0f2f6; border-radius: 10px; margin: 5px;'>
                                <div style='font-size: 24px;'>#{idx + 1}</div>
                                <div style='font-size: 18px; font-weight: bold; color: #2e7d32; margin: 10px 0;'>{crop}</div>
                                <div style='font-size: 16px; color: #666;'>{prob:.1f}%</div>
                            </div>
                        """, unsafe_allow_html=True)
                        st.progress(float(prob/100))
            st.markdown("---")
            st.markdown("### 📋 Input Parameters Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                    **🌱 Soil Nutrients:**
                    - Nitrogen (N): {N} kg/ha
                    - Phosphorus (P): {P} kg/ha
                    - Potassium (K): {K} kg/ha
                    - pH Level: {ph}
                """)
            with col2:
                st.markdown(f"""
                    **🌤️ Climate:**
                    - Temperature: {temperature}°C
                    - Humidity: {humidity}%
                    - Rainfall: {rainfall} mm
                """)
            with col3:
                st.markdown(f"""
                    **📊 Calculated Features:**
                    - NPK Average: {(N + P + K) / 3:.1f}
                    - Temp-Humidity Index: {temperature * humidity / 100:.1f}
                    - pH Category: {ph_cat.split()[1]}
                    - Rainfall Level: {rain_cat.split()[1] if len(rain_cat.split()) > 1 else rain_cat}
                """)
            st.success("✅ Recommendation generated successfully!")
            # After result:
            importlib.import_module("fertiliser_management")
    elif dashboard_page == "Chatbot":
        importlib.import_module("chatbot")
    elif dashboard_page == "Logout":
        st.session_state["farmer_logged_in"] = False
        st.session_state["farmer_name"] = ""
        st.session_state["farmer_id"] = None
        st.rerun()

# Make chat support available everywhere (sidebar persistent button)
with st.sidebar:
    if st.session_state.get("farmer_logged_in", False):
        st.markdown("---")
        if st.button("💬 Chat Support", key="chat_support"):
            st.session_state["show_chat"] = True

# Always show chat if requested
if st.session_state.get("show_chat", False):
    importlib.import_module("chatbot")
