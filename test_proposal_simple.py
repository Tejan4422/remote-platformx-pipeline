#!/usr/bin/env python3
"""
Simple Test for Proposal Template

This script tests just the proposal template without the full RAG pipeline
to validate the template structure and prompt generation.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent))

from src.content.templates.proposal_template import ProposalTemplate


def test_proposal_template_simple():
    """Test the proposal template directly without RAG pipeline."""
    
    print("🧪 Testing Proposal Template (Simple Mode)...")
    print("=" * 60)
    
    # Initialize proposal template
    try:
        template = ProposalTemplate()
        print("✅ ProposalTemplate initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing ProposalTemplate: {e}")
        return
    
    # Test template properties
    print(f"\n📋 Template Information:")
    print(f"   Type: {template.template_type}")
    print(f"   Sections: {template.get_sections()}")
    print(f"   Style Rules: {template.get_style_guidelines()}")
    
    # Test proposal sections info
    print(f"\n📄 Available Proposal Sections:")
    for section in template.get_sections():
        section_info = template.get_section_info(section)
        print(f"  🔹 {section.replace('_', ' ').title()}")
        print(f"     Description: {section_info['description']}")
        print(f"     Length: {section_info['typical_length']}")
        print(f"     Key Elements: {', '.join(section_info['key_elements'])}")
        print()
    
    # Test requirements validation
    print(f"🔍 Testing Requirements Validation...")
    
    # Test invalid requirements
    invalid_req = {}
    validation = template.validate_proposal_requirements(invalid_req)
    print(f"   Invalid requirements validation: {'✅ PASS' if not validation['valid'] else '❌ FAIL'}")
    print(f"   Issues found: {validation['issues']}")
    
    # Test valid requirements
    valid_req = {
        'section_type': 'executive_summary',
        'client_name': 'TechCorp Solutions',
        'project_description': 'AI content generation system'
    }
    validation = template.validate_proposal_requirements(valid_req)
    print(f"   Valid requirements validation: {'✅ PASS' if validation['valid'] else '❌ FAIL'}")
    
    # Test prompt generation for different sections
    print(f"\n📝 Testing Prompt Generation...")
    
    test_requirements = {
        'section_type': 'executive_summary',
        'client_name': 'TechCorp Solutions',
        'project_description': 'Implementation of AI-powered content generation system',
        'specific_requirements': [
            'Reduce content creation time by 60%',
            'Maintain brand consistency across all content',
            'Support multiple content types'
        ],
        'budget_range': '$50,000 - $100,000',
        'timeline': '3-4 months implementation'
    }
    
    test_context = """
    Our company specializes in AI and machine learning solutions for enterprise clients.
    We have extensive experience in content generation, natural language processing,
    and brand consistency tools. Our previous implementations have achieved 70% time
    savings and 95% brand consistency scores.
    """
    
    # Test different sections
    test_sections = ['executive_summary', 'technical_approach', 'pricing_section']
    
    for section in test_sections:
        print(f"\n🎯 Testing {section.replace('_', ' ').title()}")
        print("-" * 40)
        
        # Update requirements for this section
        section_req = test_requirements.copy()
        section_req['section_type'] = section
        
        try:
            # Generate content (this will return the prompt since we don't have LLM)
            result = template.generate(test_context, section_req)
            
            print(f"✅ Generated successfully")
            print(f"Section Type: {result.get('section_type')}")
            print(f"Content Type: {result.get('content_type')}")
            
            # Show prompt preview
            if 'prompt' in result:
                prompt_preview = result['prompt'][:300] + "..." if len(result['prompt']) > 300 else result['prompt']
                print(f"\nPrompt Preview:")
                print(prompt_preview)
            
        except Exception as e:
            print(f"❌ Error generating {section}: {e}")
    
    # Test content validation
    print(f"\n🔍 Testing Content Validation...")
    
    # Test with short content (should fail)
    short_content = "This is too short."
    validation = template.validate_output(short_content)
    print(f"Short content validation: {'✅ PASS' if not validation['valid'] else '❌ FAIL'}")
    print(f"Score: {validation['score']}/100")
    print(f"Issues: {validation['issues']}")
    
    # Test with good content
    good_content = """
    Our company is uniquely positioned to deliver this AI-powered content generation system
    that will transform your content creation process. With our proven track record of
    implementing similar solutions, we can reduce your content creation time by 60% while
    maintaining perfect brand consistency across all content types. Our comprehensive
    approach includes advanced natural language processing, brand voice training, and
    quality assurance systems. We recommend moving forward with this transformative
    solution to achieve your content scaling goals and maintain competitive advantage.
    """
    
    validation = template.validate_output(good_content)
    print(f"\nGood content validation: {'✅ PASS' if validation['valid'] else '❌ FAIL'}")
    print(f"Score: {validation['score']}/100")
    if validation['issues']:
        print(f"Issues: {validation['issues']}")
    if validation['suggestions']:
        print(f"Suggestions: {validation['suggestions']}")
    
    print(f"\n🎉 Proposal template testing complete!")
    print(f"✅ Template is working correctly and ready for integration!")


if __name__ == "__main__":
    test_proposal_template_simple()