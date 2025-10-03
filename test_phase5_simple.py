#!/usr/bin/env python3
"""
Phase 5: Simple Test Requests
Quick and simple test requests for manual validation
"""

import requests
import json
from typing import Dict

class SimpleTestRequests:
    """Simple test requests for manual validation"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
    
    def test_health(self):
        """Simple health check test"""
        print("🏥 Testing Health Check...")
        try:
            response = requests.get(f"{self.base_url}/health")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API is running - Version: {data['data']['version']}")
            else:
                print(f"❌ Health check failed")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def test_vector_store_status(self):
        """Simple vector store status test"""
        print("\n📊 Testing Vector Store Status...")
        try:
            response = requests.get(f"{self.base_url}/api/vector-store/status")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()['data']
                print(f"✅ Store exists: {data['exists']}")
                print(f"📚 Documents: {data['total_documents']}")
                print(f"🎯 Ready: {data['ready_for_queries']}")
            else:
                print(f"❌ Status check failed")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def test_vector_store_stats(self):
        """Simple vector store stats test"""
        print("\n📈 Testing Vector Store Stats...")
        try:
            response = requests.get(f"{self.base_url}/api/vector-store/stats")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()['data']
                vs = data['vector_store']
                storage = data['storage_summary']
                print(f"✅ Store exists: {vs['exists']}")
                print(f"📚 Documents: {vs['total_documents']}")
                print(f"🔢 Dimension: {vs['vector_dimension']}")
                print(f"💾 Size: {storage['total_size_mb']} MB")
            else:
                print(f"❌ Stats check failed")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def test_simple_query(self):
        """Simple direct query test"""
        print("\n🔍 Testing Simple Query...")
        try:
            query_data = {
                "query": "What is your project management approach?",
                "top_k": 2
            }
            response = requests.post(f"{self.base_url}/api/query", json=query_data)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()['data']
                print(f"✅ Query successful")
                print(f"💡 Answer length: {len(data['answer'])}")
                print(f"📊 Quality: {data.get('quality_score', 'N/A')}")
            else:
                print(f"❌ Query failed: {response.status_code}")
                if response.status_code == 404:
                    print("   💡 Vector store might be empty")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def run_quick_tests(self):
        """Run all quick tests"""
        print("🚀 PHASE 5: SIMPLE TEST REQUESTS")
        print("="*50)
        
        self.test_health()
        self.test_vector_store_status()
        self.test_vector_store_stats()
        self.test_simple_query()
        
        print("\n✅ Quick tests completed!")

# Sample cURL commands for manual testing
SAMPLE_CURL_COMMANDS = """
# PHASE 5: Sample cURL Commands for Manual Testing

## 1. Health Check
curl -X GET "http://localhost:8001/health" \\
  -H "accept: application/json"

## 2. Vector Store Status
curl -X GET "http://localhost:8001/api/vector-store/status" \\
  -H "accept: application/json"

## 3. Vector Store Statistics
curl -X GET "http://localhost:8001/api/vector-store/stats" \\
  -H "accept: application/json"

## 4. Direct Query
curl -X POST "http://localhost:8001/api/query" \\
  -H "accept: application/json" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "What is your project management methodology?",
    "top_k": 3
  }'

## 5. Upload RFP Document (replace test.xlsx with actual file)
curl -X POST "http://localhost:8001/api/upload-rfp" \\
  -H "accept: application/json" \\
  -H "Content-Type: multipart/form-data" \\
  -F "file=@test.xlsx"

## 6. Get Requirements (replace SESSION_ID)
curl -X GET "http://localhost:8001/api/requirements/SESSION_ID" \\
  -H "accept: application/json"

## 7. Generate Responses (replace SESSION_ID)
curl -X POST "http://localhost:8001/api/generate-responses" \\
  -H "accept: application/json" \\
  -H "Content-Type: application/json" \\
  -d '{
    "requirements": ["What is your experience?", "How do you ensure quality?"],
    "top_k": 3,
    "session_id": "SESSION_ID"
  }'

## 8. Get Generated Responses (replace SESSION_ID)
curl -X GET "http://localhost:8001/api/responses/SESSION_ID" \\
  -H "accept: application/json"

## 9. Index RFP Responses (replace responses.xlsx with actual file)
curl -X POST "http://localhost:8001/api/index-responses" \\
  -H "accept: application/json" \\
  -H "Content-Type: multipart/form-data" \\
  -F "file=@responses.xlsx"

## 10. Clean Session (replace SESSION_ID)
curl -X DELETE "http://localhost:8001/api/session/SESSION_ID" \\
  -H "accept: application/json"
"""

if __name__ == "__main__":
    # Run simple tests
    tester = SimpleTestRequests()
    tester.run_quick_tests()
    
    # Save cURL commands to file
    with open('phase5_curl_commands.txt', 'w') as f:
        f.write(SAMPLE_CURL_COMMANDS)
    
    print(f"\n📄 Sample cURL commands saved to: phase5_curl_commands.txt")