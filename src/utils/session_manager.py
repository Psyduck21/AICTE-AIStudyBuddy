"""Session state management for AI Study Buddy Pro"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set

import streamlit as st
from ..config import get_config_dict
from ..utils.logger import logger
from ..utils.study_utils import update_study_stats, get_learning_progress

config = get_config_dict()
SESSION_FILE = os.path.join("data", "session_data.json")

def initialize_session_state():
    """Initialize or reset session state with default values"""
    defaults = {
        # Core navigation
        "mode": "📖 Learn",
        "current_topic": None,
        
        # Study content
        "flashcards": [],  # Current flashcard deck
        "card_index": 0,  # Current position in flashcard deck
        "marked_cards": set(),  # Cards marked for review
        "show_answer": False,  # Whether to show flashcard answer
        "quiz_history": [],  # List of past quiz attempts with scores and feedback
        "current_quiz": None,  # Current active quiz questions
        "quiz_answers": {},  # User's answers for current quiz
        
        # Progress tracking
        "study_stats": {
            "start_time": datetime.now().isoformat(),
            "study_sessions": [],
            "total_time": 0,
            "session_count": 0,
            "current_streak": 0,
            "max_streak": 0,
            "last_study_session": None
        },
        "topics_mastered": set(),
        
        # User interaction
        "last_question": "",
        "chat_history": [],
        "interaction_log": [],  # Track user actions and app state changes
        
        # Settings
        "ui_preferences": {
            "theme": "system",  # "light", "dark", or "system" (default)
            "font_size": "medium",  # Always lowercase
            "animations": True,
            "sidebar_expanded": True
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def save_session_state() -> bool:
    """Save current session state to file"""
    if not config["SAVE_SESSION_DATA"]:
        return False
    
    try:
        os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
        
        # Convert set to list for JSON serialization
        topics_mastered = list(st.session_state.get("topics_mastered", set()))
        
        session_data = {
            # Study stats
            "study_stats": st.session_state.get("study_stats", {}),
            "topics_mastered": topics_mastered,
            
            # Quiz and flashcard states
            "quiz_history": st.session_state.get("quiz_history", []),  # List of past quiz attempts
            "flashcards": st.session_state.get("flashcards", []),
            "card_index": st.session_state.get("card_index", 0),
            "marked_cards": list(st.session_state.get("marked_cards", set())),
            "show_answer": st.session_state.get("show_answer", False),
            "current_quiz": st.session_state.get("current_quiz", None),
            "quiz_answers": st.session_state.get("quiz_answers", {}),
            
            # Chat and interaction history
            "chat_history": st.session_state.get("chat_history", []),
            "last_question": st.session_state.get("last_question", ""),
            "interaction_log": st.session_state.get("interaction_log", [])[-100:],  # Keep last 100 interactions
            
            # UI states
            "mode": st.session_state.get("mode", "📖 Learn"),
            "current_topic": st.session_state.get("current_topic", None),
            "ui_preferences": st.session_state.get("ui_preferences", {
                "theme": "system",  # "light", "dark", or "system" (default)
                "font_size": "medium",
                "animations": True, 
                "sidebar_expanded": True
            }),
            
            # Timestamp
            "last_updated": datetime.now().isoformat()
        }
        
        with open(SESSION_FILE, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
            
        logger.info("Session state saved successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error saving session state: {e}")
        return False


def load_saved_session() -> None:
    """Load saved session state and update current session"""
    if not config["SAVE_SESSION_DATA"]:
        return
    
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'r') as f:
                data = json.load(f)
            
            # Convert list back to set for topics_mastered
            if "topics_mastered" in data:
                data["topics_mastered"] = set(data["topics_mastered"])
                
            # Update session state with loaded data
            for key, value in data.items():
                if key in st.session_state:
                    st.session_state[key] = value
                    
            logger.info("Session state loaded successfully")
            
    except Exception as e:
        logger.error(f"Error loading session state: {e}")

def update_study_session():
    """Update study statistics for current session"""
    if "session_start" in st.session_state:
        duration = (datetime.now() - datetime.fromisoformat(
            st.session_state.session_start)).seconds
        st.session_state.study_stats = update_study_stats(
            st.session_state.study_stats,
            duration
        )
    st.session_state.session_start = datetime.now().isoformat()

def get_topic_progress() -> Dict[str, float]:
    """Get learning progress for all topics"""
    if not st.session_state.get("quiz_history"):
        return {}
        
    topics = list(st.session_state.quiz_history.keys())
    scores = {topic: [score for _, score in history] 
             for topic, history in st.session_state.quiz_history.items()}
             
    return get_learning_progress(topics, scores)

def update_quiz_history(topic: str, score: float):
    """Update quiz history with new score"""
    if "quiz_history" not in st.session_state:
        st.session_state.quiz_history = {}
        
    if topic not in st.session_state.quiz_history:
        st.session_state.quiz_history[topic] = []
        
    st.session_state.quiz_history[topic].append(
        (datetime.now().isoformat(), score)
    )
    
    # Update mastery status
    recent_scores = [score for _, score in 
                    st.session_state.quiz_history[topic][-3:]]
    if len(recent_scores) >= 3 and all(score >= 0.8 for score in recent_scores):
        if "topics_mastered" not in st.session_state:
            st.session_state.topics_mastered = set()
        st.session_state.topics_mastered.add(topic)

def add_chat_message(role: str, content: str):
    """Add a message to the chat history"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })

def get_chat_history() -> List[Dict[str, str]]:
    """Get the chat history for the current session"""
    return st.session_state.get("chat_history", [])