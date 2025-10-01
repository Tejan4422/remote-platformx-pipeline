import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.interfaces import (
    index_rfp_responses,
    upload_rfp_interface, 
    direct_query_interface
)
from app.ui_components import display_sidebar_status
from app.processing_utils import initialize_session_state

def main():
    st.set_page_config(
        page_title="RFP Response Generator",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("🔍 RFP Response Generator")
    st.markdown("Upload your RFP document to extract requirements, then generate professional responses using our organizational knowledge base!")
    
    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["📝 Generate RFP Responses", "📚 Index RFP Responses"])
    
    with tab1:
        generate_rfp_responses()
    
    with tab2:
        index_rfp_responses()
    
    # Sidebar with status and help (available for both tabs)
    with st.sidebar:
        st.markdown("## 📊 System Status")
        
        # Vector store status (common to both tabs)
        vector_store_exists = Path("test_store/index.faiss").exists() and Path("test_store/docstore.pkl").exists()
        if vector_store_exists:
            try:
                from vector_store.vector_store import FAISSStore
                store = FAISSStore.load("test_store")
                st.success(f"✅ Vector store ready ({len(store.texts)} documents)")
            except:
                st.success("✅ Vector store ready")
        else:
            st.info("🔄 Vector store will be created when documents are added")
        
        # Tab-specific status
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

def generate_rfp_responses():
    """Main RFP response generation functionality"""
    # Initialize session state
    if 'requirements' not in st.session_state:
        st.session_state.requirements = []
    if 'responses' not in st.session_state:
        st.session_state.responses = []
    if 'vector_store_ready' not in st.session_state:
        st.session_state.vector_store_ready = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Create sub-tabs for different input methods
    input_tab1, input_tab2 = st.tabs(["📄 Upload RFP Document", "💬 Direct Query"])
    
    with input_tab1:
        upload_rfp_interface()
    
    with input_tab2:
        direct_query_interface()

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
    
    # Show file format info
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
        
        # Add sample Excel download
        st.markdown("**📥 Need a template?**")
        if st.button("⬇️ Download Sample Excel Template", key="download_template"):
            import pandas as pd
            import io
            
            # Create sample template
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
            
            df = pd.DataFrame(template_data)
            
            # Create Excel file in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='RFP Requirements', index=False)
            
            st.download_button(
                label="📄 Download Template",
                data=output.getvalue(),
                file_name="rfp_requirements_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    if rfp_file is not None:
        st.info(f"📎 Uploaded file: **{rfp_file.name}** ({rfp_file.type})")
        
        if st.button("🔍 Extract Requirements", type="primary", key="extract_button"):
            with st.spinner("Extracting requirements from document..."):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{rfp_file.name.split('.')[-1]}") as temp_file:
                    temp_file.write(rfp_file.getvalue())
                    temp_path = temp_file.name
                
                try:
                    from ingestion.requirement_extractor import RequirementExtractor
                    extractor = RequirementExtractor()
                    
                    # Check if it's a structured file (Excel)
                    if temp_path.lower().endswith(('.xlsx', '.xls')):
                        # Use metadata extraction for structured files
                        extraction_result = extractor.extract_with_metadata(temp_path)
                        requirements = extraction_result['requirements']
                        
                        # Store extraction metadata in session state for response generation
                        st.session_state.extraction_metadata = extraction_result
                        
                        if extraction_result['has_structure'] and extraction_result['column_name']:
                            st.info(f"📊 Found requirements in column: '{extraction_result['column_name']}'")
                    else:
                        # Use regular extraction for PDF/DOCX
                        requirements = extract_requirements_from_file(temp_path)
                        st.session_state.extraction_metadata = None
                    
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
                        else:
                            # Show extracted text for PDF/DOCX debugging
                            full_text = extractor._extract_text_from_pdf(temp_path) if temp_path.endswith('.pdf') else ""
                            if full_text:
                                st.text_area("Raw text extracted from document:", full_text[:1000] + "..." if len(full_text) > 1000 else full_text, height=200)
                    
                except Exception as e:
                    st.error(f"Error extracting requirements: {str(e)}")
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
    
    # Show extracted requirements and generate responses
    show_requirements_and_generate()

def direct_query_interface():
    """Interface for direct queries to the vector store"""
    st.header("💬 Ask Questions Directly")
    st.markdown("Query the organizational knowledge base directly without uploading documents.")
    
    # Check vector store status first
    vector_store_exists = Path("test_store/index.faiss").exists() and Path("test_store/docstore.pkl").exists()
    
    if not vector_store_exists:
        st.error("❌ No knowledge base found. Please upload documents to the 'Index RFP Responses' tab first.")
        return
    
    st.success("✅ Knowledge base is ready for queries")
    
    # Query input
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_area(
            "Enter your question or requirement:",
            placeholder="e.g., What is your experience with cloud migration?\nHow do you handle data security?\nDescribe your project management approach.",
            height=100,
            key="direct_query_input"
        )
    
    with col2:
        st.markdown("### Settings")
        top_k = st.slider("Context chunks", 1, 10, 3, key="direct_query_top_k")
        ollama_model = st.selectbox("Model", ["llama3", "llama2", "mistral", "codellama"], index=0, key="direct_query_model")
    
    # Quick question templates
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
                if st.button(f"� {template}", key=f"template_{i}"):
                    st.session_state.direct_query_input = template
                    st.experimental_rerun()
    
    # Query execution
    if st.button("🚀 Get Answer", type="primary", disabled=not query.strip(), key="execute_direct_query"):
        if query.strip():
            with st.spinner("Searching knowledge base and generating response..."):
                try:
                    # Initialize RAG pipeline
                    rag = RAGPipeline(model=ollama_model)
                    
                    # Get response
                    result = rag.ask(query.strip(), top_k)
                    
                    # Add to chat history
                    chat_entry = {
                        "timestamp": datetime.now(),
                        "query": query.strip(),
                        "response": result["answer"],
                        "quality_score": result.get("quality_score", 0),
                        "quality_status": result.get("quality_status", "Unknown"),
                        "context_chunks": len(result.get("context", "").split("\n\n"))
                    }
                    st.session_state.chat_history.append(chat_entry)
                    
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
                    
                    # Show retrieved context
                    with st.expander("📚 Retrieved Context", expanded=False):
                        st.markdown("**Sources used to generate this response:**")
                        context_chunks = result.get("context", "").split("\n\n")
                        for i, chunk in enumerate(context_chunks, 1):
                            if chunk.strip():
                                st.text_area(f"Source {i}", chunk, height=150, disabled=True)
                    
                    # Clear the query input
                    st.session_state.direct_query_input = ""
                    
                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
                    st.exception(e)
    
    # Chat History
    if st.session_state.chat_history:
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
    # Show extracted requirements
    if st.session_state.requirements:
        st.subheader("�📋 Extracted Requirements")
        
        # Option to edit requirements
        edit_mode = st.checkbox("✏️ Edit Requirements")
        
        if edit_mode:
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
        else:
            # Just display requirements
            for i, req in enumerate(st.session_state.requirements, 1):
                with st.expander(f"Requirement {i}", expanded=False):
                    st.write(req)
        
        # Check Vector Store Status and Generate Responses
        vector_store_exists = Path("test_store/index.faiss").exists() and Path("test_store/docstore.pkl").exists()
        
        if vector_store_exists:
            st.session_state.vector_store_ready = True
            with st.expander("📊 Vector Store Information", expanded=False):
                st.success("✅ Using organizational knowledge base")
                if st.button("🔍 Inspect Vector Store", key="inspect_store"):
                    try:
                        from vector_store.vector_store import FAISSStore
                        store = FAISSStore.load("test_store")
                        st.write(f"Vector store contains {len(store.texts)} documents")
                    except Exception as e:
                        st.error(f"Error inspecting vector store: {e}")
            
            # Step 2: Generate Responses
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
            
            # Generate all responses button and logic follows here...
            generate_all_responses_interface(top_k, ollama_model)
        else:
            st.error("⚠️ No organizational vector store found. Please contact your administrator to set up the knowledge base.")
            st.session_state.vector_store_ready = False

def generate_all_responses_interface(top_k, ollama_model):
    """Handle the generation of all responses interface"""
    if st.button("🚀 Generate All Responses", type="primary", key="generate_responses"):
        # Initialize RAG pipeline
        rag = RAGPipeline(model=ollama_model)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Create containers for compact progress display
        progress_container = st.container()
        with progress_container:
            col1, col2, col3 = st.columns(3)
            with col1:
                completed_count = st.empty()
            with col2:
                current_processing = st.empty()
            with col3:
                eta_display = st.empty()
        
        results = []
        start_time = datetime.now()
        
        try:
            for i, requirement in enumerate(st.session_state.requirements):
                # Update current processing status
                current_processing.info(f"🔄 Processing {i+1}/{len(st.session_state.requirements)}")
                status_text.text(f"Processing: {requirement[:80]}...")
                
                # Process requirement
                result = rag.ask(requirement, top_k)
                
                results.append({
                    "requirement": requirement,
                    "response": result["answer"],
                    "status": "success",
                    "quality_score": result.get("quality_score", 0),
                    "quality_status": result.get("quality_status", "Unknown"),
                    "quality_breakdown": result.get("quality_breakdown", {}),
                    "quality_feedback": result.get("quality_feedback", [])
                })
                
                # Update progress
                progress_percentage = (i + 1) / len(st.session_state.requirements)
                progress_bar.progress(progress_percentage)
                
                # Update completed count
                completed_count.success(f"✅ Completed: {i+1}/{len(st.session_state.requirements)}")
                
                # Calculate and display ETA
                if i > 0:  # Calculate ETA after first item
                    elapsed = datetime.now() - start_time
                    avg_time_per_req = elapsed / (i + 1)
                    remaining_reqs = len(st.session_state.requirements) - (i + 1)
                    eta = avg_time_per_req * remaining_reqs
                    eta_display.info(f"⏱️ ETA: {str(eta).split('.')[0]}")
            
            st.session_state.responses = results
            
            # Clear progress displays and show completion
            progress_container.empty()
            status_text.empty()
            
            # Display final results
            completion_time = datetime.now() - start_time
            st.success(f"🎉 Generated responses for all {len(results)} requirements in {str(completion_time).split('.')[0]}!")
            
            # Show preview of results
            show_response_preview(results)
        
        except Exception as e:
            # Clear progress displays on error
            progress_container.empty()
            status_text.empty()
            st.error(f"Error generating responses: {str(e)}")
            st.exception(e)

def show_response_preview(results):
    """Show preview of generated responses"""
    with st.expander("📋 Preview Generated Responses", expanded=True):
        if len(results) <= 5:
            # Show all if 5 or fewer
            for i, result in enumerate(results, 1):
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
                        
                        # Quality breakdown
                        if result.get("quality_breakdown"):
                            st.markdown("**Quality Breakdown:**")
                            breakdown = result["quality_breakdown"]
                            q_col1, q_col2, q_col3, q_col4 = st.columns(4)
                            with q_col1:
                                st.metric("Completeness", f"{breakdown.get('completeness', 0):.0f}")
                            with q_col2:
                                st.metric("Clarity", f"{breakdown.get('clarity', 0):.0f}")
                            with q_col3:
                                st.metric("Professional", f"{breakdown.get('professionalism', 0):.0f}")
                            with q_col4:
                                st.metric("Relevance", f"{breakdown.get('relevance', 0):.0f}")
                            
                            # Quality feedback
                            if result.get("quality_feedback"):
                                st.markdown("**Improvement Suggestions:**")
                                for feedback in result["quality_feedback"]:
                                    st.info(f"💡 {feedback}")
                    
                    st.markdown("---")
        else:
            # Show first 3 and provide summary for larger sets
            for i, result in enumerate(results[:3], 1):
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
                        
                        # Quality breakdown
                        if result.get("quality_breakdown"):
                            st.markdown("**Quality Breakdown:**")
                            breakdown = result["quality_breakdown"]
                            q_col1, q_col2, q_col3, q_col4 = st.columns(4)
                            with q_col1:
                                st.metric("Completeness", f"{breakdown.get('completeness', 0):.0f}")
                            with q_col2:
                                st.metric("Clarity", f"{breakdown.get('clarity', 0):.0f}")
                            with q_col3:
                                st.metric("Professional", f"{breakdown.get('professionalism', 0):.0f}")
                            with q_col4:
                                st.metric("Relevance", f"{breakdown.get('relevance', 0):.0f}")
                            
                            # Quality feedback
                            if result.get("quality_feedback"):
                                st.markdown("**Improvement Suggestions:**")
                                for feedback in result["quality_feedback"]:
                                    st.info(f"💡 {feedback}")
                    
                    st.markdown("---")
            
            st.info(f"📊 Showing first 3 of {len(results)} responses. Download the complete results below to see all responses.")
            
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
    
    # Step 3: Download Results
    if st.session_state.responses:
        st.header("📥 Download Results")
        
        st.success(f"Ready to download results for {len(st.session_state.responses)} requirements!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Excel Format")
            try:
                output_gen = OutputGenerator()
                
                # Check if we have structured data from Excel/CSV input
                if (hasattr(st.session_state, 'extraction_metadata') and 
                    st.session_state.extraction_metadata and 
                    st.session_state.extraction_metadata.get('has_structure') and
                    'dataframe' in st.session_state.extraction_metadata):
                    
                    # Generate structured Excel preserving original format
                    excel_bytes = output_gen.generate_structured_excel_bytes(
                        st.session_state.responses,
                        st.session_state.extraction_metadata['dataframe'],
                        st.session_state.extraction_metadata['column_name']
                    )
                    st.info("📋 Preserving original Excel structure with added responses")
                else:
                    # Generate standard Excel format
                    excel_bytes = output_gen.generate_excel_bytes(st.session_state.responses)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"rfp_responses_{timestamp}.xlsx"
                
                st.download_button(
                    label="⬇️ Download Excel",
                    data=excel_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
            except Exception as e:
                st.error(f"Error generating Excel: {str(e)}")
        
        with col2:
            st.subheader("📄 PDF Format")
            try:
                pdf_gen = PDFGenerator()
                pdf_bytes = pdf_gen.generate_pdf_bytes(st.session_state.responses, "RFP Response Document")
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"rfp_responses_{timestamp}.pdf"
                
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    type="primary"
                )
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")

if __name__ == "__main__":
    main()