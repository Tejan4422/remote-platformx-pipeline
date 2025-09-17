import faiss
import numpy as np
from typing import List, Tuple, Dict
import pickle
from pathlib import Path

class FAISSStore:
    def __init__(self, dimension: int = 1536):
        """Initialize FAISS vector store
        Args:
            dimension (int): Dimension of vectors (1536 for OpenAI embeddings)
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.document_map: Dict[int, str] = {}
        self.current_id = 0

    def add_texts(self, texts: List[str], embeddings: List[List[float]]) -> List[int]:
        """Add texts and their embeddings to the store
        Args:
            texts (List[str]): List of text chunks
            embeddings (List[List[float]]): List of embeddings
        Returns:
            List[int]: List of document IDs
        """
        if not texts or not embeddings:
            return []
        
        embeddings_array = np.array(embeddings).astype('float32')
        doc_ids = list(range(self.current_id, self.current_id + len(texts)))
        
        # Add embeddings to FAISS
        self.index.add(embeddings_array)
        
        # Map IDs to texts
        for doc_id, text in zip(doc_ids, texts):
            self.document_map[doc_id] = text
            
        self.current_id += len(texts)
        return doc_ids

    def similarity_search(self, query_embedding: List[float], k: int = 5) -> List[Tuple[int, str, float]]:
        """Search for similar vectors
        Args:
            query_embedding (List[float]): Query vector
            k (int): Number of results to return
        Returns:
            List[Tuple[int, str, float]]: List of (id, text, score) tuples
        """
        query_array = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_array, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx != -1:  # FAISS returns -1 for no results
                results.append((int(idx), self.document_map[int(idx)], float(distance)))
        
        return results

    def save(self, directory: str):
        """Save the vector store to disk
        Args:
            directory (str): Directory to save the store
        """
        save_dir = Path(directory)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(save_dir / "index.faiss"))
        
        # Save document map
        with open(save_dir / "docstore.pkl", "wb") as f:
            pickle.dump(
                {
                    "document_map": self.document_map,
                    "current_id": self.current_id
                }, 
                f
            )

    @classmethod
    def load(cls, directory: str) -> "FAISSStore":
        """Load vector store from disk
        Args:
            directory (str): Directory containing the store
        Returns:
            FAISSStore: Loaded vector store
        """
        load_dir = Path(directory)
        
        # Create instance
        store = cls()
        
        # Load FAISS index
        store.index = faiss.read_index(str(load_dir / "index.faiss"))
        
        # Load document map
        with open(load_dir / "docstore.pkl", "rb") as f:
            data = pickle.load(f)
            store.document_map = data["document_map"]
            store.current_id = data["current_id"]
        
        return store