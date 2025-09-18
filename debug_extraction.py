#!/usr/bin/env python3
"""
Debug the requirement extraction to see what's going wrong
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent))

from src.ingestion.requirement_extractor import RequirementExtractor

def debug_extraction():
    """Debug the extraction process step by step"""
    
    extractor = RequirementExtractor()
    pdf_path = "/Users/tejan/Documents/Projects/Local-RAG-App/local-rag-app/data/raw/Test_rfp - Sheet1.pdf"
    
    print("🔍 Debug: Requirement Extraction Process")
    print("=" * 50)
    
    # Step 1: Extract raw text
    print("\n1️⃣ Extracting raw text from PDF...")
    try:
        raw_text = extractor._extract_text(pdf_path)
        print(f"Raw text length: {len(raw_text)} characters")
        print("\nFirst 500 characters of raw text:")
        print("-" * 40)
        print(repr(raw_text[:500]))
        print("-" * 40)
        
        # Step 2: Clean text
        print("\n2️⃣ Cleaning text...")
        cleaned_text = extractor._clean_text(raw_text)
        print(f"Cleaned text length: {len(cleaned_text)} characters")
        print("\nFirst 500 characters of cleaned text:")
        print("-" * 40)
        print(repr(cleaned_text[:500]))
        print("-" * 40)
        
        # Step 3: Show lines
        print("\n3️⃣ Text split into lines:")
        print("-" * 40)
        lines = cleaned_text.split('\n')
        for i, line in enumerate(lines[:20], 1):  # Show first 20 lines
            if line.strip():
                print(f"Line {i:2d}: {repr(line.strip())}")
        print("-" * 40)
        
        # Step 4: Test pattern extraction
        print("\n4️⃣ Testing pattern extraction...")
        pattern_reqs = extractor._extract_by_patterns(cleaned_text)
        print(f"Pattern extraction found: {len(pattern_reqs)} requirements")
        for i, req in enumerate(pattern_reqs[:10], 1):
            print(f"  {i}. {repr(req[:80])}")
        
        # Step 5: Final extraction
        print("\n5️⃣ Final extraction result:")
        requirements = extractor._extract_requirements(raw_text)
        print(f"Total requirements extracted: {len(requirements)}")
        for i, req in enumerate(requirements[:10], 1):
            print(f"  {i}. {req}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_extraction()