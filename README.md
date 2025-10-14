# 📘 AI Study Buddy Pro

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.50.0-red.svg)](https://streamlit.io)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An AI-powered intelligent tutoring system leveraging LLMs and vector search to provide personalized learning experiences through interactive quizzes, smart flashcards, and adaptive content exploration.

---

## � Project Structure

```
AiStudyBuddy/
├── run.py                  # Entry point
├── requirements.txt        # Main dependencies
├── requirements-dev.txt    # Dev dependencies
├── .gitignore              # Git ignore rules
├── README.md               # Project documentation
├── src/
│   ├── app.py              # Main Streamlit app
│   ├── api/                # (Reserved for API integrations)
│   ├── config/
│   │   ├── config.py       # Configuration management
│   │   └── __init__.py
│   ├── core/
│   │   ├── llm.py          # LLM integration
│   │   ├── vectordb.py     # Vector DB operations
│   │   └── __init__.py
│   ├── utils/
│   │   ├── helper.py       # PDF/text processing
│   │   ├── logger.py       # Logging
│   │   ├── session_manager.py # Session state
│   │   ├── utils.py        # Utility functions
│   │   └── __init__.py
│   └── __init__.py
├── tests/
│   ├── test_utils.py
│   └── test_vectordb.py     
```

---

## ✨ Features
- **Learn Mode**: Upload PDFs, ask questions, get multi-level explanations with source context.
- **Quiz Master**: Adaptive quiz generation, instant feedback, performance analytics.
- **Flashcards**: Smart card generation, spaced repetition ready, review management.
- **Progress Dashboard**: Visualize learning progress, score trends, analytics.
- **Concept Explorer**: Deep dive into concepts, related topics, and recommendations.

---

## 🚀 Quickstart

1. **Clone & Setup Environment**
   ```bash
   git clone <repo-url>
   cd AiStudyBuddy
   python -m venv myenv
   myenv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   ```
2. **Configure**
   - Add your API keys and settings in `src/config/config.py` or a `.env` file if needed.
3. **Run the App**
   ```bash
   streamlit run src/app.py
   ```

---

## 🛠 Development
- **Linting**: `black`, `flake8`, `mypy` (see `requirements-dev.txt`)
- **Testing**: `pytest tests/`
- **Pre-commit**: `pre-commit install`

---

## 🧩 Core Modules
- `src/core/llm.py`: LLM (e.g., Gemini/OpenAI) integration
- `src/core/vectordb.py`: Vector search and retrieval
- `src/utils/helper.py`: PDF/text chunking
- `src/utils/session_manager.py`: Session state
- `src/utils/logger.py`: Logging
- `src/utils/utils.py`: Utility functions
- `src/config/config.py`: Central config

---

## 🧪 Testing
```bash
pytest tests/
```

---

## 📚 Documentation
- See code docstrings and comments for API usage.
- Main entry: `src/app.py`

---

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.

---

Built with ❤️ for students worldwide.

1. **PDF Processing Engine** (`helper.py`)
   - Text extraction
   - Chunk management
   - Metadata processing

2. **Vector Database** (`vectordb.py`)
   - FAISS indexing
   - Semantic search
   - Hybrid retrieval

3. **LLM Integration** (`llm.py`)
   - Google Gemini integration
   - Context management
   - Response generation

4. **Session Management** (`session_manager.py`)
   - State persistence
   - Data serialization
   - Cache management

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Google Gemini API key
- 2GB+ RAM
- 500MB disk space

### Step-by-Step Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/ai-study-buddy-pro.git
   cd ai-study-buddy-pro
   ```

2. Create and activate virtual environment
   ```bash
   # Windows
   python -m venv myenv
   myenv\Scripts\activate

   # Linux/macOS
   python -m venv myenv
   source myenv/bin/activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables
   ```bash
   # Create .env file
   echo "gemini_api_key=your_api_key_here" > .env
   ```

5. Run the application
   ```bash
   streamlit run app.py
   ```

## ⚙️ Configuration

Configuration is managed through `config.py`. Key settings:

### PDF Processing
```python
MAX_CHUNK_TOKENS = 400    # Token limit per chunk
MAX_PDF_SIZE_MB = 50      # Maximum PDF file size
OVERLAP_TOKENS = 50       # Chunk overlap
```

### Vector Database
```python
TOP_K_RETRIEVAL = 5       # Results per query
SIMILARITY_THRESHOLD = 0.5 # Minimum relevance score
```

### LLM Settings
```python
TEMPERATURE = 0.7         # Response creativity
MAX_OUTPUT_TOKENS = 2048  # Response length limit
```

### Feature Flags
```python
ENABLE_QUIZ_MODE = True
ENABLE_FLASHCARDS = True
ENABLE_CONCEPT_EXPLORER = True
```

## 🎮 Usage

### Learn Mode Workflow

1. **Upload Study Material**
   ```python
   # Supported formats
   - PDF documents (.pdf)
   - Max size: 50MB
   - Text extractable content
   ```

2. **Ask Questions**
   - Select difficulty level
   - Choose explanation type
   - Enable/disable quiz generation
   - View source attribution

3. **Create Flashcards**
   - Auto-generate from answers
   - Custom flashcard creation
   - Review scheduling

### Quiz Mode Features

1. **Quiz Generation**
   ```python
   # Customization options
   questions = 1-20
   difficulty = ["Easy", "Medium", "Hard", "Mixed"]
   time_limit = Optional[minutes]
   ```

2. **Progress Tracking**
   - Score history
   - Performance trends
   - Learning recommendations

## 📚 API Reference

### PDF Processing

```python
def process_pdf(file_path: str) -> List[Dict]:
    """
    Extract and chunk text from PDF with metadata.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        List of chunks with metadata
    """
```

### Vector Database

```python
def retrieve(
    query: str,
    top_k: int = 5,
    threshold: float = 0.5
) -> List[Dict]:
    """
    Retrieve relevant chunks based on semantic similarity.
    
    Args:
        query: Search query
        top_k: Number of results
        threshold: Minimum similarity score
        
    Returns:
        List of relevant chunks with scores
    """
```

### LLM Integration

```python
def generate_answer(
    query: str,
    retrieved_chunks: List[Dict],
    difficulty: str = "College",
    explanation_type: str = "Explanation"
) -> str:
    """
    Generate contextual answer using LLM.
    
    Args:
        query: User question
        retrieved_chunks: Context chunks
        difficulty: Explanation level
        explanation_type: Response format
        
    Returns:
        Formatted answer with citations
    """
```

## 🛠 Development

### Setup Development Environment

1. Install development dependencies
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Install pre-commit hooks
   ```bash
   pre-commit install
   ```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Document all functions
- Write unit tests

### Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=./ tests/
```

### Logging

```python
# Log levels
DEBUG: Detailed debugging info
INFO: General operations
WARNING: Unexpected behavior
ERROR: Function/operation failures
CRITICAL: Application failures
```

## 🚨 Troubleshooting

### Common Issues

1. **Missing API Key**
   ```
   Error: Missing API key
   Solution: Add gemini_api_key to .env file
   ```

2. **PDF Processing Errors**
   ```
   Error: No text extracted
   Solution: Ensure PDF has extractable text
   ```

3. **Memory Issues**
   ```
   Error: Memory error during embedding
   Solution: Reduce MAX_CHUNK_TOKENS in config
   ```

### Debugging

1. Enable debug logging
   ```python
   LOG_LEVEL = "DEBUG"  # In config.py
   ```

2. Check log file
   ```bash
   tail -f app.log
   ```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

### Guidelines

- Follow code style
- Add unit tests
- Update documentation
- Test thoroughly

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

## 👥 Support

- GitHub Issues: Bug reports/Feature requests
- Documentation: Installation/Usage help
- Email: akshat.prj@gmail.com

---

Built with ❤️ for students worldwide
