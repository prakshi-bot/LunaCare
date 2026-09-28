"""
LunaCare: Menstrual Cycle Calculator & Tracker
----------------------------------------------
Provides an educational cycle projection based on user inputs:
- Date of last period
- Average cycle length
Calculates estimated next period, luteal phase timing, and estimated fertile window.
Explicitly highlights normal biological variance and non-certainty.
"""

from datetime import date, timedelta
import streamlit as st
from components.cards import render_disclaimer_banner


def render_cycle_page():
    """Renders the Menstrual Cycle Calculator page."""
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.8rem;">🌸</span>
                <h1 style="margin: 0; font-size: 1.8rem; color: #B97988;">Cycle Calculator</h1>
            </div>
            <p style="color: #4A3B4F; font-size: 0.95rem; margin-top: 4px;">
                Track cycle rhythms and calculate estimated dates for your next period and follicular transitions.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_disclaimer_banner(
        "Menstrual cycle predictions are biological estimates. Cycles can naturally fluctuate due to stress, "
        "illness, travel, hormonal shifts, and lifestyle changes. Never use calendar calculations as a reliable method of contraception."
    )

    c1, c2 = st.columns([5, 6])

    with c1:
        st.markdown("<h3 style='font-size: 1.2rem; color: #B97988;'>Enter Your Cycle Details</h3>", unsafe_allow_html=True)
        
        last_period_date = st.date_input(
            "First day of your last period:",
            value=date.today() - timedelta(days=14),
            max_value=date.today(),
            help="Select the first day you experienced full menstrual bleeding (not light spotting).",
        )

        cycle_length = st.slider(
            "Average cycle length (days):",
            min_value=21,
            max_value=45,
            value=28,
            help="Typical menstrual cycles range from 21 to 35 days (28 days is the clinical average).",
        )

        period_duration = st.slider(
            "Average period duration (days):",
            min_value=2,
            max_value=10,
            value=5,
            help="Normal flow lasts between 3 and 7 days.",
        )

        calc_clicked = st.button("✨ Calculate Cycle Projections", use_container_width=True, type="primary")

    with c2:
        st.markdown("<h3 style='font-size: 1.2rem; color: #B97988;'>Estimated Projections</h3>", unsafe_allow_html=True)

        if not calc_clicked and "cycle_calculated" not in st.session_state:
            st.info("👈 Enter your dates on the left and click 'Calculate Cycle Projections' to see your estimates.")
        else:
            st.session_state.cycle_calculated = True

            # Use shared deterministic calculation logic from tools.cycle_calculator
            from tools.cycle_calculator import compute_cycle_projections
            projections = compute_cycle_projections(last_period_date, cycle_length)

            next_period = projections["next_period_date"]
            estimated_ovulation = projections["estimated_ovulation_date"]
            fertile_window_start = projections["fertile_window_start"]
            fertile_window_end = projections["fertile_window_end"]

            # Days remaining until next period
            days_until = (next_period - date.today()).days

            st.markdown(
                f"""
                <div class="luna-card" style="border: 2px solid #E7C9D0; background: linear-gradient(135deg, #FFF8FB 0%, #F1E2E6 100%);">
                    <div style="font-size: 0.82rem; font-weight: 700; color: #B97988; text-transform: uppercase; letter-spacing: 0.08em;">
                        Next Expected Menstruation
                    </div>
                    <div style="font-size: 2rem; font-weight: 800; color: #B97988; margin-4px 0;">
                        {next_period.strftime('%A, %B %d, %Y')}
                    </div>
                    <div style="font-size: 0.95rem; color: {'#B97988' if days_until >= 0 else '#E0876A'}; font-weight: 600;">
                        {f'Approx. {days_until} days from today' if days_until > 0 else ('Expected today!' if days_until == 0 else f'Passed by {-days_until} days')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

            m_col1, m_col2 = st.columns(2)
            with m_col1:
                st.markdown(
                    f"""
                    <div class="luna-card">
                        <div style="font-size: 1.4rem;">🥚</div>
                        <div style="font-size: 0.82rem; font-weight: 700; color: #B97988; text-transform: uppercase;">
                            Estimated Ovulation
                        </div>
                        <div style="font-size: 1.15rem; font-weight: 700; color: #B97988; margin-top: 4px;">
                            {estimated_ovulation.strftime('%b %d, %Y')}
                        </div>
                        <div style="font-size: 0.78rem; color: #4A3B4F; margin-top: 2px;">
                            Day {cycle_length - 14} of current cycle
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with m_col2:
                st.markdown(
                    f"""
                    <div class="luna-card">
                        <div style="font-size: 1.4rem;">🌱</div>
                        <div style="font-size: 0.82rem; font-weight: 700; color: #B97988; text-transform: uppercase;">
                            Estimated Fertile Window
                        </div>
                        <div style="font-size: 1.15rem; font-weight: 700; color: #B97988; margin-top: 4px;">
                            {fertile_window_start.strftime('%b %d')} – {fertile_window_end.strftime('%b %d')}
                        </div>
                        <div style="font-size: 0.78rem; color: #4A3B4F; margin-top: 2px;">
                            Based on sperm viability & egg lifespan
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                """
                <div style="font-size: 0.82rem; color: #4A3B4F; line-height: 1.5; margin-top: 1rem; padding: 0.8rem; background: #FFF8FB; border-radius: 8px; border: 1px solid #E7C9D0;">
                    <strong style="color: #B97988;">Notice:</strong> Ovulation varies even in regular cycles. These estimations are based on standard physiological averages and are intended for awareness and cycle self-knowledge only.
                </div>
                """,
                unsafe_allow_html=True,
            )
