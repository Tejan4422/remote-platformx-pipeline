from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent.parent
# Load .env file from project root
load_dotenv(ROOT_DIR / '.env')

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text: str) -> list[float]:
    """Generate embeddings for a given text using a local Hugging Face model."""
    embedding = model.encode(text)
    return embedding.tolist()