from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent.parent
# Load .env file from project root
load_dotenv(ROOT_DIR / '.env')

# Lazy loading of the model
_model = None

def get_model():
    """Get the SentenceTransformer model, loading it lazily"""
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def embed_text(text: str):
    """Generate embeddings for a given text using a local Hugging Face model."""
    model = get_model()
    embedding = model.encode(text)
    return embedding