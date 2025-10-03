#!/usr/bin/env python3
"""
Test script for Phase 4: Knowledge Base API endpoints
Tests the new RFP indexing and vector store management endpoints
"""

import requests
import json
import pandas as pd
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

class Phase4APITester:
    """Test client for Phase 4 Knowledge Base APIs"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def create_sample_rfp_data(self, filename: str) -> str:
        """Create a sample RFP response Excel file for testing"""
        # Sample RFP response data
        data = {
            'Requirement': [
                'Provide details about your company structure and ownership',
                'Describe your project management methodology',
                'What is your approach to quality assurance and testing?',
                'Explain your data security and privacy measures',
                'Describe your team qualifications and experience',
                'What is your pricing model and cost structure?',
                'Provide references from similar projects',
                'Describe your technical architecture and infrastructure',
                'What is your implementation timeline and methodology?',
                'Explain your support and maintenance approach'
            ],
            'Response': [
                'Our company is a privately held organization established in 2010 with headquarters in San Francisco. We have a flat organizational structure that promotes innovation and quick decision-making.',
                'We follow Agile methodology with Scrum framework. Our projects are managed in 2-week sprints with daily standups, sprint planning, and retrospective meetings to ensure continuous improvement.',
                'We implement a comprehensive QA process including automated testing, manual testing, and code reviews. Our QA team works in parallel with development to ensure quality throughout the development lifecycle.',
                'We implement enterprise-grade security measures including encryption at rest and in transit, regular security audits, SOC 2 compliance, and strict access controls with multi-factor authentication.',
                'Our team consists of senior developers with 5+ years experience, certified project managers, and specialized domain experts. Team members hold relevant certifications in their respective fields.',
                'We offer flexible pricing models including fixed-price, time-and-materials, and dedicated team models. Our rates are competitive and transparent with no hidden costs.',
                'We have successfully delivered 50+ similar projects for Fortune 500 companies. Client references are available upon request with documented case studies and testimonials.',
                'Our architecture follows microservices patterns with cloud-native design. We use containerization, API-first approach, and implement scalable, fault-tolerant systems.',
                'Our implementation follows a phased approach: Discovery (2 weeks), Design (3 weeks), Development (8-12 weeks), Testing (2 weeks), and Deployment (1 week) with regular client checkpoints.',
                'We provide 24/7 support, regular maintenance updates, performance monitoring, and dedicated account management. Our support includes bug fixes, feature enhancements, and training.'
            ]
        }
        
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        return filename
    
    def create_multiple_sample_files(self, count: int = 3) -> list:
        """Create multiple sample RFP files for batch testing"""
        files = []
        for i in range(count):
            # Create unique data for each file
            data = {
                'Question': [  # Different column name to test detection
                    f'File {i+1}: What is your development approach?',
                    f'File {i+1}: Describe your team structure',
                    f'File {i+1}: What are your security measures?'
                ],
                'Answer': [  # Different column name to test detection
                    f'File {i+1}: We use modern development practices with continuous integration and automated testing.',
                    f'File {i+1}: Our team consists of experienced professionals with diverse skill sets and proven track records.',
                    f'File {i+1}: We implement comprehensive security protocols including regular audits and compliance standards.'
                ]
            }
            filename = f"temp_rfp_batch_{i+1}.xlsx"
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False)
            files.append(filename)
        return files
    
    def test_health_check(self) -> Dict[str, Any]:
        """Test the health check endpoint"""
        print("🏥 Testing health check...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            result = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
            print(f"✅ Health check: {result['success']}")
            return result
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_vector_store_stats_empty(self) -> Dict[str, Any]:
        """Test vector store stats when empty"""
        print("\n📊 Testing vector store stats (empty state)...")
        try:
            response = self.session.get(f"{self.base_url}/api/vector-store/stats")
            result = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
            
            if result['success']:
                data = result['response']['data']
                print(f"📈 Vector store exists: {data['vector_store']['exists']}")
                print(f"📈 Total documents: {data['vector_store']['total_documents']}")
                print(f"📈 Storage size: {data['storage_summary']['total_size_mb']} MB")
            
            return result
        except Exception as e:
            print(f"❌ Vector store stats test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_index_rfp_responses(self) -> Dict[str, Any]:
        """Test indexing RFP responses"""
        print("\n📚 Testing RFP response indexing...")
        
        # Create sample data
        sample_file = "temp_rfp_sample.xlsx"
        self.create_sample_rfp_data(sample_file)
        
        try:
            with open(sample_file, 'rb') as f:
                files = {'file': (sample_file, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = self.session.post(f"{self.base_url}/api/index-responses", files=files)
            
            result = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
            
            if result['success']:
                data = result['response']['data']
                print(f"✅ Successfully indexed {data['indexing_results']['documents_added']} documents")
                print(f"📄 RFP pairs found: {data['indexing_results']['rfp_pairs_found']}")
                print(f"🏪 Vector store documents: {data['vector_store_info']['total_documents']}")
                print(f"📋 Requirement column: {data['indexing_results']['requirement_column']}")
                print(f"💬 Response column: {data['indexing_results']['response_column']}")
            else:
                print(f"❌ Indexing failed: {result}")
            
            # Clean up
            os.remove(sample_file)
            return result
            
        except Exception as e:
            print(f"❌ RFP indexing test failed: {e}")
            if os.path.exists(sample_file):
                os.remove(sample_file)
            return {'success': False, 'error': str(e)}
    
    def test_upload_historical_data(self) -> Dict[str, Any]:
        """Test batch upload of historical data"""
        print("\n📦 Testing historical data batch upload...")
        
        # Create multiple sample files
        sample_files = self.create_multiple_sample_files(3)
        
        try:
            files = []
            file_handles = []
            
            for filename in sample_files:
                f = open(filename, 'rb')
                file_handles.append(f)
                files.append(('files', (filename, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')))
            
            data = {'description': 'Test batch upload of historical RFP data'}
            response = self.session.post(f"{self.base_url}/api/upload-historical-data", files=files, data=data)
            
            # Close file handles
            for f in file_handles:
                f.close()
            
            result = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
            
            if result['success']:
                data = result['response']['data']
                print(f"✅ Processed {data['upload_info']['successful_files']}/{data['upload_info']['total_files']} files")
                print(f"📚 Total documents added: {data['summary']['total_documents_added']}")
                print(f"🔗 Total pairs found: {data['summary']['total_pairs_found']}")
                
                # Show processing results
                for file_result in data['processing_results']:
                    status = "✅" if file_result['success'] else "❌"
                    print(f"  {status} {file_result['filename']}: {file_result.get('documents_added', 0)} docs")
            else:
                print(f"❌ Batch upload failed: {result}")
            
            # Clean up
            for filename in sample_files:
                if os.path.exists(filename):
                    os.remove(filename)
            
            return result
            
        except Exception as e:
            print(f"❌ Historical data upload test failed: {e}")
            # Clean up
            for f in file_handles:
                try:
                    f.close()
                except:
                    pass
            for filename in sample_files:
                if os.path.exists(filename):
                    os.remove(filename)
            return {'success': False, 'error': str(e)}
    
    def test_vector_store_stats_populated(self) -> Dict[str, Any]:
        """Test vector store stats after population"""
        print("\n📊 Testing vector store stats (populated state)...")
        try:
            response = self.session.get(f"{self.base_url}/api/vector-store/stats")
            result = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
            
            if result['success']:
                data = result['response']['data']
                print(f"📈 Vector store exists: {data['vector_store']['exists']}")
                print(f"📈 Total documents: {data['vector_store']['total_documents']}")
                print(f"📈 Vector dimension: {data['vector_store']['vector_dimension']}")
                print(f"📈 Index size: {data['vector_store']['index_size']}")
                print(f"💾 Storage size: {data['storage_summary']['total_size_mb']} MB")
                print(f"🎯 Ready for queries: {data['capabilities']['ready_for_queries']}")
                
                # Show file statistics
                for file_type, stats in data['file_statistics'].items():
                    print(f"  📁 {file_type}: {stats['size_mb']} MB")
            
            return result
        except Exception as e:
            print(f"❌ Vector store stats test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_query_after_indexing(self) -> Dict[str, Any]:
        """Test querying the vector store after indexing"""
        print("\n🔍 Testing query after indexing...")
        try:
            query_data = {
                "query": "What is your approach to project management?",
                "top_k": 3
            }
            
            response = self.session.post(f"{self.base_url}/api/query", json=query_data)
            result = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
            
            if result['success']:
                data = result['response']['data']
                print(f"✅ Query successful!")
                print(f"❓ Query: {data['query']}")
                print(f"💡 Answer: {data['answer'][:200]}...")
                print(f"📊 Quality score: {data.get('quality_score', 'N/A')}")
                print(f"🏷️ Quality status: {data.get('quality_status', 'N/A')}")
            else:
                print(f"❌ Query failed: {result}")
            
            return result
            
        except Exception as e:
            print(f"❌ Query test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Phase 4 API tests"""
        print("🚀 Starting Phase 4 Knowledge Base API Tests")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Health check
        results['health_check'] = self.test_health_check()
        
        # Test 2: Vector store stats (empty)
        results['vector_store_stats_empty'] = self.test_vector_store_stats_empty()
        
        # Test 3: Index RFP responses
        results['index_rfp_responses'] = self.test_index_rfp_responses()
        
        # Test 4: Upload historical data
        results['upload_historical_data'] = self.test_upload_historical_data()
        
        # Test 5: Vector store stats (populated)
        results['vector_store_stats_populated'] = self.test_vector_store_stats_populated()
        
        # Test 6: Query after indexing
        results['query_after_indexing'] = self.test_query_after_indexing()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result.get('success', False))
        
        for test_name, result in results.items():
            status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All Phase 4 tests passed! Knowledge Base APIs are working correctly.")
        else:
            print("⚠️ Some tests failed. Please check the error messages above.")
        
        return {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'success_rate': (passed_tests / total_tests) * 100,
                'all_passed': passed_tests == total_tests
            },
            'individual_results': results
        }

def main():
    """Main function to run the tests"""
    print("Phase 4: Knowledge Base API Testing")
    print("==================================")
    
    # Check if server is running
    tester = Phase4APITester()
    
    try:
        # Run all tests
        results = tester.run_all_tests()
        
        # Save results to file
        with open('phase4_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Test results saved to: phase4_test_results.json")
        
        return results['summary']['all_passed']
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)