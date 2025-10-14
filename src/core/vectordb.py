"""Vector database operations for AI Study Buddy Pro"""
import os
import pickle
import hashlib
import numpy as np
import faiss
from typing import Dict, List, Tuple, Optional
from ..utils.helper import get_embedding
from ..config import get_config_dict
from ..utils.logger import logger

config = get_config_dict()
VECTOR_STORE_DIR = os.path.join("data", "vector_store")
VECTOR_STORE_FILE = os.path.join(VECTOR_STORE_DIR, config["VECTOR_STORE_FILE"])
EMBEDDING_CACHE_DIR = os.path.join(VECTOR_STORE_DIR, "embeddings")
TOP_K = config["TOP_K_RETRIEVAL"]

def get_file_hash(file_path: str) -> str:
    """
    Generate a hash of the file content for tracking changes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: Hash of the file content
    """
    try:
        with open(file_path, "rb") as f:
            content = f.read()
            return hashlib.md5(content).hexdigest()
    except Exception as e:
        logger.error(f"Error generating file hash: {e}")
        return ""

def get_embedding_path(file_path: str) -> str:
    """
    Get the path where embeddings for a file should be stored.
    
    Args:
        file_path: Path to the source file
        
    Returns:
        str: Path for embedding storage
    """
    file_hash = get_file_hash(file_path)
    if not file_hash:
        return ""
    
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    return os.path.join(EMBEDDING_CACHE_DIR, f"{base_name}_{file_hash}.pkl")


def build_vector_store(chunks: List[Dict], source_file: str = None) -> Optional[faiss.Index]:
    """
    Build FAISS vector database from text chunks with caching.
    
    Args:
        chunks: List of text chunks with metadata
        source_file: Path to the source PDF file
        
    Returns:
        faiss.Index: FAISS index object
    """
    if not chunks:
        return None
    
    # Create directories if they don't exist
    os.makedirs(EMBEDDING_CACHE_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(VECTOR_STORE_FILE), exist_ok=True)
    
    # Load existing cache if available
    existing_data = {"index": None, "chunks": [], "file_map": {}}
    if os.path.exists(VECTOR_STORE_FILE):
        try:
            with open(VECTOR_STORE_FILE, "rb") as f:
                existing_data = pickle.load(f)
        except Exception as e:
            logger.error(f"Error loading existing vector store: {e}")
    
    new_embeddings = []
    if source_file:
        # Check if we have cached embeddings for this file
        embedding_path = get_embedding_path(source_file)
        if embedding_path and os.path.exists(embedding_path):
            try:
                with open(embedding_path, "rb") as f:
                    cached_data = pickle.load(f)
                    new_embeddings = cached_data["embeddings"]
                    logger.info(f"Loaded cached embeddings for {source_file}")
            except Exception as e:
                logger.error(f"Error loading cached embeddings: {e}")
    
    # Generate embeddings if not cached
    if not new_embeddings:
        new_embeddings = get_embedding([c["text"] for c in chunks])
        new_embeddings = [e for e in new_embeddings if e is not None]
        
        # Cache the new embeddings if we have a source file
        if source_file and new_embeddings:
            embedding_path = get_embedding_path(source_file)
            if embedding_path:
                try:
                    with open(embedding_path, "wb") as f:
                        pickle.dump({"embeddings": new_embeddings, "chunks": chunks}, f)
                    logger.info(f"Cached embeddings for {source_file}")
                except Exception as e:
                    logger.error(f"Error caching embeddings: {e}")
    
    if not new_embeddings:
        logger.error("No valid embeddings generated")
        return None
    
    # Convert to numpy array
    embeddings_array = np.array(new_embeddings, dtype=np.float32)
    
    # Create or update the FAISS index
    dim = len(embeddings_array[0])
    if existing_data["index"] is None:
        index = faiss.IndexFlatL2(dim)
    else:
        index = existing_data["index"]
    
    # Add new embeddings to the index
    index.add(embeddings_array)
    
    # Update the chunks and file mapping
    start_idx = len(existing_data["chunks"])
    for i, chunk in enumerate(chunks):
        chunk["index"] = start_idx + i
    existing_data["chunks"].extend(chunks)
    
    if source_file:
        existing_data["file_map"][source_file] = {
            "hash": get_file_hash(source_file),
            "chunk_indices": list(range(start_idx, start_idx + len(chunks)))
        }
    
    # Save the updated vector store
    with open(VECTOR_STORE_FILE, "wb") as f:
        pickle.dump({
            "index": index,
            "chunks": existing_data["chunks"],
            "file_map": existing_data["file_map"]
        }, f)
    
    logger.info(f"Vector store updated with {len(chunks)} new chunks")
    return index


def load_vector_store() -> Tuple[Optional[faiss.Index], List[Dict]]:
    """
    Load vector database from disk.
    
    Returns:
        Tuple[faiss.Index, List]: FAISS index and chunks
    """
    if os.path.exists(VECTOR_STORE_FILE):
        try:
            with open(VECTOR_STORE_FILE, "rb") as f:
                data = pickle.load(f)
            
            # Verify index integrity
            if data["index"] is not None and len(data["chunks"]) == data["index"].ntotal:
                logger.info(f"Vector store loaded successfully with {len(data['chunks'])} chunks")
                return data["index"], data["chunks"]
            else:
                logger.warning("Vector store index integrity check failed")
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
    return None, None

def check_file_embeddings(file_path: str) -> bool:
    """
    Check if embeddings exist and are up to date for a file.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        bool: True if valid embeddings exist
    """
    if not os.path.exists(VECTOR_STORE_FILE):
        return False
        
    try:
        with open(VECTOR_STORE_FILE, "rb") as f:
            data = pickle.load(f)
            file_map = data.get("file_map", {})
            
            if file_path in file_map:
                current_hash = get_file_hash(file_path)
                return current_hash == file_map[file_path]["hash"]
    except Exception as e:
        logger.error(f"Error checking file embeddings: {e}")
    
    return False


def retrieve(query, top_k=TOP_K, threshold=None):
    """Retrieve relevant chunks based on semantic similarity."""
    index, chunks = load_vector_store()
    
    if not index or not chunks:
        return []
    
    try:
        q_emb = np.array(get_embedding([query]), dtype=np.float32)

        # Search in FAISS
        D, I = index.search(q_emb, min(top_k, len(chunks)))

        # Sanitize text to fix spacing and formatting issues
        def sanitize_text(text):
            """Clean up text by removing extra spaces and fixing line breaks."""
            return " ".join(text.split()).replace(" ,", ",").replace(" .", ".")

        # Retrieve results with distance scores
        results = []
        for idx, distance in zip(I[0], D[0]):
            if idx < len(chunks):
                chunk = chunks[idx]
                # Sanitize the text in the chunk
                chunk["text"] = sanitize_text(chunk.get("text", ""))
                # Convert L2 distance to similarity score (lower distance = higher similarity)
                similarity = 1 / (1 + distance)

                if threshold is None or similarity > threshold:
                    chunk["similarity"] = float(similarity)
                    results.append(chunk)

        logger.debug(f"Retrieved {len(results)} chunks for query: {query[:50]}...")
        return results
    except Exception as e:
        logger.error(f"Error during retrieval: {e}")
        return []


def retrieve_by_page(page_num, top_k=10):
    """Retrieve all chunks from a specific page."""
    index, chunks = load_vector_store()
    
    if not chunks:
        return []
    
    page_chunks = [c for c in chunks if c.get("page") == page_num]
    return page_chunks[:top_k]


def search_by_keyword(keyword):
    """Search chunks by keyword."""
    index, chunks = load_vector_store()
    
    if not chunks:
        return []
    
    results = []
    keyword_lower = keyword.lower()
    
    for chunk in chunks:
        if keyword_lower in chunk["text"].lower():
            results.append(chunk)
    
    logger.debug(f"Found {len(results)} chunks for keyword: {keyword}")
    return results


def hybrid_search(query, keyword=None, top_k=TOP_K):
    """Combine semantic search with keyword filtering."""
    # First do semantic search
    semantic_results = retrieve(query, top_k=top_k*2)
    
    # If keyword provided, filter results
    if keyword:
        keyword_lower = keyword.lower()
        semantic_results = [
            r for r in semantic_results 
            if keyword_lower in r["text"].lower()
        ]
    
    return semantic_results[:top_k]


def get_similar_chunks(chunk_index, top_k=5):
    """Find similar chunks to a given chunk."""
    index, chunks = load_vector_store()
    
    if not index or chunk_index >= len(chunks):
        return []
    
    embeddings = []
    for c in chunks:
        emb = np.array(get_embedding([c["text"]]), dtype=np.float32)
        embeddings.append(emb[0])
    
    embeddings = np.array(embeddings, dtype=np.float32)
    
    target_emb = embeddings[chunk_index:chunk_index+1]
    D, I = index.search(target_emb, top_k + 1)  # +1 to exclude itself
    
    results = [chunks[i] for i in I[0][1:]]  # Skip first (itself)
    return results


def clear_vector_store():
    """Clear the vector database."""
    if os.path.exists(VECTOR_STORE_FILE):
        os.remove(VECTOR_STORE_FILE)
        logger.info("Vector store cleared")
        return True
    return False