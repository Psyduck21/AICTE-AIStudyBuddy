"""Tests for vector database operations"""
import pytest
import os
import numpy as np
from src.core.vectordb import (
    build_vector_store,
    load_vector_store,
    retrieve,
    retrieve_by_page,
    search_by_keyword,
    hybrid_search,
    clear_vector_store
)

@pytest.fixture
def sample_chunks():
    """Sample text chunks for testing"""
    return [
        {
            "text": "This is the first test chunk",
            "source": "test.pdf:1",
            "page": 1
        },
        {
            "text": "This is the second test chunk about AI",
            "source": "test.pdf:1",
            "page": 1
        },
        {
            "text": "This is the third test chunk about machine learning",
            "source": "test.pdf:2",
            "page": 2
        }
    ]


def test_build_vector_store(sample_chunks):
    """Test vector store building"""
    # Test with valid chunks
    index = build_vector_store(sample_chunks)
    assert index is not None
    
    # Test with empty chunks
    assert build_vector_store([]) is None


def test_load_vector_store(sample_chunks):
    """Test vector store loading"""
    # First build the store
    build_vector_store(sample_chunks)
    
    # Test loading
    index, chunks = load_vector_store()
    assert index is not None
    assert chunks is not None
    assert len(chunks) == len(sample_chunks)


def test_retrieve(sample_chunks):
    """Test chunk retrieval"""
    # First build the store
    build_vector_store(sample_chunks)
    
    # Test retrieval
    results = retrieve("AI and machine learning")
    assert len(results) > 0
    assert "similarity" in results[0]
    
    # Test with empty query
    assert retrieve("") == []
    
    # Test with threshold
    results = retrieve("AI", threshold=0.9)
    assert all(r["similarity"] > 0.9 for r in results)


def test_retrieve_by_page(sample_chunks):
    """Test page-based retrieval"""
    # First build the store
    build_vector_store(sample_chunks)
    
    # Test page retrieval
    page_1_chunks = retrieve_by_page(1)
    assert len(page_1_chunks) == 2
    assert all(c["page"] == 1 for c in page_1_chunks)
    
    # Test non-existent page
    assert retrieve_by_page(999) == []


def test_search_by_keyword(sample_chunks):
    """Test keyword search"""
    # First build the store
    build_vector_store(sample_chunks)
    
    # Test keyword search
    ai_chunks = search_by_keyword("AI")
    assert len(ai_chunks) == 1
    assert "AI" in ai_chunks[0]["text"]
    
    # Test case insensitivity
    ai_chunks_lower = search_by_keyword("ai")
    assert len(ai_chunks_lower) == 1
    
    # Test non-existent keyword
    assert search_by_keyword("xyz123") == []


def test_hybrid_search(sample_chunks):
    """Test hybrid search functionality"""
    # First build the store
    build_vector_store(sample_chunks)
    
    # Test with query only
    results = hybrid_search("machine learning")
    assert len(results) > 0
    
    # Test with query and keyword
    results = hybrid_search("learning", keyword="AI")
    assert len(results) >= 0
    
    # Test with non-matching keyword
    results = hybrid_search("learning", keyword="xyz123")
    assert len(results) == 0


def test_clear_vector_store(sample_chunks):
    """Test vector store clearing"""
    # First build the store
    build_vector_store(sample_chunks)
    
    # Test clearing
    assert clear_vector_store() is True
    
    # Verify store is cleared
    index, chunks = load_vector_store()
    assert index is None
    assert chunks is None
    
    # Test clearing non-existent store
    assert clear_vector_store() is False