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
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],  # Add your frontend URLs
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
            extraction_metadata = extraction_result
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

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting RFP Response Generator API Server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Alternative Docs: http://localhost:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)