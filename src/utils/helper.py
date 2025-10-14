"""Helper functions for AI Study Buddy Pro"""
import os
import sys
import numpy as np
import re
from typing import List
from PyPDF2 import PdfReader
import google.generativeai as genai
from src.config import get_config_dict
from src.utils.logger import logger
import streamlit as st

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

config = get_config_dict()
API_KEY = st.secrets.get("gemini_api_key")
if not API_KEY:
    logger.error("Missing GEMINI_API_KEY in .env file")


    
MAX_CHUNK_TOKENS = config["MAX_CHUNK_TOKENS"]

# Configure Gemini
genai.configure(api_key=API_KEY)


def chunk_text(text, max_tokens=MAX_CHUNK_TOKENS):
    """Split text into logical chunks while respecting token limits."""
    # First, split by paragraphs
    paragraphs = text.split("\n\n")
    chunks = []
    cur = ""
    
    for p in paragraphs:
        if len(cur.split()) + len(p.split()) <= max_tokens:
            cur += "\n\n" + p
        else:
            if cur.strip():
                chunks.append(cur.strip())
            cur = p
    
    if cur.strip():
        chunks.append(cur.strip())
    
    return chunks


def extract_metadata(text, page_num):
    """Extract potential section headers and structure."""
    lines = text.split("\n")
    headers = []
    
    for line in lines:
        # Look for potential headers (lines with less than 100 chars and capitalized)
        if len(line.strip()) < 100 and line.strip() and line[0].isupper():
            headers.append(line.strip())
    
    return headers[:3]  # Return top 3 potential headers


def process_pdf(file_path):
    """Extract and chunk text from PDF with metadata."""
    logger.info(f"Processing PDF: {file_path}")
    reader = PdfReader(file_path)
    chunks = []
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        
        if text and text.strip():
            # Extract metadata (potential headers)
            metadata = extract_metadata(text, i + 1)
            
            for c in chunk_text(text):
                chunks.append({
                    "text": c,
                    "source": f"{os.path.basename(file_path)}:page{i+1}",
                    "page": i + 1,
                    "headers": metadata
                })
    
    logger.info(f"Extracted {len(chunks)} chunks from PDF")
    return chunks


def get_embedding(texts: List[str]):
    """Generate embeddings for texts using Gemini API."""
    if not API_KEY:
        logger.error("Missing API key")
        raise ValueError("Missing API key. Please provide your Gemini API key.")

    genai.configure(api_key=API_KEY)

    embeddings = []
    for text in texts:
        try:
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text
            )
            embeddings.append(np.array(result["embedding"], dtype=np.float32))
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            # Return zero embedding on error
            embeddings.append(np.zeros(768, dtype=np.float32))

    return embeddings


def clean_text(text):
    """Clean and normalize text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\(\)\:]', '', text)
    return text.strip()


def extract_key_terms(text, num_terms=10):
    """Extract important keywords from text."""
    # Simple keyword extraction based on frequency and length
    words = text.lower().split()
    # Filter short words and common stopwords
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'is', 'was', 'are'}
    
    words = [w for w in words if len(w) > 3 and w not in stopwords]
    
    from collections import Counter
    word_freq = Counter(words)
    
    return [word for word, _ in word_freq.most_common(num_terms)]