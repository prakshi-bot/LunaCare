"""
=============================================================
LunaCare: AI-Powered Female Health & Wellness Assistant
=============================================================
Main Application Driver & Multi-Page Router
"""

# SQLite3 compatibility shim for Streamlit Community Cloud (Linux container requires SQLite >= 3.35.0)
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import streamlit as st
from config import APP_NAME, APP_TAGLINE, STYLES_DIR
from components.navigation import init_navigation_state, render_top_navbar
from components.sidebar import render_sidebar
from pages_content.home import render_home_page
from pages_content.chat import render_chat_page
from pages_content.health_topics import render_health_topics_page
from pages_content.symptoms import render_symptoms_page
from pages_content.cycle import render_cycle_page
from pages_content.wellness import render_wellness_page
from pages_content.mood import render_mood_page
from pages_content.about import render_about_page


# 1. Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title=f"{APP_NAME} • Female Health & Wellness AI",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 2. Inject Custom CSS Theme
def inject_custom_css():
    css_file = STYLES_DIR / "style.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


inject_custom_css()

# 3. Initialize Navigation & Session State
init_navigation_state()

# 4. Render Layout
render_sidebar()
render_top_navbar()

# 5. Page Router
current_page = st.session_state.get("current_page", "home")

if current_page == "home":
    render_home_page()
elif current_page == "chat":
    render_chat_page()
elif current_page == "health_topics":
    render_health_topics_page()
elif current_page == "symptoms":
    render_symptoms_page()
elif current_page == "cycle":
    render_cycle_page()
elif current_page == "wellness":
    render_wellness_page()
elif current_page == "mood":
    render_mood_page()
elif current_page == "about":
    render_about_page()
else:
    render_home_page()
