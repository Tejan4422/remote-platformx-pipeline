from typing import List, Tuple
import faiss  # or import chromadb if using ChromaDB

class VectorStore:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)  # Initialize FAISS index

    def add_embeddings(self, embeddings: List[List[float]]):
        """Add embeddings to the vector store."""
        self.index.add(np.array(embeddings).astype('float32'))

    def retrieve_similar(self, query_embedding: List[float], top_k: int) -> List[Tuple[str, float]]:
        """Retrieve the top_k most similar embeddings."""
        distances, indices = self.index.search(np.array([query_embedding]).astype('float32'), top_k)
        return [(str(index), float(distance)) for index, distance in zip(indices[0], distances[0])]