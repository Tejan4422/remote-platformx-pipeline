"""
Proposal Template for Business Proposal Generation

This template handles the generation of professional business proposals
including executive summaries, technical approaches, pricing sections, and more.
"""

from typing import Dict, List, Any, Optional
from .base_template import BaseTemplate


class ProposalTemplate(BaseTemplate):
    """
    Template for generating business proposals and sales documents.
    
    Supports various proposal sections like executive summaries,
    technical approaches, pricing, case studies, and team qualifications.
    """
    
    def __init__(self):
        """Initialize the proposal template with default configuration."""
        default_config = {
            'type': 'proposal',
            'structure': {
                'sections': [
                    'executive_summary',
                    'technical_approach', 
                    'pricing_section',
                    'case_study',
                    'team_qualifications',
                    'implementation_timeline',
                    'risk_mitigation'
                ],
                'required_sections': ['executive_summary', 'technical_approach'],
                'max_sections': 7
            },
            'style_rules': {
                'tone': 'professional',
                'formality': 'formal',
                'perspective': 'first_person_plural',  # "we", "our"
                'format': 'business_document',
                'persuasive_elements': True
            },
            'validation': {
                'min_words': 100,
                'max_words': 800,
                'required_elements': ['value_proposition', 'next_steps'],
                'readability_target': 'business_professional'
            },
            'prompts': self._get_default_prompts()
        }
        super().__init__(default_config)
    
    def _get_default_prompts(self) -> Dict[str, str]:
        """Get default prompt templates for each proposal section."""
        return {
            'executive_summary': """
You are writing an executive summary for a business proposal. Write a compelling, professional summary that:

1. Clearly states the value proposition
2. Highlights key benefits and outcomes
3. Demonstrates understanding of the client's needs
4. Positions your company as the ideal partner
5. Creates urgency and desire to proceed

Context from knowledge base: {context}

Client requirements: {requirements}

Write a professional executive summary (150-300 words) that:
- Uses "we" and "our" to represent your company
- Focuses on client benefits and value
- Includes a clear call to action
- Maintains a confident, professional tone
- Avoids technical jargon unless specifically needed

Executive Summary:
""",
            
            'technical_approach': """
You are writing a technical approach section for a business proposal. Create a detailed technical approach that:

1. Demonstrates deep understanding of the technical requirements
2. Outlines a clear, logical methodology
3. Explains how your approach solves the client's specific challenges
4. Highlights unique technical advantages
5. Shows feasibility and reduces perceived risk

Context from knowledge base: {context}

Technical requirements: {requirements}

Write a comprehensive technical approach (200-500 words) that:
- Uses clear, logical structure with phases or steps
- Explains the "how" and "why" of your approach
- Demonstrates technical expertise without being overly complex
- Addresses potential concerns or risks
- Shows understanding of the client's environment and constraints

Technical Approach:
""",
            
            'pricing_section': """
You are writing a pricing section for a business proposal. Create a pricing approach that:

1. Clearly presents value-based pricing
2. Explains what's included in the investment
3. Positions pricing as an investment in value
4. Addresses potential pricing concerns
5. Provides flexible options when appropriate

Context from knowledge base: {context}

Pricing requirements and constraints: {requirements}

Write a professional pricing section (100-250 words) that:
- Uses "investment" rather than "cost" language
- Clearly explains value delivered for the price
- Breaks down what's included
- Addresses any pricing concerns proactively
- Maintains transparency while positioning value

Pricing & Investment:
""",
            
            'case_study': """
You are writing a case study section for a business proposal. Create a compelling case study that:

1. Shows relevant, similar project experience
2. Demonstrates proven results and outcomes
3. Builds credibility and trust
4. Relates directly to the client's situation
5. Provides specific, measurable results

Context from knowledge base: {context}

Case study requirements: {requirements}

Write a compelling case study (150-300 words) that:
- Starts with a brief situation description
- Explains the approach taken
- Highlights specific, measurable results
- Connects to the current client's needs
- Builds confidence in your ability to deliver

Relevant Case Study:
""",
            
            'team_qualifications': """
You are writing a team qualifications section for a business proposal. Create content that:

1. Highlights relevant experience and expertise
2. Demonstrates team capability to deliver
3. Builds confidence in your team's qualifications
4. Shows understanding of project requirements
5. Positions team members as trusted experts

Context from knowledge base: {context}

Team and qualification requirements: {requirements}

Write a professional team qualifications section (150-300 words) that:
- Highlights most relevant experience for this project
- Demonstrates depth of expertise
- Shows team's track record of success
- Includes specific qualifications and certifications
- Builds confidence in delivery capability

Team Qualifications:
""",
            
            'implementation_timeline': """
You are writing an implementation timeline section for a business proposal. Create a timeline that:

1. Shows realistic, well-planned project phases
2. Demonstrates project management expertise
3. Provides confidence in delivery capability
4. Addresses key milestones and deliverables
5. Shows understanding of project complexity

Context from knowledge base: {context}

Timeline and implementation requirements: {requirements}

Write a clear implementation timeline (150-300 words) that:
- Breaks project into logical phases
- Includes key milestones and deliverables
- Shows realistic timeframes
- Addresses dependencies and critical path
- Demonstrates project management expertise

Implementation Timeline:
""",
            
            'risk_mitigation': """
You are writing a risk mitigation section for a business proposal. Create content that:

1. Proactively addresses potential project risks
2. Shows thorough project planning
3. Demonstrates risk management expertise
4. Provides client confidence in delivery
5. Positions your team as prepared and professional

Context from knowledge base: {context}

Risk and mitigation requirements: {requirements}

Write a professional risk mitigation section (100-250 words) that:
- Identifies key potential risks
- Provides specific mitigation strategies
- Shows proactive risk management
- Demonstrates experience with similar challenges
- Builds confidence in project success

Risk Mitigation:
"""
        }
    
    def generate(self, context: str, requirements: Dict[str, Any], 
                 brand_voice: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate proposal content based on requirements.
        
        Args:
            context: Knowledge base context from RAG retrieval
            requirements: Proposal requirements including section type
            brand_voice: Optional brand voice to apply
            
        Returns:
            Generated proposal content with metadata
        """
        section_type = requirements.get('section_type', 'executive_summary')
        
        # Get the prompt template for this section
        prompt = self.get_prompt_template(section_type, requirements)
        
        # Format the prompt with context and requirements
        formatted_prompt = prompt.format(
            context=context,
            requirements=self._format_requirements(requirements)
        )
        
        # For now, return the formatted prompt
        # In full implementation, this would call the LLM
        result = {
            'section_type': section_type,
            'prompt': formatted_prompt,
            'content_type': 'proposal',
            'style_rules': self.style_rules,
            'validation_rules': self.validation_rules
        }
        
        return result
    
    def get_prompt_template(self, section: str, requirements: Dict[str, Any]) -> str:
        """
        Get the prompt template for a specific proposal section.
        
        Args:
            section: The proposal section type
            requirements: Section-specific requirements
            
        Returns:
            Formatted prompt template
        """
        if section not in self.prompt_templates:
            # Fallback to executive summary if section not found
            section = 'executive_summary'
        
        return self.prompt_templates[section]
    
    def _format_requirements(self, requirements: Dict[str, Any]) -> str:
        """
        Format requirements into a readable string for prompt inclusion.
        
        Args:
            requirements: Requirements dictionary
            
        Returns:
            Formatted requirements string
        """
        formatted_parts = []
        
        # Add client name if provided
        if 'client_name' in requirements:
            formatted_parts.append(f"Client: {requirements['client_name']}")
        
        # Add project description
        if 'project_description' in requirements:
            formatted_parts.append(f"Project: {requirements['project_description']}")
        
        # Add specific requirements
        if 'specific_requirements' in requirements:
            if isinstance(requirements['specific_requirements'], list):
                formatted_parts.append("Requirements:")
                for req in requirements['specific_requirements']:
                    formatted_parts.append(f"- {req}")
            else:
                formatted_parts.append(f"Requirements: {requirements['specific_requirements']}")
        
        # Add budget information if provided
        if 'budget_range' in requirements:
            formatted_parts.append(f"Budget Range: {requirements['budget_range']}")
        
        # Add timeline if provided
        if 'timeline' in requirements:
            formatted_parts.append(f"Timeline: {requirements['timeline']}")
        
        return "\n".join(formatted_parts) if formatted_parts else "No specific requirements provided"
    
    def get_section_info(self, section: str) -> Dict[str, Any]:
        """
        Get information about a specific proposal section.
        
        Args:
            section: Section name
            
        Returns:
            Section information including description and requirements
        """
        section_info = {
            'executive_summary': {
                'description': 'High-level overview and value proposition',
                'purpose': 'Capture attention and summarize key benefits',
                'typical_length': '150-300 words',
                'key_elements': ['value proposition', 'client benefits', 'call to action']
            },
            'technical_approach': {
                'description': 'Detailed methodology and implementation plan',
                'purpose': 'Demonstrate technical expertise and feasibility',
                'typical_length': '200-500 words',
                'key_elements': ['methodology', 'phases', 'risk mitigation', 'deliverables']
            },
            'pricing_section': {
                'description': 'Investment details and value justification',
                'purpose': 'Present pricing as value investment',
                'typical_length': '100-250 words',
                'key_elements': ['pricing structure', 'value justification', 'payment terms']
            },
            'case_study': {
                'description': 'Relevant project example and results',
                'purpose': 'Build credibility through proven success',
                'typical_length': '150-300 words',
                'key_elements': ['situation', 'approach', 'results', 'relevance']
            },
            'team_qualifications': {
                'description': 'Team expertise and relevant experience',
                'purpose': 'Build confidence in team capability',
                'typical_length': '150-300 words',
                'key_elements': ['relevant experience', 'certifications', 'track record']
            },
            'implementation_timeline': {
                'description': 'Project phases and delivery schedule',
                'purpose': 'Show project management and planning',
                'typical_length': '150-300 words',
                'key_elements': ['phases', 'milestones', 'dependencies', 'deliverables']
            },
            'risk_mitigation': {
                'description': 'Potential risks and mitigation strategies',
                'purpose': 'Demonstrate thorough planning and risk awareness',
                'typical_length': '100-250 words',
                'key_elements': ['key risks', 'mitigation strategies', 'contingency plans']
            }
        }
        
        return section_info.get(section, {
            'description': 'Unknown section',
            'purpose': 'Not defined',
            'typical_length': 'Variable',
            'key_elements': []
        })
    
    def validate_proposal_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that proposal requirements are sufficient for generation.
        
        Args:
            requirements: Proposal requirements to validate
            
        Returns:
            Validation result with issues and suggestions
        """
        validation = {
            'valid': True,
            'issues': [],
            'suggestions': []
        }
        
        # Check for section type
        if 'section_type' not in requirements:
            validation['valid'] = False
            validation['issues'].append("Missing section_type in requirements")
            validation['suggestions'].append("Specify which proposal section to generate")
        
        # Check for valid section type
        section_type = requirements.get('section_type')
        if section_type and section_type not in self.get_sections():
            validation['valid'] = False
            validation['issues'].append(f"Invalid section_type: {section_type}")
            validation['suggestions'].append(f"Use one of: {', '.join(self.get_sections())}")
        
        # Suggest additional helpful information
        if 'client_name' not in requirements:
            validation['suggestions'].append("Consider adding client_name for personalization")
        
        if 'project_description' not in requirements:
            validation['suggestions'].append("Consider adding project_description for context")
        
        return validation