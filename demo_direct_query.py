#!/usr/bin/env python3
"""
Demo script showing the new direct query functionality
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app.rag_pipeline import RAGPipeline

def demo_direct_query():
    """Demonstrate the direct query functionality"""
    print("💬 Direct Query Demo")
    print("=" * 50)
    
    # Check if vector store exists
    vector_store_exists = Path("test_store/index.faiss").exists() and Path("test_store/docstore.pkl").exists()
    
    if not vector_store_exists:
        print("❌ No vector store found. Please run the indexing demo first.")
        return
    
    print("✅ Vector store found. Testing direct queries...")
    
    # Initialize RAG pipeline
    rag = RAGPipeline(model="llama3")
    
    # Test questions that should match our indexed content
    test_queries = [
        "What is your experience with cloud migration?",
        "How do you handle data security and compliance?",
        "What certifications does your team have?",
        "Describe your disaster recovery capabilities."
    ]
    
    print(f"\n🧪 Testing {len(test_queries)} sample queries:")
    print("-" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("   " + "-" * 40)
        
        try:
            # Get response
            result = rag.ask(query, top_k=3, include_quality_score=True)
            
            # Show response
            print(f"   🤖 Response: {result['answer'][:200]}...")
            
            # Show quality metrics
            if result.get('quality_score'):
                print(f"   📊 Quality: {result['quality_score']:.0f}/100 ({result.get('quality_status', 'Unknown')})")
            
            # Check if we retrieved relevant context
            context_chunks = len(result.get('context', '').split('\n\n'))
            print(f"   📚 Retrieved {context_chunks} context chunks")
            
            # Check for our test data keywords
            context = result.get('context', '').lower()
            if any(keyword in context for keyword in ['cloud migration', 'data security', 'certifications', 'disaster recovery']):
                print("   ✅ Found relevant indexed content!")
            else:
                print("   ℹ️  General knowledge base content retrieved")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Direct Query Feature Benefits:")
    print("=" * 50)
    print("""
✅ What you can now do:
1. Ask questions directly without uploading files
2. Get instant responses from your knowledge base
3. See quality scores for each response
4. View the source context that was used
5. Keep a history of your queries
6. Use quick question templates

💡 Perfect for:
- Quick queries during meetings
- Testing your knowledge base
- Getting instant answers
- Exploring what your system knows
- Training and demonstrations
""")

if __name__ == "__main__":
    demo_direct_query()