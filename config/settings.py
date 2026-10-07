import os
from dotenv import load_dotenv

load_dotenv()


# =========================
# Groq
# =========================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
    "deepseek-r1-distill-llama-70b",
]

DEFAULT_MODEL = GROQ_MODELS[0]

DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.7


# =========================
# Base de datos
# =========================

DB_FILE = "data/chat_history.db"