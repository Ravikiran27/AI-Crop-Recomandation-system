# 🌾 Crop Recommendation System

An AI-powered crop recommendation system that provides accurate crop suggestions based on soil and climate parameters using machine learning.

## 📊 Project Overview

This project uses advanced machine learning techniques to recommend the most suitable crop for cultivation based on:
- Soil nutrients (N, P, K)
- Climate conditions (temperature, humidity, rainfall)
- Soil pH level

**Model Accuracy:** 99.55% (Cross-validation)

## 🚀 Features

- **High Accuracy Model**: XGBoost classifier with 99.55% accuracy
- **Feature Engineering**: Advanced feature creation for better predictions
- **Comprehensive Analytics**: Detailed model performance metrics and visualizations
- **Production Ready**: Exportable model for deployment
- **Web Application**: Ready-to-deploy Streamlit and Gradio apps
- **22 Crop Types**: Supports rice, maize, chickpea, kidney beans, pigeon peas, moth beans, mung bean, black gram, lentil, pomegranate, banana, mango, grapes, watermelon, muskmelon, apple, orange, papaya, coconut, cotton, jute, coffee

## 📁 Project Structure

```
AI Crop Recomandation system/
├── Crop_recommendation.csv                           # Dataset
├── predict-crop-recommendation-accucarcy-99-55.ipynb # Main notebook (USE THIS)
├── crop-recommendation-predication-98-accuracy.ipynb # Alternative notebook
├── models/                                           # Model files (created after training)
│   ├── crop_recommendation_model.pkl                 # Trained model pipeline
│   ├── label_encoder.pkl                             # Label encoder
│   └── model_metadata.json                           # Model information
├── app_streamlit.py                                  # Streamlit web app
├── app_gradio.py                                     # Gradio web app
├── requirements.txt                                  # Python dependencies
└── README.md                                         # This file
```

## 🛠️ Installation

1. **Clone or download this repository**

2. **Install required packages:**
```bash
pip install -r requirements.txt
```

3. **Run the Jupyter notebook:**
```bash
jupyter notebook predict-crop-recommendation-accucarcy-99-55.ipynb
```

## 📈 Model Training

The notebook includes:

1. **Data Loading and Exploration**
   - Dataset overview
   - Statistical analysis
   - Missing value checks

2. **Feature Engineering**
   - NPK average calculation
   - Temperature-Humidity Index (THI)
   - Rainfall level categorization
   - pH categorization
   - Feature interactions

3. **Model Training**
   - XGBoost Classifier
   - Pipeline with preprocessing
   - 5-fold stratified cross-validation

4. **Advanced Analytics**
   - Classification report
   - Confusion matrix
   - Per-class metrics (Precision, Recall, F1-Score)
   - Feature importance analysis
   - Cross-validation visualization

5. **Model Export**
   - Save trained model
   - Save label encoder
   - Save model metadata

## 🌐 Web Application Deployment

### Option 1: Streamlit

```bash
streamlit run app_streamlit.py
```

Open your browser at `http://localhost:8501`

### Option 2: Gradio

```bash
python app_gradio.py
```

Open the URL shown in terminal (usually `http://127.0.0.1:7860`)

## 📊 Model Performance

- **Accuracy:** 99.55%
- **Cross-Validation Mean:** 99.5%+
- **Algorithm:** XGBoost Classifier
- **Features:** 13 (7 original + 6 engineered)
- **Training Samples:** 1,760
- **Validation Samples:** 440

## 🔍 Input Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| Nitrogen (N) | 0-140 | Nitrogen content in soil (kg/ha) |
| Phosphorus (P) | 5-145 | Phosphorus content in soil (kg/ha) |
| Potassium (K) | 5-205 | Potassium content in soil (kg/ha) |
| Temperature | 8-44°C | Average temperature |
| Humidity | 14-100% | Relative humidity |
| pH | 3.5-9.9 | Soil pH level |
| Rainfall | 20-300mm | Annual rainfall |

## 💡 Usage Example

```python
import pandas as pd
import joblib

# Load model
model = joblib.load('models/crop_recommendation_model.pkl')
encoder = joblib.load('models/label_encoder.pkl')

# Create input data
input_data = pd.DataFrame({
    'N': [90], 'P': [42], 'K': [43],
    'temperature': [20.8],
    'humidity': [82.0],
    'ph': [6.5],
    'rainfall': [202.9]
})

# Apply feature engineering (see notebook for function)
input_data_fe = feature_engineer(input_data)

# Predict
prediction = model.predict(input_data_fe)
crop = encoder.inverse_transform(prediction)[0]
print(f"Recommended Crop: {crop}")
```

## 📦 Dependencies

- pandas >= 1.3.0
- numpy >= 1.21.0
- scikit-learn >= 1.0.0
- xgboost >= 1.5.0
- joblib >= 1.1.0
- streamlit >= 1.20.0
- gradio >= 3.20.0
- matplotlib >= 3.4.0
- seaborn >= 0.11.0

## 🎯 Future Enhancements

- [ ] Add weather API integration
- [ ] Include soil testing recommendations
- [ ] Multi-language support
- [ ] Mobile application
- [ ] Regional crop database
- [ ] Seasonal recommendations
- [ ] Profit estimation

## 📝 License

This project is open source and available for educational purposes.

## 👤 Author

Built with ❤️ for farmers and agricultural technology

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## ⭐ Show your support

Give a ⭐️ if this project helped you!

---

**Note:** This is a machine learning model and should be used as a decision support tool. Always consult with local agricultural experts for final decisions.
