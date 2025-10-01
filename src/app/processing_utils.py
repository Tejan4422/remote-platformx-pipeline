"""
Processing utilities for RFP generation and indexing
"""
import streamlit as st
import tempfile
import os
from datetime import datetime
from pathlib import Path

from ingestion.requirement_extractor import RequirementExtractor, extract_requirements_from_file
from ingestion.rfp_response_indexer import RFPResponseIndexer
from app.rag_pipeline import RAGPipeline


def process_requirements_batch(requirements, rag, top_k, ollama_model, start_index=1):
    """Process a batch of requirements and update session state"""
    from app.ui_components import display_progress_tracking
    
    batch_results = []
    start_time = datetime.now()
    
    # Create progress tracking containers
    progress_container = st.container()
    status_text = st.empty()
    
    try:
        for i, requirement in enumerate(requirements):
            # Update current processing status
            actual_index = start_index + i
            status_text.text(f"Processing: {requirement[:80]}...")
            
            with progress_container:
                display_progress_tracking(
                    current=i + 1,
                    total=len(requirements),
                    current_item=requirement,
                    start_time=start_time
                )
            
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
        
        # Update session state
        if start_index == 1:
            st.session_state.responses = batch_results
        else:
            if 'responses' not in st.session_state:
                st.session_state.responses = []
            st.session_state.responses.extend(batch_results)
        
        # Clear progress displays and show completion
        progress_container.empty()
        status_text.empty()
        
        # Display final results
        completion_time = datetime.now() - start_time
        st.success(f"🎉 Generated responses for {len(batch_results)} requirements in {str(completion_time).split('.')[0]}!")
        
        return batch_results
        
    except Exception as e:
        progress_container.empty()
        status_text.empty()
        st.error(f"Error processing batch: {str(e)}")
        st.exception(e)
        return []


def extract_requirements_from_upload(uploaded_file):
    """Extract requirements from uploaded file"""
    from app.ui_components import save_uploaded_file_temporarily, cleanup_temp_file
    
    temp_path = save_uploaded_file_temporarily(uploaded_file)
    
    try:
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
        
        return requirements, temp_path
        
    except Exception as e:
        cleanup_temp_file(temp_path)
        raise e


def validate_and_preview_indexing_file(uploaded_file):
    """Validate and preview file for indexing"""
    from app.ui_components import save_uploaded_file_temporarily
    
    temp_path = save_uploaded_file_temporarily(uploaded_file)
    
    try:
        indexer = RFPResponseIndexer()
        result = indexer.process_rfp_responses(temp_path)
        
        if result['success']:
            st.success(f"✅ File validated successfully!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Requirement Column", result['requirement_column'])
                st.metric("Valid Pairs Found", result['total_pairs'])
            with col2:
                st.metric("Response Column", result['response_column'])
            
            # Show preview
            if result['total_pairs'] > 0:
                st.subheader("📋 Preview of RFP Pairs")
                preview_df = result['dataframe'][[result['requirement_column'], result['response_column']]].head(3)
                st.dataframe(preview_df, use_container_width=True)
                
                # Store result for indexing
                st.session_state.validation_result = result
                st.session_state.temp_file_path = temp_path
                return True
            else:
                st.warning("No valid requirement-response pairs found in the file.")
                return False
        else:
            st.error(f"❌ Validation failed: {result['error']}")
            if 'available_columns' in result:
                st.write("**Available columns:**", result['available_columns'])
                st.write("**Detected requirement column:**", result.get('detected_requirement_col', 'None'))
                st.write("**Detected response column:**", result.get('detected_response_col', 'None'))
            return False
            
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return False


def perform_indexing():
    """Perform the actual indexing of RFP responses"""
    if 'validation_result' not in st.session_state:
        st.error("No validation result found. Please validate file first.")
        return False
    
    try:
        indexer = RFPResponseIndexer()
        indexing_result = indexer.index_rfp_responses(st.session_state.temp_file_path)
        
        if indexing_result['success']:
            st.success("🎉 Successfully indexed RFP responses!")
            
            # Show results
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Documents Added", indexing_result['documents_added'])
            with col2:
                st.metric("Previous Count", indexing_result['initial_document_count'])
            with col3:
                st.metric("New Total", indexing_result['final_document_count'])
            
            # Show what was indexed
            with st.expander("📄 Indexed Documents Preview", expanded=False):
                result = st.session_state.validation_result
                documents = indexer.create_indexable_documents(result['rfp_pairs'])
                for i, doc in enumerate(documents[:3], 1):
                    st.text_area(f"Document {i}", doc[:500] + "..." if len(doc) > 500 else doc, height=200)
                if len(documents) > 3:
                    st.info(f"... and {len(documents) - 3} more documents")
            
            # Clear session state
            cleanup_indexing_session()
            return True
        else:
            st.error(f"❌ Indexing failed: {indexing_result['error']}")
            return False
            
    except Exception as e:
        st.error(f"Error during indexing: {str(e)}")
        st.exception(e)
        return False


def cleanup_indexing_session():
    """Clean up indexing session state"""
    from app.ui_components import cleanup_temp_file
    
    if 'validation_result' in st.session_state:
        del st.session_state.validation_result
    if 'temp_file_path' in st.session_state:
        cleanup_temp_file(st.session_state.temp_file_path)
        del st.session_state.temp_file_path


def process_direct_query(query, top_k, ollama_model):
    """Process a direct query to the vector store"""
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
        
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        st.session_state.chat_history.append(chat_entry)
        
        return result
        
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")
        st.exception(e)
        return None


def check_vector_store_exists():
    """Check if vector store exists and is ready"""
    return Path("test_store/index.faiss").exists() and Path("test_store/docstore.pkl").exists()


def get_vector_store_info():
    """Get information about the current vector store"""
    indexer = RFPResponseIndexer()
    return indexer.get_vector_store_info()


def initialize_session_state():
    """Initialize session state variables"""
    if 'requirements' not in st.session_state:
        st.session_state.requirements = []
    if 'responses' not in st.session_state:
        st.session_state.responses = []
    if 'vector_store_ready' not in st.session_state:
        st.session_state.vector_store_ready = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []


def generate_download_files(responses, extraction_metadata=None):
    """Generate download files (Excel and PDF) for responses"""
    from app.output_generator import OutputGenerator
    from app.pdf_generator import PDFGenerator
    
    downloads = {}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # Generate Excel
        output_gen = OutputGenerator()
        
        if (extraction_metadata and 
            extraction_metadata.get('has_structure') and
            'dataframe' in extraction_metadata):
            # Generate structured Excel preserving original format
            excel_bytes = output_gen.generate_structured_excel_bytes(
                responses,
                extraction_metadata['dataframe'],
                extraction_metadata['column_name']
            )
        else:
            # Generate standard Excel format
            excel_bytes = output_gen.generate_excel_bytes(responses)
        
        downloads['excel'] = {
            'data': excel_bytes,
            'filename': f"rfp_responses_{timestamp}.xlsx",
            'mime': "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
    except Exception as e:
        st.error(f"Error generating Excel: {str(e)}")
    
    try:
        # Generate PDF
        pdf_gen = PDFGenerator()
        pdf_bytes = pdf_gen.generate_pdf_bytes(responses, "RFP Response Document")
        
        downloads['pdf'] = {
            'data': pdf_bytes,
            'filename': f"rfp_responses_{timestamp}.pdf",
            'mime': "application/pdf"
        }
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
    
    return downloads