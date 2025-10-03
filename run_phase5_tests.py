#!/usr/bin/env python3
"""
Phase 5: Main Test Runner
Coordinates all Phase 5 testing activities
"""

import subprocess
import sys
import json
import time
from pathlib import Path

class Phase5TestRunner:
    """Main test runner for Phase 5"""
    
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.results = {}
    
    def check_server_health(self) -> bool:
        """Check if the API server is running"""
        print("🏥 Checking API server health...")
        try:
            import requests
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API server is running")
                return True
            else:
                print(f"❌ API server returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to API server: {e}")
            print(f"💡 Make sure server is running on {self.base_url}")
            return False
    
    def run_simple_tests(self) -> bool:
        """Run simple validation tests"""
        print("\n" + "="*60)
        print("RUNNING: Simple Test Requests")
        print("="*60)
        
        try:
            result = subprocess.run([
                sys.executable, 'test_phase5_simple.py'
            ], capture_output=True, text=True, timeout=60)
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            success = result.returncode == 0
            self.results['simple_tests'] = {
                'success': success,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            return success
            
        except subprocess.TimeoutExpired:
            print("❌ Simple tests timed out")
            self.results['simple_tests'] = {'success': False, 'error': 'Timeout'}
            return False
        except Exception as e:
            print(f"❌ Error running simple tests: {e}")
            self.results['simple_tests'] = {'success': False, 'error': str(e)}
            return False
    
    def run_complete_tests(self) -> bool:
        """Run complete system tests"""
        print("\n" + "="*60)
        print("RUNNING: Complete System Tests")
        print("="*60)
        
        try:
            result = subprocess.run([
                sys.executable, 'test_phase5_complete.py'
            ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            success = result.returncode == 0
            self.results['complete_tests'] = {
                'success': success,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            return success
            
        except subprocess.TimeoutExpired:
            print("❌ Complete tests timed out")
            self.results['complete_tests'] = {'success': False, 'error': 'Timeout'}
            return False
        except Exception as e:
            print(f"❌ Error running complete tests: {e}")
            self.results['complete_tests'] = {'success': False, 'error': str(e)}
            return False
    
    def run_session_validation(self) -> bool:
        """Run session handling validation"""
        print("\n" + "="*60)
        print("RUNNING: Session Handling Validation")
        print("="*60)
        
        try:
            result = subprocess.run([
                sys.executable, 'test_phase5_session_validation.py'
            ], capture_output=True, text=True, timeout=180)  # 3 minute timeout
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            success = result.returncode == 0
            self.results['session_validation'] = {
                'success': success,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            return success
            
        except subprocess.TimeoutExpired:
            print("❌ Session validation timed out")
            self.results['session_validation'] = {'success': False, 'error': 'Timeout'}
            return False
        except Exception as e:
            print(f"❌ Error running session validation: {e}")
            self.results['session_validation'] = {'success': False, 'error': str(e)}
            return False
    
    def generate_final_report(self) -> dict:
        """Generate final Phase 5 test report"""
        print("\n" + "="*80)
        print("PHASE 5: FINAL TEST REPORT")
        print("="*80)
        
        # Count successes
        total_suites = len(self.results)
        passed_suites = sum(1 for r in self.results.values() if r.get('success', False))
        failed_suites = total_suites - passed_suites
        
        print(f"📊 TEST SUITE RESULTS:")
        print(f"   Total Test Suites: {total_suites}")
        print(f"   ✅ Passed: {passed_suites}")
        print(f"   ❌ Failed: {failed_suites}")
        print(f"   📈 Success Rate: {(passed_suites/total_suites)*100:.1f}%")
        
        print(f"\n📝 SUITE BREAKDOWN:")
        for suite_name, result in self.results.items():
            status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
            suite_display = suite_name.replace('_', ' ').title()
            print(f"   {status} {suite_display}")
            
            if not result.get('success', False) and 'error' in result:
                print(f"       Error: {result['error']}")
        
        # Load detailed results from JSON files if available
        detailed_results = {}
        
        json_files = [
            'phase5_test_results.json',
            'phase5_session_validation.json'
        ]
        
        for json_file in json_files:
            if Path(json_file).exists():
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        detailed_results[json_file] = data
                except Exception as e:
                    print(f"⚠️ Could not load {json_file}: {e}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if passed_suites == total_suites:
            print("🎉 ALL PHASE 5 TESTS PASSED!")
            print("✅ Individual endpoint testing: COMPLETE")
            print("✅ Session handling validation: COMPLETE")
            print("✅ File cleanup verification: COMPLETE")
            print("✅ System ready for production!")
        elif passed_suites > 0:
            print("⚠️ PARTIAL SUCCESS")
            print(f"✅ {passed_suites} test suite(s) passed")
            print(f"❌ {failed_suites} test suite(s) failed")
            print("🔍 Review failed tests and fix issues")
        else:
            print("❌ ALL TESTS FAILED")
            print("🚨 Critical issues detected - system not ready")
            print("🔧 Review server logs and configuration")
        
        # Recommendations
        recommendations = []
        if failed_suites > 0:
            recommendations.append("🔍 Review failed test outputs for specific error details")
            recommendations.append("📊 Check server logs for additional error information")
        
        if 'simple_tests' in self.results and not self.results['simple_tests'].get('success'):
            recommendations.append("🏥 Verify API server is running and accessible")
        
        if 'session_validation' in self.results and not self.results['session_validation'].get('success'):
            recommendations.append("💾 Check file system permissions for temp_uploads directory")
        
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   {rec}")
        
        # Generate summary
        summary = {
            'phase': 'Phase 5: Testing & Validation',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_suites': total_suites,
            'passed_suites': passed_suites,
            'failed_suites': failed_suites,
            'success_rate': (passed_suites/total_suites)*100,
            'all_passed': passed_suites == total_suites,
            'suite_results': self.results,
            'detailed_results': detailed_results,
            'recommendations': recommendations
        }
        
        return summary
    
    def run_all_tests(self) -> bool:
        """Run all Phase 5 tests"""
        print("🚀 PHASE 5: TESTING & VALIDATION")
        print("="*80)
        print("Testing all endpoints individually")
        print("Creating simple test requests")
        print("Verifying session handling works")
        print("Checking file cleanup")
        print("="*80)
        
        # Check server health first
        if not self.check_server_health():
            print("\n❌ Cannot proceed with tests - API server not accessible")
            return False
        
        # Run test suites
        all_passed = True
        
        # 1. Simple tests
        if not self.run_simple_tests():
            all_passed = False
        
        # 2. Complete system tests
        if not self.run_complete_tests():
            all_passed = False
        
        # 3. Session validation
        if not self.run_session_validation():
            all_passed = False
        
        # Generate final report
        summary = self.generate_final_report()
        
        # Save summary to file
        with open('phase5_final_report.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📄 Final report saved to: phase5_final_report.json")
        
        return all_passed

def main():
    """Main function"""
    runner = Phase5TestRunner()
    success = runner.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)