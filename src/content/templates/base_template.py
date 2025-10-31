"""
Base Template Class for Content Generation

This module provides the abstract base class for all content templates.
Templates define structure, prompts, and validation rules for different content types.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import yaml


class BaseTemplate(ABC):
    """
    Abstract base class for all content templates.
    
    This class defines the common interface and shared functionality
    for generating different types of content using the RAG pipeline.
    """
    
    def __init__(self, template_config: Dict[str, Any]):
        """
        Initialize the template with configuration.
        
        Args:
            template_config: Dictionary containing template configuration
                - type: Template type identifier
                - structure: Required sections and format
                - style_rules: Writing style and tone guidelines
                - validation: Content validation rules
        """
        self.template_type = template_config.get('type', 'unknown')
        self.structure = template_config.get('structure', {})
        self.style_rules = template_config.get('style_rules', {})
        self.validation_rules = template_config.get('validation', {})
        self.prompt_templates = template_config.get('prompts', {})
    
    @abstractmethod
    def generate(self, context: str, requirements: Dict[str, Any], 
                 brand_voice: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate content using this template.
        
        Args:
            context: Retrieved knowledge base context
            requirements: Specific requirements for this content
            brand_voice: Optional brand voice profile to apply
            
        Returns:
            Dictionary containing generated content and metadata
        """
        pass
    
    @abstractmethod
    def get_prompt_template(self, section: str, requirements: Dict[str, Any]) -> str:
        """
        Build LLM prompt for a specific section.
        
        Args:
            section: The content section to generate
            requirements: Specific requirements for this section
            
        Returns:
            Formatted prompt string for the LLM
        """
        pass
    
    def validate_output(self, content: str, section: str = 'main') -> Dict[str, Any]:
        """
        Validate generated content against template rules.
        
        Args:
            content: Generated content to validate
            section: Section being validated
            
        Returns:
            Validation result with score and feedback
        """
        validation_result = {
            'valid': True,
            'score': 100,
            'issues': [],
            'suggestions': []
        }
        
        # Check minimum length
        min_words = self.validation_rules.get('min_words', 10)
        word_count = len(content.split())
        if word_count < min_words:
            validation_result['valid'] = False
            validation_result['score'] -= 20
            validation_result['issues'].append(f"Content too short: {word_count} words (minimum: {min_words})")
            validation_result['suggestions'].append(f"Add more detail to reach at least {min_words} words")
        
        # Check maximum length
        max_words = self.validation_rules.get('max_words', 1000)
        if word_count > max_words:
            validation_result['valid'] = False
            validation_result['score'] -= 10
            validation_result['issues'].append(f"Content too long: {word_count} words (maximum: {max_words})")
            validation_result['suggestions'].append(f"Condense content to under {max_words} words")
        
        # Check for required elements
        required_elements = self.validation_rules.get('required_elements', [])
        for element in required_elements:
            if element.lower() not in content.lower():
                validation_result['score'] -= 15
                validation_result['issues'].append(f"Missing required element: {element}")
                validation_result['suggestions'].append(f"Include information about {element}")
        
        return validation_result
    
    def get_sections(self) -> List[str]:
        """
        Get list of sections this template can generate.
        
        Returns:
            List of section names
        """
        return list(self.structure.get('sections', ['main']))
    
    def get_style_guidelines(self) -> Dict[str, Any]:
        """
        Get style guidelines for this template.
        
        Returns:
            Dictionary of style rules and guidelines
        """
        return self.style_rules
    
    def load_config_from_file(self, config_path: str) -> Dict[str, Any]:
        """
        Load template configuration from YAML file.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            return {}
        except yaml.YAMLError as e:
            print(f"Error loading template config: {e}")
            return {}


class TemplateRegistry:
    """
    Registry for managing and accessing content templates.
    """
    
    def __init__(self):
        self.templates: Dict[str, BaseTemplate] = {}
    
    def register_template(self, template_type: str, template: BaseTemplate):
        """Register a template in the registry."""
        self.templates[template_type] = template
    
    def get_template(self, template_type: str) -> Optional[BaseTemplate]:
        """Get a template by type."""
        return self.templates.get(template_type)
    
    def list_templates(self) -> List[str]:
        """List all registered template types."""
        return list(self.templates.keys())
    
    def get_template_info(self, template_type: str) -> Dict[str, Any]:
        """Get information about a template."""
        template = self.get_template(template_type)
        if template:
            return {
                'type': template.template_type,
                'sections': template.get_sections(),
                'style_rules': template.get_style_guidelines()
            }
        return {}


# Global template registry instance
template_registry = TemplateRegistry()