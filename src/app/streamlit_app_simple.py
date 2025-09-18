import streamlit as st
from pathlib import Path
import sys
import os
import tempfile
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.requirement_extractor import extract_requirements_from_file
from app.rag_pipeline import RAGPipeline
from app.output_generator import OutputGenerator
from app.pdf_generator import PDFGenerator

def main():
    st.set_page_config(
        page_title="RFP Response Generator",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("🔍 RFP Response Generator")
    st.markdown("Upload your RFP document to extract requirements and generate professional responses using our pre-built knowledge base!")
    
    # Initialize session state
    if 'requirements' not in st.session_state:
        st.session_state.requirements = []
    if 'responses' not in st.session_state:
        st.session_state.responses = []
    
    # Check if vector store exists
    vector_store_path = Path("test_store")
    vector_store_ready = vector_store_path.exists() and (vector_store_path / "index.faiss").exists()
    
    if not vector_store_ready:
        st.error("❌ Vector store not found! Please ensure your knowledge base is properly set up in the 'test_store' directory.")
        st.stop()
    
    # Step 1: Upload RFP Document and Extract Requirements
    st.header("📄 Step 1: Upload RFP Document")
    st.markdown("Upload your RFP document containing the requirements you need to respond to.")
    
    rfp_file = st.file_uploader(
        "Upload your RFP document", 
        type=['pdf', 'docx'],
        help="Upload a PDF or DOCX file containing the RFP requirements you want to respond to."
    )
    
    if rfp_file:
        if st.button("🔍 Extract Requirements", type="primary"):
            with st.spinner("Extracting requirements from document..."):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{rfp_file.name.split('.')[-1]}") as temp_file:
                    temp_file.write(rfp_file.getvalue())
                    temp_path = temp_file.name
                
                try:
                    # Extract requirements
                    requirements = extract_requirements_from_file(temp_path)
                    st.session_state.requirements = requirements
                    
                    if requirements:
                        st.success(f"✅ Extracted {len(requirements)} requirements from the document!")
                    else:
                        st.warning("⚠️ No requirements found. Please try uploading a different document or check the file content.")
                        
                        # Show extracted text for debugging
                        from ingestion.requirement_extractor import RequirementExtractor
                        extractor = RequirementExtractor()
                        full_text = extractor._extract_text(temp_path)
                        st.text_area("Raw text extracted from document:", full_text[:1000] + "..." if len(full_text) > 1000 else full_text, height=200)
                    
                except Exception as e:
                    st.error(f"Error extracting requirements: {str(e)}")
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
    
    # Show extracted requirements
    if st.session_state.requirements:
        st.header("📋 Step 2: Review Extracted Requirements")
        
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
        
        # Step 3: Generate Responses
        st.header("⚡ Step 3: Generate Responses")
        st.success(f"✅ Knowledge base is ready! Using existing vector store with company information.")
        
        col1, col2 = st.columns(2)
        with col1:
            top_k = st.slider("Number of context chunks to retrieve", 1, 10, 3)
        with col2:
            ollama_model = st.selectbox("Ollama Model", ["llama3", "llama2", "mistral", "codellama"], index=0)
        
        if st.button("🚀 Generate All Responses", type="primary"):
            # Initialize RAG pipeline with existing vector store
            rag = RAGPipeline(model=ollama_model, store_dir="test_store")
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            results_container = st.container()
            
            results = []
            
            try:
                for i, requirement in enumerate(st.session_state.requirements):
                    status_text.text(f"Processing requirement {i+1}/{len(st.session_state.requirements)}: {requirement[:50]}...")
                    
                    # Process requirement using existing vector store
                    result = rag.ask(requirement, top_k)
                    results.append({
                        "requirement": requirement,
                        "response": result["answer"],
                        "status": "success"
                    })
                    
                    # Update progress
                    progress_bar.progress((i + 1) / len(st.session_state.requirements))
                    
                    # Show progress in real-time
                    with results_container:
                        st.write(f"✅ Completed requirement {i+1}")
                
                st.session_state.responses = results
                status_text.text("✅ All responses generated successfully!")
                
                # Display results summary
                st.success(f"🎉 Generated responses for all {len(results)} requirements!")
                
                # Show a preview
                with st.expander("📋 Preview Generated Responses", expanded=True):
                    for i, result in enumerate(results[:3], 1):  # Show first 3
                        st.markdown(f"### Requirement {i}")
                        st.markdown(f"**Question:** {result['requirement'][:150]}...")
                        st.markdown(f"**Response:** {result['response'][:300]}...")
                        st.markdown("---")
                    
                    if len(results) > 3:
                        st.info(f"Showing first 3 of {len(results)} responses. Download full results below.")
            
            except Exception as e:
                st.error(f"Error generating responses: {str(e)}")
                st.exception(e)
    
    # Step 4: Download Results
    if st.session_state.responses:
        st.header("📥 Step 4: Download Results")
        
        st.success(f"Ready to download results for {len(st.session_state.responses)} requirements!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📊 Excel Format")
            try:
                output_gen = OutputGenerator()
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
        st.markdown("## 📊 System Status")
        
        # Vector store status
        if vector_store_ready:
            st.success("✅ Knowledge base ready")
            st.caption("Using pre-built company knowledge base")
        else:
            st.error("❌ Knowledge base not found")
        
        # Requirements status
        if st.session_state.requirements:
            st.success(f"✅ {len(st.session_state.requirements)} requirements extracted")
        else:
            st.info("🔄 Upload RFP document to extract requirements")
        
        # Responses status
        if st.session_state.responses:
            st.success(f"✅ {len(st.session_state.responses)} responses generated")
        else:
            st.info("🔄 Generate responses using RAG pipeline")
        
        st.markdown("---")
        st.markdown("## 🔄 Reset")
        if st.button("🗑️ Clear Session Data"):
            st.session_state.requirements = []
            st.session_state.responses = []
            st.success("Session data cleared!")
            st.experimental_rerun()
        
        st.markdown("---")
        st.markdown("## 💡 How It Works")
        st.markdown("""
        1. **Upload RFP**: Upload your RFP document 
        2. **Extract**: Automatically extract requirements
        3. **Review**: Check and edit requirements if needed
        4. **Generate**: Use existing knowledge base to create responses
        5. **Download**: Get Excel, PDF, or CSV files
        
        **Note:** Responses are generated from your pre-built company knowledge base stored in the system.
        """)

if __name__ == "__main__":
    main()