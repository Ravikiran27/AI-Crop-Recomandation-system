import streamlit as st
import pandas as pd

st.title("Farmers Management")

# Load farmer database
def load_farmers():
    return pd.read_csv('data/farmers.csv')

farmers = load_farmers()
st.dataframe(farmers)

# Add new farmer
with st.form("Add Farmer"):
    name = st.text_input("Name")
    contact = st.text_input("Contact")
    location = st.text_input("Location")
    crops_grown = st.text_input("Crops Grown (comma separated)")
    notes = st.text_area("Notes")
    submitted = st.form_submit_button("Add Farmer")
    if submitted:
        new_id = farmers['id'].max() + 1 if not farmers.empty else 1
        new_row = {"id": new_id, "name": name, "contact": contact, "location": location, "crops_grown": crops_grown, "notes": notes}
        farmers = pd.concat([farmers, pd.DataFrame([new_row])], ignore_index=True)
        farmers.to_csv('data/farmers.csv', index=False)
        st.success("Farmer added!")
        st.experimental_rerun()
