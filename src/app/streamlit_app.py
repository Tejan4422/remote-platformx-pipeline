import streamlit as st
from pathlib import Path
import sys
import os
import tempfile
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.document_processor import process_document
from ingestion.requirement_extractor import extract_requirements_from_file
from app.rag_pipeline import RAGPipeline
from app.output_generator import OutputGenerator
from app.pdf_generator import PDFGenerator

def process_requirements_batch(requirements, rag, top_k, ollama_model, start_index=1):
    """Process a batch of requirements and update session state"""
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
    
    batch_results = []
    start_time = datetime.now()
    
    try:
        for i, requirement in enumerate(requirements):
            # Update current processing status
            actual_index = start_index + i
            current_processing.info(f"🔄 Processing {actual_index}/{start_index + len(requirements) - 1}")
            status_text.text(f"Processing: {requirement[:80]}...")
            
            # Process requirement
            result = rag.ask(requirement, top_k)
            batch_results.append({
                "requirement": requirement,
                "response": result["answer"],
                "status": "success",
                "quality_score": result.get("quality_score", 0),
                "quality_status": result.get("quality_status", "Unknown"),
                "quality_breakdown": result.get("quality_breakdown", {}),
                "quality_feedback": result.get("quality_feedback", [])
            })
            
            # Update progress
            progress_percentage = (i + 1) / len(requirements)
            progress_bar.progress(progress_percentage)
            
            # Update completed count
            completed_count.success(f"✅ Completed: {actual_index}")
            
            # Calculate and display ETA
            if i > 0:
                elapsed = datetime.now() - start_time
                avg_time_per_req = elapsed / (i + 1)
                remaining_reqs = len(requirements) - (i + 1)
                eta = avg_time_per_req * remaining_reqs
                eta_display.info(f"⏱️ ETA: {str(eta).split('.')[0]}")
        
        # Update session state (append or replace based on start_index)
        if start_index == 1:
            st.session_state.responses = batch_results
        else:
            # Append to existing responses
            if 'responses' not in st.session_state:
                st.session_state.responses = []
            st.session_state.responses.extend(batch_results)
        
        # Clear progress displays and show completion
        progress_container.empty()
        status_text.empty()
        
        # Display final results
        completion_time = datetime.now() - start_time
        st.success(f"🎉 Generated responses for {len(batch_results)} requirements in {str(completion_time).split('.')[0]}!")
        
    except Exception as e:
        progress_container.empty()
        status_text.empty()
        st.error(f"Error processing batch: {str(e)}")
        st.exception(e)

def main():
    st.set_page_config(
        page_title="RFP Response Generator",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("🔍 RFP Response Generator")
    st.markdown("Upload your RFP document and knowledge base, then generate professional responses automatically!")
    
    # Initialize session state
    if 'requirements' not in st.session_state:
        st.session_state.requirements = []
    if 'responses' not in st.session_state:
        st.session_state.responses = []
    if 'vector_store_ready' not in st.session_state:
        st.session_state.vector_store_ready = False
    if 'knowledge_docs_processed' not in st.session_state:
        st.session_state.knowledge_docs_processed = False
    if 'show_knowledge_upload' not in st.session_state:
        st.session_state.show_knowledge_upload = False
    
    # Step 1: Upload RFP Document
    st.header("📄 Step 1: Upload RFP Document")
    st.markdown("**Supported formats:** PDF, DOCX, Excel (XLSX/XLS), CSV")
    
    rfp_file = st.file_uploader(
        "Upload your RFP document containing requirements", 
        type=['pdf', 'docx', 'xlsx', 'xls', 'csv'],
        help="Upload a PDF, DOCX, Excel (XLSX/XLS), or CSV file containing the RFP requirements you want to respond to.",
        key="rfp_uploader"
    )
    
    # Show file format info
    with st.expander("📝 File Format Guidelines", expanded=False):
        st.markdown("""
        **PDF/DOCX Files:**
        - Should contain numbered questions/requirements (1., 2., G1:, A1:, etc.)
        
        **Excel/CSV Files:**
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
                    
                    # Check if it's a structured file (Excel/CSV)
                    if temp_path.lower().endswith(('.xlsx', '.xls', '.csv')):
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
                        if temp_path.lower().endswith(('.xlsx', '.xls', '.csv')):
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
    
    # Show extracted requirements
    if st.session_state.requirements:
        st.subheader("📋 Extracted Requirements")
        
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
    
    # Step 2: Upload Knowledge Base OR Use Existing Vector Store
    if st.session_state.requirements:
        st.header("🧠 Step 2: Knowledge Base Setup")
        
        # Check if vector store already exists
        vector_store_exists = Path("test_store/index.faiss").exists() and Path("test_store/docstore.pkl").exists()
        
        if vector_store_exists:
            st.success("✅ Existing vector store found! You can proceed directly to generate responses.")
            st.session_state.vector_store_ready = True
            
            col1, col2 = st.columns(2)
            with col1:
                st.info("📊 Using pre-built knowledge base")
                if st.button("🔍 Inspect Vector Store", key="inspect_store"):
                    try:
                        from vector_store.vector_store import FAISSStore
                        store = FAISSStore.load("test_store")
                        st.write(f"Vector store contains {len(store.texts)} documents")
                    except Exception as e:
                        st.error(f"Error inspecting vector store: {e}")
            
            with col2:
                st.markdown("**Want to update the knowledge base?**")
                if st.button("🔄 Upload New Documents", key="show_upload"):
                    st.session_state.show_knowledge_upload = True
        else:
            st.warning("⚠️ No existing vector store found. Please upload knowledge base documents.")
            st.session_state.show_knowledge_upload = True
        
        # Show knowledge base upload section if needed
        if st.session_state.get('show_knowledge_upload', False) or not vector_store_exists:
            st.markdown("**Upload documents that contain information to answer the RFP requirements.**")
            
            knowledge_files = st.file_uploader(
                "Upload knowledge base documents", 
                type=['pdf', 'docx'],
                accept_multiple_files=True,
                help="Upload documents containing information that will be used to answer the RFP requirements.",
                key="knowledge_files"
            )
            
            if knowledge_files:
                if st.button("🔨 Process Knowledge Base", type="primary"):
                    with st.spinner("Processing documents and building knowledge base..."):
                        try:
                            # Create directories
                            Path("data/raw").mkdir(parents=True, exist_ok=True)
                            Path("data/processed").mkdir(parents=True, exist_ok=True)
                            
                            all_chunks = []
                            
                            # Process each uploaded file
                            progress_bar = st.progress(0)
                            for idx, uploaded_file in enumerate(knowledge_files):
                                # Save temporarily
                                temp_path = Path("data/raw") / uploaded_file.name
                                with open(temp_path, "wb") as f:
                                    f.write(uploaded_file.getvalue())
                                
                                # Process document
                                chunks = process_document(str(temp_path))
                                all_chunks.extend(chunks)
                                
                                progress_bar.progress((idx + 1) / len(knowledge_files))
                                st.success(f"✅ Processed {uploaded_file.name}: {len(chunks)} chunks")
                            
                            # Build vector store
                            st.info("Building vector store...")
                            
                            # Import and use existing vector store functionality
                            from retrieval.embeddings import embed_text
                            from vector_store.vector_store import FAISSStore
                            
                            # Create vector store
                            vector_store = FAISSStore(dimension=384)  # sentence-transformers dimension
                            
                            # Create embeddings and add to vector store
                            chunk_progress = st.progress(0)
                            for i, chunk in enumerate(all_chunks):
                                embedding = embed_text(chunk)
                                vector_store.add_text(chunk, embedding)
                                chunk_progress.progress((i + 1) / len(all_chunks))
                            
                            # Save vector store
                            vector_store.save("test_store")
                            
                            st.session_state.vector_store_ready = True
                            st.session_state.knowledge_docs_processed = True
                            st.session_state.show_knowledge_upload = False
                            st.success(f"🎉 Knowledge base built successfully with {len(all_chunks)} text chunks!")
                            st.experimental_rerun()
                            
                        except Exception as e:
                            st.error(f"Error building knowledge base: {str(e)}")
                            st.exception(e)
    
    # Step 3: Generate Responses
    if st.session_state.requirements:
        st.header("⚡ Step 3: Generate Responses")
        
        if st.session_state.vector_store_ready:
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
                    # Process only the selected batch
                    selected_requirements = st.session_state.requirements[start_from-1:start_from-1+actual_batch_size]
                    process_requirements_batch(selected_requirements, rag, top_k, ollama_model, start_from)
            
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
                        req_start = datetime.now()
                        result = rag.ask(requirement, top_k)
                        req_end = datetime.now()
                        
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
                    
                    # Show a preview with better organization
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
                
                except Exception as e:
                    # Clear progress displays on error
                    progress_container.empty()
                    status_text.empty()
                    st.error(f"Error generating responses: {str(e)}")
                    st.exception(e)
        else:
            st.info("📋 Complete Step 2 (Knowledge Base Setup) to enable response generation.")
            if not Path("test_store/index.faiss").exists():
                st.warning("⚠️ No vector store found. Please upload knowledge base documents in Step 2.")
    
    # Step 4: Download Results
    if st.session_state.responses:
        st.header("📥 Step 4: Download Results")
        
        st.success(f"Ready to download results for {len(st.session_state.responses)} requirements!")
        
        col1, col2, col3 = st.columns(3)
        
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
        
        with col3:
            st.subheader("📋 CSV Format")
            try:
                output_gen = OutputGenerator()
                csv_bytes = output_gen.generate_csv_bytes(st.session_state.responses)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"rfp_responses_{timestamp}.csv"
                
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_bytes,
                    file_name=filename,
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error generating CSV: {str(e)}")
    
    # Sidebar with status and help
    with st.sidebar:
        st.markdown("## � Progress Status")
        
        # Requirements status
        if st.session_state.requirements:
            st.success(f"✅ {len(st.session_state.requirements)} requirements extracted")
        else:
            st.info("🔄 Upload RFP document to extract requirements")
        
        # Knowledge base status
        vector_store_exists = Path("test_store/index.faiss").exists() and Path("test_store/docstore.pkl").exists()
        if vector_store_exists:
            st.success("✅ Vector store ready")
            st.session_state.vector_store_ready = True
        elif st.session_state.vector_store_ready:
            st.success("✅ Knowledge base ready")
        else:
            st.info("🔄 Upload knowledge documents or use existing vector store")
        
        # Responses status
        if st.session_state.responses:
            st.success(f"✅ {len(st.session_state.responses)} responses generated")
            
            # Quality Summary
            quality_scores = [resp.get("quality_score", 0) for resp in st.session_state.responses if resp.get("quality_score")]
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                status_counts = {}
                for resp in st.session_state.responses:
                    status = resp.get("quality_status", "Unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                # Quality overview in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Avg Quality", f"{avg_quality:.1f}/100")
                with col2:
                    st.metric("🌟 Excellent", status_counts.get("Excellent", 0))
                with col3:
                    st.metric("✅ Good", status_counts.get("Good", 0))
                with col4:
                    st.metric("⚠️ Needs Review", status_counts.get("Needs Review", 0) + status_counts.get("Poor", 0))
        else:
            st.info("🔄 Generate responses using RAG pipeline")
        
        st.markdown("---")
        st.markdown("## 🔄 Reset")
        if st.button("🗑️ Clear All Data"):
            st.session_state.requirements = []
            st.session_state.responses = []
            st.session_state.vector_store_ready = False
            st.session_state.knowledge_docs_processed = False
            st.session_state.show_knowledge_upload = False
            if 'extraction_metadata' in st.session_state:
                del st.session_state.extraction_metadata
            st.success("All data cleared!")
            st.experimental_rerun()
        
        st.markdown("---")
        st.markdown("## 💡 Tips")
        st.markdown("""
        - **Excel/CSV files:** Make sure requirements are in a clear column
        - **PDF files:** Use numbered questions (1., 2., G1:, etc.)
        - **Vector store:** Pre-built knowledge base will be used if available
        - **Models:** Start with llama3 for best results
        """)

if __name__ == "__main__":
    main()