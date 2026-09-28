"""
LunaCare: Centralized Configuration Module
------------------------------------------
This module centralizes all system paths, brand styling tokens,
AI model defaults, health topic definitions, and medical safety notices.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# ==========================================
# 1. Project Directory Paths
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
VECTOR_STORE_DIR = BASE_DIR / "vector_store"
STYLES_DIR = BASE_DIR / "styles"

# Ensure runtime directories exist
KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
STYLES_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. Application Branding & Identity
# ==========================================
APP_NAME = "LunaCare"
APP_TAGLINE = "Your space for better-informed health decisions."
APP_SUBTITLE = "An AI-powered, RAG-based female health and wellness educational companion."
APP_VERSION = "1.0.0 (Educational Edition)"

# Brand Color Palette (HSL & Hex references)
COLORS = {
    "bg_main": "#F8DDE3",         # Soft light pink main background
    "bg_card": "#FFF8FB",         # Subtle pink-tinted white
    "primary_rose": "#B97988",    # Muted rose primary
    "rose_hover": "#A86474",      # Primary button hover
    "secondary_rose": "#D9AEB8",  # Soft rose secondary accent
    "surface_accent": "#F1E2E6",  # Light surface accent
    "charcoal": "#4A3B4F",        # Soft dark neutral/purple text
    "slate_muted": "#6B5B70",     # Secondary body text
    "border": "#E7C9D0",          # Soft delicate rose border
    "accent_warning": "#E0876A",  # Soft terracotta for alerts
}

# ==========================================
# 3. Medical Safety & Educational Notice
# ==========================================
MEDICAL_DISCLAIMER = (
    "LunaCare provides general health and wellness information for educational purposes only. "
    "It is not a substitute for professional medical advice, clinical diagnosis, or treatment. "
    "Always consult a qualified healthcare provider with any questions you may have regarding a medical condition. "
    "If you think you may have a medical emergency, please call your local emergency services immediately."
)

# ==========================================
# 4. LLM & Embedding Configuration (Phase 2 & Phase 3)
# ==========================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3.6-flash")

# Generation Parameters:
# TEMPERATURE: Controls output randomness (0.0 = deterministic/focused, 1.0 = creative).
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))

# MAX_OUTPUT_TOKENS: Maximum length budget for generated assistant responses.
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "1024"))

# Phase 3 RAG & Embedding Parameters:
# Official Google embedding model for multimodal and textual embeddings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")
EMBEDDING_DIMENSIONALITY = int(os.getenv("EMBEDDING_DIMENSIONALITY", "3072"))

# Text chunking settings for PDF ingestion
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# Vector database retrieval settings
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "4"))
CHROMA_COLLECTION_NAME = "lunacare_health"

# Distance threshold: Cosine distance in Chroma (0.0 = identical, 1.0+ = distant).
# If the lowest distance for a query exceeds this threshold, the context is considered insufficient.
SIMILARITY_DISTANCE_THRESHOLD = float(os.getenv("SIMILARITY_DISTANCE_THRESHOLD", "0.70"))

# Phase 4 Conversational Memory Settings:
# MEMORY_WINDOW: Maximum number of recent conversational messages (user + assistant turns)
# sent to Gemini as context, strictly excluding the initial greeting.
# For example, MEMORY_WINDOW = 8 retains up to the 8 most recent user/assistant turns (4 exchanges),
# preventing token bloat while supporting natural follow-up understanding.
MEMORY_WINDOW = int(os.getenv("MEMORY_WINDOW", "8"))

# Phase 5 Tools / Menstrual Cycle Calculator Settings:
# The 20-45 day range is strictly an application input validation constraint
# (not a medically defined physiological limit) used to prevent erroneous date inputs.
DEFAULT_CYCLE_LENGTH = 28
MIN_CYCLE_LENGTH = 20
MAX_CYCLE_LENGTH = 45

# ==========================================
# 5. Suggested Starter Questions
# ==========================================
SUGGESTED_QUESTIONS = [
    "What causes menstrual cramps?",
    "What are common symptoms associated with PCOS?",
    "What are some ways to maintain menstrual hygiene?",
    "What can I do to manage stress and hormonal balance?",
    "When should I consult a healthcare professional about unusual menstrual symptoms?",
]

# ==========================================
# 6. Curated Health Topic Definitions
# ==========================================
HEALTH_TOPICS = [
    {
        "id": "menstrual_health",
        "title": "Menstrual Health",
        "icon": "🌸",
        "summary": "Understanding cycle phases, flow variations, normal physiology, and cramp management.",
        "badge": "Core Health",
    },
    {
        "id": "menstrual_hygiene",
        "title": "Menstrual Hygiene",
        "icon": "🧼",
        "summary": "Safe hygiene practices, product selection (pads, cups, tampons), and infection prevention.",
        "badge": "Hygiene & Care",
    },
    {
        "id": "pcos",
        "title": "PCOS & Hormonal Balance",
        "icon": "🦋",
        "summary": "Polycystic Ovary Syndrome symptoms, metabolic factors, lifestyle guidance, and clinical checkups.",
        "badge": "Hormones",
    },
    {
        "id": "reproductive_health",
        "title": "Reproductive Anatomy & Health",
        "icon": "🌿",
        "summary": "Reproductive anatomy, routine pelvic exams, cervical health, and preventive wellness checks.",
        "badge": "Wellness",
    },
    {
        "id": "pregnancy_basics",
        "title": "Pregnancy Basics",
        "icon": "🌱",
        "summary": "First-trimester milestones, nutrition fundamentals, prenatal vitamins, and warning signs.",
        "badge": "Maternal",
    },
    {
        "id": "mental_wellness",
        "title": "Women's Mental Wellness",
        "icon": "🧠",
        "summary": "Navigating PMS/PMDD mood shifts, chronic stress, sleep hygiene, and emotional resilience.",
        "badge": "Mental Health",
    },
    {
        "id": "general_womens_health",
        "title": "General Health & Nutrition",
        "icon": "✨",
        "summary": "Bone density, iron levels, cardiovascular health, and age-specific preventive care.",
        "badge": "Preventive",
    },
]
def get_api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "").strip()