"""
Main interface components for the Streamlit app
"""
import streamlit as st
from datetime import datetime
from pathlib import Path

from app.ui_components import (
    show_file_format_guidelines, 
    show_indexing_format_guidelines,
    show_quick_question_templates,
    display_quality_metrics,
    display_response_preview,
    show_vector_store_status
)
from app.processing_utils import (
    extract_requirements_from_upload,
    validate_and_preview_indexing_file,
    perform_indexing,
    cleanup_indexing_session,
    process_direct_query,
    check_vector_store_exists,
    get_vector_store_info,
    process_requirements_batch,
    generate_download_files
)
from app.rag_pipeline import RAGPipeline


def index_rfp_responses():
    """Interface for indexing new RFP response documents to the vector store"""
    st.markdown("## 📚 Add Historical RFP Responses to Knowledge Base")
    st.markdown("""
    Upload Excel files containing historical RFP responses to expand your organizational knowledge base. 
    These responses will be indexed and made available for future RFP response generation.
    """)
    
    # Vector store status
    store_info = get_vector_store_info()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if store_info['exists']:
            st.success(f"✅ Vector store ready ({store_info['total_documents']} documents)")
        else:
            st.info("🔄 Vector store will be created when you add the first document")
    
    with col2:
        if st.button("🔍 Inspect Vector Store", key="inspect_store_index"):
            if store_info['exists']:
                st.write("**Vector Store Information:**")
                st.json(store_info)
            else:
                st.warning("No vector store found yet")
    
    # File upload section
    st.subheader("📄 Upload RFP Response Document")
    st.markdown("**Expected format:** Excel file with 'Requirement' and 'Response' columns")
    
    show_indexing_format_guidelines()
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an Excel file containing RFP responses",
        type=['xlsx', 'xls'],
        help="Upload an Excel file with requirement and response columns",
        key="index_file_uploader"
    )
    
    if uploaded_file is not None:
        st.info(f"📎 Uploaded: **{uploaded_file.name}**")
        
        # Preview and validation
        if st.button("🔍 Preview and Validate", key="preview_index_file"):
            with st.spinner("Analyzing file structure..."):
                validate_and_preview_indexing_file(uploaded_file)
        
        # Indexing section
        if 'validation_result' in st.session_state and st.session_state.validation_result['success']:
            st.subheader("🚀 Index RFP Responses")
            
            result = st.session_state.validation_result
            st.info(f"Ready to index {result['total_pairs']} RFP response pairs to the vector store")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📚 Add to Knowledge Base", type="primary", key="index_responses"):
                    with st.spinner("Indexing RFP responses..."):
                        perform_indexing()
            
            with col2:
                if st.button("❌ Cancel", key="cancel_index"):
                    cleanup_indexing_session()
                    st.info("Operation cancelled")
                    st.experimental_rerun()


def upload_rfp_interface():
    """Interface for uploading RFP documents"""
    st.header("📄 Upload RFP Document")
    st.markdown("**Supported formats:** PDF, DOCX, Excel (XLSX/XLS)")
    
    rfp_file = st.file_uploader(
        "Upload your RFP document containing requirements", 
        type=['pdf', 'docx', 'xlsx', 'xls'],
        help="Upload a PDF, DOCX, or Excel (XLSX/XLS) file containing the RFP requirements you want to respond to.",
        key="rfp_uploader"
    )
    
    show_file_format_guidelines()
    
    if rfp_file is not None:
        st.info(f"📎 Uploaded file: **{rfp_file.name}** ({rfp_file.type})")
        
        if st.button("🔍 Extract Requirements", type="primary", key="extract_button"):
            with st.spinner("Extracting requirements from document..."):
                try:
                    requirements, temp_path = extract_requirements_from_upload(rfp_file)
                    st.session_state.requirements = requirements
                    
                    if requirements:
                        st.success(f"✅ Extracted {len(requirements)} requirements from the document!")
                    else:
                        st.warning("⚠️ No requirements found. Please try uploading a different document or check the file content.")
                        
                        # Show debugging info for structured files
                        if temp_path.lower().endswith(('.xlsx', '.xls')):
                            st.write("**Available columns in your file:**")
                            if 'extraction_metadata' in st.session_state and 'dataframe' in st.session_state.extraction_metadata:
                                df = st.session_state.extraction_metadata['dataframe']
                                st.write(list(df.columns))
                                st.write("**Sample data:**")
                                st.dataframe(df.head())
                
                except Exception as e:
                    st.error(f"Error extracting requirements: {str(e)}")
                finally:
                    # Clean up temporary file
                    import os
                    if 'temp_path' in locals() and os.path.exists(temp_path):
                        os.unlink(temp_path)
    
    # Show extracted requirements and generate responses
    show_requirements_and_generate()


def direct_query_interface():
    """Interface for direct queries to the vector store"""
    st.header("💬 Ask Questions Directly")
    st.markdown("Query the organizational knowledge base directly without uploading documents.")
    
    # Check vector store status first
    if not check_vector_store_exists():
        st.error("❌ No knowledge base found. Please upload documents to the 'Index RFP Responses' tab first.")
        return
    
    st.success("✅ Knowledge base is ready for queries")
    
    # Add helpful tip
    st.info("💡 **Tip:** Type your question below and click 'Get Answer'. The system will search the knowledge base and generate a response. You can use the template questions below for quick start!")
    
    # Query input
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_area(
            "Enter your question or requirement:",
            placeholder="e.g., What is your experience with cloud migration?\nHow do you handle data security?\nDescribe your project management approach.",
            height=100,
            key="direct_query_input",
            help="Clear, specific questions work best. You can ask about experience, processes, certifications, or any topic in your knowledge base."
        )
    
    with col2:
        st.markdown("### Settings")
        top_k = st.slider("Context chunks", 1, 10, 3, key="direct_query_top_k")
        ollama_model = st.selectbox("Model", ["llama3", "llama2", "mistral", "codellama"], index=0, key="direct_query_model")
    
    # Quick question templates
    show_quick_question_templates("direct_query_input")
    
    # Query execution
    if st.button("🚀 Get Answer", type="primary", disabled=not query.strip(), key="execute_direct_query"):
        if query.strip():
            with st.spinner("Searching knowledge base and generating response..."):
                result = process_direct_query(query, top_k, ollama_model)
                
                if result:
                    # Display result
                    st.success("✅ Response generated successfully!")
                    
                    # Show response with quality metrics
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown("### 🤖 Response")
                    with col2:
                        quality_score = result.get("quality_score", 0)
                        quality_emoji = "🌟" if quality_score >= 80 else "✅" if quality_score >= 60 else "⚠️" if quality_score >= 40 else "❌"
                        st.metric("Quality", f"{quality_emoji} {quality_score:.0f}/100")
                    with col3:
                        st.metric("Context", f"{len(result.get('context', '').split(chr(10)+chr(10)))} chunks")
                    
                    # Response text
                    st.markdown(f"**Question:** {query}")
                    st.markdown("**Answer:**")
                    st.write(result["answer"])
                    
                    # Show quality breakdown if available
                    if result.get("quality_breakdown"):
                        display_quality_metrics(result)
                    
                    # Show retrieved context
                    with st.expander("📚 Retrieved Context", expanded=False):
                        st.markdown("**Sources used to generate this response:**")
                        context_chunks = result.get("context", "").split("\n\n")
                        for i, chunk in enumerate(context_chunks, 1):
                            if chunk.strip():
                                st.text_area(f"Source {i}", chunk, height=150, disabled=True)
                    
                    # Success message with instruction
                    st.info("💡 Query processed successfully! You can ask another question above or check the history below.")
    
    # Chat History
    show_chat_history()


def show_chat_history():
    """Display chat history for direct queries"""
    if st.session_state.get('chat_history'):
        st.markdown("---")
        st.subheader("📜 Query History")
        
        # Show recent queries
        recent_count = st.selectbox("Show recent queries:", [5, 10, 20, "All"], index=0)
        if recent_count == "All":
            display_history = st.session_state.chat_history
        else:
            display_history = st.session_state.chat_history[-recent_count:]
        
        for i, entry in enumerate(reversed(display_history), 1):
            with st.expander(f"Query {len(display_history) - i + 1}: {entry['query'][:80]}{'...' if len(entry['query']) > 80 else ''}", expanded=False):
                st.write(f"**Time:** {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Question:** {entry['query']}")
                st.write(f"**Answer:** {entry['response']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Quality Score", f"{entry['quality_score']:.0f}/100")
                with col2:
                    st.metric("Status", entry['quality_status'])
        
        # Clear history option
        if st.button("🗑️ Clear Query History", key="clear_chat_history"):
            st.session_state.chat_history = []
            st.success("Query history cleared!")
            st.experimental_rerun()


def show_requirements_and_generate():
    """Show extracted requirements and handle response generation"""
    if not st.session_state.requirements:
        return
    
    st.subheader("📋 Extracted Requirements")
    
    # Option to edit requirements
    edit_mode = st.checkbox("✏️ Edit Requirements")
    
    if edit_mode:
        show_requirements_editor()
    else:
        # Just display requirements
        for i, req in enumerate(st.session_state.requirements, 1):
            with st.expander(f"Requirement {i}", expanded=False):
                st.write(req)
    
    # Check Vector Store Status and Generate Responses
    if check_vector_store_exists():
        st.session_state.vector_store_ready = True
        show_vector_store_info_section()
        show_response_generation_interface()
    else:
        st.error("⚠️ No organizational vector store found. Please contact your administrator to set up the knowledge base.")
        st.session_state.vector_store_ready = False


def show_requirements_editor():
    """Show requirements editor interface"""
    st.info("Edit the requirements below. Each text area represents one requirement.")
    edited_requirements = []
    
    for i, req in enumerate(st.session_state.requirements):
        edited_req = st.text_area(f"Requirement {i+1}", value=req, key=f"req_edit_{i}", height=100)
        if edited_req.strip():
            edited_requirements.append(edited_req.strip())
    
    # Option to add new requirement
    new_req = st.text_area("Add New Requirement (optional)", key="new_req", height=100)
    if new_req.strip():
        edited_requirements.append(new_req.strip())
    
    if st.button("💾 Save Changes"):
        st.session_state.requirements = edited_requirements
        st.success("Requirements updated!")
        st.experimental_rerun()


def show_vector_store_info_section():
    """Show vector store information section"""
    with st.expander("📊 Vector Store Information", expanded=False):
        st.success("✅ Using organizational knowledge base")
        if st.button("🔍 Inspect Vector Store", key="inspect_store"):
            try:
                from vector_store.vector_store import FAISSStore
                store = FAISSStore.load("test_store")
                st.write(f"Vector store contains {len(store.texts)} documents")
            except Exception as e:
                st.error(f"Error inspecting vector store: {e}")


def show_response_generation_interface():
    """Show response generation interface"""
    st.header("⚡ Generate Responses")
    st.success("🚀 Ready to generate responses using RAG pipeline!")
    
    col1, col2 = st.columns(2)
    with col1:
        top_k = st.slider("Number of context chunks to retrieve", 1, 10, 3)
    with col2:
        ollama_model = st.selectbox("Ollama Model", ["llama3", "llama2", "mistral", "codellama"], index=0)
    
    # Show processing estimate
    num_requirements = len(st.session_state.requirements)
    estimated_time = num_requirements * 3  # Rough estimate: 3 seconds per requirement
    
    if num_requirements > 10:
        st.warning(f"⚠️ You have {num_requirements} requirements. This may take approximately {estimated_time//60} minutes to complete. Consider processing in smaller batches for better experience.")
    else:
        st.info(f"📊 Processing {num_requirements} requirements (estimated time: ~{estimated_time} seconds)")
    
    # Add batch processing option for large sets
    if num_requirements > 20:
        show_batch_processing_interface(top_k, ollama_model, num_requirements)
    
    # Generate all responses button
    show_generate_all_interface(top_k, ollama_model)


def show_batch_processing_interface(top_k, ollama_model, num_requirements):
    """Show batch processing interface for large requirement sets"""
    col1, col2 = st.columns(2)
    with col1:
        batch_size = st.number_input("Process in batches of:", min_value=5, max_value=num_requirements, value=min(10, num_requirements))
    with col2:
        start_from = st.number_input("Start from requirement #:", min_value=1, max_value=num_requirements, value=1)
    
    actual_batch_size = min(batch_size, num_requirements - start_from + 1)
    st.info(f"Will process requirements {start_from} to {start_from + actual_batch_size - 1}")
    
    if st.button(f"🚀 Generate Responses (Batch: {start_from}-{start_from + actual_batch_size - 1})", type="primary", key="generate_batch"):
        # Initialize RAG pipeline
        rag = RAGPipeline(model=ollama_model)
        
        # Process only the selected batch
        selected_requirements = st.session_state.requirements[start_from-1:start_from-1+actual_batch_size]
        process_requirements_batch(selected_requirements, rag, top_k, ollama_model, start_from)


def show_generate_all_interface(top_k, ollama_model):
    """Show generate all responses interface"""
    if st.button("🚀 Generate All Responses", type="primary", key="generate_responses"):
        # Initialize RAG pipeline
        rag = RAGPipeline(model=ollama_model)
        
        # Process all requirements
        results = process_requirements_batch(st.session_state.requirements, rag, top_k, ollama_model, 1)
        
        if results:
            # Show preview of results
            display_response_preview(results)
            
            # Show download section
            show_download_section()


def show_download_section():
    """Show download section for generated responses"""
    if not st.session_state.responses:
        return
    
    st.header("📥 Download Results")
    st.success(f"Ready to download results for {len(st.session_state.responses)} requirements!")
    
    # Generate download files
    extraction_metadata = st.session_state.get('extraction_metadata')
    downloads = generate_download_files(st.session_state.responses, extraction_metadata)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Excel Format")
        if 'excel' in downloads:
            if extraction_metadata and extraction_metadata.get('has_structure'):
                st.info("📋 Preserving original Excel structure with added responses")
            
            st.download_button(
                label="⬇️ Download Excel",
                data=downloads['excel']['data'],
                file_name=downloads['excel']['filename'],
                mime=downloads['excel']['mime'],
                type="primary"
            )
    
    with col2:
        st.subheader("📄 PDF Format")
        if 'pdf' in downloads:
            st.download_button(
                label="⬇️ Download PDF",
                data=downloads['pdf']['data'],
                file_name=downloads['pdf']['filename'],
                mime=downloads['pdf']['mime'],
                type="primary"
            )