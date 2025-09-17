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
        
        # Extract text content from tuples (id, text, score)
        texts = [result[1] for result in results]
        
        # Combine retrieved chunks into context
        context = "\n\n".join(texts)
        return context
    
    def generate_answer(self, query: str, context: str) -> str:
        """Generate answer using Ollama"""
        prompt = f"""You are a professional sales consultant responding to a Request for Proposal (RFP). Based on the provided context, answer the requirement thoroughly and professionally.

Guidelines:
- Provide a concise summary between 100-150 words
- Treat the input as a question requiring detailed explanation
- Elaborate thoroughly - avoid simple yes/no answers
- Do not reference specific document names, file sources, or business entity names
- Answer as a knowledgeable sales professional would
- If information is insufficient, state "Based on available information, I cannot provide a complete response to this requirement" rather than fabricating details
- Focus on capabilities and solutions rather than documentation references

Context:
{context}

Requirement: {query}

Response:"""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9
                    }
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