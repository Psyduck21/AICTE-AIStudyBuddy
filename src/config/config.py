"""
Configuration file for AI Study Buddy Pro
Customize settings here without modifying core code
"""
import os
from typing import Dict, Any

# --- PDF Processing ---
MAX_CHUNK_TOKENS = 400  # Size of text chunks for embedding
MAX_PDF_SIZE_MB = 50    # Maximum PDF file size
OVERLAP_TOKENS = 50     # Token overlap between chunks (for context)

# --- Vector Database ---
VECTOR_STORE_FILE = "vector_store.pkl"
TOP_K_RETRIEVAL = 5     # Number of chunks to retrieve per query
SIMILARITY_THRESHOLD = 0.5  # Minimum similarity score for results

# --- LLM Settings ---
LLM_MODEL = "models/gemini-2.5-flash-lite"
EMBEDDING_MODEL = "models/gemini-embedding-001"
TEMPERATURE = 0.7       # Creativity level (0-1)
MAX_OUTPUT_TOKENS = 2048

# --- Quiz Settings ---
DEFAULT_QUIZ_QUESTIONS = 5
MIN_QUIZ_QUESTIONS = 1
MAX_QUIZ_QUESTIONS = 20
QUIZ_DIFFICULTIES = ["Easy", "Medium", "Hard", "Mixed"]
QUIZ_TIME_LIMIT_MINUTES = None  # None = No time limit

# --- Flashcard Settings ---
DEFAULT_FLASHCARDS = 5
MIN_FLASHCARDS = 1
MAX_FLASHCARDS = 50
FLASHCARD_REVIEW_THRESHOLD = 3  # Days before suggesting review

# --- UI Settings ---
PAGE_TITLE = "📘 AI Study Buddy Pro"
PAGE_ICON = "📘"
LAYOUT = "wide" 
THEME = "system"  # "light", "dark", or "system" to use OS preference

# --- Difficulty Levels ---
DIFFICULTY_LEVELS = {
    "ELI5 (Very Simple)": "Explain as if explaining to a 5-year-old. Use simple words and everyday analogies.",
    "High School": "Provide a clear explanation suitable for high school level understanding.",
    "College": "Provide a detailed college-level explanation with technical terms.",
    "Advanced": "Provide an advanced, in-depth explanation with nuanced details and advanced concepts."
}

# --- Explanation Types ---
EXPLANATION_TYPES = {
    "Explanation": "Provide a comprehensive explanation.",
    "Analogy": "Use relatable analogies and metaphors to explain.",
    "Step-by-Step": "Break down the concept into clear, numbered steps."
}

# --- File Storage ---
SAMPLE_DOCS_DIR = os.path.join("data", "sample_docs")
TEMP_DIR = os.path.join("data", "temp")
UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB chunks

# --- API Settings ---
API_TIMEOUT = 30  # Seconds
MAX_RETRIES = 3
RATE_LIMIT_REQUESTS_PER_MINUTE = 60

# --- Performance ---
CACHE_EMBEDDINGS = True
CACHE_QUIZ_GENERATIONS = False
BATCH_EMBEDDING_SIZE = 10

# --- Feature Flags ---
ENABLE_QUIZ_MODE = True
ENABLE_FLASHCARDS = True
ENABLE_CONCEPT_EXPLORER = True
ENABLE_PROGRESS_DASHBOARD = True
ENABLE_AUDIO_EXPLANATIONS = False  # Coming soon
ENABLE_EXPORT_ANKI = False  # Coming soon
ENABLE_SPACED_REPETITION = False  # Coming soon

# --- Prompt Templates ---
SYSTEM_PROMPT = """You are an expert educator and tutor with deep knowledge across all subjects.
Your role is to help students understand complex concepts in simple, engaging ways.
Always provide accurate, well-structured explanations.
Cite your sources when referencing specific documents.
Be encouraging and supportive in your responses."""

QUIZ_SYSTEM_PROMPT = """You are an expert quiz designer creating educational assessments.
Generate clear, unambiguous multiple-choice questions that test understanding.
Ensure options are plausible but clearly distinguished.
Provide helpful explanations for why answers are correct or incorrect."""

FLASHCARD_SYSTEM_PROMPT = """You are an expert in creating study materials.
Extract the most important Q&A pairs that capture key concepts.
Make questions specific and answers concise but complete.
Focus on testable knowledge that students need to master."""

# --- Logging ---
ENABLE_LOGGING = True
LOG_FILE = "app.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# --- Analytics (Future)---
TRACK_USER_PROGRESS = True
ANONYMOUS_ANALYTICS = True
SAVE_SESSION_DATA = False

# --- Customization ---
APP_COLOR_PRIMARY = "#1f77b4"
APP_COLOR_SUCCESS = "#2ca02c"
APP_COLOR_WARNING = "#ff7f0e"
APP_COLOR_ERROR = "#d62728"

def validate_config() -> bool:
    """
    Validate configuration values.
    
    Returns:
        bool: True if configuration is valid
    """
    try:
        assert MAX_CHUNK_TOKENS > 0, "MAX_CHUNK_TOKENS must be positive"
        assert TOP_K_RETRIEVAL > 0, "TOP_K_RETRIEVAL must be positive"
        assert 0 <= TEMPERATURE <= 1, "TEMPERATURE must be between 0 and 1"
        assert 0 <= SIMILARITY_THRESHOLD <= 1, "SIMILARITY_THRESHOLD must be between 0 and 1"
        assert MIN_QUIZ_QUESTIONS <= DEFAULT_QUIZ_QUESTIONS <= MAX_QUIZ_QUESTIONS
        assert MIN_FLASHCARDS <= DEFAULT_FLASHCARDS <= MAX_FLASHCARDS
        
        # Create necessary directories
        os.makedirs(SAMPLE_DOCS_DIR, exist_ok=True)
        os.makedirs(TEMP_DIR, exist_ok=True)
        
        return True
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False

def get_config_dict() -> Dict[str, Any]:
    """
    Return all configuration as a dictionary.
    
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    import sys
    current_module = sys.modules[__name__]
    config = {}
    for item in dir(current_module):
        if not item.startswith('_') and item.isupper():
            config[item] = getattr(current_module, item)
    return config