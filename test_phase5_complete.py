#!/usr/bin/env python3
"""
Phase 5: Complete System Testing & Validation
Tests all endpoints individually and validates full system workflow
"""

import requests
import json
import pandas as pd
import tempfile
import os
import time
from pathlib import Path
from typing import Dict, Any, List
import uuid

class Phase5SystemTester:
    """Comprehensive system tester for all API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_session_ids = []  # Track session IDs for cleanup
        self.test_files = []  # Track temporary files for cleanup
        
    def cleanup_test_data(self):
        """Clean up any test data created during testing"""
        # Clean up test files
        for file_path in self.test_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🧹 Cleaned up test file: {file_path}")
            except Exception as e:
                print(f"⚠️ Could not remove {file_path}: {e}")
        
        # Clean up sessions via API
        for session_id in self.test_session_ids:
            try:
                response = self.session.delete(f"{self.base_url}/api/session/{session_id}")
                if response.status_code == 200:
                    print(f"🧹 Cleaned up session: {session_id}")
                else:
                    print(f"⚠️ Could not clean session {session_id}: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Error cleaning session {session_id}: {e}")
    
    def create_test_rfp_file(self, filename: str, num_requirements: int = 5) -> str:
        """Create a test RFP file with sample requirements"""
        requirements = [
            "Describe your company's experience with similar projects",
            "What is your project management methodology?",
            "Explain your quality assurance process",
            "Detail your security and compliance measures",
            "Provide information about your team's qualifications",
            "What is your pricing structure and payment terms?",
            "How do you handle project risks and mitigation?",
            "Describe your technical architecture approach",
            "What support and maintenance do you provide?",
            "Explain your implementation timeline and milestones"
        ]
        
        data = {
            'Requirement': requirements[:num_requirements],
            'Description': [f"Detailed requirement {i+1} for RFP testing" for i in range(num_requirements)]
        }
        
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        self.test_files.append(filename)
        return filename
    
    def create_test_responses_file(self, filename: str, num_pairs: int = 3) -> str:
        """Create a test RFP responses file for indexing"""
        data = {
            'Requirement': [
                'What is your experience with cloud infrastructure?',
                'How do you ensure data security?',
                'Describe your development methodology'
            ][:num_pairs],
            'Response': [
                'We have 10+ years of experience with AWS, Azure, and GCP cloud platforms, having migrated over 50 enterprise applications to cloud infrastructure.',
                'We implement enterprise-grade security including encryption at rest and in transit, multi-factor authentication, regular security audits, and SOC 2 compliance.',
                'We follow Agile/Scrum methodology with 2-week sprints, daily standups, continuous integration, and automated testing to ensure high-quality deliverables.'
            ][:num_pairs]
        }
        
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        self.test_files.append(filename)
        return filename
    
    # =======================================================================
    # PHASE 5 TEST 1: INDIVIDUAL ENDPOINT TESTING
    # =======================================================================
    
    def test_1_health_check(self) -> Dict[str, Any]:
        """Test 1: Health check endpoint"""
        print("\n" + "="*60)
        print("TEST 1: HEALTH CHECK ENDPOINT")
        print("="*60)
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            result = {
                'endpoint': '/health',
                'method': 'GET',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_time': response.elapsed.total_seconds(),
                'response': response.json() if response.status_code == 200 else response.text
            }
            
            if result['success']:
                data = result['response']['data']
                print(f"✅ Health Check: PASS")
                print(f"⏱️ Response Time: {result['response_time']:.3f}s")
                print(f"🏷️ Version: {data.get('version', 'N/A')}")
                print(f"📅 Timestamp: {data.get('timestamp', 'N/A')}")
            else:
                print(f"❌ Health Check: FAIL ({result['status_code']})")
            
            return result
            
        except Exception as e:
            print(f"❌ Health Check: ERROR - {e}")
            return {'success': False, 'error': str(e)}
    
    def test_2_vector_store_status(self) -> Dict[str, Any]:
        """Test 2: Vector store status endpoint"""
        print("\n" + "="*60)
        print("TEST 2: VECTOR STORE STATUS ENDPOINT")
        print("="*60)
        
        try:
            response = self.session.get(f"{self.base_url}/api/vector-store/status")
            result = {
                'endpoint': '/api/vector-store/status',
                'method': 'GET',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_time': response.elapsed.total_seconds(),
                'response': response.json() if response.status_code == 200 else response.text
            }
            
            if result['success']:
                data = result['response']['data']
                print(f"✅ Vector Store Status: PASS")
                print(f"⏱️ Response Time: {result['response_time']:.3f}s")
                print(f"📊 Store Exists: {data.get('exists', False)}")
                print(f"📚 Total Documents: {data.get('total_documents', 0)}")
                print(f"🎯 Ready for Queries: {data.get('ready_for_queries', False)}")
            else:
                print(f"❌ Vector Store Status: FAIL ({result['status_code']})")
            
            return result
            
        except Exception as e:
            print(f"❌ Vector Store Status: ERROR - {e}")
            return {'success': False, 'error': str(e)}
    
    def test_3_upload_rfp(self) -> Dict[str, Any]:
        """Test 3: Upload RFP document endpoint"""
        print("\n" + "="*60)
        print("TEST 3: UPLOAD RFP DOCUMENT ENDPOINT")
        print("="*60)
        
        # Create test file
        test_file = f"test_rfp_{uuid.uuid4().hex[:8]}.xlsx"
        self.create_test_rfp_file(test_file, 3)
        
        try:
            with open(test_file, 'rb') as f:
                files = {'file': (test_file, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = self.session.post(f"{self.base_url}/api/upload-rfp", files=files)
            
            result = {
                'endpoint': '/api/upload-rfp',
                'method': 'POST',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_time': response.elapsed.total_seconds(),
                'response': response.json() if response.status_code == 200 else response.text
            }
            
            if result['success']:
                data = result['response']
                session_id = data.get('session_id')
                if session_id:
                    self.test_session_ids.append(session_id)
                
                print(f"✅ Upload RFP: PASS")
                print(f"⏱️ Response Time: {result['response_time']:.3f}s")
                print(f"🆔 Session ID: {session_id}")
                print(f"📋 Requirements Found: {len(data.get('requirements', []))}")
                print(f"📄 File: {data.get('file_info', {}).get('filename', 'N/A')}")
                
                # Store session ID for later tests
                result['session_id'] = session_id
            else:
                print(f"❌ Upload RFP: FAIL ({result['status_code']})")
            
            return result
            
        except Exception as e:
            print(f"❌ Upload RFP: ERROR - {e}")
            return {'success': False, 'error': str(e)}
    
    def test_4_get_requirements(self, session_id: str = None) -> Dict[str, Any]:
        """Test 4: Get requirements for session endpoint"""
        print("\n" + "="*60)
        print("TEST 4: GET REQUIREMENTS ENDPOINT")
        print("="*60)
        
        if not session_id:
            print("⚠️ No session ID provided, skipping test")
            return {'success': False, 'error': 'No session ID'}
        
        try:
            response = self.session.get(f"{self.base_url}/api/requirements/{session_id}")
            result = {
                'endpoint': f'/api/requirements/{session_id}',
                'method': 'GET',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_time': response.elapsed.total_seconds(),
                'response': response.json() if response.status_code == 200 else response.text
            }
            
            if result['success']:
                data = result['response']['data']
                print(f"✅ Get Requirements: PASS")
                print(f"⏱️ Response Time: {result['response_time']:.3f}s")
                print(f"📋 Requirements Count: {data.get('total_requirements', 0)}")
                print(f"📄 File: {data.get('file_info', {}).get('filename', 'N/A')}")
                print(f"⏰ Upload Time: {data.get('file_info', {}).get('upload_time', 'N/A')}")
            else:
                print(f"❌ Get Requirements: FAIL ({result['status_code']})")
            
            return result
            
        except Exception as e:
            print(f"❌ Get Requirements: ERROR - {e}")
            return {'success': False, 'error': str(e)}
    
    def test_5_direct_query(self) -> Dict[str, Any]:
        """Test 5: Direct query endpoint"""
        print("\n" + "="*60)
        print("TEST 5: DIRECT QUERY ENDPOINT")
        print("="*60)
        
        try:
            query_data = {
                "query": "What is your approach to project management?",
                "top_k": 3
            }
            
            response = self.session.post(f"{self.base_url}/api/query", json=query_data)
            result = {
                'endpoint': '/api/query',
                'method': 'POST',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_time': response.elapsed.total_seconds(),
                'response': response.json() if response.status_code == 200 else response.text
            }
            
            if result['success']:
                data = result['response']['data']
                print(f"✅ Direct Query: PASS")
                print(f"⏱️ Response Time: {result['response_time']:.3f}s")
                print(f"❓ Query: {data.get('query', 'N/A')}")
                print(f"💡 Answer Length: {len(data.get('answer', ''))}")
                print(f"📊 Quality Score: {data.get('quality_score', 'N/A')}")
                print(f"🏷️ Quality Status: {data.get('quality_status', 'N/A')}")
            else:
                print(f"❌ Direct Query: FAIL ({result['status_code']})")
                if result['status_code'] == 404:
                    print("   💡 This might be expected if vector store is empty")
            
            return result
            
        except Exception as e:
            print(f"❌ Direct Query: ERROR - {e}")
            return {'success': False, 'error': str(e)}
    
    def test_6_generate_responses(self, session_id: str = None) -> Dict[str, Any]:
        """Test 6: Generate responses endpoint"""
        print("\n" + "="*60)
        print("TEST 6: GENERATE RESPONSES ENDPOINT")
        print("="*60)
        
        if not session_id:
            print("⚠️ No session ID provided, skipping test")
            return {'success': False, 'error': 'No session ID'}
        
        try:
            # Use sample requirements for testing
            request_data = {
                "requirements": [
                    "What is your experience with cloud platforms?",
                    "How do you ensure project quality?"
                ],
                "top_k": 3,
                "session_id": session_id
            }
            
            response = self.session.post(f"{self.base_url}/api/generate-responses", json=request_data)
            result = {
                'endpoint': '/api/generate-responses',
                'method': 'POST',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_time': response.elapsed.total_seconds(),
                'response': response.json() if response.status_code == 200 else response.text
            }
            
            if result['success']:
                data = result['response']['data']
                summary = data.get('summary', {})
                print(f"✅ Generate Responses: PASS")
                print(f"⏱️ Response Time: {result['response_time']:.3f}s")
                print(f"📋 Total Requirements: {summary.get('total_requirements', 0)}")
                print(f"✅ Successful Responses: {summary.get('successful_responses', 0)}")
                print(f"❌ Failed Responses: {summary.get('failed_responses', 0)}")
                print(f"📊 Success Rate: {summary.get('success_rate', 0):.1f}%")
            else:
                print(f"❌ Generate Responses: FAIL ({result['status_code']})")
                if result['status_code'] == 404:
                    print("   💡 This might be expected if vector store is empty")
            
            return result
            
        except Exception as e:
            print(f"❌ Generate Responses: ERROR - {e}")
            return {'success': False, 'error': str(e)}
    
    def test_7_get_responses(self, session_id: str = None) -> Dict[str, Any]:
        """Test 7: Get responses for session endpoint"""
        print("\n" + "="*60)
        print("TEST 7: GET RESPONSES ENDPOINT")
        print("="*60)
        
        if not session_id:
            print("⚠️ No session ID provided, skipping test")
            return {'success': False, 'error': 'No session ID'}
        
        try:
            response = self.session.get(f"{self.base_url}/api/responses/{session_id}")
            result = {
                'endpoint': f'/api/responses/{session_id}',
                'method': 'GET',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_time': response.elapsed.total_seconds(),
                'response': response.json() if response.status_code == 200 else response.text
            }
            
            if result['success']:
                data = result['response']['data']
                summary = data.get('summary', {})
                print(f"✅ Get Responses: PASS")
                print(f"⏱️ Response Time: {result['response_time']:.3f}s")
                print(f"📋 Total Requirements: {summary.get('total_requirements', 0)}")
                print(f"💬 Total Responses: {summary.get('total_responses', 0)}")
                print(f"✅ Successful Responses: {summary.get('successful_responses', 0)}")
                print(f"📊 Success Rate: {summary.get('success_rate', 0):.1f}%")
            else:
                print(f"❌ Get Responses: FAIL ({result['status_code']})")
                if result['status_code'] == 404:
                    print("   💡 This is expected if no responses were generated yet")
            
            return result
            
        except Exception as e:
            print(f"❌ Get Responses: ERROR - {e}")
            return {'success': False, 'error': str(e)}
    
    def test_8_index_responses(self) -> Dict[str, Any]:
        """Test 8: Index RFP responses endpoint (Phase 4)"""
        print("\n" + "="*60)
        print("TEST 8: INDEX RFP RESPONSES ENDPOINT")
        print("="*60)
        
        # Create test responses file
        test_file = f"test_responses_{uuid.uuid4().hex[:8]}.xlsx"
        self.create_test_responses_file(test_file, 2)
        
        try:
            with open(test_file, 'rb') as f:
                files = {'file': (test_file, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = self.session.post(f"{self.base_url}/api/index-responses", files=files)
            
            result = {
                'endpoint': '/api/index-responses',
                'method': 'POST',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_time': response.elapsed.total_seconds(),
                'response': response.json() if response.status_code == 200 else response.text
            }
            
            if result['success']:
                data = result['response']['data']
                indexing_results = data.get('indexing_results', {})
                print(f"✅ Index RFP Responses: PASS")
                print(f"⏱️ Response Time: {result['response_time']:.3f}s")
                print(f"📚 Documents Added: {indexing_results.get('documents_added', 0)}")
                print(f"🔗 RFP Pairs Found: {indexing_results.get('rfp_pairs_found', 0)}")
                print(f"📈 Final Document Count: {indexing_results.get('final_document_count', 0)}")
                print(f"📋 Requirement Column: {indexing_results.get('requirement_column', 'N/A')}")
                print(f"💬 Response Column: {indexing_results.get('response_column', 'N/A')}")
            else:
                print(f"❌ Index RFP Responses: FAIL ({result['status_code']})")
            
            return result
            
        except Exception as e:
            print(f"❌ Index RFP Responses: ERROR - {e}")
            return {'success': False, 'error': str(e)}
    
    def test_9_vector_store_stats(self) -> Dict[str, Any]:
        """Test 9: Vector store statistics endpoint (Phase 4)"""
        print("\n" + "="*60)
        print("TEST 9: VECTOR STORE STATISTICS ENDPOINT")
        print("="*60)
        
        try:
            response = self.session.get(f"{self.base_url}/api/vector-store/stats")
            result = {
                'endpoint': '/api/vector-store/stats',
                'method': 'GET',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_time': response.elapsed.total_seconds(),
                'response': response.json() if response.status_code == 200 else response.text
            }
            
            if result['success']:
                data = result['response']['data']
                vector_store = data.get('vector_store', {})
                storage = data.get('storage_summary', {})
                capabilities = data.get('capabilities', {})
                
                print(f"✅ Vector Store Stats: PASS")
                print(f"⏱️ Response Time: {result['response_time']:.3f}s")
                print(f"📊 Store Exists: {vector_store.get('exists', False)}")
                print(f"📚 Total Documents: {vector_store.get('total_documents', 0)}")
                print(f"🔢 Vector Dimension: {vector_store.get('vector_dimension', 0)}")
                print(f"💾 Storage Size: {storage.get('total_size_mb', 0)} MB")
                print(f"🎯 Ready for Queries: {capabilities.get('ready_for_queries', False)}")
                print(f"🔍 Supports Search: {capabilities.get('supports_similarity_search', False)}")
            else:
                print(f"❌ Vector Store Stats: FAIL ({result['status_code']})")
            
            return result
            
        except Exception as e:
            print(f"❌ Vector Store Stats: ERROR - {e}")
            return {'success': False, 'error': str(e)}
    
    def test_10_session_cleanup(self, session_id: str = None) -> Dict[str, Any]:
        """Test 10: Session cleanup endpoint"""
        print("\n" + "="*60)
        print("TEST 10: SESSION CLEANUP ENDPOINT")
        print("="*60)
        
        if not session_id:
            print("⚠️ No session ID provided, skipping test")
            return {'success': False, 'error': 'No session ID'}
        
        try:
            response = self.session.delete(f"{self.base_url}/api/session/{session_id}")
            result = {
                'endpoint': f'/api/session/{session_id}',
                'method': 'DELETE',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_time': response.elapsed.total_seconds(),
                'response': response.json() if response.status_code == 200 else response.text
            }
            
            if result['success']:
                print(f"✅ Session Cleanup: PASS")
                print(f"⏱️ Response Time: {result['response_time']:.3f}s")
                print(f"🧹 Session {session_id} cleaned up successfully")
                
                # Remove from our tracking list
                if session_id in self.test_session_ids:
                    self.test_session_ids.remove(session_id)
            else:
                print(f"❌ Session Cleanup: FAIL ({result['status_code']})")
            
            return result
            
        except Exception as e:
            print(f"❌ Session Cleanup: ERROR - {e}")
            return {'success': False, 'error': str(e)}
    
    # =======================================================================
    # PHASE 5 MAIN TEST RUNNER
    # =======================================================================
    
    def run_all_individual_tests(self) -> Dict[str, Any]:
        """Run all individual endpoint tests"""
        print("🚀 PHASE 5: COMPLETE SYSTEM TESTING & VALIDATION")
        print("="*80)
        print("Testing all endpoints individually...")
        
        results = {}
        session_id = None
        
        # Test 1: Health Check
        results['health_check'] = self.test_1_health_check()
        
        # Test 2: Vector Store Status
        results['vector_store_status'] = self.test_2_vector_store_status()
        
        # Test 3: Upload RFP (creates session)
        upload_result = self.test_3_upload_rfp()
        results['upload_rfp'] = upload_result
        if upload_result.get('success'):
            session_id = upload_result.get('session_id')
        
        # Test 4: Get Requirements (uses session)
        results['get_requirements'] = self.test_4_get_requirements(session_id)
        
        # Test 5: Direct Query
        results['direct_query'] = self.test_5_direct_query()
        
        # Test 6: Generate Responses (uses session)
        results['generate_responses'] = self.test_6_generate_responses(session_id)
        
        # Test 7: Get Responses (uses session)
        results['get_responses'] = self.test_7_get_responses(session_id)
        
        # Test 8: Index RFP Responses (Phase 4)
        results['index_responses'] = self.test_8_index_responses()
        
        # Test 9: Vector Store Stats (Phase 4)
        results['vector_store_stats'] = self.test_9_vector_store_stats()
        
        # Test 10: Session Cleanup
        results['session_cleanup'] = self.test_10_session_cleanup(session_id)
        
        return results
    
    def generate_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        print("\n" + "="*80)
        print("PHASE 5 TEST SUMMARY")
        print("="*80)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result.get('success', False))
        failed_tests = total_tests - passed_tests
        
        # Categorize tests
        core_endpoints = ['health_check', 'upload_rfp', 'get_requirements', 'direct_query', 'generate_responses', 'get_responses']
        phase4_endpoints = ['index_responses', 'vector_store_stats', 'vector_store_status']
        utility_endpoints = ['session_cleanup']
        
        core_passed = sum(1 for endpoint in core_endpoints if results.get(endpoint, {}).get('success', False))
        phase4_passed = sum(1 for endpoint in phase4_endpoints if results.get(endpoint, {}).get('success', False))
        utility_passed = sum(1 for endpoint in utility_endpoints if results.get(endpoint, {}).get('success', False))
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 BY CATEGORY:")
        print(f"   🏗️ Core Endpoints: {core_passed}/{len(core_endpoints)} passed")
        print(f"   🆕 Phase 4 Endpoints: {phase4_passed}/{len(phase4_endpoints)} passed")
        print(f"   🔧 Utility Endpoints: {utility_passed}/{len(utility_endpoints)} passed")
        
        print(f"\n📝 DETAILED RESULTS:")
        for test_name, result in results.items():
            status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
            endpoint = result.get('endpoint', f'/{test_name}')
            method = result.get('method', 'GET')
            response_time = result.get('response_time', 0)
            print(f"   {status} {method} {endpoint} ({response_time:.3f}s)")
        
        # Performance Analysis
        avg_response_time = sum(r.get('response_time', 0) for r in results.values()) / len(results)
        max_response_time = max(r.get('response_time', 0) for r in results.values())
        
        print(f"\n⏱️ PERFORMANCE:")
        print(f"   Average Response Time: {avg_response_time:.3f}s")
        print(f"   Maximum Response Time: {max_response_time:.3f}s")
        
        # Generate recommendations
        recommendations = []
        if failed_tests > 0:
            recommendations.append("🔍 Review failed tests and check server logs")
        if max_response_time > 5.0:
            recommendations.append("⚡ Consider optimizing slow endpoints")
        if phase4_passed < len(phase4_endpoints):
            recommendations.append("📚 Verify vector store setup for Phase 4 endpoints")
        
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   {rec}")
        
        summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'core_endpoints_passed': core_passed,
            'phase4_endpoints_passed': phase4_passed,
            'utility_endpoints_passed': utility_passed,
            'avg_response_time': avg_response_time,
            'max_response_time': max_response_time,
            'recommendations': recommendations,
            'all_tests_passed': failed_tests == 0
        }
        
        return summary

def main():
    """Main function to run Phase 5 testing"""
    print("PHASE 5: TESTING & VALIDATION")
    print("=" * 50)
    
    tester = Phase5SystemTester()
    
    try:
        # Run all individual endpoint tests
        results = tester.run_all_individual_tests()
        
        # Generate comprehensive summary
        summary = tester.generate_test_summary(results)
        
        # Save results to file
        output_data = {
            'phase': 'Phase 5: Testing & Validation',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': summary,
            'detailed_results': results
        }
        
        with open('phase5_test_results.json', 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: phase5_test_results.json")
        
        # Overall conclusion
        if summary['all_tests_passed']:
            print("\n🎉 ALL TESTS PASSED! System is ready for production.")
        else:
            print(f"\n⚠️ {summary['failed_tests']} test(s) failed. Please review and fix issues.")
        
        return summary['all_tests_passed']
        
    except Exception as e:
        print(f"❌ Phase 5 testing failed: {e}")
        return False
    
    finally:
        # Clean up test data
        print(f"\n🧹 Cleaning up test data...")
        tester.cleanup_test_data()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)