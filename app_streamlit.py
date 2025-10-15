import streamlit as st
import pandas as pd
import joblib
import numpy as np
from pandas.api.types import CategoricalDtype

# Page configuration
st.set_page_config(
    page_title="Crop Recommendation System",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        height: 3em;
        border-radius: 10px;
        font-size: 18px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .recommendation-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    .crop-name {
        font-size: 48px;
        font-weight: bold;
        margin: 10px 0;
    }
    .confidence-text {
        font-size: 24px;
        margin-top: 10px;
    }
    h1 {
        color: #2e7d32;
    }
    h2 {
        color: #1976d2;
    }
    .subtitle {
        color: #666;
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
    
    # Convert to categorical type
    ph_order = CategoricalDtype(categories=["Acidic", "Neutral", "Alkaline"], ordered=True)
    data["ph_category"] = data["ph_category"].astype(ph_order)
    
    data['temp_rain_interaction'] = data['temperature'] * data['rainfall']
    data['ph_rain_interaction'] = data['ph'] * data['rainfall']
    
    return data

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

# Load the model
model, encoder, model_loaded = load_model()

# Header
st.markdown("<h1 style='text-align: center;'>🌾 AI-Powered Crop Recommendation System</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle' style='text-align: center;'>Get intelligent crop recommendations based on soil and climate conditions</p>", unsafe_allow_html=True)

# Check if model is loaded
if not model_loaded:
    st.error("⚠️ Model files not found! Please run the training notebook first to generate the model files.")
    st.info("📝 Run all cells in 'predict-crop-recommendation-accucarcy-99-55.ipynb' to create the model.")
    st.stop()

# Get preset values if available
preset = st.session_state.get('preset', {})

# Create two columns for layout
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 🌱 Soil Nutrients")
    
    # Soil nutrients with better UI
    N = st.slider(
        '**Nitrogen (N)** - Ratio of Nitrogen in soil',
        min_value=0, max_value=140, value=preset.get('N', 90),
        help="Nitrogen content in kg/ha"
    )
    
    P = st.slider(
        '**Phosphorus (P)** - Ratio of Phosphorus in soil',
        min_value=5, max_value=145, value=preset.get('P', 42),
        help="Phosphorus content in kg/ha"
    )
    
    K = st.slider(
        '**Potassium (K)** - Ratio of Potassium in soil',
        min_value=5, max_value=205, value=preset.get('K', 43),
        help="Potassium content in kg/ha"
    )
    
    ph = st.slider(
        '**pH Level** - Soil acidity/alkalinity',
        min_value=3.5, max_value=9.9, value=preset.get('ph', 6.5), step=0.1,
        help="pH scale (3.5-9.9)"
    )
    
    # Display pH category
    if ph < 5.5:
        ph_cat = "🔴 Acidic"
    elif ph <= 7.5:
        ph_cat = "🟢 Neutral"
    else:
        ph_cat = "🔵 Alkaline"
    st.info(f"Soil Type: {ph_cat}")

with col2:
    st.markdown("### 🌤️ Climate Conditions")
    
    temperature = st.slider(
        '**Temperature** - Average temperature',
        min_value=8.0, max_value=44.0, value=preset.get('temp', 20.8), step=0.1,
        help="Temperature in Celsius"
    )
    
    humidity = st.slider(
        '**Humidity** - Relative humidity',
        min_value=14.0, max_value=100.0, value=preset.get('humidity', 82.0), step=0.1,
        help="Relative humidity in percentage"
    )
    
    rainfall = st.slider(
        '**Rainfall** - Annual rainfall',
        min_value=20.0, max_value=300.0, value=preset.get('rainfall', 202.9), step=0.1,
        help="Rainfall in mm"
    )
    
    # Display rainfall category
    if rainfall < 50:
        rain_cat = "💧 Low"
    elif rainfall < 100:
        rain_cat = "💧💧 Medium"
    elif rainfall < 200:
        rain_cat = "💧💧💧 High"
    else:
        rain_cat = "💧💧💧💧 Very High"
    st.info(f"Rainfall Level: {rain_cat}")

# Spacer
st.markdown("---")

# Predict button
if st.button('🔍 Get Crop Recommendation', use_container_width=True):
    
    # Create input dataframe
    input_data = pd.DataFrame({
        'N': [N],
        'P': [P],
        'K': [K],
        'temperature': [temperature],
        'humidity': [humidity],
        'ph': [ph],
        'rainfall': [rainfall]
    })
    
    # Apply feature engineering
    input_data_fe = feature_engineer(input_data.copy())
    
    # Make prediction
    with st.spinner('🤔 Analyzing soil and climate data...'):
        prediction = model.predict(input_data_fe)
        predicted_crop = encoder.inverse_transform(prediction)[0]
        
        # Get probabilities
        proba = model.predict_proba(input_data_fe)[0]
        confidence = proba.max() * 100
        top_5_idx = proba.argsort()[-5:][::-1]
    
    # Display main recommendation
    st.markdown(f"""
        <div class='recommendation-box'>
            <h2 style='color: white; margin: 0;'>🎯 Recommended Crop</h2>
            <div class='crop-name'>{predicted_crop.upper()}</div>
            <div class='confidence-text'>Confidence: {confidence:.1f}%</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Display top 5 recommendations
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
    
    # Display input parameters summary
    st.markdown("---")
    st.markdown("### 📋 Input Parameters Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            **🌱 Soil Nutrients:**
            - Nitrogen (N): {} kg/ha
            - Phosphorus (P): {} kg/ha
            - Potassium (K): {} kg/ha
            - pH Level: {}
        """.format(N, P, K, ph))
    
    with col2:
        st.markdown("""
            **🌤️ Climate:**
            - Temperature: {}°C
            - Humidity: {}%
            - Rainfall: {} mm
        """.format(temperature, humidity, rainfall))
    
    with col3:
        st.markdown("""
            **📊 Calculated Features:**
            - NPK Average: {:.1f}
            - Temp-Humidity Index: {:.1f}
            - pH Category: {}
            - Rainfall Level: {}
        """.format(
            (N + P + K) / 3,
            temperature * humidity / 100,
            ph_cat.split()[1],
            rain_cat.split()[1] if len(rain_cat.split()) > 1 else rain_cat
        ))
    
    # Success message
    st.success("✅ Recommendation generated successfully!")

# Sidebar information
with st.sidebar:
    st.markdown("## ℹ️ About")
    st.info("""
        This AI-powered system uses **XGBoost** machine learning algorithm 
        to recommend the best crop based on:
        - Soil nutrients (N, P, K, pH)
        - Climate conditions (Temperature, Humidity, Rainfall)
        
        **Model Accuracy:** 99.55%
    """)
    
    st.markdown("## 🎯 How to Use")
    st.markdown("""
        1. Adjust the sliders for soil nutrients
        2. Set climate conditions
        3. Click **Get Crop Recommendation**
        4. View your personalized crop suggestion
    """)
    
    st.markdown("## 🌾 Supported Crops")
    if encoder is not None:
        crops_list = sorted(encoder.classes_)
        crops_text = ", ".join(crops_list)
        st.markdown(f"**{len(crops_list)} crops:** {crops_text}")
    
    st.markdown("---")
    st.markdown("### 💡 Quick Presets")
    
    if st.button("🌾 Rice Preset"):
        st.session_state['preset'] = {
            'N': 90, 'P': 42, 'K': 43,
            'temp': 20.8, 'humidity': 82.0,
            'ph': 6.5, 'rainfall': 202.9
        }
        st.rerun()
    
    if st.button("🌸 Cotton Preset"):
        st.session_state['preset'] = {
            'N': 117, 'P': 46, 'K': 20,
            'temp': 26.0, 'humidity': 80.0,
            'ph': 7.5, 'rainfall': 78.0
        }
        st.rerun()
    
    if st.button("☕ Coffee Preset"):
        st.session_state['preset'] = {
            'N': 101, 'P': 29, 'K': 30,
            'temp': 23.0, 'humidity': 58.0,
            'ph': 6.4, 'rainfall': 132.0
        }
        st.rerun()
    
    if st.button("🌽 Maize Preset"):
        st.session_state['preset'] = {
            'N': 78, 'P': 54, 'K': 23,
            'temp': 22.0, 'humidity': 65.0,
            'ph': 6.2, 'rainfall': 85.0
        }
        st.rerun()
    
    if st.button("🔄 Reset to Default"):
        if 'preset' in st.session_state:
            del st.session_state['preset']
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🌾 Built with ❤️ for Agricultural Innovation</p>
        <p>Powered by Machine Learning | XGBoost Classifier</p>
    </div>
""", unsafe_allow_html=True)
