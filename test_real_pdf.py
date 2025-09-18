#!/usr/bin/env python3
"""
Test the real PDF with the improved extraction
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent))

from src.ingestion.requirement_extractor import RequirementExtractor

def test_real_pdf():
    """Test with the real PDF file to see clean extraction"""
    
    extractor = RequirementExtractor()
    pdf_path = "/Users/tejan/Documents/Projects/Local-RAG-App/local-rag-app/data/raw/Test_rfp - Sheet1.pdf"
    
    print("📄 Testing Real PDF Extraction")
    print("=" * 50)
    
    try:
        requirements = extractor.extract_from_file(pdf_path)
        
        print(f"✅ Extracted {len(requirements)} requirements\n")
        
        for i, req in enumerate(requirements, 1):
            print(f"{i:2d}. {req}")
            print("-" * 80)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_pdf()