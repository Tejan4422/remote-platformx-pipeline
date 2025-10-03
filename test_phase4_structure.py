#!/usr/bin/env python3
"""
Simplified test for Phase 4 API endpoints structure
Tests endpoint availability without requiring full model loading
"""

import requests
import json
from typing import Dict, Any

class SimplePhase4Tester:
    """Simple test client for Phase 4 endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
    
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
    
    def test_endpoint_availability(self) -> Dict[str, Any]:
        """Test if our new endpoints are available in the API"""
        print("\n🔍 Testing endpoint availability...")
        
        endpoints_to_test = [
            '/api/vector-store/stats',
            '/api/index-responses',
            '/api/upload-historical-data'
        ]
        
        results = {}
        
        for endpoint in endpoints_to_test:
            try:
                # Use OPTIONS to check if endpoint exists
                response = self.session.options(f"{self.base_url}{endpoint}")
                if response.status_code == 405:  # Method not allowed means endpoint exists
                    results[endpoint] = {'exists': True, 'status': 'Available'}
                    print(f"✅ {endpoint}: Available")
                elif response.status_code == 404:
                    results[endpoint] = {'exists': False, 'status': 'Not Found'}
                    print(f"❌ {endpoint}: Not Found")
                else:
                    results[endpoint] = {'exists': True, 'status': f'Status {response.status_code}'}
                    print(f"⚠️ {endpoint}: Status {response.status_code}")
            except Exception as e:
                results[endpoint] = {'exists': False, 'error': str(e)}
                print(f"❌ {endpoint}: Error - {e}")
        
        return results
    
    def test_openapi_schema(self) -> Dict[str, Any]:
        """Test if endpoints are in OpenAPI schema"""
        print("\n📋 Testing OpenAPI schema...")
        try:
            response = self.session.get(f"{self.base_url}/openapi.json")
            if response.status_code != 200:
                return {'success': False, 'error': f'OpenAPI schema not available: {response.status_code}'}
            
            schema = response.json()
            paths = schema.get('paths', {})
            
            expected_endpoints = [
                '/api/vector-store/stats',
                '/api/index-responses',
                '/api/upload-historical-data'
            ]
            
            found_endpoints = []
            missing_endpoints = []
            
            for endpoint in expected_endpoints:
                if endpoint in paths:
                    found_endpoints.append(endpoint)
                    print(f"✅ {endpoint}: Found in schema")
                else:
                    missing_endpoints.append(endpoint)
                    print(f"❌ {endpoint}: Missing from schema")
            
            # Show all available endpoints that contain our keywords
            print("\n📍 Available API endpoints:")
            for path in sorted(paths.keys()):
                if any(keyword in path for keyword in ['api', 'vector', 'index', 'upload']):
                    methods = list(paths[path].keys())
                    print(f"  {path}: {', '.join(methods)}")
            
            return {
                'success': len(found_endpoints) > 0,
                'found_endpoints': found_endpoints,
                'missing_endpoints': missing_endpoints,
                'total_endpoints': len(paths),
                'schema_available': True
            }
            
        except Exception as e:
            print(f"❌ OpenAPI schema test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_simple_tests(self) -> Dict[str, Any]:
        """Run simplified structure tests"""
        print("🚀 Starting Phase 4 Endpoint Structure Tests")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Health check
        results['health_check'] = self.test_health_check()
        
        # Test 2: Endpoint availability
        results['endpoint_availability'] = self.test_endpoint_availability()
        
        # Test 3: OpenAPI schema
        results['openapi_schema'] = self.test_openapi_schema()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        health_ok = results['health_check'].get('success', False)
        schema_ok = results['openapi_schema'].get('success', False)
        
        print(f"✅ Health Check: {'PASS' if health_ok else 'FAIL'}")
        print(f"📋 OpenAPI Schema: {'PASS' if schema_ok else 'FAIL'}")
        
        if schema_ok:
            found = len(results['openapi_schema']['found_endpoints'])
            missing = len(results['openapi_schema']['missing_endpoints'])
            print(f"🎯 Endpoints Found: {found}/3")
            
            if found == 3:
                print("🎉 All Phase 4 endpoints are properly registered!")
            elif found > 0:
                print("⚠️ Some Phase 4 endpoints are missing from the schema.")
            else:
                print("❌ No Phase 4 endpoints found in schema.")
        
        return results

def main():
    """Main function to run the structure tests"""
    print("Phase 4: API Structure Testing")
    print("==============================")
    
    # Check if server is running
    tester = SimplePhase4Tester()
    
    try:
        results = tester.run_simple_tests()
        
        # Save results to file
        with open('phase4_structure_test.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Test results saved to: phase4_structure_test.json")
        
        # Return success based on basic connectivity
        return results['health_check'].get('success', False)
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)