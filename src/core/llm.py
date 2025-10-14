"""LLM operations for AI Study Buddy Pro"""
import os
import re
import json
import random
import google.generativeai as genai
from typing import List, Dict, Optional

from ..config import get_config_dict
from ..utils.logger import logger

config = get_config_dict()
API_KEY = os.getenv("GEMINI_API_KEY")
MAX_CHUNK_TOKENS = config["MAX_CHUNK_TOKENS"]
LLM_MODEL = config["LLM_MODEL"]
TEMPERATURE = config["TEMPERATURE"]

def generate_answer(
    query: str,
    retrieved_chunks: List[Dict],
    quiz: bool = False,
    detail: str = "College",
    explanation_type: str = "Explanation"
) -> str:
    """
    Generate contextual answers with different difficulty levels and explanation types.
    
    Args:
        query: User's question
        retrieved_chunks: List of relevant text chunks
        quiz: Whether to generate quiz questions
        detail: Difficulty level
        explanation_type: Type of explanation
        
    Returns:
        str: Generated answer with citations
    """
    if not retrieved_chunks:
        return "No document found. Upload a PDF first."

    if not API_KEY:
        logger.error("Missing API key")
        return "Missing API key. Please provide your Gemini API key."
    
    try:
        genai.configure(api_key=API_KEY)

        # Build context text with token limit
        context_text = ""
        token_count = 0
        for c in retrieved_chunks:
            t_len = len(c["text"].split())
            if token_count + t_len > MAX_CHUNK_TOKENS * config["TOP_K_RETRIEVAL"]:
                break
            context_text += f"[Source: {c['source']}]\n{c['text']}\n\n"
            token_count += t_len

        prompt = construct_prompt(query, context_text, quiz, detail, explanation_type)
        model = genai.GenerativeModel(LLM_MODEL)
        response = model.generate_content(prompt)
        
        logger.info(f"Generated answer for query: {query[:50]}...")
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        return f"Error generating answer: {str(e)}"


def generate_flashcards(
    query: str,
    retrieved_chunks: List[Dict],
    num_cards: int = 5
) -> List[Dict]:
    """
    Generate flashcard Q&A pairs from content.
    
    Args:
        query: Topic for flashcards
        retrieved_chunks: List of relevant text chunks
        num_cards: Number of flashcards to generate
        
    Returns:
        List[Dict]: List of flashcard objects
    """
    if not retrieved_chunks or not API_KEY:
        return []

    try:
        genai.configure(api_key=API_KEY)
        context_text = "\n\n".join([c["text"] for c in retrieved_chunks[:3]])

        prompt = f"""
Generate {num_cards} educational flashcards about {query} from this content.
Each flashcard should have a clear question and concise answer.

Guidelines:
- Questions should be clear and specific
- Answers should be concise but informative
- Avoid raw JSON symbols or formatting
- Focus on key concepts and definitions
- Keep answers under 100 words

Format as clean JSON with this structure:
[
  {{
    "question": "What is X?",
    "answer": "Clear, concise definition of X."
  }}
]

Content:
{context_text}
"""

        model = genai.GenerativeModel(LLM_MODEL)
        response = model.generate_content(prompt)

        raw_text = ""
        try:
            raw_text = (response.text or "").strip()
        except Exception:
            raw_text = str(response).strip()

        if not raw_text:
            logger.error("Empty response from LLM when generating flashcards")
            logger.debug("LLM response object: %r", response)
            return []

        try:
            flashcards = json.loads(raw_text)
            logger.info(f"Generated {len(flashcards)} flashcards for topic: {query[:50]}...")
            return flashcards
        except json.JSONDecodeError as je:
            logger.error("Error parsing LLM JSON for flashcards: %s", je)
            logger.debug("LLM raw response (first 2000 chars): %s", raw_text[:2000])
            # Fallback: return simple Q&A pairs by splitting sentences
            cards = []
            parts = [s.strip() for s in re.split(r'[\.\?\!]\s+', raw_text) if s.strip()]
            for p in parts[:num_cards]:
                cards.append({"question": p[:120] + '?', "answer": p[:240]})
            logger.info(f"Generated {len(cards)} flashcards (fallback) for topic: {query[:50]}...")
            return cards
    except Exception as e:
        logger.error(f"Error generating flashcards: {e}")
        return []


def generate_quiz_adaptive(context: List[Dict], num_questions=5, difficulty="Mixed", quiz_history=None) -> List[Dict]:
    if not context or not API_KEY:
        return []

    # Prepare context
    context_text = "\n\n".join([c.get("text", "") for c in context[:10]])  # more chunks

    # Difficulty adaptation
    adaptation = ""
    if quiz_history and len(quiz_history) > 0:
        last_quiz = quiz_history[-1]
        score_percent = (last_quiz["score"] / last_quiz["total"]) * 100
        if score_percent > 80:
            adaptation = "Make questions slightly harder."
        elif score_percent < 40:
            adaptation = "Make questions slightly easier."

    prompt = f"""
Generate {num_questions} multiple choice questions based on the text below.
Difficulty: {difficulty}. {adaptation}
Format strictly as JSON array:
[
  {{
    "question": "Question text?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct": "Correct option text",
    "explanation": "Explanation text"
  }}
]

TEXT:
{context_text}
"""
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(LLM_MODEL)
        response = model.generate_content(prompt)
        raw_text = (response.text or "").strip()

        # Extract JSON block only
        json_match = re.search(r"\[.*\]", raw_text, flags=re.DOTALL)
        if json_match:
            quiz_data = json.loads(json_match.group())
            # Sanitize
            for q in quiz_data:
                q["question"] = q.get("question", "").strip()
                q["options"] = [o.strip() for o in q.get("options", [])]
                q["correct"] = q.get("correct", "").strip()
                q["explanation"] = q.get("explanation", "").strip()
            return quiz_data

        # If LLM output is invalid, fallback
        return _fallback_quiz_from_context(context, num_questions)

    except Exception as e:
        logger.error(f"LLM quiz generation failed: {e}")
        return _fallback_quiz_from_context(context, num_questions)


def generate_concept_map(
    query: str,
    retrieved_chunks: List[Dict]
) -> Dict:
    """
    Generate related concepts and connections.
    
    Args:
        query: Main concept to explore
        retrieved_chunks: List of relevant text chunks
        
    Returns:
        Dict: Concept map with definitions and relationships
    """
    if not retrieved_chunks or not API_KEY:
        return {}

    try:
        genai.configure(api_key=API_KEY)
        context_text = "\n\n".join([c["text"] for c in retrieved_chunks[:3]])

        prompt = f"""
Analyze the following text about '{query}' and extract:
1. Main concept definition (2-3 sentences)
2. Key subtopics (list 3-5)
3. Related concepts (list 3-5)
4. Real-world applications (list 2-3)

Format as JSON:
{{
  "definition": "...",
  "subtopics": [...],
  "related": [...],
  "applications": [...]
}}

Return ONLY JSON, no other text.

TEXT:
{context_text}
"""

        model = genai.GenerativeModel(LLM_MODEL)
        response = model.generate_content(prompt)

        raw_text = ""
        try:
            raw_text = (response.text or "").strip()
        except Exception:
            raw_text = str(response).strip()

        if not raw_text:
            logger.error("Empty response from LLM when generating concept map")
            logger.debug("LLM response object: %r", response)
            return {}

        try:
            concept_map = json.loads(raw_text)
            logger.info(f"Generated concept map for: {query[:50]}...")
            return concept_map
        except json.JSONDecodeError as je:
            logger.error("Error parsing LLM JSON for concept map: %s", je)
            logger.debug("LLM raw response (first 2000 chars): %s", raw_text[:2000])
            return {}
    except Exception as e:
        logger.error(f"Error generating concept map: {e}")
        return {}


def construct_prompt(
    query: str,
    context_text: str,
    quiz: bool = False,
    detail: str = "College",
    explanation_type: str = "Explanation"
) -> str:
    """
    Construct a prompt for the LLM.
    
    Args:
        query: User's question
        context_text: Retrieved context
        quiz: Whether to generate quiz questions
        detail: Difficulty level
        explanation_type: Type of explanation
        
    Returns:
        str: Formatted prompt
    """
    difficulty_map = config["DIFFICULTY_LEVELS"]
    explanation_map = config["EXPLANATION_TYPES"]

    task_quiz = "Also, create 1-2 quiz questions with answers." if quiz else ""
    difficulty_instruction = difficulty_map.get(detail, difficulty_map["College"])
    explanation_instruction = explanation_map.get(explanation_type, explanation_map["Explanation"])

    return f"""
You are a knowledgeable tutor. Answer the following question using ONLY the CONTEXT provided.

{difficulty_instruction}
{explanation_instruction}
{task_quiz}

Cite sources inline in the format [DocName:PageX]. Do not make up information.

CONTEXT:
{context_text}

QUESTION: {query}
"""


def _fallback_quiz_from_context(context: List[Dict], num_questions=5) -> List[Dict]:
    """Deterministic fallback: take sentences and create MCQs with dummy options"""
    quiz = []
    sentences = []
    for c in context:
        sents = re.split(r'(?<=[.?!])\s+', c.get("text", ""))
        sentences.extend([s.strip() for s in sents if len(s.strip()) > 20])
    random.shuffle(sentences)

    for i in range(min(num_questions, len(sentences))):
        q_text = sentences[i]
        # Create dummy options
        options = [q_text]  # correct
        while len(options) < 4:
            option = random.choice(sentences)
            if option not in options:
                options.append(option)
        random.shuffle(options)
        quiz.append({
            "question": q_text,
            "options": options,
            "correct": q_text,
            "explanation": "Fallback generated from context."
        })
    return quiz
