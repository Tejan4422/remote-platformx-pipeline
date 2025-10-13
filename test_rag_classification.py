#!/usr/bin/env python3
"""
Test script to verify the RAG pipeline with requirement classification
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.app.rag_pipeline import RAGPipeline

def test_rag_with_classification():
    """Test the RAG pipeline with requirement classification"""
    
    # Initialize RAG pipeline
    rag = RAGPipeline()
    
    # Test requirements
    test_requirements = [
        "The system must use PostgreSQL database and REST APIs",
        "All user data must be encrypted at rest and in transit", 
        "Users should be able to create and edit customer profiles",
        "The system must respond to queries within 2 seconds",
        "Generate monthly sales reports with charts and dashboards"
    ]
    
    print("Testing RAG Pipeline with Requirement Classification")
    print("=" * 60)
    
    for i, requirement in enumerate(test_requirements, 1):
        print(f"\n{i}. Testing Requirement: {requirement}")
        print("-" * 50)
        
        try:
            # Use the RAG pipeline to get response and classification
            result = rag.ask(requirement, top_k=2, include_quality_score=True, include_category=True)
            
            print(f"Category: {result.get('category', 'Not classified')}")
            print(f"Quality Score: {result.get('quality_score', 'N/A')}")
            print(f"Response: {result['answer'][:100]}..." if len(result['answer']) > 100 else f"Response: {result['answer']}")
            
        except Exception as e:
            print(f"Error processing requirement: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_rag_with_classification()