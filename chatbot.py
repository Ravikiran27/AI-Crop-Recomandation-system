import streamlit as st
import google.generativeai as genai

st.title("AI Chatbot for Farmers")

api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyA6IY3vNUPKBEneRYcomPg2fRvNtLb0vRI")
genai.configure(api_key=api_key)

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

farmer_name = st.session_state.get("farmer_name", "Farmer")
st.markdown(f"Hello, **{farmer_name}**! Ask me anything about crops, fertilisers, or farming.")
prompt = st.text_input("Ask the AI anything about crops, fertilisers, or farming:")

if st.button("Send") and prompt:
    model = genai.GenerativeModel("gemini-pro")
    context_prompt = f"Farmer name: {farmer_name}. " + prompt
    response = model.generate_content(context_prompt)
    answer = response.text
    st.session_state["chat_history"].append({"user": prompt, "bot": answer})

for chat in st.session_state["chat_history"]:
    st.markdown(f"**You:** {chat['user']}")
    st.markdown(f"**AI:** {chat['bot']}")
