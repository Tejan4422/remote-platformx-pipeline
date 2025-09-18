#!/usr/bin/env python3
"""
Test script for the RFP Response Generator system
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

def test_requirement_extraction():
    """Test requirement extraction functionality"""
    print("Testing requirement extraction...")
    
    from src.ingestion.requirement_extractor import RequirementExtractor
    
    # Test with sample text
    sample_text = """
    Requirements for this RFP:
    
    1. Describe your company's experience with cloud migrations.
    2. Explain how you ensure data security during transitions.
    3. What is your approach to project management and timelines?
    4. Please provide details about your team's qualifications.
    """
    
    extractor = RequirementExtractor()
    requirements = extractor._extract_requirements(sample_text)
    
    print(f"Extracted {len(requirements)} requirements:")
    for i, req in enumerate(requirements, 1):
        print(f"{i}. {req}")
    
    return len(requirements) > 0

def test_output_generation():
    """Test output generation functionality"""
    print("\nTesting output generation...")
    
    from src.app.output_generator import OutputGenerator
    from src.app.pdf_generator import PDFGenerator
    
    # Sample results
    sample_results = [
        {
            "requirement": "Describe your company's experience with cloud migrations.",
            "response": "Our company has extensive experience with cloud migrations, having successfully completed over 200 migrations across various industries including healthcare, finance, and manufacturing. We specialize in AWS, Azure, and GCP platforms.",
            "status": "success"
        },
        {
            "requirement": "Explain how you ensure data security during transitions.",
            "response": "We implement a comprehensive security framework that includes end-to-end encryption, multi-factor authentication, regular security audits, and compliance with industry standards such as SOC 2, GDPR, and HIPAA.",
            "status": "success"
        }
    ]
    
    try:
        # Test Excel generation
        output_gen = OutputGenerator()
        excel_bytes = output_gen.generate_excel_bytes(sample_results)
        print(f"✅ Excel generation successful ({len(excel_bytes)} bytes)")
        
        # Test PDF generation
        pdf_gen = PDFGenerator()
        pdf_bytes = pdf_gen.generate_pdf_bytes(sample_results)
        print(f"✅ PDF generation successful ({len(pdf_bytes)} bytes)")
        
        # Test CSV generation
        csv_bytes = output_gen.generate_csv_bytes(sample_results)
        print(f"✅ CSV generation successful ({len(csv_bytes)} bytes)")
        
        return True
    except Exception as e:
        print(f"❌ Output generation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running RFP Response Generator Tests\n")
    
    tests_passed = 0
    total_tests = 2
    
    # Test requirement extraction
    if test_requirement_extraction():
        print("✅ Requirement extraction test passed")
        tests_passed += 1
    else:
        print("❌ Requirement extraction test failed")
    
    # Test output generation
    if test_output_generation():
        print("✅ Output generation test passed")
        tests_passed += 1
    else:
        print("❌ Output generation test failed")
    
    print(f"\n📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The system is ready to use.")
        print("\n🚀 To run the Streamlit app:")
        print("streamlit run src/app/streamlit_app.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()