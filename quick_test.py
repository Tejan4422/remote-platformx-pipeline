#!/usr/bin/env python3
"""
Quick test for requirement extraction
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent))

def test_extraction_with_sample():
    """Test with sample RFP content"""
    from src.ingestion.requirement_extractor import RequirementExtractor
    
    sample_rfp = """
    SECTION 3: TECHNICAL REQUIREMENTS
    
    The following requirements must be addressed in your proposal:
    
    1. Please describe your company's experience with cloud migration projects in the last 3 years.
    
    2. What is your approach to ensuring data security during migration processes?
    
    3. Describe your project management methodology and how you handle timeline adherence.
    
    4. Please provide details about your team's technical certifications and expertise.
    
    5. How do you handle post-migration support and maintenance?
    
    Additional Questions:
    
    A. What backup and disaster recovery solutions do you offer?
    B. Describe your 24/7 support capabilities.
    C. What are your pricing models for ongoing services?
    """
    
    extractor = RequirementExtractor()
    requirements = extractor._extract_numbered_questions(sample_rfp)
    
    print(f"Sample RFP Test:")
    print(f"Extracted {len(requirements)} requirements:")
    print("-" * 50)
    
    for i, req in enumerate(requirements, 1):
        print(f"{i}. {req}")
        print()
    
    return len(requirements) > 0

def test_output_only():
    """Test output generation without RAG"""
    from src.app.output_generator import OutputGenerator
    from src.app.pdf_generator import PDFGenerator
    
    sample_results = [
        {
            "requirement": "Please describe your company's experience with cloud migration projects.",
            "response": "Our company has extensive experience with cloud migration, having successfully completed over 150 projects in the past three years. We specialize in AWS, Azure, and Google Cloud platforms, with expertise in lift-and-shift, re-platforming, and cloud-native transformations. Our team has migrated enterprise workloads ranging from simple web applications to complex ERP systems, ensuring minimal downtime and seamless transitions.",
            "status": "success"
        },
        {
            "requirement": "What is your approach to ensuring data security during migration?",
            "response": "We implement a comprehensive security framework that includes end-to-end encryption, multi-factor authentication, and continuous monitoring. Our approach follows industry standards like SOC 2, GDPR, and HIPAA compliance. We conduct thorough security assessments before migration, implement zero-trust architecture principles, and provide detailed audit trails throughout the process.",
            "status": "success"
        }
    ]
    
    try:
        output_gen = OutputGenerator()
        excel_bytes = output_gen.generate_excel_bytes(sample_results)
        print(f"✅ Excel generation: {len(excel_bytes)} bytes")
        
        pdf_gen = PDFGenerator()
        pdf_bytes = pdf_gen.generate_pdf_bytes(sample_results)
        print(f"✅ PDF generation: {len(pdf_bytes)} bytes")
        
        return True
    except Exception as e:
        print(f"❌ Output generation error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Quick RFP System Test\n")
    
    success_count = 0
    
    if test_extraction_with_sample():
        print("✅ Requirement extraction test passed")
        success_count += 1
    else:
        print("❌ Requirement extraction test failed")
    
    print()
    
    if test_output_only():
        print("✅ Output generation test passed")
        success_count += 1
    else:
        print("❌ Output generation test failed")
    
    print(f"\n📊 Results: {success_count}/2 tests passed")
    
    if success_count == 2:
        print("\n🎉 Core components working! Try the Streamlit app:")
        print("streamlit run src/app/streamlit_app.py")
    else:
        print("\n⚠️ Some issues detected. Check error messages above.")