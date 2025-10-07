#!/usr/bin/env python3
"""
FastAPI Server for RFP Response Generator
Provides REST API endpoints for the RAG-based RFP processing system
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid
import tempfile
import shutil

# FastAPI imports
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# Add src to path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import our existing RAG components
from app.rag_pipeline import RAGPipeline
from ingestion.requirement_extractor import RequirementExtractor, extract_requirements_from_file
from ingestion.rfp_response_indexer import RFPResponseIndexer
from retrieval.vector_store import VectorStore

# Initialize FastAPI app
app = FastAPI(
    title="RFP Response Generator API",
    description="REST API for RAG-based RFP processing and response generation",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173", "http://localhost:3000", "*"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for session management (in production, use Redis or database)
sessions: Dict[str, Dict] = {}
temp_files: Dict[str, str] = {}

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3
    model: Optional[str] = "llama3"

class GenerateResponsesRequest(BaseModel):
    requirements: List[str]
    top_k: Optional[int] = 3
    model: Optional[str] = "llama3"
    session_id: str

class IndexResponsesRequest(BaseModel):
    file_path: Optional[str] = None
    rfp_pairs: Optional[List[Dict[str, str]]] = None
    metadata: Optional[Dict[str, Any]] = None

class UploadResponse(BaseModel):
    success: bool
    message: str
    session_id: str
    requirements: List[str]
    extraction_metadata: Optional[Dict] = None
    file_info: Dict[str, Any]

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    session_id: Optional[str] = None

# Health check endpoint
@app.get("/")
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return APIResponse(
        success=True,
        message="RFP Response Generator API is running",
        data={
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "status": "healthy"
        }
    )

# Vector store status endpoint
@app.get("/api/vector-store/status")
async def get_vector_store_status():
    """Get the current status of the vector store"""
    try:
        # Check if vector store exists
        vector_store_path = Path("test_store")
        faiss_path = vector_store_path / "index.faiss"
        docstore_path = vector_store_path / "docstore.pkl"
        
        exists = faiss_path.exists() and docstore_path.exists()
        
        total_documents = 0
        if exists:
            try:
                # Try to get document count (this is a simple check)
                indexer = RFPResponseIndexer()
                store_info = indexer.get_vector_store_info()
                total_documents = store_info.get('total_documents', 0)
            except Exception as e:
                print(f"Error getting document count: {e}")
        
        return APIResponse(
            success=True,
            message="Vector store status retrieved",
            data={
                "exists": exists,
                "total_documents": total_documents,
                "vector_store_path": str(vector_store_path),
                "ready_for_queries": exists
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking vector store: {str(e)}")

# File upload and requirement extraction endpoint
@app.post("/api/upload-rfp", response_model=UploadResponse)
async def upload_rfp_document(file: UploadFile = File(...)):
    """
    Upload an RFP document and extract requirements
    Supports PDF, DOCX, XLSX, XLS files
    """
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.xlsx', '.xls'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Create temporary file
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    
    temp_file_path = temp_dir / f"{session_id}_{file.filename}"
    
    try:
        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Store temp file path for cleanup
        temp_files[session_id] = str(temp_file_path)
        
        # Extract requirements
        extractor = RequirementExtractor()
        
        # Check if it's a structured file (Excel)
        if file_extension in {'.xlsx', '.xls'}:
            # Use metadata extraction for structured files
            extraction_result = extractor.extract_with_metadata(str(temp_file_path))
            requirements = extraction_result['requirements']
            # Convert DataFrame to dict for JSON serialization
            extraction_metadata = {}
            for key, value in extraction_result.items():
                try:
                    if hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict', None)):
                        extraction_metadata[key] = value.to_dict('records')
                    else:
                        extraction_metadata[key] = value
                except Exception as e:
                    # Fallback to string representation if serialization fails
                    extraction_metadata[key] = str(value)
                    print(f"Warning: Could not serialize {key}: {e}")
        else:
            # Use regular extraction for PDF/DOCX
            requirements = extractor.extract_from_file(str(temp_file_path))
            extraction_metadata = None
        
        # Store session data
        sessions[session_id] = {
            'requirements': requirements,
            'extraction_metadata': extraction_metadata,
            'uploaded_file': file.filename,
            'file_type': file_extension,
            'timestamp': datetime.now().isoformat(),
            'temp_file_path': str(temp_file_path)
        }
        
        file_info = {
            'filename': file.filename,
            'size': file.size if hasattr(file, 'size') else 'unknown',
            'type': file.content_type,
            'extension': file_extension
        }
        
        return UploadResponse(
            success=True,
            message=f"Successfully extracted {len(requirements)} requirements from {file.filename}",
            session_id=session_id,
            requirements=requirements,
            extraction_metadata=extraction_metadata,
            file_info=file_info
        )
        
    except Exception as e:
        # Clean up on error
        if temp_file_path.exists():
            temp_file_path.unlink()
        if session_id in temp_files:
            del temp_files[session_id]
        if session_id in sessions:
            del sessions[session_id]
            
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# Get requirements for a session
@app.get("/api/requirements/{session_id}")
async def get_requirements(session_id: str):
    """Get extracted requirements for a specific session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[session_id]
    
    return APIResponse(
        success=True,
        message="Requirements retrieved successfully",
        session_id=session_id,
        data={
            'requirements': session_data['requirements'],
            'extraction_metadata': session_data.get('extraction_metadata'),
            'file_info': {
                'filename': session_data['uploaded_file'],
                'file_type': session_data['file_type'],
                'upload_time': session_data['timestamp']
            },
            'total_requirements': len(session_data['requirements'])
        }
    )

# Get generated responses for a session
@app.get("/api/responses/{session_id}")
async def get_responses(session_id: str):
    """Get generated responses for a specific session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[session_id]
    
    if 'responses' not in session_data:
        raise HTTPException(
            status_code=404, 
            detail="No responses found for this session. Generate responses first using /api/generate-responses"
        )
    
    responses = session_data['responses']
    successful_responses = [r for r in responses if r['status'] == 'success']
    
    return APIResponse(
        success=True,
        message="Responses retrieved successfully",
        session_id=session_id,
        data={
            'responses': responses,
            'summary': {
                'total_requirements': len(session_data['requirements']),
                'total_responses': len(responses),
                'successful_responses': len(successful_responses),
                'success_rate': len(successful_responses) / len(responses) * 100 if responses else 0
            },
            'generation_info': {
                'response_generation_time': session_data.get('response_generation_time'),
                'upload_time': session_data['timestamp']
            }
        }
    )

# Direct query endpoint
@app.post("/api/query")
async def direct_query(request: QueryRequest):
    """
    Direct query endpoint - Query the vector store directly
    """
    try:
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline()
        
        # Check if vector store exists
        vector_store_path = Path("test_store")
        if not (vector_store_path / "index.faiss").exists():
            raise HTTPException(
                status_code=404, 
                detail="Vector store not found. Please upload and index some documents first."
            )
        
        # Perform direct query
        result = rag_pipeline.ask(
            query=request.query,
            top_k=request.top_k,
            include_quality_score=True
        )
        
        return APIResponse(
            success=True,
            message="Query executed successfully",
            data={
                'query': request.query,
                'answer': result['answer'],
                'context': result['context'],
                'quality_score': result.get('quality_score'),
                'quality_status': result.get('quality_status'),
                'parameters': {
                    'top_k': request.top_k,
                    'model': request.model
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing query: {str(e)}")

# Generate responses endpoint
@app.post("/api/generate-responses")
async def generate_responses(request: GenerateResponsesRequest):
    """
    Generate responses for multiple requirements using the RAG pipeline
    """
    try:
        # Validate session exists
        if request.session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline()
        
        # Check if vector store exists
        vector_store_path = Path("test_store")
        if not (vector_store_path / "index.faiss").exists():
            raise HTTPException(
                status_code=404, 
                detail="Vector store not found. Please upload and index some documents first."
            )
        
        # Generate responses for each requirement
        responses = []
        for i, requirement in enumerate(request.requirements):
            try:
                result = rag_pipeline.ask(
                    query=requirement,
                    top_k=request.top_k,
                    include_quality_score=True
                )
                
                responses.append({
                    'requirement_index': i,
                    'requirement': requirement,
                    'answer': result['answer'],
                    'quality_score': result.get('quality_score'),
                    'quality_status': result.get('quality_status'),
                    'status': 'success'
                })
                
            except Exception as req_error:
                responses.append({
                    'requirement_index': i,
                    'requirement': requirement,
                    'answer': None,
                    'error': str(req_error),
                    'status': 'error'
                })
        
        # Update session with generated responses
        sessions[request.session_id]['responses'] = responses
        sessions[request.session_id]['response_generation_time'] = datetime.now().isoformat()
        
        # Calculate success metrics
        successful_responses = [r for r in responses if r['status'] == 'success']
        failed_responses = [r for r in responses if r['status'] == 'error']
        
        return APIResponse(
            success=True,
            message=f"Generated responses for {len(successful_responses)}/{len(request.requirements)} requirements",
            session_id=request.session_id,
            data={
                'responses': responses,
                'summary': {
                    'total_requirements': len(request.requirements),
                    'successful_responses': len(successful_responses),
                    'failed_responses': len(failed_responses),
                    'success_rate': len(successful_responses) / len(request.requirements) * 100
                },
                'parameters': {
                    'top_k': request.top_k,
                    'model': request.model
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating responses: {str(e)}")

# Clean up session endpoint
@app.delete("/api/session/{session_id}")
async def cleanup_session(session_id: str):
    """Clean up session data and temporary files"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Clean up temp file
    if session_id in temp_files:
        temp_file_path = Path(temp_files[session_id])
        if temp_file_path.exists():
            temp_file_path.unlink()
        del temp_files[session_id]
    
    # Remove session data
    del sessions[session_id]
    
    return APIResponse(
        success=True,
        message="Session cleaned up successfully",
        session_id=session_id
    )

# ============================================================================
# PHASE 4: KNOWLEDGE BASE APIs
# ============================================================================

# Index RFP responses endpoint
@app.post("/api/index-responses")
async def index_rfp_responses(file: UploadFile = File(...)):
    """
    Index RFP responses from an uploaded Excel file to the vector store
    Expected format: Excel file with 'Requirement' and 'Response' columns
    """
    # Validate file type
    allowed_extensions = {'.xlsx', '.xls'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type for RFP indexing. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    temp_file_path = temp_dir / f"index_{uuid.uuid4()}_{file.filename}"
    
    try:
        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Initialize indexer
        indexer = RFPResponseIndexer()
        
        # Index the RFP responses
        result = indexer.index_rfp_responses(str(temp_file_path))
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Unknown indexing error'))
        
        # Clean up temp file
        temp_file_path.unlink()
        
        return APIResponse(
            success=True,
            message=f"Successfully indexed {result['documents_added']} RFP responses from {file.filename}",
            data={
                'file_info': {
                    'filename': file.filename,
                    'size': file.size if hasattr(file, 'size') else 'unknown',
                    'type': file.content_type
                },
                'indexing_results': {
                    'documents_added': result['documents_added'],
                    'rfp_pairs_found': result['total_pairs'],
                    'requirement_column': result['requirement_column'],
                    'response_column': result['response_column'],
                    'initial_document_count': result['initial_document_count'],
                    'final_document_count': result['final_document_count'],
                    'timestamp': result['timestamp']
                },
                'vector_store_info': {
                    'path': result['vector_store_path'],
                    'total_documents': result['final_document_count']
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        if temp_file_path.exists():
            temp_file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error indexing RFP responses: {str(e)}")

# Upload historical data endpoint 
@app.post("/api/upload-historical-data")
async def upload_historical_data(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    description: Optional[str] = None
):
    """
    Upload multiple historical data files for batch indexing
    Supports multiple Excel files with RFP response data
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Validate all files
    allowed_extensions = {'.xlsx', '.xls'}
    for file in files:
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.filename}. Allowed: {', '.join(allowed_extensions)}"
            )
    
    upload_id = str(uuid.uuid4())
    temp_dir = Path("temp_uploads") / upload_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Save all files
        saved_files = []
        for file in files:
            temp_file_path = temp_dir / f"{file.filename}"
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append({
                'filename': file.filename,
                'path': str(temp_file_path),
                'size': file.size if hasattr(file, 'size') else 'unknown'
            })
        
        # Process files and index
        indexer = RFPResponseIndexer()
        total_documents_added = 0
        total_pairs_found = 0
        processing_results = []
        
        for file_info in saved_files:
            try:
                result = indexer.index_rfp_responses(file_info['path'])
                if result['success']:
                    total_documents_added += result['documents_added']
                    total_pairs_found += result['total_pairs']
                    processing_results.append({
                        'filename': file_info['filename'],
                        'success': True,
                        'documents_added': result['documents_added'],
                        'pairs_found': result['total_pairs'],
                        'requirement_column': result['requirement_column'],
                        'response_column': result['response_column']
                    })
                else:
                    processing_results.append({
                        'filename': file_info['filename'],
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    })
            except Exception as e:
                processing_results.append({
                    'filename': file_info['filename'],
                    'success': False,
                    'error': str(e)
                })
        
        # Clean up temp directory
        shutil.rmtree(temp_dir)
        
        successful_files = [r for r in processing_results if r['success']]
        failed_files = [r for r in processing_results if not r['success']]
        
        return APIResponse(
            success=len(successful_files) > 0,
            message=f"Processed {len(successful_files)}/{len(files)} files successfully. Added {total_documents_added} documents to vector store.",
            data={
                'upload_info': {
                    'upload_id': upload_id,
                    'description': description,
                    'timestamp': datetime.now().isoformat(),
                    'total_files': len(files),
                    'successful_files': len(successful_files),
                    'failed_files': len(failed_files)
                },
                'summary': {
                    'total_documents_added': total_documents_added,
                    'total_pairs_found': total_pairs_found
                },
                'processing_results': processing_results,
                'successful_files': successful_files,
                'failed_files': failed_files
            }
        )
        
    except Exception as e:
        # Clean up on error
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        raise HTTPException(status_code=500, detail=f"Error processing historical data: {str(e)}")

# Get vector store stats endpoint
@app.get("/api/vector-store/stats")
async def get_vector_store_stats():
    """
    Get comprehensive statistics about the vector store
    """
    try:
        indexer = RFPResponseIndexer()
        store_info = indexer.get_vector_store_info()
        
        # Get additional file system info
        vector_store_path = Path("test_store")
        faiss_path = vector_store_path / "index.faiss"
        docstore_path = vector_store_path / "docstore.pkl"
        
        file_stats = {}
        if faiss_path.exists():
            faiss_stat = faiss_path.stat()
            file_stats['faiss_index'] = {
                'size_bytes': faiss_stat.st_size,
                'size_mb': round(faiss_stat.st_size / (1024 * 1024), 2),
                'modified': datetime.fromtimestamp(faiss_stat.st_mtime).isoformat()
            }
        
        if docstore_path.exists():
            docstore_stat = docstore_path.stat()
            file_stats['document_store'] = {
                'size_bytes': docstore_stat.st_size,
                'size_mb': round(docstore_stat.st_size / (1024 * 1024), 2),
                'modified': datetime.fromtimestamp(docstore_stat.st_mtime).isoformat()
            }
        
        # Calculate total size
        total_size_bytes = sum(
            stats['size_bytes'] for stats in file_stats.values()
        )
        
        return APIResponse(
            success=True,
            message="Vector store statistics retrieved successfully",
            data={
                'vector_store': {
                    'exists': store_info['exists'],
                    'path': store_info['path'],
                    'total_documents': store_info.get('total_documents', 0),
                    'vector_dimension': store_info.get('vector_dimension', 0),
                    'index_size': store_info.get('index_size', 0)
                },
                'file_statistics': file_stats,
                'storage_summary': {
                    'total_size_bytes': total_size_bytes,
                    'total_size_mb': round(total_size_bytes / (1024 * 1024), 2),
                    'files_count': len(file_stats)
                },
                'capabilities': {
                    'ready_for_queries': store_info['exists'],
                    'supports_similarity_search': store_info['exists'],
                    'can_add_documents': True
                },
                'metadata': {
                    'retrieved_at': datetime.now().isoformat(),
                    'vector_store_path': str(vector_store_path)
                }
            }
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Error retrieving vector store statistics: {str(e)}",
            data={
                'error_details': str(e),
                'vector_store_path': str(Path("test_store"))
            }
        )

# Download/Export responses endpoint
@app.get("/api/download-responses/{session_id}")
async def download_responses(session_id: str, format: str = "excel"):
    """
    Download generated responses in Excel or PDF format
    """
    try:
        # Validate session exists
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = sessions[session_id]
        
        if 'responses' not in session_data:
            raise HTTPException(
                status_code=404, 
                detail="No responses found for this session. Generate responses first."
            )
        
        responses = session_data['responses']
        requirements = session_data['requirements']
        
        if format.lower() == "excel":
            # Generate Excel file
            import pandas as pd
            import io
            
            # Prepare data for Excel
            data = []
            for response in responses:
                data.append({
                    'Requirement': response['requirement'],
                    'Generated_Response': response.get('answer', 'N/A'),
                    'Quality_Score': response.get('quality_score', 'N/A'),
                    'Quality_Status': response.get('quality_status', 'N/A'),
                    'Status': response['status']
                })
            
            df = pd.DataFrame(data)
            
            # Create Excel file in memory
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='RFP_Responses', index=False)
            
            excel_buffer.seek(0)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rfp_responses_{session_id[:8]}_{timestamp}.xlsx"
            
            from fastapi.responses import StreamingResponse
            
            return StreamingResponse(
                io.BytesIO(excel_buffer.getvalue()),
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        elif format.lower() == "pdf":
            # Generate PDF file
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            import io
            
            # Create PDF buffer
            pdf_buffer = io.BytesIO()
            
            # Create the PDF document
            doc = SimpleDocTemplate(pdf_buffer, pagesize=A4,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=12,
                spaceBefore=12,
                spaceAfter=6,
                textColor=colors.HexColor('#2563eb')
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=12,
                wordWrap='CJK'
            )
            
            # Add title
            title = Paragraph("RFP Response Report", title_style)
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            # Add metadata
            metadata_data = [
                ['Session ID:', session_id[:8]],
                ['Generated:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                ['Total Requirements:', str(len(requirements))],
                ['Successful Responses:', str(len([r for r in responses if r.get('status') == 'success']))],
            ]
            
            metadata_table = Table(metadata_data, colWidths=[2*inch, 3*inch])
            metadata_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(metadata_table)
            elements.append(Spacer(1, 20))
            
            # Add responses
            for i, response in enumerate(responses):
                # Requirement header
                req_heading = Paragraph(f"Requirement {i+1}", heading_style)
                elements.append(req_heading)
                
                # Requirement text
                req_text = Paragraph(f"<b>Question:</b> {response['requirement']}", normal_style)
                elements.append(req_text)
                
                # Response text
                response_text = response.get('answer', 'No response generated')
                resp_paragraph = Paragraph(f"<b>Generated Response:</b> {response_text}", normal_style)
                elements.append(resp_paragraph)
                
                # Quality information
                quality_score = response.get('quality_score', 0)
                quality_status = response.get('quality_status', 'Unknown')
                quality_text = Paragraph(f"<b>Quality Score:</b> {quality_score}% ({quality_status})", normal_style)
                elements.append(quality_text)
                
                # Add spacing between requirements
                elements.append(Spacer(1, 20))
                
                # Add page break every 3 requirements to avoid overly long pages
                if (i + 1) % 3 == 0 and i < len(responses) - 1:
                    elements.append(PageBreak())
            
            # Build PDF
            doc.build(elements)
            pdf_buffer.seek(0)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rfp_responses_{session_id[:8]}_{timestamp}.pdf"
            
            from fastapi.responses import StreamingResponse
            
            return StreamingResponse(
                io.BytesIO(pdf_buffer.getvalue()),
                media_type='application/pdf',
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use 'excel' or 'pdf'.")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating download: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("Starting RFP Response Generator API Server...")
    print("API Documentation: http://localhost:8001/docs")
    print("Alternative Docs: http://localhost:8001/redoc")
    try:
        uvicorn.run("api_server:app", host="0.0.0.0", port=8001, reload=False)
    except Exception as e:
        print(f"Error starting server: {e}")
        uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)