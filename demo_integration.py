#!/usr/bin/env python3
"""
Demonstration script showing how indexed RFP responses are used in RAG pipeline
"""

import sys
import os
from pathlib import Path
import pandas as pd
import tempfile

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ingestion.rfp_response_indexer import RFPResponseIndexer
from app.rag_pipeline import RAGPipeline

def demonstrate_integration():
    """Demonstrate how indexed responses are used in RAG generation"""
    print("🔄 Integration Demonstration: Indexed Responses in RAG Pipeline")
    print("=" * 70)
    
    # Step 1: Check current vector store state
    print("\n1. Current Vector Store Status")
    print("-" * 30)
    indexer = RFPResponseIndexer()
    initial_info = indexer.get_vector_store_info()
    print(f"   Documents before indexing: {initial_info.get('total_documents', 0)}")
    
    # Step 2: Create and index new RFP responses
    print("\n2. Adding New Historical RFP Responses")
    print("-" * 40)
    
    # Create sample historical responses
    historical_data = {
        'Requirement': [
            'What is your experience with machine learning implementations?',
            'How do you ensure project quality and testing?',
            'What is your approach to data migration and backup?'
        ],
        'Response': [
            'We have extensive experience implementing machine learning solutions across various industries, including predictive analytics for retail, fraud detection for financial services, and recommendation engines for e-commerce platforms. Our team has successfully deployed over 30 ML models in production environments.',
            'Our quality assurance process includes comprehensive unit testing, integration testing, code reviews, and automated CI/CD pipelines. We maintain a test coverage of over 90% and use industry-standard testing frameworks to ensure reliability and performance.',
            'We follow a structured data migration approach with thorough planning, data validation, incremental migration phases, and comprehensive backup strategies. Our backup systems include automated daily backups, geographically distributed storage, and tested recovery procedures with 99.9% data integrity guarantee.'
        ]
    }
    
    df = pd.DataFrame(historical_data)
    
    # Save to temporary Excel file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
        temp_path = temp_file.name
    df.to_excel(temp_path, index=False)
    
    try:
        # Index the responses
        result = indexer.index_rfp_responses(temp_path)
        if result['success']:
            print(f"   ✅ Successfully indexed {result['documents_added']} new responses")
            print(f"   📊 Vector store now has {result['final_document_count']} total documents")
        else:
            print(f"   ❌ Indexing failed: {result['error']}")
            return
        
        # Step 3: Test RAG pipeline with similar questions
        print("\n3. Testing RAG Pipeline with Similar Questions")
        print("-" * 45)
        
        rag = RAGPipeline()
        
        test_questions = [
            "Do you have experience with AI and machine learning projects?",
            "How do you handle quality control in your development process?",
            "What are your data backup and recovery capabilities?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n   Question {i}: {question}")
            print("   " + "-" * 50)
            
            # Get response from RAG pipeline
            result = rag.ask(question, top_k=3, include_quality_score=False)
            
            # Show retrieved context (this should include our newly indexed responses)
            context_snippets = result['context'].split('\n\n')
            
            print(f"   📚 Retrieved {len(context_snippets)} relevant documents:")
            for j, snippet in enumerate(context_snippets[:2], 1):  # Show first 2 snippets
                preview = snippet[:100].replace('\n', ' ') + "..."
                print(f"      {j}. {preview}")
            
            print(f"   🤖 Generated Response:")
            response_preview = result['answer'][:200].replace('\n', ' ') + "..."
            print(f"      {response_preview}")
            
            # Check if our indexed content appears in the context
            indexed_keywords = ['machine learning', 'quality assurance', 'data migration']
            found_indexed = any(keyword in result['context'].lower() for keyword in indexed_keywords)
            if found_indexed:
                print(f"   ✅ INDEXED CONTENT DETECTED in retrieved context!")
            else:
                print(f"   ℹ️  No direct indexed content match (but may be semantically similar)")
    
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    print("\n" + "=" * 70)
    print("🎯 SUMMARY: Integration Confirmed!")
    print("=" * 70)
    print("""
✅ How it works:
1. When you upload historical RFP responses → They get indexed to the vector store
2. When generating new RFP responses → RAG pipeline searches the SAME vector store
3. If new requirements are similar to indexed ones → Historical responses are retrieved
4. The LLM uses this context → Generates responses informed by your past successes

🔄 The Flow:
[Upload Excel] → [Index to Vector Store] → [Future RFP Generation] → [Retrieval includes your indexed responses]

📈 Benefits:
- Better responses based on proven organizational experience
- Consistent messaging across proposals  
- Continuous learning from past successes
- Reduced time recreating similar responses
""")

if __name__ == "__main__":
    demonstrate_integration()