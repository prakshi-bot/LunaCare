"""
LunaCare: Navigation Controller Component
-----------------------------------------
Manages routing between different application pages via Streamlit session state.
Ensures seamless switching between Landing Page, Chat, Topics, Tools, and Wellness.
"""

import streamlit as st


PAGES = [
    {"id": "home", "label": "Home", "icon": "🌙"},
    {"id": "chat", "label": "AI Health Chat", "icon": "💬"},
    {"id": "health_topics", "label": "Health Topics", "icon": "📚"},
    {"id": "symptoms", "label": "Symptom Guide", "icon": "🩺"},
    {"id": "cycle", "label": "Cycle Calculator", "icon": "🌸"},
    {"id": "wellness", "label": "Wellness Center", "icon": "🧘‍♀️"},
    {"id": "mood", "label": "Mood Tracker", "icon": "📊"},
    {"id": "about", "label": "About LunaCare", "icon": "🌸"},
]


def init_navigation_state():
    """Initializes the active page in session state if not already set."""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"


def navigate_to(page_id: str):
    """Sets the active page and triggers a rerun."""
    st.session_state.current_page = page_id
    st.rerun()


def render_top_navbar():
    """
    Renders an elegant top brand bar and quick navigation tabs.
    """
    init_navigation_state()
    
    col1, col2 = st.columns([3, 7])
    
    with col1:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 12px; padding: 4px 0;">
                <div style="width: 38px; height: 38px; border-radius: 12px; background: linear-gradient(135deg, #B97988, #D9AEB8); display: flex; align-items: center; justify-content: center; color: #FFF; font-size: 1.2rem; box-shadow: 0 4px 12px rgba(185,121,136,0.22);">
                    🌙
                </div>
                <div>
                    <div style="font-size: 1.35rem; font-weight: 800; color: #B97988; line-height: 1.1; letter-spacing: -0.02em;">LunaCare</div>
                    <div style="font-size: 0.72rem; font-weight: 500; color: #B97988; letter-spacing: 0.05em; text-transform: uppercase;">Wellness & Health AI</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        # Quick navigation pill links in top bar
        nav_cols = st.columns(len(PAGES))
        for idx, p in enumerate(PAGES):
            with nav_cols[idx]:
                is_active = st.session_state.current_page == p["id"]
                label = f"{p['icon']} {p['label']}" if not is_active else f"👉 {p['label']}"
                btn_type = "primary" if is_active else "secondary"
                if st.button(p["label"], key=f"topnav_{p['id']}", use_container_width=True, type=btn_type):
                    navigate_to(p["id"])
                    
    st.markdown("<hr style='margin: 0.8rem 0 1.5rem 0; border: none; border-top: 1px solid #E7C9D0;'>", unsafe_allow_html=True)
