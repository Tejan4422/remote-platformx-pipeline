#!/usr/bin/env python3
"""
Simple test script for the FastAPI server
"""
import requests
import time
import subprocess
import sys
import os
from pathlib import Path

def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing FastAPI Server...")
    
    try:
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test vector store status
        print("\n2. Testing vector store status...")
        response = requests.get(f"{base_url}/api/vector-store/status", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test file upload (if test file exists)
        test_file_path = Path("data/raw/Test_rfp - Sheet1.pdf")
        if test_file_path.exists():
            print("\n3. Testing file upload...")
            with open(test_file_path, 'rb') as f:
                files = {'file': (test_file_path.name, f, 'application/pdf')}
                response = requests.post(f"{base_url}/api/upload-rfp", files=files, timeout=30)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   Session ID: {result['session_id']}")
                    print(f"   Requirements found: {len(result['requirements'])}")
                    if result['requirements']:
                        print(f"   First requirement: {result['requirements'][0][:100]}...")
                    
                    # Test getting requirements
                    session_id = result['session_id']
                    print(f"\n4. Testing get requirements for session {session_id[:8]}...")
                    response = requests.get(f"{base_url}/api/requirements/{session_id}", timeout=5)
                    print(f"   Status: {response.status_code}")
                    
                    # Test generate responses endpoint
                    if response.status_code == 200 and result['requirements']:
                        print(f"\n4.1. Testing generate responses...")
                        # Use first 2 requirements for testing
                        test_requirements = result['requirements'][:2]
                        generate_data = {
                            "requirements": test_requirements,
                            "top_k": 3,
                            "model": "llama3",
                            "session_id": session_id
                        }
                        response = requests.post(f"{base_url}/api/generate-responses", json=generate_data, timeout=60)
                        print(f"   Status: {response.status_code}")
                        if response.status_code == 200:
                            gen_result = response.json()
                            print(f"   Generated responses: {gen_result['data']['summary']['successful_responses']}/{gen_result['data']['summary']['total_requirements']}")
                            
                            # Test get responses endpoint
                            print(f"\n4.2. Testing get responses...")
                            response = requests.get(f"{base_url}/api/responses/{session_id}", timeout=5)
                            print(f"   Status: {response.status_code}")
                        else:
                            print(f"   Error: {response.text}")
                    
                    # Test cleanup
                    print(f"\n5. Testing session cleanup...")
                    response = requests.delete(f"{base_url}/api/session/{session_id}", timeout=5)
                    print(f"   Status: {response.status_code}")
                    print(f"   Response: {response.json()}")
                else:
                    print(f"   Error: {response.text}")
        else:
            print(f"\n3. Skipping file upload test - {test_file_path} not found")
        
        # Test direct query endpoint
        print("\n6. Testing direct query endpoint...")
        query_data = {
            "query": "What are the main technical requirements?",
            "top_k": 3,
            "model": "llama3"
        }
        response = requests.post(f"{base_url}/api/query", json=query_data, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Query: {result['data']['query']}")
            print(f"   Response: {result['data']['response'][:200]}...")
        else:
            print(f"   Response: {response.text}")
        
        print("\n✅ All available tests passed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_file_upload_with_curl():
    """Generate curl command for testing file upload"""
    test_file_path = Path("data/raw/Test_rfp - Sheet1.pdf")
    if test_file_path.exists():
        curl_command = f'''curl -X POST "http://localhost:8000/api/upload-rfp" \\
     -H "accept: application/json" \\
     -H "Content-Type: multipart/form-data" \\
     -F "file=@{test_file_path}"'''
        
        print("\n📋 Curl command to test file upload:")
        print(curl_command)
    else:
        print(f"\n❌ Test file not found: {test_file_path}")

if __name__ == "__main__":
    success = test_api()
    
    if not success:
        print("\n💡 To test manually:")
        test_file_upload_with_curl()
        print("\n📖 API Documentation: http://localhost:8000/docs")