import sys
from pathlib import Path
import requests
import json

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.retrieval.embeddings import embed_text
from src.vector_store.vector_store import FAISSStore
from app.quality_scorer import RFPQualityScorer

class RAGPipeline:
    def __init__(self, store_dir="test_store", ollama_url="http://localhost:11434", model="llama3"):
        self.store_dir = store_dir
        self.ollama_url = ollama_url
        self.model = model
        self.vector_store = None
        self.quality_scorer = RFPQualityScorer()
        
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
        prompt = f"""You are a business professional providing direct, detailed, factual responses. Answer the question concisely without pleasantries.

Guidelines:
- Maximum 150 words
- Start directly with the answer - no "Thank you for your question" or similar phrases
- Be specific and elaborate where possible
- Write in flowing paragraphs like a human would speak
- Be confident about capabilities
- State facts confidently
- If you don't have specific information, acknowledge it naturally rather than saying you "cannot provide a complete response"

Context: {context}

Question: {query}

Response:"""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.5,
                        "top_p": 0.8
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            raw_response = response.json()["response"]
            # Clean up any AI-like formatting that might remain
            cleaned_response = self._humanize_response(raw_response)
            return cleaned_response
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Ollama: {e}"
        except KeyError:
            return "Error: Invalid response from Ollama"
    
    def _humanize_response(self, response: str) -> str:
        """Clean up AI-like formatting to make responses sound more human"""
        import re
        
        # Remove common AI phrases and patterns including pleasantries
        ai_patterns = [
            r"Thank you for.*?(question|inquiry).*?\.",
            r"I'm (happy|pleased) to.*?\.",
            r"We're proud to.*?\.",
            r"Here's (my|a.*?) response:\s*",
            r"Based on.*?information,?\s*",
            r"Let me.*?:\s*",
            r"I hope this helps.*?\.",
            r"(Please don't hesitate to|If you have any.*?questions).*?\.",
            r"\*\*(Summary|Detailed Explanation):\*\*\s*",
            r"\*\*.*?\*\*\s*",  # Remove any bold markdown
            r"^Summary:\s*",
            r"^Detailed Explanation:\s*",
            r"^Response:\s*",
            r"^Answer:\s*",
        ]
        
        cleaned = response
        for pattern in ai_patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove bullet points and convert to flowing text
        cleaned = re.sub(r"^\s*[-•*]\s*", "", cleaned, flags=re.MULTILINE)
        
        # Remove excessive line breaks and normalize spacing
        cleaned = re.sub(r"\n\s*\n\s*\n", "\n\n", cleaned)
        cleaned = re.sub(r"^\s+", "", cleaned)
        cleaned = re.sub(r"\s+$", "", cleaned)
        
        # Remove markdown-style formatting
        cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned)  # Bold
        cleaned = re.sub(r"\*(.*?)\*", r"\1", cleaned)      # Italic
        
        return cleaned.strip()
    
    def ask(self, query: str, top_k: int = 3, include_quality_score: bool = True) -> dict:
        """Complete RAG pipeline: retrieve + generate + score quality"""
        print(f"Query: {query}")
        
        # Step 1: Retrieve relevant context
        context = self.retrieve_context(query, top_k)
        print(f"Retrieved {top_k} chunks")
        
        # Step 2: Generate answer
        answer = self.generate_answer(query, context)
        
        # Step 3: Score response quality (if enabled)
        quality_score = None
        if include_quality_score:
            quality_score = self.quality_scorer.score_response(query, answer)
            print(f"Quality Score: {quality_score.overall_score}/100 ({quality_score.status})")
        
        result = {
            "query": query,
            "context": context,
            "answer": answer
        }
        
        if quality_score:
            result.update({
                "quality_score": quality_score.overall_score,
                "quality_status": quality_score.status,
                "quality_breakdown": {
                    "completeness": quality_score.completeness,
                    "clarity": quality_score.clarity,
                    "professionalism": quality_score.professionalism,
                    "relevance": quality_score.relevance
                },
                "quality_feedback": quality_score.feedback
            })
        
        return result
    
    def process_requirements_batch(self, requirements: list, top_k: int = 3, progress_callback=None) -> list:
        """Process multiple requirements in batch"""
        results = []
        total_requirements = len(requirements)
        
        print(f"Processing {total_requirements} requirements...")
        
        for i, requirement in enumerate(requirements):
            print(f"Processing requirement {i+1}/{total_requirements}")
            
            try:
                result = self.ask(requirement, top_k)
                results.append({
                    "requirement": requirement,
                    "response": result["answer"],
                    "status": "success"
                })
            except Exception as e:
                print(f"Error processing requirement {i+1}: {e}")
                results.append({
                    "requirement": requirement,
                    "response": f"Error processing requirement: {str(e)}",
                    "status": "error"
                })
            
            # Call progress callback if provided (for Streamlit progress bar)
            if progress_callback:
                progress_callback(i + 1, total_requirements)
        
        print(f"Completed processing {total_requirements} requirements")
        return results

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