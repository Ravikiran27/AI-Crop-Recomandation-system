
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
        # ...existing crop recommendation code...
        # After showing the crop recommendation result, show fertiliser recommendation module
        # (Assumes fertiliser_management.py provides a function or UI for this)
        # Show fertiliser recommendation only after result
        # ...existing code for crop recommendation...
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
        if st.button("💬 Chat Support"):
            importlib.import_module("chatbot")
