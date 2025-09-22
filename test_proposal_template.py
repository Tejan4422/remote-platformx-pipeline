#!/usr/bin/env python3
"""
Quick Test for Proposal Template

This script tests the proposal template functionality to ensure
it's working correctly before integrating with the UI.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent))

from src.content.content_generator import ContentGenerator


def test_proposal_template():
    """Test the proposal template with sample requirements."""
    
    print("🧪 Testing Proposal Template...")
    print("=" * 50)
    
    # Initialize content generator
    try:
        generator = ContentGenerator()
        print("✅ Content Generator initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Content Generator: {e}")
        return
    
    # Test listing content types
    content_types = generator.list_content_types()
    print(f"📋 Available content types: {content_types}")
    
    # Test proposal sections
    proposal_sections = generator.get_proposal_sections()
    print(f"\n📄 Available proposal sections:")
    for section in proposal_sections:
        print(f"  - {section['display_name']}: {section['description']}")
    
    # Test requirements for executive summary
    test_requirements = {
        'section_type': 'executive_summary',
        'client_name': 'TechCorp Solutions',
        'project_description': 'Implementation of AI-powered content generation system',
        'specific_requirements': [
            'Reduce content creation time by 60%',
            'Maintain brand consistency across all content',
            'Support multiple content types',
            'Ensure enterprise security and compliance'
        ],
        'budget_range': '$50,000 - $100,000',
        'timeline': '3-4 months implementation'
    }
    
    print(f"\n🎯 Testing Executive Summary generation...")
    print(f"Requirements: {test_requirements}")
    
    # Test without RAG pipeline (will show prompt)
    try:
        result = generator.generate_content('proposal', test_requirements)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            if 'validation' in result:
                print(f"   Validation issues: {result['validation']}")
        else:
            print("✅ Proposal generation successful!")
            print(f"\n📝 Generated content type: {result.get('content_type')}")
            print(f"📄 Section type: {result.get('section_type')}")
            print(f"🔍 Search query: {result.get('search_query')}")
            
            # Show the prompt that would be sent to LLM
            if 'prompt' in result:
                print(f"\n📋 Generated Prompt Preview:")
                print("-" * 40)
                prompt_preview = result['prompt'][:500] + "..." if len(result['prompt']) > 500 else result['prompt']
                print(prompt_preview)
            
            # Show generated content if available
            if 'generated_content' in result:
                print(f"\n📝 Generated Content:")
                print("-" * 40)
                print(result['generated_content'])
    
    except Exception as e:
        print(f"❌ Error generating content: {e}")
    
    # Test different section types
    print(f"\n🧪 Testing different proposal sections...")
    
    section_tests = [
        'technical_approach',
        'pricing_section',
        'case_study'
    ]
    
    for section in section_tests:
        test_req = test_requirements.copy()
        test_req['section_type'] = section
        
        try:
            result = generator.generate_content('proposal', test_req)
            if 'error' not in result:
                print(f"✅ {section.replace('_', ' ').title()}: Generated successfully")
            else:
                print(f"❌ {section.replace('_', ' ').title()}: {result['error']}")
        except Exception as e:
            print(f"❌ {section.replace('_', ' ').title()}: Error - {e}")
    
    print(f"\n🎉 Proposal template testing complete!")


if __name__ == "__main__":
    test_proposal_template()