# Technical Architecture - Content Generation Suite

## 🏗️ System Architecture Overview

The Content Generation Suite extends the existing RAG pipeline with a new content generation layer that maintains the robustness of the current system while adding sophisticated content creation capabilities.

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    Content Generation Suite                     │
├─────────────────────────────────────────────────────────────────┤
│  User Interface Layer (Streamlit)                              │
│  ├── Content Type Selection                                    │
│  ├── Brand Voice Management                                    │
│  ├── Template Customization                                    │
│  └── Quality Review & Export                                   │
├─────────────────────────────────────────────────────────────────┤
│  Content Generation Layer (NEW)                                │
│  ├── Content Router      ├── Template Engine                  │
│  ├── Brand Voice Manager ├── Style Enforcer                   │
│  └── Quality Validator   └── Output Formatter                 │
├─────────────────────────────────────────────────────────────────┤
│  RAG Pipeline Layer (EXISTING - Enhanced)                      │
│  ├── Knowledge Retrieval ├── Context Assembly                 │
│  ├── LLM Integration     ├── Response Generation              │
│  └── Quality Scoring     └── Batch Processing                 │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer (EXISTING)                                         │
│  ├── Vector Store (FAISS) ├── Document Storage                │
│  ├── Knowledge Base       ├── Brand Voice Profiles            │
│  └── Content Templates    └── Quality Metrics                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Component Specifications

### 1. Content Router (`src/content/generator/content_router.py`)

**Purpose**: Route content generation requests to appropriate templates and processors

```python
class ContentRouter:
    """
    Routes content generation requests based on content type,
    manages template selection, and coordinates the generation pipeline
    """
    
    def __init__(self, rag_pipeline, template_manager, brand_manager):
        self.rag_pipeline = rag_pipeline
        self.template_manager = template_manager
        self.brand_manager = brand_manager
        self.supported_types = [
            'rfp_response', 'marketing_copy', 'technical_doc', 
            'sales_proposal', 'social_media', 'email_campaign'
        ]
    
    def route_request(self, content_type: str, requirements: dict) -> dict:
        """Route content generation request to appropriate handler"""
        
    def validate_requirements(self, content_type: str, requirements: dict) -> bool:
        """Validate that requirements match content type expectations"""
        
    def get_content_schema(self, content_type: str) -> dict:
        """Return the required schema for a specific content type"""
```

**Key Features**:
- Content type validation and routing
- Requirement schema enforcement
- Template-requirement matching
- Error handling and fallbacks

### 2. Template Engine (`src/content/templates/`)

**Purpose**: Manage content templates and generation logic

#### Base Template Class
```python
class BaseTemplate:
    """
    Abstract base class for all content templates
    Defines common interface and shared functionality
    """
    
    def __init__(self, template_config: dict):
        self.template_type = template_config['type']
        self.structure = template_config['structure']
        self.style_rules = template_config['style_rules']
        self.validation_rules = template_config['validation']
    
    def generate(self, context: str, requirements: dict, brand_voice: str = None) -> dict:
        """Generate content using template logic"""
        
    def validate_output(self, content: str) -> dict:
        """Validate generated content against template rules"""
        
    def get_prompt_template(self, requirements: dict) -> str:
        """Build LLM prompt based on template and requirements"""
```

#### Specific Template Implementations

**Marketing Template** (`marketing_template.py`)
```python
class MarketingTemplate(BaseTemplate):
    """Template for marketing content generation"""
    
    SUPPORTED_SUBTYPES = [
        'social_media_post', 'ad_copy', 'email_subject', 
        'blog_outline', 'product_description'
    ]
    
    def generate_social_media_post(self, context, requirements):
        """Generate social media content with platform-specific formatting"""
        
    def generate_ad_copy(self, context, requirements):
        """Generate advertising copy with CTA and persuasive elements"""
        
    def generate_email_campaign(self, context, requirements):
        """Generate email content with personalization"""
```

**Technical Documentation Template** (`technical_template.py`)
```python
class TechnicalTemplate(BaseTemplate):
    """Template for technical documentation"""
    
    SUPPORTED_SUBTYPES = [
        'api_documentation', 'user_manual', 'specification',
        'how_to_guide', 'troubleshooting'
    ]
    
    def generate_api_docs(self, context, requirements):
        """Generate API documentation with code examples"""
        
    def generate_user_manual(self, context, requirements):
        """Generate step-by-step user instructions"""
```

**Sales Proposal Template** (`proposal_template.py`)
```python
class ProposalTemplate(BaseTemplate):
    """Template for sales and proposal content"""
    
    SUPPORTED_SUBTYPES = [
        'executive_summary', 'technical_approach', 
        'pricing_section', 'case_study', 'testimonial'
    ]
    
    def generate_executive_summary(self, context, requirements):
        """Generate compelling executive summary"""
        
    def generate_technical_approach(self, context, requirements):
        """Generate detailed technical methodology"""
```

### 3. Brand Voice Manager (`src/content/brand/`)

**Purpose**: Learn, store, and apply brand voice characteristics

#### Brand Voice Analyzer (`brand_voice_analyzer.py`)
```python
class BrandVoiceAnalyzer:
    """
    Analyzes documents to extract brand voice characteristics
    """
    
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.style_extractors = {
            'tone': ToneAnalyzer(),
            'vocabulary': VocabularyAnalyzer(),
            'structure': StructureAnalyzer(),
            'formality': FormalityAnalyzer()
        }
    
    def analyze_documents(self, documents: List[str]) -> dict:
        """Extract brand voice characteristics from sample documents"""
        
    def create_voice_profile(self, brand_name: str, documents: List[str]) -> dict:
        """Create comprehensive brand voice profile"""
        
    def extract_style_patterns(self, text: str) -> dict:
        """Extract specific style patterns from text"""
```

#### Style Enforcer (`style_enforcer.py`)
```python
class StyleEnforcer:
    """
    Applies brand voice characteristics to generated content
    """
    
    def __init__(self, voice_profiles_store):
        self.voice_profiles = voice_profiles_store
        self.style_transformers = {
            'tone_adjustment': ToneTransformer(),
            'vocabulary_alignment': VocabularyTransformer(),
            'structure_formatting': StructureTransformer()
        }
    
    def apply_brand_voice(self, content: str, brand_name: str) -> str:
        """Transform content to match brand voice"""
        
    def validate_brand_consistency(self, content: str, brand_name: str) -> dict:
        """Check how well content matches brand voice"""
        
    def suggest_improvements(self, content: str, brand_name: str) -> List[str]:
        """Suggest specific improvements for brand alignment"""
```

### 4. Quality Validator (`src/content/validation/`)

**Purpose**: Validate content quality and provide improvement suggestions

#### Content Validator (`content_validator.py`)
```python
class ContentValidator:
    """
    Validates generated content against quality metrics
    """
    
    def __init__(self, quality_config):
        self.quality_metrics = {
            'readability': ReadabilityScorer(),
            'coherence': CoherenceScorer(),
            'completeness': CompletenessScorer(),
            'tone_consistency': ToneScorer(),
            'factual_accuracy': FactualScorer()
        }
    
    def validate_content(self, content: str, content_type: str) -> dict:
        """Comprehensive content quality validation"""
        
    def generate_quality_report(self, content: str, validation_result: dict) -> dict:
        """Generate detailed quality assessment report"""
        
    def suggest_improvements(self, content: str, quality_issues: List[str]) -> List[str]:
        """Provide specific improvement suggestions"""
```

## 🔄 Data Flow Architecture

### Content Generation Process
```
1. User Input
   ├── Content Type Selection
   ├── Requirements Input
   ├── Brand Voice Selection (optional)
   └── Template Customization (optional)
   
2. Request Processing
   ├── Content Router validates and routes request
   ├── Template Engine selects appropriate template
   ├── Brand Voice Manager loads voice profile
   └── Requirements are transformed to prompts
   
3. Knowledge Retrieval (Existing RAG)
   ├── Requirements are embedded
   ├── Vector store search for relevant context
   ├── Context assembly and ranking
   └── Prompt construction with context
   
4. Content Generation
   ├── LLM generates initial content
   ├── Template Engine applies structure rules
   ├── Brand Voice Manager applies style
   └── Multiple iterations if needed
   
5. Quality Validation
   ├── Content Validator runs quality checks
   ├── Brand consistency validation
   ├── Template compliance verification
   └── Quality score calculation
   
6. Output Processing
   ├── Format according to output requirements
   ├── Generate quality report
   ├── Create improvement suggestions
   └── Package for delivery
```

### Data Storage Architecture

#### Enhanced Vector Store Structure
```
vector_store/
├── knowledge_embeddings/     # Existing knowledge base
├── brand_voice_embeddings/   # Brand-specific style patterns
├── template_embeddings/      # Template and structure patterns
└── quality_patterns/         # Quality assessment patterns
```

#### Brand Voice Storage
```python
brand_profiles = {
    "company_name": {
        "voice_characteristics": {
            "tone": ["professional", "friendly", "authoritative"],
            "vocabulary": ["technical", "industry_specific"],
            "sentence_structure": ["average_length", "complexity"],
            "formality_level": "semi-formal"
        },
        "style_embeddings": np.array(...),
        "example_texts": [...],
        "created_date": "2025-09-22",
        "last_updated": "2025-09-22"
    }
}
```

#### Template Configuration
```python
template_config = {
    "marketing_copy": {
        "structure": {
            "sections": ["headline", "body", "cta"],
            "max_length": 500,
            "required_elements": ["value_proposition"]
        },
        "style_rules": {
            "tone": "persuasive",
            "format": "conversational",
            "cta_required": True
        },
        "validation": {
            "min_words": 50,
            "max_words": 500,
            "readability_score": 70
        }
    }
}
```

## 🛡️ Integration Points with Existing System

### 1. RAG Pipeline Integration
- **Leverage existing**: Knowledge retrieval, vector search, LLM integration
- **Enhance**: Add template-aware prompt construction
- **Extend**: Support for brand-aware context retrieval

### 2. Quality Scoring Enhancement
- **Current**: RFP-specific quality metrics
- **Enhanced**: Content-type-specific quality assessment
- **Added**: Brand consistency scoring

### 3. Document Processing Extension
- **Current**: RFP and knowledge document processing
- **Enhanced**: Brand document analysis and style extraction
- **Added**: Template document processing

### 4. UI Framework Extension
- **Current**: RFP-focused Streamlit interface
- **Enhanced**: Multi-content-type interface
- **Added**: Brand management, template customization

## 🔌 API Design

### REST API Endpoints (Future)
```python
# Content Generation
POST /api/v1/generate
{
    "content_type": "marketing_copy",
    "subtype": "social_media_post",
    "requirements": {...},
    "brand_voice": "company_name",
    "template_customization": {...}
}

# Brand Voice Management
POST /api/v1/brands/{brand_name}/train
PUT /api/v1/brands/{brand_name}/update
GET /api/v1/brands/{brand_name}/profile

# Template Management
GET /api/v1/templates
GET /api/v1/templates/{template_type}
POST /api/v1/templates/custom
```

## 📊 Performance Considerations

### Scalability Design
- **Stateless Components**: All components designed for horizontal scaling
- **Caching Strategy**: Template caching, brand voice caching
- **Batch Processing**: Support for bulk content generation
- **Resource Management**: Memory-efficient vector operations

### Optimization Strategies
- **Template Precompilation**: Pre-process templates for faster generation
- **Brand Voice Caching**: Cache frequently used brand profiles
- **Vector Store Optimization**: Efficient similarity search
- **LLM Response Caching**: Cache similar requests

## 🧪 Testing Strategy

### Unit Testing
- Template engine functionality
- Brand voice analysis and application
- Content validation logic
- Quality scoring accuracy

### Integration Testing
- End-to-end content generation flows
- RAG pipeline integration
- UI component interactions
- API endpoint functionality

### Quality Assurance
- Content quality benchmarking
- Brand voice accuracy testing
- Template compliance verification
- Performance testing under load

---

*This technical architecture document provides the detailed blueprint for implementing the Content Generation Suite while leveraging and enhancing the existing RAG system.*

**Last Updated**: September 2025  
**Status**: Design Phase  
**Next Phase**: Implementation Planning