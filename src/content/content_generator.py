"""
Content Generator - Integrates templates with RAG pipeline

This module provides the main content generation interface that combines
the template system with the existing RAG pipeline for knowledge retrieval.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to sys.path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.app.rag_pipeline import RAGPipeline
from .templates.base_template import template_registry
from .templates.proposal_template import ProposalTemplate


class ContentGenerator:
    """
    Main content generation class that combines templates with RAG pipeline.
    
    This class serves as the bridge between the template system and the
    existing RAG pipeline, handling content generation requests.
    """
    
    def __init__(self, rag_pipeline: Optional[RAGPipeline] = None):
        """
        Initialize the content generator.
        
        Args:
            rag_pipeline: Optional RAG pipeline instance. If None, creates new one.
        """
        self.rag_pipeline = rag_pipeline or RAGPipeline()
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize and register all available templates."""
        # Register proposal template
        proposal_template = ProposalTemplate()
        template_registry.register_template('proposal', proposal_template)
    
    def generate_content(self, content_type: str, requirements: Dict[str, Any], 
                        top_k: int = 3) -> Dict[str, Any]:
        """
        Generate content using the specified template and requirements.
        
        Args:
            content_type: Type of content to generate ('proposal', 'rfp_response', etc.)
            requirements: Content requirements and parameters
            top_k: Number of knowledge base chunks to retrieve
            
        Returns:
            Generated content with metadata
        """
        # Handle existing RFP response type
        if content_type == 'rfp_response':
            return self._generate_rfp_response(requirements, top_k)
        
        # Handle template-based content generation
        template = template_registry.get_template(content_type)
        if not template:
            return {
                'error': f"Unknown content type: {content_type}",
                'available_types': self.list_content_types()
            }
        
        # Validate requirements
        if hasattr(template, 'validate_proposal_requirements'):
            validation = template.validate_proposal_requirements(requirements)
            if not validation['valid']:
                return {
                    'error': 'Invalid requirements',
                    'validation': validation
                }
        
        # Create search query from requirements
        search_query = self._build_search_query(requirements)
        
        # Retrieve relevant context using RAG pipeline
        context = self.rag_pipeline.retrieve_context(search_query, top_k)
        
        # Generate content using template
        template_result = template.generate(context, requirements)
        
        # Generate actual content using LLM (integrate with existing pipeline)
        if 'prompt' in template_result:
            # Use the existing RAG pipeline to generate the final content
            llm_response = self._generate_with_llm(template_result['prompt'])
            
            # Validate the generated content
            validation = template.validate_output(llm_response)
            
            result = {
                'content_type': content_type,
                'section_type': requirements.get('section_type', 'main'),
                'generated_content': llm_response,
                'context_used': context,
                'validation': validation,
                'style_rules': template_result.get('style_rules', {}),
                'requirements': requirements,
                'search_query': search_query
            }
            
            return result
        
        return template_result
    
    def _generate_rfp_response(self, requirements: Dict[str, Any], top_k: int) -> Dict[str, Any]:
        """
        Generate RFP response using existing pipeline.
        
        Args:
            requirements: Should contain 'query' or 'requirement'
            top_k: Number of chunks to retrieve
            
        Returns:
            RFP response result
        """
        query = requirements.get('query') or requirements.get('requirement', '')
        if not query:
            return {'error': 'Missing query or requirement for RFP response'}
        
        # Use existing RAG pipeline
        result = self.rag_pipeline.ask(query, top_k)
        
        return {
            'content_type': 'rfp_response',
            'generated_content': result['answer'],
            'context_used': result['context'],
            'validation': {
                'valid': True,
                'score': result.get('quality_score', 85)
            },
            'requirements': requirements,
            'search_query': query
        }
    
    def _build_search_query(self, requirements: Dict[str, Any]) -> str:
        """
        Build search query from requirements for knowledge retrieval.
        
        Args:
            requirements: Content requirements
            
        Returns:
            Search query string
        """
        query_parts = []
        
        # Add project description
        if 'project_description' in requirements:
            query_parts.append(requirements['project_description'])
        
        # Add specific requirements
        if 'specific_requirements' in requirements:
            if isinstance(requirements['specific_requirements'], list):
                query_parts.extend(requirements['specific_requirements'])
            else:
                query_parts.append(str(requirements['specific_requirements']))
        
        # Add section-specific context
        section_type = requirements.get('section_type', '')
        if section_type:
            if section_type == 'technical_approach':
                query_parts.append("methodology implementation approach technical solution")
            elif section_type == 'pricing_section':
                query_parts.append("pricing cost investment budget")
            elif section_type == 'case_study':
                query_parts.append("similar projects case studies experience results")
            elif section_type == 'team_qualifications':
                query_parts.append("team experience qualifications expertise")
        
        return " ".join(query_parts) if query_parts else "general information"
    
    def _generate_with_llm(self, prompt: str) -> str:
        """
        Generate content using the LLM through existing pipeline.
        
        Args:
            prompt: Formatted prompt for the LLM
            
        Returns:
            Generated content
        """
        try:
            # Use the existing LLM generation logic
            response = self.rag_pipeline.generate_answer("", prompt)  # Empty query, full prompt
            return response
        except Exception as e:
            return f"Error generating content: {str(e)}"
    
    def list_content_types(self) -> List[str]:
        """
        List all available content types.
        
        Returns:
            List of available content type names
        """
        template_types = template_registry.list_templates()
        return ['rfp_response'] + template_types
    
    def get_content_type_info(self, content_type: str) -> Dict[str, Any]:
        """
        Get information about a specific content type.
        
        Args:
            content_type: Content type to get info for
            
        Returns:
            Content type information
        """
        if content_type == 'rfp_response':
            return {
                'type': 'rfp_response',
                'description': 'Generate responses to RFP requirements',
                'required_fields': ['query'],
                'sections': ['main']
            }
        
        return template_registry.get_template_info(content_type)
    
    def get_proposal_sections(self) -> List[Dict[str, Any]]:
        """
        Get detailed information about all proposal sections.
        
        Returns:
            List of proposal section information
        """
        proposal_template = template_registry.get_template('proposal')
        if not proposal_template:
            return []
        
        sections = []
        for section in proposal_template.get_sections():
            section_info = proposal_template.get_section_info(section)
            sections.append({
                'name': section,
                'display_name': section.replace('_', ' ').title(),
                **section_info
            })
        
        return sections