# Streamlit frontend
import streamlit as st

# streamlit run app.py

st.set_page_config(page_title="Hello Worl App", layout="centered")

st.markdown(
    "<h1 style='text-align: center; font-size: 80px;'>Helo, World! 🌍</h1>",
    unsafe_allow_html=True
)
