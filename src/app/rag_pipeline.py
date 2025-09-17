import sys
from pathlib import Path
import requests
import json

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.retrieval.embeddings import embed_text
from src.vector_store.vector_store import FAISSStore

class RAGPipeline:
    def __init__(self, store_dir="test_store", ollama_url="http://localhost:11434", model="llama3"):
        self.store_dir = store_dir
        self.ollama_url = ollama_url
        self.model = model
        self.vector_store = None
        
    def load_vector_store(self):
        """Load the vector store"""
        self.vector_store = FAISSStore.load(self.store_dir)
        print(f"Vector store loaded from {self.store_dir}")
    
    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Retrieve relevant chunks for the query"""
        if not self.vector_store:
            self.load_vector_store()
        
        # Embed the query
        query_embedding = embed_text(query)
        
        # Search for similar chunks
        results = self.vector_store.similarity_search(query_embedding, top_k)
        
        # Combine retrieved chunks into context
        context = "\n\n".join(results)
        return context
    
    def generate_answer(self, query: str, context: str) -> str:
        """Generate answer using Ollama"""
        prompt = f"""Answer the following question based only on the provided context. If the answer cannot be found in the context, say "I don't have enough information to answer that question."

Context:
{context}

Question: {query}

Answer:"""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Ollama: {e}"
        except KeyError:
            return "Error: Invalid response from Ollama"
    
    def ask(self, query: str, top_k: int = 3) -> dict:
        """Complete RAG pipeline: retrieve + generate"""
        print(f"Query: {query}")
        
        # Step 1: Retrieve relevant context
        context = self.retrieve_context(query, top_k)
        print(f"Retrieved {top_k} chunks")
        
        # Step 2: Generate answer
        answer = self.generate_answer(query, context)
        
        return {
            "query": query,
            "context": context,
            "answer": answer
        }

def main():
    # Initialize RAG pipeline
    rag = RAGPipeline()
    
    print("RAG Pipeline initialized. Type 'quit' to exit.")
    
    while True:
        query = input("\nEnter your question: ")
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query.strip():
            continue
        
        # Get answer from RAG pipeline
        result = rag.ask(query)
        
        print(f"\n{'='*50}")
        print(f"Answer: {result['answer']}")
        print(f"{'='*50}")

if __name__ == "__main__":
    main()