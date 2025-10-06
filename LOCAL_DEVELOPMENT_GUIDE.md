# Local Development Guide

## Overview

This document provides instructions for setting up, running, and testing the RFP Response Generator system in a local development environment. The system consists of a FastAPI backend server and a React TypeScript frontend application.

## Architecture

```
Backend (FastAPI)     Frontend (React + Vite)
localhost:8001   <->  localhost:8080
```

## Prerequisites

### System Requirements
- Python 3.8 or higher
- Node.js 16.x or higher
- npm or yarn package manager
- Git

### External Dependencies
- Ollama (for local LLM inference)
- FAISS vector store (included in requirements)

## Environment Setup

### 1. Clone and Navigate to Repository
```bash
git clone <repository-url>
cd local-rag-app
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Verify Vector Store
Ensure the vector store exists:
```bash
ls -la test_store/
# Should contain: index.faiss, docstore.pkl
```

#### Configure Ollama
```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama service
ollama serve

# Pull required model (in separate terminal)
ollama pull llama3
```

### 3. Frontend Setup

#### Install Node Dependencies
```bash
cd frontend
npm install
cd ..
```

## Running the Application

### Start Services in Order

#### 1. Start Backend Server
```bash
python api_server.py
```

Expected output:
```
Starting RFP Response Generator API Server...
API Documentation: http://localhost:8001/docs
Alternative Docs: http://localhost:8001/redoc
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

#### 2. Start Frontend Development Server
```bash
cd frontend
npm run dev
```

Expected output:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:8080/
➜  Network: use --host to expose
➜  press h + enter to show help
```

## Service Verification

### Backend Health Check
```bash
curl http://localhost:8001/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-XX-XXTXX:XX:XX.XXXXXX",
  "version": "1.0.0"
}
```

### Frontend Access
Navigate to: http://localhost:8080

### API Documentation
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Testing Procedures

### 1. System Integration Test
```bash
python quick_test.py
```

This validates:
- Vector store accessibility
- Model availability
- Core RAG functionality

### 2. API Endpoint Testing

#### Upload RFP Document
```bash
curl -X POST "http://localhost:8001/api/upload-rfp" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/raw/Test_rfp - Sheet1.pdf" \
  -F "description=Test RFP upload"
```

#### Extract Requirements
```bash
curl -X POST "http://localhost:8001/api/extract-requirements" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-id"}'
```

#### Generate RAG Responses
```bash
curl -X POST "http://localhost:8001/api/generate-responses" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "requirements": ["Requirement 1", "Requirement 2"]
  }'
```

### 3. Frontend Workflow Testing

#### Complete RFP Processing Workflow
1. Access http://localhost:8080
2. Navigate to "Upload RFP Document"
3. Upload test PDF file
4. Review extracted requirements
5. Generate responses
6. Download results as Excel

#### Expected Workflow States
- File upload progress indication
- Requirement extraction completion
- Response generation with quality scores
- Successful Excel download

### 4. Performance Testing

#### Vector Store Statistics
```bash
curl http://localhost:8001/api/vector-store/stats
```

Expected metrics:
- Document count: >0
- Index size information
- Last modification timestamps

#### Response Quality Validation
- Quality scores should range 75-95%
- Response generation time <30 seconds per requirement
- Memory usage stable during processing

## Troubleshooting

### Common Issues

#### Backend Fails to Start
**Error**: `ModuleNotFoundError: No module named 'app'`
**Solution**: Ensure you're running from the project root directory

#### Vector Store Not Found
**Error**: `Vector store not found in test_store/ directory`
**Solution**: 
1. Verify `test_store/index.faiss` and `test_store/docstore.pkl` exist
2. Run initial indexing if files are missing

#### Ollama Connection Failed
**Error**: `Connection refused to localhost:11434`
**Solution**:
1. Start Ollama service: `ollama serve`
2. Verify model availability: `ollama list`
3. Pull required model: `ollama pull llama3`

#### Frontend Build Errors
**Error**: `Module not found` during npm install
**Solution**:
1. Clear npm cache: `npm cache clean --force`
2. Delete node_modules: `rm -rf node_modules`
3. Reinstall: `npm install`

#### CORS Errors
**Error**: Cross-origin requests blocked
**Solution**: Backend allows origins: localhost:8080, localhost:5173, localhost:3000

### Log Files

#### Backend Logs
- Console output for real-time debugging
- API request/response logging enabled
- Error stack traces displayed

#### Frontend Logs
- Browser console for client-side issues
- Network tab for API communication
- Vite dev server logs in terminal

## Development Commands

### Backend Development
```bash
# Run with auto-reload
uvicorn api_server:app --host 0.0.0.0 --port 8001 --reload

# Run tests
python -m pytest tests/

# Check API endpoints
python test_api.py
```

### Frontend Development
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## API Reference

### Core Endpoints
- `POST /api/upload-rfp` - Upload RFP document
- `POST /api/extract-requirements` - Extract requirements from uploaded document
- `POST /api/generate-responses` - Generate RAG responses for requirements
- `GET /api/download/{session_id}` - Download results as Excel file
- `GET /api/vector-store/stats` - Get vector store statistics
- `GET /health` - Health check endpoint

### Response Formats
All API responses follow consistent JSON structure:
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2024-XX-XXTXX:XX:XX"
}
```

## Quality Metrics

### Expected Performance
- Document upload: <5 seconds for files <10MB
- Requirement extraction: <15 seconds
- Response generation: <30 seconds per requirement
- Quality scores: 75-95% range
- System memory usage: <2GB during processing

### Success Criteria
- All API endpoints return HTTP 200 for valid requests
- Frontend displays all workflow stages correctly
- Generated responses contain relevant content
- Excel download produces valid, formatted file
- No memory leaks during extended operation

## Security Considerations

### Local Development Only
This setup is intended for local development and testing only. Do not expose these services to external networks without additional security measures.

### File Upload Restrictions
- Maximum file size: 50MB
- Supported formats: PDF, DOCX, TXT
- Files stored temporarily and cleaned up after processing

### API Access
- No authentication required for local development
- CORS configured for common localhost ports
- File system access restricted to designated directories
