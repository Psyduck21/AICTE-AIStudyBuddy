"""Main application module for AI Study Buddy Pro - Corrected Version"""

import os
import sys
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.helper import process_pdf
from src.core.vectordb import (
    build_vector_store,
    retrieve,
    load_vector_store,
    check_file_embeddings,
)
from src.core.llm import generate_answer, generate_flashcards, generate_quiz_adaptive
from src.utils.session_manager import save_session_state, load_saved_session, initialize_session_state
from src.config import get_config_dict
from src.utils.logger import logger
from src.utils.utils import (
    truncate_text,
)

# --------------------- PAGE CONFIGURATION ---------------------
config = get_config_dict()
st.set_page_config(
    page_title=config.get("PAGE_TITLE", "AI Study Buddy Pro"),
    page_icon=config.get("PAGE_ICON", "📘"),
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------- INITIALIZATION ---------------------
def init_session():
    """Initialize session state and configuration"""

    # Custom Styling
    st.markdown("""
        <style>
        .main { max-width: 1200px; margin: 0 auto; }
        h1 { color: #1e3d59; font-size: 2.5rem; margin-bottom: 1.5rem; font-weight: 700; }
        h2 { color: #2b4f76; font-size: 1.8rem; margin-top: 2rem; font-weight: 600; }
        .stButton > button {
            background-color: #1e3d59;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #2b4f76;
            transform: translateY(-2px);
        }
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            border: 2px solid #eee;
            border-radius: 8px;
            padding: 0.75rem;
        }
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #1e3d59;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize Session State Defaults
    defaults = {
        "mode": "Learn",
        "current_topic": None,
        "last_question": "",
        "documents": [],
        "flashcards": [],
        "quiz_history": [],
        "current_quiz": None,
        "quiz_answers": {},
        "show_answer": False,
        "current_card_index": 0,
        "marked_cards": set(),
        "notes": [],
        "study_stats": {
            "session_count": 0,
            "total_time": 0,
            "current_streak": 0,
            "topics_mastered": set(),
        },
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    return config

if "flashcards" not in st.session_state:
    st.session_state.flashcards = []
if "current_card_index" not in st.session_state:
    st.session_state.current_card_index = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False
if "marked_cards" not in st.session_state:
    st.session_state.marked_cards = set()
if "quiz_history" not in st.session_state:
    st.session_state.quiz_history = []

# --------------------- MAIN FUNCTION ---------------------
def main():
    """Main application entry point"""
    config = init_session()

    # Sidebar navigation
    with st.sidebar:
        st.title("📘 Study Buddy Pro")

        # Stats Section
        stats = st.session_state.get("study_stats", {})
        if stats and stats.get("session_count", 0) > 0:
            col1, col2 = st.columns(2)
            col1.metric("Sessions", stats["session_count"])
            hours = stats["total_time"] / 3600
            col2.metric("Study Time", f"{hours:.1f}h")

        st.divider()
        st.markdown("### Navigation")
        modes = ["Learn", "Quiz", "Flashcards", "Dashboard", "Explorer"]
        selected = st.radio("Select Mode:", modes, index=modes.index(st.session_state.mode))
        st.session_state.mode = selected

        st.divider()
        if st.button("🧹 Clear Session", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # Main Section Header
    st.title(f"AI Study Buddy Pro - {st.session_state.mode}")
    st.divider()

    # Mode Routing
    mode = st.session_state.mode
    if mode == "Learn":
        learn_mode()
    elif mode == "Quiz":
        quiz_mode()
    elif mode == "Flashcards":
        flashcard_mode()
    elif mode == "Dashboard":
        dashboard_mode()
    elif mode == "Explorer":
        explorer_mode()


# --------------------- LEARN MODE ---------------------
def learn_mode():
    """Learn mode - Upload PDFs and ask questions"""
    st.header("📘 Study Materials & Questions")

    # --- Initialize session state variables ---
    if "last_uploaded_file" not in st.session_state:
        st.session_state["last_uploaded_file"] = None
    if "last_question" not in st.session_state:
        st.session_state["last_question"] = ""

    # --- Section 1: Upload PDF ---
    st.subheader("Upload PDF")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    # If a new file is uploaded
    if uploaded_file:
        try:
            os.makedirs("data/sample_docs", exist_ok=True)
            file_path = f"data/sample_docs/{uploaded_file.name}"

            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            with st.spinner("Processing PDF..."):
                if check_file_embeddings(file_path):
                    st.info("✅ Using cached embeddings")
                else:
                    chunks = process_pdf(file_path)
                    build_vector_store(chunks, source_file=file_path)
                st.success("✅ PDF processed successfully!")

            # Save file path for persistence
            st.session_state["last_uploaded_file"] = file_path

        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            st.error(f"Error: {e}")

    # --- Section 2: If a file is already uploaded (this or previous session) ---
    elif st.session_state["last_uploaded_file"]:
        st.success(f"✅ Loaded previous PDF: {os.path.basename(st.session_state['last_uploaded_file'])}")

    else:
        st.info("📄 Please upload a PDF to start learning.")

    # --- Section 3: Ask Questions (only show if a PDF exists) ---
    if st.session_state["last_uploaded_file"]:
        st.markdown("---")
        st.subheader("Ask Questions")

        question = st.text_input(
            "What would you like to know?",
            value=st.session_state.get("last_question", ""),
            placeholder="Ask about your uploaded materials...",
        )

        if question and st.button("Get Answer", use_container_width=True, type="primary"):
            st.session_state["last_question"] = question

            try:
                with st.spinner("Finding answer..."):
                    context = retrieve(question)
                    if not context:
                        st.warning("⚠️ No relevant content found in the uploaded PDF.")
                        return

                    # Generate and show the answer
                    answer = generate_answer(question, context)
                    st.markdown("### 🧠 Answer:")
                    st.write(answer)

                    # Expandable section for references
                    with st.expander("📚 View Sources"):
                        for i, c in enumerate(context, 1):
                            st.write(f"**Source {i}:** {c.get('source', 'Unknown')}")
                            st.caption(truncate_text(c.get('text', ''), 200))

            except Exception as e:
                logger.error(f"Question error: {e}")
                st.error(f"Error: {e}")


# --------------------- QUIZ MODE ---------------------
def quiz_mode():
    """Quiz mode - Test knowledge"""
    st.header("🧩 Quiz Master")

    index, chunks = load_vector_store() or (None, None)
    if not chunks:
        st.warning("⚠️ No study materials found. Please upload a PDF first.")
        return

    if st.session_state.current_quiz is None:
        st.subheader("Configure Quiz")
        num_questions = st.slider("Number of Questions", 1, 20, 5)
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"])
        topic = st.text_input("Topic (optional)", placeholder="Leave empty for general quiz")

        if st.button("Generate Quiz", use_container_width=True, type="primary"):
            try:
                with st.spinner("Creating quiz..."):
                    context = retrieve(topic) if topic else chunks[:num_questions * 2]
                    quiz = generate_quiz_adaptive(
                        context=context,
                        num_questions=num_questions,
                        difficulty=difficulty,
                        quiz_history=st.session_state.quiz_history,
                    )
                    if quiz:
                        st.session_state.current_quiz = quiz
                        st.session_state.quiz_answers = {}
                        st.rerun()
                    else:
                        st.error("⚠️ Quiz generation failed.")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        render_quiz()


def render_quiz():
    """Display and handle quiz logic"""
    quiz = st.session_state.current_quiz
    print(quiz)
    total = len(quiz)
    st.subheader(f"Quiz Progress: {len(st.session_state.quiz_answers)}/{total}")
    st.progress(len(st.session_state.quiz_answers) / total)
    for i, q in enumerate(quiz):
        print(q)
        st.markdown(f"### Q{i + 1}: {q.get('question', 'Question unavailable')}")
        options = q.get("options", [])
        # print(options)
        if not options:
            continue

        if i not in st.session_state.quiz_answers:
            answer = st.radio("Select:", options, key=f"q_{i}", label_visibility="collapsed")
            if st.button("Submit", key=f"submit_{i}"):
                st.session_state.quiz_answers[i] = answer
                st.rerun()
        else:
            st.info(f"Your answer: {st.session_state.quiz_answers[i]}")
        st.divider()

    if len(st.session_state.quiz_answers) == total:
        if st.button("Submit Quiz", type="primary", use_container_width=True):
            evaluate_quiz(quiz)

def evaluate_quiz(quiz):
    """Evaluate quiz results"""
    score = 0
    feedback = []
    for i, q in enumerate(quiz):
        user_answer = st.session_state.quiz_answers.get(i, "")
        correct = q.get("correct") or q.get("answer", "")
        is_correct = user_answer.lower() == str(correct).lower()
        score += int(is_correct)
        feedback.append({
            "question": q.get("question", ""),
            "user_answer": user_answer,
            "correct_answer": correct,
            "is_correct": is_correct,
        })

    st.session_state.quiz_history.append({
        "timestamp": datetime.now(),
        "score": score,
        "total": len(quiz),
        "feedback": feedback,
    })

    pct = (score / len(quiz)) * 100
    st.success(f"✅ Score: {score}/{len(quiz)} ({pct:.1f}%)")

    st.subheader("📝 Quiz Feedback")

    for fb in feedback:
        st.markdown("---")  # separator between questions
        st.markdown(f"**Question:** {fb['question']}")
        
        if fb["is_correct"]:
            st.success(f"✔️ Correct! Your answer: {fb['user_answer']}")
        else:
            st.error(f"❌ Incorrect")
            st.markdown(f"- **Your answer:** {fb['user_answer']}")
            st.markdown(f"- **Correct answer:** {fb['correct_answer']}")
        
        # Optional: show explanation if available
        if fb.get("explanation"):
            st.info(f"💡 Explanation: {fb['explanation']}")


    if st.button("Try Again"):
        st.session_state.current_quiz = None
        st.session_state.quiz_answers = {}
        st.rerun()


# --------------------- FLASHCARD MODE ---------------------
def flashcard_mode():
    """Flashcard review mode"""
    st.header("🃏 Flashcards")

    # Check if flashcards exist in session
    if not st.session_state.flashcards:
        st.subheader("Create Flashcard Set")

        topic = st.text_input(
            "Enter topic",
            placeholder="e.g., Data Structures, Biology, etc."
        )
        num_cards = st.slider("Number of cards", 5, 20, 10)

        if topic and st.button("Generate Flashcards", type="primary", use_container_width=True):
            try:
                with st.spinner("Creating flashcards..."):
                    context = retrieve(topic)
                    if context:
                        cards = generate_flashcards(topic, context)
                        formatted = []
                        for card in cards:
                            formatted.append({
                                "front": card.get("question", card.get("front", "")),
                                "back": card.get("answer", card.get("back", "")),
                                "mastered": False
                            })
                        st.session_state.flashcards = formatted
                        st.session_state.current_card_index = 0
                        st.rerun()
                    else:
                        st.error("No content found")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    else:
        # Study mode
        total = len(st.session_state.flashcards)
        idx = st.session_state.current_card_index
        card = st.session_state.flashcards[idx]

        # Progress tracking
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Card", f"{idx + 1}/{total}")
        with col2:
            st.metric("Mastered", len(st.session_state.marked_cards))
        with col3:
            st.metric("Remaining", total - len(st.session_state.marked_cards))

        st.progress((idx + 1) / total)

        # Flashcard content
        st.markdown("---")
        st.subheader("Question:")
        st.info(card["front"])

        if st.session_state.show_answer:
            st.subheader("Answer:")
            st.success(card["back"])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Got It!", use_container_width=True):
                st.session_state.marked_cards.add(idx)
                if idx < total - 1:
                    st.session_state.current_card_index += 1
                st.session_state.show_answer = False
                st.rerun()

        with col2:
            if st.button("Review Later", use_container_width=True):
                if idx < total - 1:
                    st.session_state.current_card_index += 1
                st.session_state.show_answer = False
                st.rerun()

        if not st.session_state.show_answer:
            if st.button("Show Answer", type="primary", use_container_width=True):
                st.session_state.show_answer = True
                st.rerun()

        # Navigation buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            if idx > 0 and st.button("Previous"):
                st.session_state.current_card_index -= 1
                st.session_state.show_answer = False
                st.rerun()

        with col2:
            if st.button("New Set", use_container_width=True):
                st.session_state.flashcards = []
                st.session_state.current_card_index = 0
                st.session_state.show_answer = False
                st.rerun()

        with col3:
            if idx < total - 1 and st.button("Next"):
                st.session_state.current_card_index += 1
                st.session_state.show_answer = False
                st.rerun()


# --------------------- DASHBOARD MODE ---------------------
def dashboard_mode():
    """Dashboard mode for tracking progress"""
    st.header("📊 Your Progress")
    if not st.session_state.quiz_history:
        st.info("Take some quizzes to see your progress!")
        return

    scores = [q["score"] / q["total"] * 100 for q in st.session_state.quiz_history]
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Quizzes", len(scores))
    col2.metric("Average Score", f"{sum(scores) / len(scores):.1f}%")
    col3.metric("Best Score", f"{max(scores):.1f}%")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[q["timestamp"] for q in st.session_state.quiz_history],
        y=scores,
        mode="lines+markers",
        name="Scores",
    ))
    fig.update_layout(title="Score Progress", xaxis_title="Date", yaxis_title="Score (%)")
    st.plotly_chart(fig, use_container_width=True)


# --------------------- EXPLORER MODE ---------------------
def explorer_mode():
    """Explore concepts in uploaded material"""
    st.header("🔍 Concept Explorer")
    query = st.text_input("Search for a concept:")
    if query:
        try:
            with st.spinner("Searching..."):
                results = retrieve(query, top_k=5)
                if not results:
                    st.warning("No results found.")
                    return
                for i, r in enumerate(results, 1):
                    with st.expander(f"Result {i}"):
                        st.write(r.get("text", "No text"))
                        st.caption(f"Source: {r.get('source', 'Unknown')}")
        except Exception as e:
            st.error(f"Error: {e}")


# --------------------- ENTRY POINT ---------------------
if __name__ == "__main__":
    main()
