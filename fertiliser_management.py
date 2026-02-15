import streamlit as st
import google.generativeai as genai
import pandas as pd

st.title("Fertiliser Recommendation & Gemini AI Suggestions")

fertilisers = load_fertilisers()

# Gemini API setup
api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyA6IY3vNUPKBEneRYcomPg2fRvNtLb0vRI")
genai.configure(api_key=api_key)

# Recommendation history
if "fertiliser_history" not in st.session_state:
    st.session_state["fertiliser_history"] = []

# Fertiliser recommendation using Gemini API
crop = st.selectbox("Select Crop", ["Rice", "Wheat", "Cotton", "Maize"])
if st.button("Get Gemini Fertiliser Recommendation"):
    prompt = f"Suggest the best fertiliser for {crop} crop with brief reason."
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    suggestion = response.text
    st.session_state["fertiliser_history"].append({"crop": crop, "suggestion": suggestion})
    st.markdown(f"### Gemini AI Fertiliser Recommendation for {crop}")
    st.info(suggestion)

# Show history
st.markdown("---")
st.markdown("### Fertiliser Recommendation History")
for entry in st.session_state["fertiliser_history"]:
    st.markdown(f"**Crop:** {entry['crop']}<br>**Suggestion:** {entry['suggestion']}", unsafe_allow_html=True)

# Add new fertiliser
with st.form("Add Fertiliser"):
    name = st.text_input("Name")
    type_ = st.text_input("Type")
    suitable_crops = st.text_input("Suitable Crops (comma separated)")
    application = st.text_area("Application")
    notes = st.text_area("Notes")
    submitted = st.form_submit_button("Add Fertiliser")
    if submitted:
        new_id = fertilisers['id'].max() + 1 if not fertilisers.empty else 1
        new_row = {"id": new_id, "name": name, "type": type_, "suitable_crops": suitable_crops, "application": application, "notes": notes}
        fertilisers = pd.concat([fertilisers, pd.DataFrame([new_row])], ignore_index=True)
        fertilisers.to_csv('data/fertilisers.csv', index=False)
        st.success("Fertiliser added!")
        st.rerun()
