#!/usr/bin/env python3
"""
Complete Workflow Test - Test the full RFP processing workflow
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8001"

def test_complete_rfp_workflow():
    """Test the complete RFP processing workflow"""
    print("🚀 Testing Complete RFP Workflow")
    print("="*50)
    
    # Step 1: Check vector store status
    print("\n1. Checking Vector Store Status...")
    response = requests.get(f"{BASE_URL}/api/vector-store/status")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Vector Store Status: {data['data']['total_documents']} documents indexed")
        has_knowledge_base = data['data']['exists']
    else:
        print("❌ Failed to check vector store status")
        return False
    
    # Step 2: Upload RFP document
    print("\n2. Uploading RFP Document...")
    test_file_path = Path("data/raw/Test_rfp - Sheet1.pdf")
    if not test_file_path.exists():
        print(f"❌ Test file not found: {test_file_path}")
        return False
    
    with open(test_file_path, 'rb') as f:
        files = {'file': (test_file_path.name, f, 'application/pdf')}
        response = requests.post(f"{BASE_URL}/api/upload-rfp", files=files)
    
    if response.status_code == 200:
        upload_data = response.json()
        session_id = upload_data['session_id']
        requirements = upload_data['requirements']
        print(f"✅ Upload successful: {len(requirements)} requirements extracted")
        print(f"📋 Session ID: {session_id}")
    else:
        print(f"❌ Upload failed: {response.status_code}")
        return False
    
    # Step 3: Get requirements details
    print("\n3. Retrieving Requirements Details...")
    response = requests.get(f"{BASE_URL}/api/requirements/{session_id}")
    if response.status_code == 200:
        req_data = response.json()
        detailed_requirements = req_data['data']['requirements']
        print(f"✅ Retrieved {len(detailed_requirements)} detailed requirements")
        
        # Display requirements
        for i, req in enumerate(detailed_requirements[:3], 1):  # Show first 3
            print(f"  {i}. {req[:100]}...")
    else:
        print(f"❌ Failed to retrieve requirements: {response.status_code}")
        return False
    
    # Step 4: Test direct query (if knowledge base exists)
    if has_knowledge_base:
        print("\n4. Testing Direct Query...")
        query_data = {
            "query": "What are your data security measures?",
            "top_k": 3,
            "model": "llama3"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/query", 
            json=query_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            query_result = response.json()
            print("✅ Direct query successful")
            print(f"📊 Quality Score: {query_result['data'].get('quality_score', 'N/A')}")
        else:
            print(f"❌ Direct query failed: {response.status_code}")
    else:
        print("\n4. ⚠️ Skipping direct query - no knowledge base available")
    
    # Step 5: Generate responses (if knowledge base exists)
    if has_knowledge_base:
        print("\n5. Generating Responses...")
        # Use first 2 requirements for testing
        test_requirements = detailed_requirements[:2]
        
        request_data = {
            "requirements": test_requirements,
            "top_k": 3,
            "model": "llama3",
            "session_id": session_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/generate-responses", 
            json=request_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            gen_data = response.json()
            print("✅ Response generation successful")
            print(f"📊 Success Rate: {gen_data['data']['summary']['success_rate']:.1f}%")
            print(f"📝 Generated {gen_data['data']['summary']['successful_responses']} responses")
        else:
            print(f"❌ Response generation failed: {response.status_code}")
            return False
        
        # Step 6: Retrieve generated responses
        print("\n6. Retrieving Generated Responses...")
        response = requests.get(f"{BASE_URL}/api/responses/{session_id}")
        if response.status_code == 200:
            resp_data = response.json()
            responses = resp_data['data']['responses']
            print(f"✅ Retrieved {len(responses)} responses")
            
            # Show sample response
            if responses and responses[0]['status'] == 'success':
                sample_resp = responses[0]
                print(f"📄 Sample Response Quality: {sample_resp.get('quality_score', 'N/A')}")
                print(f"📝 Sample Answer: {sample_resp['answer'][:150]}...")
        else:
            print(f"❌ Failed to retrieve responses: {response.status_code}")
    else:
        print("\n5-6. ⚠️ Skipping response generation - no knowledge base available")
    
    # Step 7: Clean up session
    print("\n7. Cleaning Up Session...")
    response = requests.delete(f"{BASE_URL}/api/session/{session_id}")
    if response.status_code == 200:
        print("✅ Session cleaned up successfully")
    else:
        print(f"⚠️ Session cleanup failed: {response.status_code}")
    
    print("\n" + "="*50)
    print("🎉 Complete Workflow Test Finished!")
    
    return True

def analyze_missing_frontend_features():
    """Analyze what features are missing in the frontend"""
    print("\n📋 Missing Frontend Features Analysis")
    print("="*50)
    
    missing_features = [
        {
            "feature": "Requirements Display & Editor",
            "description": "Show extracted requirements in expandable cards with edit capability",
            "importance": "High",
            "frontend_implementation": "Cards/accordions with text editing"
        },
        {
            "feature": "RAG Configuration Settings",
            "description": "Allow users to configure top_k and model selection",
            "importance": "Medium", 
            "frontend_implementation": "Settings panel with sliders/dropdowns"
        },
        {
            "feature": "Response Generation Interface",
            "description": "Generate responses button with progress tracking",
            "importance": "High",
            "frontend_implementation": "Button with loading states and progress bars"
        },
        {
            "feature": "Quality Metrics Display",
            "description": "Show quality scores and breakdown for each response",
            "importance": "High",
            "frontend_implementation": "Metrics cards with score visualization"
        },
        {
            "feature": "Response Preview & Management",
            "description": "Display generated responses with context sources",
            "importance": "High",
            "frontend_implementation": "Response cards with expandable context"
        },
        {
            "feature": "Batch Processing Options",
            "description": "Handle large requirement sets with batch processing",
            "importance": "Medium",
            "frontend_implementation": "Pagination or batch size controls"
        },
        {
            "feature": "Download/Export Functionality", 
            "description": "Export results as Excel/PDF with original structure",
            "importance": "High",
            "frontend_implementation": "Download buttons with file generation"
        },
        {
            "feature": "Session Management",
            "description": "Manage multiple sessions and cleanup",
            "importance": "Medium",
            "frontend_implementation": "Session history and cleanup controls"
        }
    ]
    
    for i, feature in enumerate(missing_features, 1):
        print(f"\n{i}. {feature['feature']} [{feature['importance']} Priority]")
        print(f"   Description: {feature['description']}")
        print(f"   Implementation: {feature['frontend_implementation']}")
    
    print(f"\n📊 Total Missing Features: {len(missing_features)}")
    high_priority = len([f for f in missing_features if f['importance'] == 'High'])
    print(f"🔴 High Priority: {high_priority}")
    print(f"🟡 Medium Priority: {len(missing_features) - high_priority}")

if __name__ == "__main__":
    # Test the complete workflow
    success = test_complete_rfp_workflow()
    
    if success:
        # Analyze missing features
        analyze_missing_frontend_features()
        
        print("\n" + "="*50)
        print("📝 RECOMMENDATIONS FOR FRONTEND UI:")
        print("="*50)
        print("1. Add requirements display page after upload")
        print("2. Implement response generation interface")
        print("3. Add quality metrics visualization")
        print("4. Create download/export functionality")
        print("5. Add RAG configuration options")
        print("6. Implement session management")