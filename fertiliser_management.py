st.title("Fertiliser Recommendation & Database")
fertilisers = load_fertilisers()
st.dataframe(fertilisers)
st.markdown(f"### Recommended Fertilisers for {crop}")
st.dataframe(recommended)

import streamlit as st
import pandas as pd

st.title("Fertiliser Recommendation & Database")

# Load fertiliser database
def load_fertilisers():
    return pd.read_csv('data/fertilisers.csv')

fertilisers = load_fertilisers()
st.dataframe(fertilisers)

# Fertiliser recommendation
crop = st.selectbox("Select Crop", fertilisers['suitable_crops'].str.split(';').explode().unique())
recommended = fertilisers[fertilisers['suitable_crops'].str.contains(crop)]
st.markdown(f"### Recommended Fertilisers for {crop}")
st.dataframe(recommended)

import streamlit as st
import pandas as pd

st.title("Fertiliser Recommendation & Database")

# Load fertiliser database
def load_fertilisers():
    return pd.read_csv('data/fertilisers.csv')

fertilisers = load_fertilisers()
st.dataframe(fertilisers)

crop = st.selectbox("Select Crop", fertilisers['suitable_crops'].str.split(';').explode().unique())
recommended = fertilisers[fertilisers['suitable_crops'].str.contains(crop)]
st.markdown(f"### Recommended Fertilisers for {crop}")
st.dataframe(recommended)

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
        st.experimental_rerun()
