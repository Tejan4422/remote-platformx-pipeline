#!/usr/bin/env python3
"""
Test the existing vector store
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent))

def test_vector_store():
    """Test if we can load the existing vector store"""
    try:
        from src.vector_store.vector_store import FAISSStore
        
        # Try to load the existing vector store
        vector_store = FAISSStore.load("test_store")
        
        print(f"✅ Vector store loaded successfully!")
        print(f"   - Dimension: {vector_store.dimension}")
        print(f"   - Number of documents: {len(vector_store.document_map)}")
        print(f"   - Current ID: {vector_store.current_id}")
        
        # Test search with a sample query
        from src.retrieval.embeddings import embed_text
        
        query = "What are the company's capabilities?"
        query_embedding = embed_text(query)
        
        results = vector_store.similarity_search(query_embedding, k=3)
        
        print(f"\n🔍 Sample search results for '{query}':")
        for i, (doc_id, text, score) in enumerate(results, 1):
            print(f"{i}. ID: {doc_id}, Score: {score:.4f}")
            print(f"   Text: {text[:100]}...")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading vector store: {e}")
        return False

def test_rag_pipeline():
    """Test the RAG pipeline with existing vector store"""
    try:
        from src.app.rag_pipeline import RAGPipeline
        
        rag = RAGPipeline(store_dir="test_store")
        
        # Test a simple query
        test_query = "What are the main services offered?"
        result = rag.ask(test_query, top_k=2)
        
        print(f"✅ RAG pipeline test successful!")
        print(f"   Query: {test_query}")
        print(f"   Response: {result['answer'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG pipeline test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Existing Vector Store\n")
    
    success_count = 0
    
    if test_vector_store():
        success_count += 1
    
    print()
    
    if test_rag_pipeline():
        success_count += 1
    
    print(f"\n📊 Results: {success_count}/2 tests passed")
    
    if success_count == 2:
        print("\n🎉 System ready! Your existing vector store is working perfectly.")
        print("   Run: ./demo.sh")
    else:
        print("\n⚠️ Some issues detected with the vector store.")