#!/usr/bin/env python3
"""
Test the enhanced requirement extraction logic with various edge cases
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent))

from src.ingestion.requirement_extractor import RequirementExtractor

def test_numbered_requirements():
    """Test extraction of various numbered requirement formats"""
    test_text = """
    SECTION 1: TECHNICAL REQUIREMENTS
    
    1. The vendor must provide a comprehensive project plan.
    
    1.1 The plan should include detailed timelines.
    1.2 The plan must identify key milestones.
    1.3 Risk mitigation strategies should be outlined.
    
    2. System performance requirements:
    
    2.1.1 Response time must be under 2 seconds.
    2.1.2 System availability should be 99.9%.
    2.1.3 The system must support 1000 concurrent users.
    
    3. Documentation requirements:
    a) User manuals must be provided.
    b) Technical documentation should be comprehensive.
    c) Training materials are required.
    """
    
    extractor = RequirementExtractor()
    requirements = extractor._extract_requirements(test_text)
    
    print("🔢 Numbered Requirements Test:")
    print(f"   Extracted {len(requirements)} requirements")
    for i, req in enumerate(requirements[:10], 1):  # Show first 10
        print(f"   {i}. {req[:80]}{'...' if len(req) > 80 else ''}")
    print()
    
    return len(requirements) > 5  # Should extract multiple requirements

def test_question_formats():
    """Test extraction of various question formats"""
    test_text = """
    PROPOSAL QUESTIONNAIRE
    
    Q1. How many years of experience does your company have in this field?
    
    Question 2: What is your approach to project management?
    
    3) Please describe your quality assurance methodology.
    
    A. Can you provide references from similar projects?
    
    B) What certifications do your team members hold?
    
    • How do you handle change requests?
    • What is your escalation process?
    • Describe your disaster recovery plan.
    """
    
    extractor = RequirementExtractor()
    requirements = extractor._extract_requirements(test_text)
    
    print("❓ Question Formats Test:")
    print(f"   Extracted {len(requirements)} requirements")
    for i, req in enumerate(requirements[:8], 1):
        print(f"   {i}. {req[:80]}{'...' if len(req) > 80 else ''}")
    print()
    
    return len(requirements) >= 6  # Should extract most questions

def test_table_extraction():
    """Test extraction from table-like structures"""
    test_text = """
    EVALUATION CRITERIA
    
    Criterion | Weight | Description
    Technical Approach | 40% | Vendor's methodology and technical solution
    Experience | 30% | Relevant project experience and qualifications
    Cost | 20% | Total cost of ownership and value proposition
    References | 10% | Quality of client references and testimonials
    
    Required Certifications:
    ISO 27001    Information Security Management
    SOC 2        Service Organization Control
    PCI DSS      Payment Card Industry Data Security
    """
    
    extractor = RequirementExtractor()
    requirements = extractor._extract_requirements(test_text)
    
    print("📊 Table Extraction Test:")
    print(f"   Extracted {len(requirements)} requirements")
    for i, req in enumerate(requirements, 1):
        print(f"   {i}. {req[:80]}{'...' if len(req) > 80 else ''}")
    print()
    
    return len(requirements) > 3  # Should extract table content

def test_ocr_errors():
    """Test handling of common OCR errors"""
    test_text = """
    REQUIREMENTS
    
    1.The vendor must provide24/7 support.
    2.System must integratewith existing infrastructure.
    3.Data migrationshould be completed within30 days.
    4.All personnelmust have securityclearance.
    
    A.What is yourcompany's approachto data security?
    B.How doyou handlecompliance requirements?
    C.Pleasedescribe yourbackup and recoveryprocedures.
    """
    
    extractor = RequirementExtractor()
    requirements = extractor._extract_requirements(test_text)
    
    print("🔧 OCR Error Handling Test:")
    print(f"   Extracted {len(requirements)} requirements")
    for i, req in enumerate(requirements, 1):
        print(f"   {i}. {req[:80]}{'...' if len(req) > 80 else ''}")
    print()
    
    return len(requirements) >= 5  # Should handle OCR errors and extract requirements

def test_mixed_formats():
    """Test extraction from documents with mixed formatting"""
    test_text = """
    REQUEST FOR PROPOSAL
    
    PART I: GENERAL REQUIREMENTS
    
    1. Company Information
    Please provide the following information about your organization:
    
    a) Years in business
    b) Number of employees
    c) Annual revenue
    d) Geographic presence
    
    SECTION 2: TECHNICAL SPECIFICATIONS
    
    The proposed solution must meet the following criteria:
    
    • Must support Windows and Linux platforms
    • Should integrate with REST APIs
    • Database compatibility with PostgreSQL and MySQL required
    • Real-time processing capabilities needed
    
    II. Project Timeline
    
    Q1: When can you begin the project?
    Q2: What is your estimated completion timeframe?
    Q3: How do you handle project delays?
    
    EVALUATION FACTORS
    
    Factor                    Weight    Description
    Technical Merit           35%       Innovation and feasibility
    Past Performance         25%       Previous project success
    Management Approach       25%       Project management methodology
    Cost                      15%       Total project cost
    """
    
    extractor = RequirementExtractor()
    requirements = extractor._extract_requirements(test_text)
    
    print("🔀 Mixed Formats Test:")
    print(f"   Extracted {len(requirements)} requirements")
    for i, req in enumerate(requirements[:15], 1):  # Show first 15
        print(f"   {i}. {req[:80]}{'...' if len(req) > 80 else ''}")
    print()
    
    return len(requirements) >= 10  # Should extract from various formats

def test_edge_cases():
    """Test edge cases and error conditions"""
    test_cases = [
        "",  # Empty text
        "   \n\n   ",  # Whitespace only
        "This is just a regular paragraph without any requirements.",  # No requirements
        "1. 2. 3. 4. 5.",  # Just numbers
        "PAGE 1\nTABLE OF CONTENTS\nREFERENCES",  # Common non-requirement content
    ]
    
    extractor = RequirementExtractor()
    
    print("🚫 Edge Cases Test:")
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            requirements = extractor._extract_requirements(test_case)
            print(f"   {i}. Empty/invalid text: {len(requirements)} requirements extracted ✓")
        except Exception as e:
            print(f"   {i}. Error handling test: Failed with {e} ❌")
            return False
    
    return True

def test_real_world_sample():
    """Test with the existing PDF file"""
    print("📄 Real World Sample Test:")
    
    try:
        extractor = RequirementExtractor()
        # Test with the existing PDF file
        pdf_path = "/Users/tejan/Documents/Projects/Local-RAG-App/local-rag-app/data/raw/Test_rfp - Sheet1.pdf"
        requirements = extractor.extract_from_file(pdf_path)
        
        print(f"   Extracted {len(requirements)} requirements from real PDF")
        
        if requirements:
            print("   Sample requirements:")
            for i, req in enumerate(requirements[:5], 1):
                print(f"   {i}. {req[:100]}{'...' if len(req) > 100 else ''}")
        
        return len(requirements) > 0
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    print("🧪 Enhanced Requirement Extraction Test Suite")
    print("=" * 60)
    
    tests = [
        ("Numbered Requirements", test_numbered_requirements),
        ("Question Formats", test_question_formats),
        ("Table Extraction", test_table_extraction),
        ("OCR Error Handling", test_ocr_errors),
        ("Mixed Formats", test_mixed_formats),
        ("Edge Cases", test_edge_cases),
        ("Real World Sample", test_real_world_sample),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} Test...")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The enhanced extraction logic is working well.")
    else:
        print("⚠️ Some tests failed. Review the extraction logic for improvements.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)