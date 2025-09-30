#!/usr/bin/env python3
"""
Test script for RFP Response Indexer functionality
"""

import sys
import os
from pathlib import Path
import pandas as pd
import tempfile

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ingestion.rfp_response_indexer import RFPResponseIndexer

def create_sample_rfp_file():
    """Create a sample RFP response Excel file for testing"""
    sample_data = {
        'Requirement': [
            'Describe your company\'s experience with cloud migration projects.',
            'What is your approach to data security and compliance?',
            'How do you handle project timeline management?',
            'What certifications does your team possess?',
            'Describe your disaster recovery procedures.'
        ],
        'Response': [
            'Our company has successfully completed over 50 cloud migration projects in the past 5 years, specializing in AWS, Azure, and Google Cloud platforms. We have helped organizations migrate from legacy on-premises systems to modern cloud architectures with minimal downtime.',
            'We implement a comprehensive security framework that includes encryption at rest and in transit, multi-factor authentication, regular security audits, and compliance with SOC 2, ISO 27001, and industry-specific regulations such as HIPAA and PCI DSS.',
            'We use agile project management methodologies with weekly sprints, clear milestone tracking, and regular stakeholder communication. Our average project delivery rate is 95% on-time with proactive risk management and contingency planning.',
            'Our team holds various industry certifications including AWS Solutions Architect, Microsoft Azure Expert, PMP, CISSP, and CISA. We maintain continuous education programs to stay current with technology trends and best practices.',
            'Our disaster recovery plan includes automated backups, geographically distributed data centers, real-time replication, and tested recovery procedures with RTO of 4 hours and RPO of 1 hour. We conduct quarterly DR drills to ensure system reliability.'
        ],
        'Priority': ['High', 'High', 'Medium', 'Low', 'High'],
        'Category': ['Experience', 'Security', 'Management', 'Qualifications', 'Operations']
    }
    
    df = pd.DataFrame(sample_data)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
        temp_path = temp_file.name
    
    # Save to Excel
    df.to_excel(temp_path, index=False, sheet_name='RFP Responses')
    return temp_path

def test_rfp_indexer():
    """Test the RFP Response Indexer functionality"""
    print("🧪 Testing RFP Response Indexer")
    print("=" * 50)
    
    # Create indexer
    indexer = RFPResponseIndexer()
    
    # Test 1: Check initial vector store status
    print("\n1. Checking initial vector store status...")
    store_info = indexer.get_vector_store_info()
    print(f"   Vector store exists: {store_info['exists']}")
    if store_info['exists']:
        print(f"   Total documents: {store_info['total_documents']}")
    
    # Test 2: Create sample RFP file
    print("\n2. Creating sample RFP response file...")
    sample_file = create_sample_rfp_file()
    print(f"   Created: {sample_file}")
    
    try:
        # Test 3: Process the file
        print("\n3. Processing RFP response file...")
        processing_result = indexer.process_rfp_responses(sample_file)
        
        if processing_result['success']:
            print(f"   ✅ Processing successful!")
            print(f"   Requirement column: {processing_result['requirement_column']}")
            print(f"   Response column: {processing_result['response_column']}")
            print(f"   Total pairs found: {processing_result['total_pairs']}")
        else:
            print(f"   ❌ Processing failed: {processing_result['error']}")
            return False
        
        # Test 4: Create indexable documents
        print("\n4. Creating indexable documents...")
        documents = indexer.create_indexable_documents(processing_result['rfp_pairs'])
        print(f"   Created {len(documents)} documents")
        print(f"   Sample document preview:")
        print(f"   {documents[0][:200]}...")
        
        # Test 5: Index the responses
        print("\n5. Indexing RFP responses to vector store...")
        indexing_result = indexer.index_rfp_responses(sample_file)
        
        if indexing_result['success']:
            print(f"   ✅ Indexing successful!")
            print(f"   Documents added: {indexing_result['documents_added']}")
            print(f"   Initial count: {indexing_result['initial_document_count']}")
            print(f"   Final count: {indexing_result['final_document_count']}")
        else:
            print(f"   ❌ Indexing failed: {indexing_result['error']}")
            return False
        
        # Test 6: Check updated vector store
        print("\n6. Checking updated vector store...")
        updated_store_info = indexer.get_vector_store_info()
        print(f"   Vector store exists: {updated_store_info['exists']}")
        print(f"   Total documents: {updated_store_info['total_documents']}")
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up temporary file
        if os.path.exists(sample_file):
            os.unlink(sample_file)
            print(f"\n🧹 Cleaned up temporary file: {sample_file}")

def test_column_detection():
    """Test column detection with various column name formats"""
    print("\n🧪 Testing Column Detection")
    print("=" * 50)
    
    # Test different column name variations
    test_cases = [
        (['Requirement', 'Response'], ('Requirement', 'Response')),
        (['question', 'answer'], ('question', 'answer')),
        (['RFP_Requirements', 'Our_Response'], ('RFP_Requirements', 'Our_Response')),
        (['Item', 'Solution'], ('Item', 'Solution')),
        (['Query', 'Reply'], ('Query', 'Reply')),
        (['Task', 'Description'], ('Task', 'Description')),
    ]
    
    indexer = RFPResponseIndexer()
    
    for i, (columns, expected) in enumerate(test_cases, 1):
        # Create test DataFrame
        df = pd.DataFrame({
            columns[0]: [f'Test requirement {i}'],
            columns[1]: [f'Test response {i}'],
            'Extra_Column': ['Extra data']
        })
        
        req_col, resp_col = indexer.detect_columns(df)
        print(f"{i}. Columns {columns} -> Detected: ({req_col}, {resp_col})")
        
        if (req_col, resp_col) == expected:
            print("   ✅ Correct detection")
        else:
            print("   ❌ Incorrect detection")

if __name__ == "__main__":
    print("🚀 Starting RFP Response Indexer Tests")
    print("=" * 60)
    
    # Test column detection
    test_column_detection()
    
    # Test main functionality
    success = test_rfp_indexer()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("\nNext steps:")
        print("1. Run the Streamlit app: streamlit run src/app/streamlit_app.py")
        print("2. Go to the 'Index RFP Responses' tab")
        print("3. Upload an Excel file with Requirement and Response columns")
        print("4. The responses will be added to your vector store for future use")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)