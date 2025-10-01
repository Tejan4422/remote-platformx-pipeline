"""
UI Components and Helper Functions for Streamlit App
"""
import streamlit as st
import pandas as pd
import io
import tempfile
import os
from pathlib import Path
from datetime import datetime


def create_sample_rfp_template():
    """Create and return sample RFP template data"""
    template_data = {
        'ID': [1, 2, 3, 4, 5],
        'Requirement': [
            'Describe your company\'s experience with similar projects in the past 3 years.',
            'What is your approach to project management and timeline adherence?',
            'How do you ensure data security and compliance during implementation?',
            'What certifications and qualifications does your team possess?',
            'Describe your post-implementation support and maintenance services.'
        ],
        'Priority': ['High', 'High', 'Medium', 'Low', 'Medium'],
        'Category': ['Experience', 'Management', 'Security', 'Qualifications', 'Support']
    }
    return pd.DataFrame(template_data)


def create_sample_indexing_template():
    """Create and return sample indexing template data"""
    sample_data = {
        'Requirement': [
            'Describe your company\'s experience with cloud migration projects.',
            'What is your approach to data security and compliance?',
            'How do you handle project timeline management?',
            'What certifications does your team possess?'
        ],
        'Response': [
            'Our company has successfully completed over 50 cloud migration projects in the past 5 years, specializing in AWS, Azure, and Google Cloud platforms. We have helped organizations migrate from legacy on-premises systems to modern cloud architectures.',
            'We implement a comprehensive security framework that includes encryption at rest and in transit, multi-factor authentication, regular security audits, and compliance with SOC 2, ISO 27001, and industry-specific regulations.',
            'We use agile project management methodologies with weekly sprints, clear milestone tracking, and regular stakeholder communication. Our average project delivery rate is 95% on-time with proactive risk management.',
            'Our team holds various industry certifications including AWS Solutions Architect, Microsoft Azure Expert, PMP, CISSP, and CISA. We maintain continuous education programs to stay current with technology trends.'
        ]
    }
    return pd.DataFrame(sample_data)


def generate_excel_download_button(df, filename, label, button_key=None):
    """Generate Excel download button for DataFrame"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Data', index=False)
    
    return st.download_button(
        label=label,
        data=output.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=button_key
    )


def show_file_format_guidelines():
    """Display file format guidelines in an expander"""
    with st.expander("📝 File Format Guidelines", expanded=False):
        st.markdown("""
        **PDF/DOCX Files:**
        - Should contain numbered questions/requirements (1., 2., G1:, A1:, etc.)
        
        **Excel Files:**
        - Should have a column containing requirements/questions
        - Supported column names: Requirements, Questions, Queries, Items, Tasks, etc.
        - Example:
        ```
        | ID | Requirement | Priority |
        |----|-------------|----------|
        | 1  | What is your experience? | High |
        | 2  | How do you handle security? | Medium |
        ```
        """)
        
        st.markdown("**📥 Need a template?**")
        if st.button("⬇️ Download Sample Excel Template", key="download_template"):
            template_df = create_sample_rfp_template()
            generate_excel_download_button(
                template_df, 
                "rfp_requirements_template.xlsx",
                "📄 Download Template"
            )


def show_indexing_format_guidelines():
    """Display indexing file format guidelines"""
    with st.expander("📋 File Format Guidelines", expanded=False):
        st.markdown("""
        **Required Columns:**
        - **Requirement/Question column:** Should contain the RFP requirements or questions
        - **Response/Answer column:** Should contain your organization's responses
        
        **Accepted column names:**
        - Requirements: requirement, requirements, question, questions, query, queries, item, items, task, tasks
        - Responses: response, responses, answer, answers, reply, replies, solution, solutions
        
        **Example format:**
        ```
        | Requirement | Response |
        |-------------|----------|
        | What is your experience with cloud migration? | We have 10+ years of experience... |
        | How do you ensure data security? | Our security framework includes... |
        ```
        """)
        
        if st.button("⬇️ Download Sample Template", key="download_index_template"):
            sample_df = create_sample_indexing_template()
            generate_excel_download_button(
                sample_df,
                "sample_rfp_responses.xlsx", 
                "📄 Download Sample RFP Responses Template"
            )


def show_quick_question_templates(input_key):
    """Display quick question templates"""
    with st.expander("💡 Quick Question Templates", expanded=False):
        st.markdown("Click on any template to use it as your query:")
        
        template_questions = [
            "What is your experience with cloud migration projects?",
            "How do you handle data security and compliance?",
            "What certifications does your team possess?",
            "Describe your project management methodology.",
            "What is your approach to disaster recovery?",
            "How do you ensure quality in software development?",
            "What support services do you provide post-implementation?",
            "Describe your experience with AI/ML implementations."
        ]
        
        cols = st.columns(2)
        for i, template in enumerate(template_questions):
            col = cols[i % 2]
            with col:
                if st.button(f"💡 {template}", key=f"template_{i}"):
                    st.session_state[input_key] = template
                    st.experimental_rerun()


def display_quality_metrics(result, show_breakdown=True):
    """Display quality metrics for a response"""
    quality_score = result.get("quality_score", 0)
    quality_status = result.get("quality_status", "Unknown")
    
    # Quality emoji
    quality_emoji = "🌟" if quality_score >= 80 else "✅" if quality_score >= 60 else "⚠️" if quality_score >= 40 else "❌"
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Quality", f"{quality_emoji} {quality_score:.0f}/100")
    with col2:
        st.metric("Status", quality_status)
    
    if show_breakdown and result.get("quality_breakdown"):
        with st.expander("📊 Quality Analysis", expanded=False):
            breakdown = result["quality_breakdown"]
            q_col1, q_col2, q_col3, q_col4 = st.columns(4)
            with q_col1:
                st.metric("Completeness", f"{breakdown.get('completeness', 0):.0f}/100")
            with q_col2:
                st.metric("Clarity", f"{breakdown.get('clarity', 0):.0f}/100")
            with q_col3:
                st.metric("Professionalism", f"{breakdown.get('professionalism', 0):.0f}/100")
            with q_col4:
                st.metric("Relevance", f"{breakdown.get('relevance', 0):.0f}/100")
            
            if result.get("quality_feedback"):
                st.markdown("**Improvement Suggestions:**")
                for feedback in result["quality_feedback"]:
                    st.info(f"💡 {feedback}")


def display_progress_tracking(current, total, current_item=None, start_time=None):
    """Display progress tracking components"""
    progress_bar = st.progress(current / total if total > 0 else 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success(f"✅ Completed: {current}/{total}")
    with col2:
        if current_item:
            st.info(f"🔄 Processing: {current_item[:50]}...")
    with col3:
        if start_time and current > 0:
            elapsed = datetime.now() - start_time
            avg_time = elapsed / current
            remaining = total - current
            eta = avg_time * remaining
            st.info(f"⏱️ ETA: {str(eta).split('.')[0]}")
    
    return progress_bar


def show_vector_store_status():
    """Display vector store status information"""
    vector_store_exists = Path("test_store/index.faiss").exists() and Path("test_store/docstore.pkl").exists()
    
    if vector_store_exists:
        try:
            from vector_store.vector_store import FAISSStore
            store = FAISSStore.load("test_store")
            st.success(f"✅ Vector store ready ({len(store.texts)} documents)")
            return True
        except:
            st.success("✅ Vector store ready")
            return True
    else:
        st.info("🔄 Vector store will be created when documents are added")
        return False


def save_uploaded_file_temporarily(uploaded_file):
    """Save uploaded file temporarily and return path"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
        temp_file.write(uploaded_file.getvalue())
        return temp_file.name


def cleanup_temp_file(file_path):
    """Clean up temporary file"""
    if os.path.exists(file_path):
        os.unlink(file_path)


def display_response_preview(results, max_preview=3):
    """Display preview of generated responses"""
    with st.expander("📋 Preview Generated Responses", expanded=True):
        display_count = min(len(results), max_preview)
        
        for i, result in enumerate(results[:display_count], 1):
            with st.container():
                # Header with quality indicator
                quality_emoji = "🌟" if result.get("quality_status") == "Excellent" else "✅" if result.get("quality_status") == "Good" else "⚠️" if result.get("quality_status") == "Needs Review" else "❌"
                quality_score = result.get("quality_score", 0)
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{i}. {result['requirement'][:100]}{'...' if len(result['requirement']) > 100 else ''}**")
                with col2:
                    st.markdown(f"{quality_emoji} **{quality_score:.0f}/100**")
                
                with st.expander("View Response & Quality Details", expanded=False):
                    st.write(result['response'])
                    display_quality_metrics(result, show_breakdown=True)
                
                st.markdown("---")
        
        if len(results) > max_preview:
            st.info(f"📊 Showing first {max_preview} of {len(results)} responses. Download the complete results to see all responses.")
            
            # Show summary statistics
            avg_response_length = sum(len(r['response']) for r in results) / len(results)
            successful_responses = sum(1 for r in results if r['status'] == 'success')
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Responses", len(results))
            with col2:
                st.metric("Success Rate", f"{successful_responses}/{len(results)}")
            with col3:
                st.metric("Avg Response Length", f"{int(avg_response_length)} chars")


def display_sidebar_status():
    """Display sidebar status information"""
    with st.sidebar:
        st.markdown("## 📊 System Status")
        
        # Vector store status
        show_vector_store_status()
        
        st.markdown("---")
        st.markdown("## 📝 RFP Generation Status")
        
        # Requirements status
        if hasattr(st.session_state, 'requirements') and st.session_state.requirements:
            st.success(f"✅ {len(st.session_state.requirements)} requirements extracted")
        else:
            st.info("🔄 Upload RFP document to extract requirements")
        
        # Responses status
        if hasattr(st.session_state, 'responses') and st.session_state.responses:
            st.success(f"✅ {len(st.session_state.responses)} responses generated")
            
            # Quality Summary
            quality_scores = [resp.get("quality_score", 0) for resp in st.session_state.responses if resp.get("quality_score")]
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                status_counts = {}
                for resp in st.session_state.responses:
                    status = resp.get("quality_status", "Unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                # Quality overview
                st.metric("📊 Avg Quality", f"{avg_quality:.1f}/100")
                quality_col1, quality_col2 = st.columns(2)
                with quality_col1:
                    st.metric("🌟 Excellent", status_counts.get("Excellent", 0))
                    st.metric("✅ Good", status_counts.get("Good", 0))
                with quality_col2:
                    st.metric("⚠️ Needs Review", status_counts.get("Needs Review", 0))
                    st.metric("❌ Poor", status_counts.get("Poor", 0))
        else:
            st.info("🔄 Generate responses using RAG pipeline")
        
        st.markdown("---")
        st.markdown("## 🔄 Reset")
        if st.button("🗑️ Clear All Data"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                if key in ['requirements', 'responses', 'vector_store_ready', 'extraction_metadata', 'validation_result', 'temp_file_path']:
                    del st.session_state[key]
            st.success("All data cleared!")
            st.experimental_rerun()
        
        st.markdown("---")
        st.markdown("## 💡 Tips")
        st.markdown("""
        **RFP Generation:**
        - Excel files: Clear requirement columns
        - PDF files: Numbered questions (1., 2., G1:, etc.)
        - Start with llama3 for best results
        
        **Knowledge Base:**
        - Upload Excel with Requirement + Response columns
        - Historical responses improve future generation
        - Vector store automatically updates
        """)