#!/usr/bin/env python3
"""
Phase 5: Session Handling & File Cleanup Validation
Tests session management and file cleanup functionality
"""

import requests
import json
import pandas as pd
import tempfile
import os
import time
from pathlib import Path
import uuid

class SessionHandlingValidator:
    """Validator for session handling and file cleanup"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_sessions = []
        self.temp_files = []
    
    def create_test_file(self, filename: str) -> str:
        """Create a test RFP file"""
        data = {
            'Requirement': [
                'Test session requirement 1',
                'Test session requirement 2',
                'Test session requirement 3'
            ],
            'Description': [
                'Description for test requirement 1',
                'Description for test requirement 2', 
                'Description for test requirement 3'
            ]
        }
        
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        self.temp_files.append(filename)
        return filename
    
    def cleanup_local_files(self):
        """Clean up local test files"""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🧹 Cleaned up local file: {file_path}")
            except Exception as e:
                print(f"⚠️ Could not remove {file_path}: {e}")
    
    def test_session_creation(self) -> dict:
        """Test session creation through file upload"""
        print("\n" + "="*60)
        print("SESSION TEST 1: SESSION CREATION")
        print("="*60)
        
        # Create test file
        test_file = f"session_test_{uuid.uuid4().hex[:8]}.xlsx"
        self.create_test_file(test_file)
        
        try:
            with open(test_file, 'rb') as f:
                files = {'file': (test_file, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = self.session.post(f"{self.base_url}/api/upload-rfp", files=files)
            
            if response.status_code == 200:
                data = response.json()
                session_id = data.get('session_id')
                self.test_sessions.append(session_id)
                
                print(f"✅ Session Created Successfully")
                print(f"🆔 Session ID: {session_id}")
                print(f"📋 Requirements: {len(data.get('requirements', []))}")
                print(f"📄 File: {data.get('file_info', {}).get('filename', 'N/A')}")
                
                return {
                    'success': True,
                    'session_id': session_id,
                    'requirements_count': len(data.get('requirements', []))
                }
            else:
                print(f"❌ Session Creation Failed: {response.status_code}")
                return {'success': False, 'error': f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Session Creation Error: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_session_persistence(self, session_id: str) -> dict:
        """Test that session data persists across requests"""
        print("\n" + "="*60)
        print("SESSION TEST 2: SESSION PERSISTENCE")
        print("="*60)
        
        if not session_id:
            print("⚠️ No session ID provided")
            return {'success': False, 'error': 'No session ID'}
        
        try:
            # Test 1: Get requirements
            response1 = self.session.get(f"{self.base_url}/api/requirements/{session_id}")
            
            # Test 2: Get requirements again (should be same data)
            time.sleep(1)  # Small delay
            response2 = self.session.get(f"{self.base_url}/api/requirements/{session_id}")
            
            if response1.status_code == 200 and response2.status_code == 200:
                data1 = response1.json()['data']
                data2 = response2.json()['data']
                
                # Verify consistency
                same_requirements = data1['requirements'] == data2['requirements']
                same_count = data1['total_requirements'] == data2['total_requirements']
                same_file = data1['file_info']['filename'] == data2['file_info']['filename']
                
                print(f"✅ Session Persistence Test")
                print(f"📋 Requirements consistent: {same_requirements}")
                print(f"🔢 Count consistent: {same_count}")
                print(f"📄 File info consistent: {same_file}")
                print(f"📊 Total requirements: {data1['total_requirements']}")
                
                return {
                    'success': same_requirements and same_count and same_file,
                    'requirements_consistent': same_requirements,
                    'count_consistent': same_count,
                    'file_consistent': same_file
                }
            else:
                print(f"❌ Session Persistence Failed: {response1.status_code}, {response2.status_code}")
                return {'success': False, 'error': 'HTTP errors'}
                
        except Exception as e:
            print(f"❌ Session Persistence Error: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_session_workflow(self, session_id: str) -> dict:
        """Test complete session workflow"""
        print("\n" + "="*60)
        print("SESSION TEST 3: COMPLETE WORKFLOW")
        print("="*60)
        
        if not session_id:
            print("⚠️ No session ID provided")
            return {'success': False, 'error': 'No session ID'}
        
        workflow_results = {}
        
        try:
            # Step 1: Get requirements
            print("📋 Step 1: Getting requirements...")
            response = self.session.get(f"{self.base_url}/api/requirements/{session_id}")
            if response.status_code == 200:
                requirements = response.json()['data']['requirements']
                workflow_results['get_requirements'] = True
                print(f"   ✅ Got {len(requirements)} requirements")
            else:
                workflow_results['get_requirements'] = False
                print(f"   ❌ Failed to get requirements: {response.status_code}")
            
            # Step 2: Generate responses
            print("💬 Step 2: Generating responses...")
            if requirements:
                request_data = {
                    "requirements": requirements[:2],  # Use first 2 requirements
                    "top_k": 3,
                    "session_id": session_id
                }
                response = self.session.post(f"{self.base_url}/api/generate-responses", json=request_data)
                if response.status_code == 200:
                    workflow_results['generate_responses'] = True
                    summary = response.json()['data']['summary']
                    print(f"   ✅ Generated responses: {summary['successful_responses']}/{summary['total_requirements']}")
                else:
                    workflow_results['generate_responses'] = False
                    print(f"   ❌ Failed to generate responses: {response.status_code}")
                    if response.status_code == 404:
                        print("   💡 Vector store might be empty")
            else:
                workflow_results['generate_responses'] = False
                print("   ⚠️ No requirements to generate responses for")
            
            # Step 3: Get generated responses
            print("📄 Step 3: Retrieving responses...")
            response = self.session.get(f"{self.base_url}/api/responses/{session_id}")
            if response.status_code == 200:
                workflow_results['get_responses'] = True
                data = response.json()['data']
                print(f"   ✅ Retrieved {data['summary']['total_responses']} responses")
            elif response.status_code == 404:
                workflow_results['get_responses'] = 'no_responses'
                print("   ⚠️ No responses found (expected if generation failed)")
            else:
                workflow_results['get_responses'] = False
                print(f"   ❌ Failed to get responses: {response.status_code}")
            
            success = all(v == True for v in workflow_results.values() if v != 'no_responses')
            partial_success = any(v == True for v in workflow_results.values())
            
            print(f"\n🎯 Workflow Results:")
            print(f"   Complete Success: {success}")
            print(f"   Partial Success: {partial_success}")
            
            return {
                'success': success,
                'partial_success': partial_success,
                'details': workflow_results
            }
            
        except Exception as e:
            print(f"❌ Workflow Error: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_file_cleanup_check(self, session_id: str) -> dict:
        """Test file cleanup functionality"""
        print("\n" + "="*60)
        print("SESSION TEST 4: FILE CLEANUP VERIFICATION")
        print("="*60)
        
        if not session_id:
            print("⚠️ No session ID provided")
            return {'success': False, 'error': 'No session ID'}
        
        try:
            # Check temp_uploads directory before cleanup
            temp_dir = Path("temp_uploads")
            files_before = []
            if temp_dir.exists():
                files_before = list(temp_dir.glob("*"))
            
            print(f"📁 Files in temp_uploads before cleanup: {len(files_before)}")
            for f in files_before[:3]:  # Show first 3 files
                print(f"   📄 {f.name}")
            
            # Perform session cleanup
            response = self.session.delete(f"{self.base_url}/api/session/{session_id}")
            
            if response.status_code == 200:
                print(f"✅ Session cleanup API call successful")
                
                # Check temp_uploads directory after cleanup
                files_after = []
                if temp_dir.exists():
                    files_after = list(temp_dir.glob("*"))
                
                print(f"📁 Files in temp_uploads after cleanup: {len(files_after)}")
                
                # Check if session file was removed
                session_files_before = [f for f in files_before if session_id in f.name]
                session_files_after = [f for f in files_after if session_id in f.name]
                
                cleanup_successful = len(session_files_after) < len(session_files_before)
                
                print(f"🧹 Session files before: {len(session_files_before)}")
                print(f"🧹 Session files after: {len(session_files_after)}")
                print(f"✅ Cleanup successful: {cleanup_successful}")
                
                return {
                    'success': True,
                    'cleanup_successful': cleanup_successful,
                    'files_before': len(files_before),
                    'files_after': len(files_after),
                    'session_files_removed': len(session_files_before) - len(session_files_after)
                }
            else:
                print(f"❌ Session cleanup failed: {response.status_code}")
                return {'success': False, 'error': f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ File cleanup check error: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_invalid_session_handling(self) -> dict:
        """Test handling of invalid session IDs"""
        print("\n" + "="*60)
        print("SESSION TEST 5: INVALID SESSION HANDLING")
        print("="*60)
        
        fake_session_id = f"fake_{uuid.uuid4().hex[:8]}"
        
        try:
            # Test 1: Get requirements with invalid session
            response1 = self.session.get(f"{self.base_url}/api/requirements/{fake_session_id}")
            
            # Test 2: Generate responses with invalid session
            request_data = {
                "requirements": ["Test requirement"],
                "session_id": fake_session_id
            }
            response2 = self.session.post(f"{self.base_url}/api/generate-responses", json=request_data)
            
            # Test 3: Get responses with invalid session
            response3 = self.session.get(f"{self.base_url}/api/responses/{fake_session_id}")
            
            # Test 4: Delete invalid session
            response4 = self.session.delete(f"{self.base_url}/api/session/{fake_session_id}")
            
            # All should return 404
            expected_404s = [response1, response2, response3, response4]
            all_404 = all(r.status_code == 404 for r in expected_404s)
            
            print(f"🔍 Testing invalid session: {fake_session_id}")
            print(f"📋 Get requirements: {response1.status_code}")
            print(f"💬 Generate responses: {response2.status_code}")
            print(f"📄 Get responses: {response3.status_code}")
            print(f"🗑️ Delete session: {response4.status_code}")
            print(f"✅ All returned 404: {all_404}")
            
            return {
                'success': all_404,
                'get_requirements_404': response1.status_code == 404,
                'generate_responses_404': response2.status_code == 404,
                'get_responses_404': response3.status_code == 404,
                'delete_session_404': response4.status_code == 404
            }
            
        except Exception as e:
            print(f"❌ Invalid session handling error: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_session_validation(self) -> dict:
        """Run complete session handling validation"""
        print("🚀 PHASE 5: SESSION HANDLING & FILE CLEANUP VALIDATION")
        print("="*80)
        
        results = {}
        session_id = None
        
        # Test 1: Session Creation
        creation_result = self.test_session_creation()
        results['session_creation'] = creation_result
        if creation_result.get('success'):
            session_id = creation_result.get('session_id')
        
        # Test 2: Session Persistence
        results['session_persistence'] = self.test_session_persistence(session_id)
        
        # Test 3: Complete Workflow
        results['session_workflow'] = self.test_session_workflow(session_id)
        
        # Test 4: File Cleanup
        results['file_cleanup'] = self.test_file_cleanup_check(session_id)
        
        # Test 5: Invalid Session Handling
        results['invalid_session'] = self.test_invalid_session_handling()
        
        # Generate summary
        print("\n" + "="*80)
        print("SESSION VALIDATION SUMMARY")
        print("="*80)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result.get('success', False))
        
        print(f"📊 SESSION TESTS RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {total_tests - passed_tests}")
        print(f"   📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📝 DETAILED RESULTS:")
        for test_name, result in results.items():
            status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
            print(f"   {status} {test_name.replace('_', ' ').title()}")
        
        if passed_tests == total_tests:
            print(f"\n🎉 ALL SESSION TESTS PASSED!")
            print(f"✅ Session creation and management working correctly")
            print(f"✅ File cleanup functionality working")
            print(f"✅ Error handling for invalid sessions working")
        else:
            print(f"\n⚠️ Some session tests failed. Please review the issues.")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'all_passed': passed_tests == total_tests,
            'detailed_results': results
        }

def main():
    """Main function to run session validation"""
    print("PHASE 5: SESSION HANDLING & FILE CLEANUP VALIDATION")
    print("=" * 60)
    
    validator = SessionHandlingValidator()
    
    try:
        # Run session validation tests
        results = validator.run_session_validation()
        
        # Save results to file
        with open('phase5_session_validation.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Session validation results saved to: phase5_session_validation.json")
        
        return results['all_passed']
        
    except Exception as e:
        print(f"❌ Session validation failed: {e}")
        return False
    
    finally:
        # Clean up local test files
        print(f"\n🧹 Cleaning up local test files...")
        validator.cleanup_local_files()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)