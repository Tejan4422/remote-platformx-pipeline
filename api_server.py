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

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting RFP Response Generator API Server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Alternative Docs: http://localhost:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)