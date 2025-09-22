"""
Content Generation Suite - Streamlit App

A simple interface to test and demonstrate the new content generation capabilities,
starting with proposal generation alongside the existing RFP responses.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import traceback

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from src.content.templates.proposal_template import ProposalTemplate


def main():
    st.set_page_config(
        page_title="Content Generation Suite",
        page_icon="✍️",
        layout="wide"
    )
    
    st.title("✍️ Content Generation Suite")
    st.markdown("**Prototype**: Generate business proposals and RFP responses using AI")
    
    # Initialize session state
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = None
    if 'proposal_template' not in st.session_state:
        st.session_state.proposal_template = ProposalTemplate()
    
    # Sidebar for content type selection
    with st.sidebar:
        st.header("🎯 Content Generation")
        
        content_type = st.selectbox(
            "Select Content Type",
            ["Proposal Section", "RFP Response (Original)"],
            help="Choose the type of content you want to generate"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Current Capabilities")
        st.markdown("✅ **Proposal Sections**: 7 types available")
        st.markdown("✅ **Professional Prompts**: Business-ready")
        st.markdown("✅ **Quality Validation**: Built-in scoring")
        st.markdown("⏳ **LLM Integration**: Coming next")
    
    if content_type == "Proposal Section":
        generate_proposal_section()
    else:
        st.info("🔄 RFP Response generation will integrate with existing system")
        st.markdown("The existing RFP response functionality from your main app will be integrated here.")


def generate_proposal_section():
    """Interface for generating proposal sections."""
    
    st.header("📄 Proposal Section Generator")
    st.markdown("Generate professional proposal sections using AI and your knowledge base.")
    
    # Get proposal template
    template = st.session_state.proposal_template
    
    # Section selection
    sections = template.get_sections()
    section_names = [s.replace('_', ' ').title() for s in sections]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_section_name = st.selectbox(
            "Proposal Section Type",
            section_names,
            help="Choose which section of the proposal to generate"
        )
        
        # Convert back to internal format
        selected_section = sections[section_names.index(selected_section_name)]
    
    with col2:
        # Show section info
        section_info = template.get_section_info(selected_section)
        st.metric("Typical Length", section_info['typical_length'])
    
    # Show section details
    with st.expander("📋 Section Details", expanded=False):
        st.markdown(f"**Purpose**: {section_info['purpose']}")
        st.markdown(f"**Description**: {section_info['description']}")
        st.markdown(f"**Key Elements**: {', '.join(section_info['key_elements'])}")
    
    # Input form
    st.subheader("📝 Project Requirements")
    
    with st.form("proposal_requirements"):
        col1, col2 = st.columns(2)
        
        with col1:
            client_name = st.text_input(
                "Client Name",
                value="TechCorp Solutions",
                help="Name of the client organization"
            )
            
            project_description = st.text_area(
                "Project Description",
                value="Implementation of AI-powered content generation system for enterprise content creation",
                height=100,
                help="Brief description of the project or opportunity"
            )
        
        with col2:
            budget_range = st.text_input(
                "Budget Range (Optional)",
                value="$50,000 - $100,000",
                help="Expected budget or investment range"
            )
            
            timeline = st.text_input(
                "Timeline (Optional)",
                value="3-4 months implementation",
                help="Expected project timeline"
            )
        
        specific_requirements = st.text_area(
            "Specific Requirements",
            value="""- Reduce content creation time by 60%
- Maintain brand consistency across all content types
- Support multiple content formats (proposals, marketing, technical)
- Ensure enterprise security and compliance
- Provide analytics and performance tracking""",
            height=120,
            help="List specific project requirements (one per line)"
        )
        
        # Knowledge base context (simulate RAG retrieval)
        st.subheader("🧠 Knowledge Base Context")
        knowledge_context = st.text_area(
            "Relevant Context (simulates knowledge retrieval)",
            value="""Our company specializes in AI and machine learning solutions for enterprise clients. We have extensive experience in:
- Content generation and natural language processing
- Brand consistency and voice training systems  
- Enterprise AI implementations with 99.9% uptime
- Regulatory compliance for financial and healthcare sectors
- Previous implementations achieving 70% time savings and 95% brand consistency scores
- Team of 50+ AI engineers and content specialists
- Partnerships with major cloud providers and security vendors""",
            height=150,
            help="This simulates content retrieved from your knowledge base"
        )
        
        generate_button = st.form_submit_button("✨ Generate Proposal Section", type="primary")
    
    if generate_button:
        # Prepare requirements
        requirements = {
            'section_type': selected_section,
            'client_name': client_name,
            'project_description': project_description,
            'specific_requirements': [req.strip('- ') for req in specific_requirements.split('\n') if req.strip()],
            'budget_range': budget_range,
            'timeline': timeline
        }
        
        # Validate requirements
        validation = template.validate_proposal_requirements(requirements)
        
        if not validation['valid']:
            st.error("❌ Invalid requirements:")
            for issue in validation['issues']:
                st.error(f"• {issue}")
            return
        
        # Generate content
        with st.spinner("🔄 Generating proposal section..."):
            try:
                result = template.generate(knowledge_context, requirements)
                
                if 'error' in result:
                    st.error(f"❌ Error: {result['error']}")
                    return
                
                # Store in session state
                st.session_state.generated_content = {
                    'result': result,
                    'requirements': requirements,
                    'context': knowledge_context,
                    'timestamp': datetime.now()
                }
                
                st.success("✅ Proposal section generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error generating content: {str(e)}")
                with st.expander("🔍 Error Details"):
                    st.code(traceback.format_exc())
    
    # Display generated content
    if st.session_state.generated_content:
        display_generated_content()


def display_generated_content():
    """Display the generated proposal content."""
    
    content_data = st.session_state.generated_content
    result = content_data['result']
    requirements = content_data['requirements']
    
    st.header("📋 Generated Content")
    
    # Content metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Section Type", result['section_type'].replace('_', ' ').title())
    with col2:
        st.metric("Content Type", result['content_type'].title())
    with col3:
        st.metric("Generated At", content_data['timestamp'].strftime("%H:%M:%S"))
    
    # Generated prompt (what would be sent to LLM)
    with st.expander("📝 Generated Prompt (sent to AI)", expanded=True):
        st.markdown("**This is the prompt that would be sent to the LLM:**")
        st.text_area(
            "LLM Prompt",
            value=result.get('prompt', 'No prompt available'),
            height=400,
            help="This prompt will be sent to your local LLM (Ollama) for content generation"
        )
    
    # Requirements used
    with st.expander("📋 Requirements Used"):
        st.json(requirements)
    
    # Style rules
    with st.expander("🎨 Style Rules Applied"):
        st.json(result.get('style_rules', {}))
    
    # Simulate LLM Response
    st.subheader("🤖 Simulated AI Response")
    st.info("💡 **Note**: This is where the actual generated content would appear when integrated with your LLM")
    
    # Example response based on section type
    example_response = get_example_response(result['section_type'], requirements)
    
    st.text_area(
        "Generated Content (Example)",
        value=example_response,
        height=300,
        help="This is an example of what the AI would generate"
    )
    
    # Validation simulation
    template = st.session_state.proposal_template
    validation = template.validate_output(example_response, result['section_type'])
    
    col1, col2 = st.columns(2)
    with col1:
        score_color = "green" if validation['score'] >= 80 else "orange" if validation['score'] >= 60 else "red"
        st.markdown(f"### Quality Score: :{score_color}[{validation['score']}/100]")
    
    with col2:
        status_icon = "✅" if validation['valid'] else "⚠️"
        st.markdown(f"### Status: {status_icon} {'Valid' if validation['valid'] else 'Needs Review'}")
    
    if validation['issues']:
        st.subheader("⚠️ Issues Found")
        for issue in validation['issues']:
            st.warning(f"• {issue}")
    
    if validation['suggestions']:
        st.subheader("💡 Improvement Suggestions")
        for suggestion in validation['suggestions']:
            st.info(f"• {suggestion}")
    
    # Actions
    st.subheader("🔧 Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Regenerate"):
            st.experimental_rerun()
    
    with col2:
        if st.button("📋 Copy Prompt"):
            st.code(result.get('prompt', ''), language='text')
    
    with col3:
        if st.button("🗑️ Clear"):
            st.session_state.generated_content = None
            st.experimental_rerun()


def get_example_response(section_type: str, requirements: dict) -> str:
    """Generate example response for demonstration."""
    
    client_name = requirements.get('client_name', 'the client')
    
    examples = {
        'executive_summary': f"""We are excited to propose our AI-powered content generation solution for {client_name}. Our comprehensive platform will transform your content creation process, reducing development time by 60% while maintaining perfect brand consistency across all content types.

Our solution addresses your core requirements through advanced natural language processing, intelligent brand voice training, and enterprise-grade security. With our proven track record of implementing similar systems for Fortune 500 companies, we've consistently delivered 70% time savings and 95% brand consistency scores.

We recommend proceeding with a phased implementation approach that minimizes risk while maximizing value. Our team is ready to begin immediately and deliver a fully operational system within your specified timeline, ensuring your content creation capabilities are transformed and your competitive advantage is secured.""",
        
        'technical_approach': f"""Our technical approach for {client_name} leverages a proven three-phase methodology that ensures successful implementation while minimizing operational disruption.

Phase 1: Foundation Setup (Weeks 1-4)
We begin by establishing the core AI infrastructure, including local LLM deployment, knowledge base integration, and security framework implementation. Our team will work closely with your IT department to ensure seamless integration with existing systems.

Phase 2: Brand Intelligence Training (Weeks 5-8)
During this phase, we analyze your existing content to extract brand voice patterns and create custom training models. This ensures all generated content maintains your unique brand identity and professional standards.

Phase 3: System Optimization and Rollout (Weeks 9-12)
The final phase focuses on performance optimization, user training, and full system deployment. We provide comprehensive documentation and conduct hands-on training sessions for your team.

Our approach includes continuous monitoring, quality assurance checkpoints, and risk mitigation strategies at each phase, ensuring successful delivery within your timeline and budget parameters.""",
        
        'pricing_section': f"""Our investment proposal for {client_name} is structured to deliver maximum value while providing transparent, predictable costs throughout the implementation and beyond.

Implementation Investment: $75,000
This includes complete system setup, brand voice training, team training, and 90 days of implementation support. The investment covers all software licensing, custom configuration, and knowledge base integration.

Ongoing Platform License: $2,500/month
Annual licensing provides unlimited content generation, platform updates, priority support, and continued brand voice refinement. This represents a 70% cost reduction compared to traditional content creation methods.

Additional Value Included:
- Six months of priority support and optimization
- Quarterly brand voice refinement sessions
- Access to new content templates and features
- Performance analytics and reporting dashboard

This investment will typically pay for itself within 6-8 months through content creation efficiency gains, making it a sound business decision that delivers immediate and long-term value.""",
        
        'case_study': f"""Similar Challenge: Global Financial Services Firm

Situation: A major financial services company faced the same content creation challenges as {client_name}, requiring 40+ hours weekly for proposal development while struggling to maintain brand consistency across multiple departments.

Our Approach: We implemented our AI content generation platform with custom financial industry templates and regulatory compliance features. The solution included specialized brand voice training and integration with their existing CRM and document management systems.

Results Achieved:
- 65% reduction in content creation time (from 40 hours to 14 hours weekly)
- 98% brand consistency score across all generated content
- $240,000 annual savings in content creation costs
- 85% user adoption rate within first 60 days
- Zero compliance issues in 18 months of operation

Relevance to Your Project: Like this client, {client_name} will benefit from industry-specific customization, seamless system integration, and measurable ROI through content creation efficiency gains."""
    }
    
    return examples.get(section_type, "Example content would be generated here based on the section type and requirements.")


if __name__ == "__main__":
    main()