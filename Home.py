import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="EV Grid Impact Intelligence Engine",
    layout="wide"
)


# --------------------------------------------------
# Sidebar Logo
# --------------------------------------------------
# from pages.ui_config import add_logo
# add_logo() 

# st.title("🚗⚡ EV Grid Impact Intelligence Engine")

# st.markdown("This tool analyzes the impact of EV penetration on distribution networks.")

#st.markdown("**Network URL:** [http://172.23.55.187:8501](http://172.23.55.187:8501)") # [text](link)

# --------------------------------------------------
# README Viewer
# --------------------------------------------------
st.header("📘 Project Documentation")

try:
    with open("README.md", "r", encoding="utf-8") as f:
        readme_content = f.read()
    st.markdown(readme_content, unsafe_allow_html=True)

except FileNotFoundError:
    st.warning("README.md file not found. Please add it to the project root folder.")
