"""
LunaCare: Curated Health Topics Explorer
----------------------------------------
Presents curated knowledge cards across core female health categories.
Allows users to explore evidence-based summaries, clinical warning signs,
and launch direct RAG queries into the chatbot.
"""

import streamlit as st
from config import HEALTH_TOPICS
from components.navigation import navigate_to


# Detailed educational content for each topic
TOPIC_DETAILS = {
    "menstrual_health": {
        "title": "Menstrual Health & Cycle Physiology",
        "icon": "🌸",
        "overview": (
            "The menstrual cycle is a vital sign of female endocrine health, typically lasting between 21 and 35 days. "
            "It consists of four distinct phases: the Menstrual Phase (shedding of the uterine lining), "
            "the Follicular Phase (estrogen rise and egg maturation), Ovulation (release of mature egg around mid-cycle), "
            "and the Luteal Phase (progesterone dominance preparing for possible implantation)."
        ),
        "key_facts": [
            "Normal bleeding duration is between 3 to 7 days.",
            "Normal blood loss is approximately 30 to 80 milliliters over the entire period.",
            "Cycle tracking helps identify ovulation windows and detect hormonal irregularities early.",
        ],
        "red_flags": [
            "Periods occurring more frequently than every 21 days or less frequently than every 35 days.",
            "Soaking through one or more sanitary pads/tampons every hour for consecutive hours.",
            "Severe pelvic pain that does not respond to over-the-counter pain relief.",
            "Bleeding after sexual intercourse or post-menopausal bleeding.",
        ],
        "starter_query": "Explain the 4 phases of the menstrual cycle in detail",
    },
    "menstrual_hygiene": {
        "title": "Menstrual Hygiene & Vulvar Care",
        "icon": "🧼",
        "overview": (
            "Practicing safe menstrual hygiene prevents bacterial vaginosis, candidiasis, and urinary tract infections. "
            "Choosing the right products and adhering to clean usage protocols ensures both physical health and everyday comfort."
        ),
        "key_facts": [
            "Sanitary Pads: Change every 4 to 6 hours regardless of flow to prevent bacterial colonization.",
            "Tampons: Change every 4 to 8 hours. Never leave a tampon in for more than 8 hours to avoid Toxic Shock Syndrome (TSS).",
            "Menstrual Cups: Medical-grade silicone cups can be worn up to 12 hours. Sterilize in boiling water between cycles.",
            "Vulvar Care: The vagina has a self-regulating acidic microbiome (pH 3.8-4.5) maintained by Lactobacillus. Use warm water only.",
        ],
        "red_flags": [
            "Sudden high fever, vomiting, diarrhea, or a sunburn-like rash while using tampons (seek immediate emergency care).",
            "Foul-smelling discharge or persistent vulvar burning and itching.",
        ],
        "starter_query": "What are the safest menstrual hygiene practices?",
    },
    "pcos": {
        "title": "PCOS & Metabolic Wellness",
        "icon": "🦋",
        "overview": (
            "Polycystic Ovary Syndrome (PCOS) is one of the most common endocrine disorders in women of reproductive age. "
            "It is closely linked to insulin resistance and an overproduction of androgens from the ovaries and adrenal glands."
        ),
        "key_facts": [
            "Affects an estimated 8% to 13% of women worldwide.",
            "Diagnosed through the Rotterdam criteria requiring at least 2 of 3 features: irregular cycles, androgen excess, or polycystic ovaries on ultrasound.",
            "Insulin resistance affects up to 70% of women with PCOS regardless of body mass index.",
            "Nutritional approaches focusing on fiber, lean proteins, and complex carbohydrates improve insulin sensitivity.",
        ],
        "red_flags": [
            "Absence of periods for more than 3 to 4 months (amenorrhea).",
            "Rapid onset of severe acne or sudden excess facial and body hair growth.",
            "Unexplained rapid weight gain and extreme lethargy.",
        ],
        "starter_query": "What are common symptoms and management strategies for PCOS?",
    },
    "reproductive_health": {
        "title": "Reproductive Anatomy & Preventive Care",
        "icon": "🌿",
        "overview": (
            "Understanding the reproductive tract (cervix, uterus, fallopian tubes, ovaries) and vulvar anatomy enables proactive self-advocacy. "
            "Routine screenings such as Pap smears and HPV tests are crucial for cervical health."
        ),
        "key_facts": [
            "Cervical Cancer Screening: Routine Pap smear and HPV screening is recommended beginning at age 21.",
            "Pelvic Floor Health: Pelvic floor muscles support the bladder, uterus, and bowel, and can be strengthened with targeted physical therapy.",
            "Annual Wellness Checks: Provide an opportunity to review contraceptive options, fertility goals, and breast health.",
        ],
        "red_flags": [
            "Unusual pelvic pressure or a feeling of heaviness in the lower pelvis.",
            "Pain during urination or painful intercourse (dyspareunia).",
            "Any palpable lumps in the breast or axillary lymph nodes.",
        ],
        "starter_query": "What preventive screenings are recommended for women's reproductive health?",
    },
    "pregnancy_basics": {
        "title": "Pregnancy Foundations & Prenatal Care",
        "icon": "🌱",
        "overview": (
            "A healthy pregnancy starts with preconception wellness and comprehensive prenatal support. "
            "Monitoring embryonic and fetal development, optimal nutrition, and recognizing warning signs ensures the safety of parent and child."
        ),
        "key_facts": [
            "Folic Acid: Daily supplementation of 400 mcg of folic acid before and during early pregnancy significantly reduces neural tube defects.",
            "First Trimester: Crucial period of organogenesis from weeks 1 to 12.",
            "Hydration & Nutrition: Adequate protein, iron, and iodine are essential for placental and fetal brain development.",
        ],
        "red_flags": [
            "Any vaginal bleeding or spotting during pregnancy.",
            "Severe abdominal cramping or unilateral sharp pelvic pain.",
            "Persistent vomiting preventing fluid retention (hyperemesis gravidarum).",
            "Sudden swelling of face/hands or sudden visual disturbances.",
        ],
        "starter_query": "What are essential first-trimester nutrition tips and prenatal vitamins?",
    },
    "mental_wellness": {
        "title": "Women's Mental Wellness & Hormones",
        "icon": "🧠",
        "overview": (
            "Fluctuations in estrogen and progesterone directly influence neurotransmitters like serotonin, dopamine, and GABA. "
            "Conditions such as Premenstrual Dysphoric Disorder (PMDD) and postpartum depression are biological, treatable endocrine-psychological conditions."
        ),
        "key_facts": [
            "PMS affects up to 75% of menstruating women; PMDD is a severe, debilitating subtype affecting 3% to 8%.",
            "Chronic elevated cortisol disrupts hypothalamic-pituitary-gonadal (HPG) axis communication, often causing missed periods.",
            "Mindfulness, sleep hygiene, and evidence-based psychotherapy (such as CBT) provide clinically validated emotional benefits.",
        ],
        "red_flags": [
            "Overwhelming feelings of hopelessness, severe panic attacks, or thoughts of self-harm.",
            "Inability to carry out daily self-care or responsibilities during the premenstrual phase.",
        ],
        "starter_query": "How do menstrual hormonal shifts affect mood and anxiety?",
    },
    "general_womens_health": {
        "title": "General Health, Nutrition & Longevity",
        "icon": "✨",
        "overview": (
            "Women's physiology has unique requirements across bone density, cardiovascular health, iron metabolism, and thyroid function. "
            "Preventive lifestyle interventions promote vitality across all life stages."
        ),
        "key_facts": [
            "Iron Metabolism: Blood loss through menstruation increases iron deficiency risks. Ferritin testing helps detect latent deficiency.",
            "Bone Density: Peak bone mass is achieved in early adulthood; weight-bearing exercises, calcium, and Vitamin D3 maintain bone integrity.",
            "Cardiovascular Wellness: Heart disease is a leading cause of mortality in women, often presenting with subtle symptoms like fatigue and shortness of breath.",
        ],
        "red_flags": [
            "Extreme chronic fatigue, cold intolerance, and brittle nails (possible thyroid or iron deficiency).",
            "Unexplained shortness of breath with mild exertion.",
        ],
        "starter_query": "What are optimal nutrition and exercise tips for long-term female health?",
    },
}


def render_health_topics_page():
    """Renders the interactive Health Topics library."""
    st.markdown(
        """
        <div style="margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.8rem;">📚</span>
                <h1 style="margin: 0; font-size: 1.8rem; color: #B97988;">Curated Health Topics</h1>
            </div>
            <p style="color: #4A3B4F; font-size: 0.95rem; margin-top: 4px;">
                Evidence-informed guides on female anatomy, endocrine wellness, hygiene, and nutrition.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Search & Filter
    search_term = st.text_input("🔍 Filter topics by keyword...", placeholder="e.g. PCOS, hygiene, pregnancy, cramps")

    filtered_topics = HEALTH_TOPICS
    if search_term:
        filtered_topics = [
            t for t in HEALTH_TOPICS 
            if search_term.lower() in t["title"].lower() or search_term.lower() in t["summary"].lower()
        ]

    # Render Grid of Cards
    cols = st.columns(2)
    for idx, topic in enumerate(filtered_topics):
        col = cols[idx % 2]
        with col:
            detail = TOPIC_DETAILS.get(topic["id"], {})
            with st.expander(f"{topic['icon']} {topic['title']} — ({topic['badge']})", expanded=(idx == 0)):
                st.markdown(f"<p style='font-size: 0.95rem; line-height: 1.6;'>{detail.get('overview', topic['summary'])}</p>", unsafe_allow_html=True)
                
                st.markdown("**Key Health Facts:**")
                for fact in detail.get("key_facts", []):
                    st.markdown(f"- {fact}")
                
                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
                st.markdown("<strong style='color: #E0876A;'>When to Consult a Physician (Red Flags):</strong>", unsafe_allow_html=True)
                for flag in detail.get("red_flags", []):
                    st.markdown(f"- ⚠️ *{flag}*")

                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                btn_col1, btn_col2 = st.columns([1, 1])
                with btn_col1:
                    if st.button(f"💬 Ask AI about {topic['title']}", key=f"topic_ask_{topic['id']}", use_container_width=True):
                        if "chat_history" not in st.session_state:
                            st.session_state.chat_history = []
                        starter = detail.get("starter_query", f"Tell me more about {topic['title']}")
                        # Navigate to chat with pre-selected query
                        st.session_state.chat_history.append({"role": "user", "content": starter})
                        navigate_to("chat")
