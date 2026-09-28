"""
LunaCare: Gentle Mood & Emotional Tracker
-----------------------------------------
Allows users to log daily emotional wellness using a 5-tier scale and personal notes.
Renders an interactive Plotly timeline chart and summary trends.
Keeps data localized within Streamlit session state for complete privacy.
"""

from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px


MOOD_LEVELS = [
    {"label": "Very Low", "score": 1, "icon": "🌧️", "color": "#7B68B0"},
    {"label": "Low", "score": 2, "icon": "☁️", "color": "#B97988"},
    {"label": "Neutral", "score": 3, "icon": "⛅", "color": "#A594D0"},
    {"label": "Good", "score": 4, "icon": "🌤️", "color": "#D48C9E"},
    {"label": "Very Good", "score": 5, "icon": "☀️", "color": "#E6A4B4"},
]


def init_mood_state():
    """Initializes sample mood history in session state if not set."""
    if "mood_logs" not in st.session_state:
        # Pre-seed with realistic sample entries from the last few days
        today = datetime.now()
        st.session_state.mood_logs = [
            {
                "timestamp": (today - timedelta(days=4)).strftime("%Y-%m-%d %H:%M"),
                "date": (today - timedelta(days=4)).strftime("%b %d"),
                "mood": "Neutral",
                "score": 3,
                "icon": "⛅",
                "note": "Felt a bit tired during the afternoon.",
            },
            {
                "timestamp": (today - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"),
                "date": (today - timedelta(days=3)).strftime("%b %d"),
                "mood": "Good",
                "score": 4,
                "icon": "🌤️",
                "note": "Went for a morning walk; calm and productive.",
            },
            {
                "timestamp": (today - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
                "date": (today - timedelta(days=2)).strftime("%b %d"),
                "mood": "Very Good",
                "score": 5,
                "icon": "☀️",
                "note": "Great energy after mindful yoga session.",
            },
            {
                "timestamp": (today - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
                "date": (today - timedelta(days=1)).strftime("%b %d"),
                "mood": "Low",
                "score": 2,
                "icon": "☁️",
                "note": "Slight pelvic cramps starting; rested with tea.",
            },
        ]


def render_mood_page():
    """Renders the Mood Tracker interface."""
    init_mood_state()

    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.8rem;">📊</span>
                <h1 style="margin: 0; font-size: 1.8rem; color: #B97988;">Gentle Mood Tracker</h1>
            </div>
            <p style="color: #4A3B4F; font-size: 0.95rem; margin-top: 4px;">
                Log emotional patterns across your cycle. Kept privately in your local browser session.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([5, 6])

    with col1:
        st.markdown("<h3 style='font-size: 1.2rem; color: #B97988;'>Log Today's Mood</h3>", unsafe_allow_html=True)
        
        selected_mood_label = st.radio(
            "How are you feeling right now?",
            options=[f"{m['icon']} {m['label']}" for m in MOOD_LEVELS],
            index=3,
            horizontal=False,
            key="mood_radio_select",
        )

        note_input = st.text_input(
            "Optional self-reflection or note:",
            placeholder="e.g. Mild headache, felt relaxed after reading...",
            key="mood_note_input",
        )

        if st.button("🌸 Record Mood Entry", use_container_width=True, type="primary"):
            # Extract mood item
            chosen = next(m for m in MOOD_LEVELS if m["label"] in selected_mood_label)
            now = datetime.now()
            st.session_state.mood_logs.append({
                "timestamp": now.strftime("%Y-%m-%d %H:%M"),
                "date": now.strftime("%b %d"),
                "mood": chosen["label"],
                "score": chosen["score"],
                "icon": chosen["icon"],
                "note": note_input if note_input else "No notes provided.",
            })
            st.success("Mood entry recorded! Your trend graph below has updated.")
            st.rerun()

    with col2:
        st.markdown("<h3 style='font-size: 1.2rem; color: #B97988;'>Weekly Trend Overview</h3>", unsafe_allow_html=True)
        
        df = pd.DataFrame(st.session_state.mood_logs)
        
        if not df.empty:
            avg_score = df["score"].mean()
            c_stat1, c_stat2 = st.columns(2)
            with c_stat1:
                st.metric("Total Logs", len(df))
            with c_stat2:
                st.metric("Average Mood Score", f"{avg_score:.1f} / 5.0")

            # Plotly Line Chart
            fig = px.line(
                df,
                x="date",
                y="score",
                markers=True,
                title="Emotional Energy Timeline",
                labels={"score": "Energy Score (1–5)", "date": "Date"},
                template="plotly_white",
            )
            fig.update_traces(
                line_color="#B97988",
                line_width=3,
                marker=dict(size=10, color="#D9AEB8"),
            )
            fig.update_layout(
                yaxis=dict(range=[0.5, 5.5], tickvals=[1, 2, 3, 4, 5], ticktext=["🌧️ Very Low", "☁️ Low", "⛅ Neutral", "🌤️ Good", "☀️ Very Good"]),
                margin=dict(l=20, r=20, t=40, b=20),
                height=260,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)

    # Recent Log Entries Table
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown("<h4 style='font-size: 1.1rem; color: #B97988;'>Recent Entries</h4>", unsafe_allow_html=True)

    for item in reversed(st.session_state.mood_logs[-5:]):
        st.markdown(
            f"""
            <div style="background: #FFF8FB; border: 1px solid #E7C9D0; border-radius: 12px; padding: 0.8rem 1.1rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 1.4rem;">{item['icon']}</span>
                    <div>
                        <strong style="color: #B97988;">{item['mood']}</strong>
                        <span style="font-size: 0.82rem; color: #4A3B4F; margin-left: 8px;">{item['note']}</span>
                    </div>
                </div>
                <div style="font-size: 0.78rem; color: #B97988; font-weight: 600;">{item['timestamp']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
