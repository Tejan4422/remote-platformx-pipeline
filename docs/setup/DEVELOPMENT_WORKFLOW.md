# Development Workflow Guide

This guide outlines the complete development workflow for the Local RAG Application, based on common development patterns and debugging scenarios.

## Complete RFP Processing Workflow

### Overview
The application provides a complete RFP (Request for Proposal) document processing pipeline:

1. **Document Upload** → 2. **Requirements Extraction** → 3. **RAG Processing** → 4. **Response Generation** → 5. **Excel Export**

### Frontend Workflow Components

#### 1. Document Upload (`DocumentUpload.tsx`)
- **Purpose**: Upload RFP documents and extract requirements
- **API Integration**: 
  - `POST /api/upload-rfp` - Upload PDF/Excel files
  - `POST /api/extract-requirements` - Extract requirements from uploaded documents
- **Session Management**: Creates and manages session IDs for workflow tracking
- **File Support**: PDF, Excel (.xlsx, .xls)

#### 2. Requirements Manager (`RequirementsManager.tsx`)
- **Purpose**: Display extracted requirements before RAG processing
- **Features**: 
  - View extracted requirements in structured format
  - Session-based requirement loading
  - Loading states and empty state handling
- **API Integration**: `GET /api/requirements/{session_id}`

#### 3. Response Generator (`ResponseGenerator.tsx`)
- **Purpose**: Configure and initiate RAG processing
- **Features**:
  - Custom query input
  - Processing parameters (top_k, model selection)
  - Quality score thresholds
- **API Integration**: `POST /api/process-requirements`

#### 4. Response Results (`ResponseResults.tsx`)
- **Purpose**: Display generated responses and quality scores
- **Features**:
  - Response text display
  - Quality score visualization (80-95% typical range)
  - Individual requirement responses
- **API Integration**: Receives processed results from RAG pipeline

#### 5. Excel Export
- **Purpose**: Download processed results as Excel file
- **API Integration**: `GET /api/download-results/{session_id}`
- **Output**: Formatted Excel with requirements and AI responses

### Direct Query Feature

#### Chat Interface (`ChatInterface.tsx`)
- **Purpose**: Direct question-answering without document upload
- **Features**:
  - Real-time AI responses
  - Quality score display
  - Chat history
- **API Integration**: `POST /api/query`
- **Use Cases**: Quick questions about existing knowledge base

## API Endpoints Reference

### Core Workflow Endpoints

#### Document Management
```typescript
// Upload RFP document
POST /api/upload-rfp
Content-Type: multipart/form-data
Body: { file: File, description?: string }
Response: { session_id: string, message: string }

// Extract requirements from uploaded document
POST /api/extract-requirements
Body: { session_id: string }
Response: { 
  data: { 
    requirements: Array<{ id: string, text: string, category?: string }> 
  } 
}
```

#### Requirements & Processing
```typescript
// Get extracted requirements
GET /api/requirements/{session_id}
Response: { 
  data: { 
    requirements: Array<{ id: string, text: string, category?: string }> 
  } 
}

// Process requirements with RAG
POST /api/process-requirements
Body: { 
  session_id: string, 
  custom_query?: string,
  top_k?: number 
}
Response: { responses: Array<ResponseData>, quality_scores: number[] }
```

#### Results & Export
```typescript
// Download results as Excel
GET /api/download-results/{session_id}
Response: Excel file download

// Direct query (no upload required)
POST /api/query
Body: { query: string, top_k?: number }
Response: { response: string, quality_score: number }
```

### System Endpoints
```typescript
// Health check
GET /health
Response: { status: "healthy" }

// Vector store status
GET /api/vector-store/status
Response: { document_count: number, status: string }
```

## Session Management

### Session Context (`SessionContext.tsx`)
- **Purpose**: Global state management for RFP workflow
- **State Management**:
  - Session ID tracking
  - Requirements storage
  - Response storage
  - Loading states

### Session Lifecycle
1. **Session Creation**: Automatic on document upload
2. **Session Persistence**: Maintained throughout workflow
3. **Session Data**: Requirements, responses, quality scores
4. **Session Cleanup**: Manual or automatic (implementation-dependent)

## Development Debugging Guide

### Common Issues & Solutions

#### Requirements Not Displaying
**Symptoms**: RequirementsManager shows empty or loading state
**Debug Steps**:
1. Check session ID in SessionContext
2. Verify API response structure: `data.data.requirements` vs `data.requirements`
3. Check console logs for API errors
4. Verify session exists in backend

**Recent Fix Applied**:
```typescript
// Fixed API response structure handling
const requirements = data?.data?.requirements || data?.requirements || [];
```

#### API Integration Issues
**Symptoms**: Components using mock data instead of real API
**Debug Steps**:
1. Verify backend server is running on port 8001
2. Check API endpoint URLs in component code
3. Verify CORS configuration
4. Check network tab for failed requests

**Example Fix**:
```typescript
// Before: Mock response
const mockResponse = { response: "Mock answer", quality_score: 85 };

// After: Real API integration
const response = await fetch('/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query, top_k })
});
```

#### File Upload Problems
**Common Issues**:
- File size limits
- Unsupported file types
- Session creation failures

**Debug Commands**:
```bash
# Test upload API directly
curl -X POST "http://localhost:8001/api/upload-rfp" \
  -F "file=@./data/raw/Test_rfp - Sheet1.pdf" \
  -F "description=Test upload"

# Check temp uploads directory
ls -la temp_uploads/
```

### Quality Score Analysis

#### Expected Quality Ranges
- **High Quality**: 90-95% (Well-matched content)
- **Good Quality**: 80-89% (Relevant but not perfect match)
- **Moderate Quality**: 70-79% (Partially relevant)
- **Low Quality**: <70% (Poor match or insufficient data)

#### Quality Score Debugging
```bash
# Test quality scoring
python test_quality_scoring.py

# Check vector store performance
python test_vector_store.py
```

## Testing Procedures

### Manual Testing Workflow

#### Complete Workflow Test
1. **Start Servers**:
   ```bash
   # Terminal 1: Backend
   python api_server.py
   
   # Terminal 2: Frontend
   cd frontend && npm run dev
   ```

2. **Test Document Upload**:
   - Navigate to http://localhost:8080
   - Upload test document (`data/raw/Test_rfp - Sheet1.pdf`)
   - Verify session creation and file processing

3. **Test Requirements Extraction**:
   - Click "Extract Requirements" button
   - Verify requirements appear in RequirementsManager
   - Check requirement text and formatting

4. **Test RAG Processing**:
   - Configure processing parameters
   - Submit for processing
   - Verify responses and quality scores

5. **Test Excel Export**:
   - Click download button
   - Verify Excel file contains requirements and responses

#### Direct Query Test
1. Navigate to Direct Query tab
2. Enter test question: "What are the key requirements for this project?"
3. Verify real AI response (not mock data)
4. Check quality score display

### Automated Testing
```bash
# API endpoint tests
python test_api.py

# Complete workflow test
python test_complete_workflow.py

# Quality scoring tests
python test_quality_scoring.py
```

## Performance Optimization

### Backend Optimization
- **Vector Store**: FAISS indexing with 83 documents
- **Model**: LLaMA3 with optimized parameters
- **Caching**: Session-based result caching
- **Concurrency**: FastAPI async support

### Frontend Optimization
- **Component Lazy Loading**: React.lazy() for code splitting
- **State Management**: Efficient SessionContext updates
- **API Caching**: React Query for request caching
- **Bundle Optimization**: Vite build optimization

## Security Considerations

### File Upload Security
- File type validation (PDF, Excel only)
- File size limits
- Temporary file cleanup
- Path traversal protection

### API Security
- CORS configuration for localhost development
- Input validation and sanitization
- Session-based access control
- Error message sanitization

## Environment Configuration

### Development Environment
```bash
# Backend requirements
Python 3.8+
FastAPI 0.68+
LLaMA3 model access
FAISS vector store

# Frontend requirements
Node.js 16+
React 18+
TypeScript 4.7+
Vite 4+
```

### Production Considerations
- Environment variable configuration
- Database migration (from memory to persistent storage)
- Load balancing for multiple instances
- Logging and monitoring setup
- SSL/TLS configuration

## Troubleshooting Reference

### Server Issues
```bash
# Check if processes are running
ps aux | grep -E "(api_server|vite)"

# Check port usage
lsof -i :8001  # Backend
lsof -i :8080  # Frontend

# Kill zombie processes
pkill -f api_server
pkill -f "vite.*dev"
```

### Development Issues
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Python environment reset
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Data Issues
```bash
# Clear vector store
rm -rf test_store/

# Clear temporary uploads
rm -rf temp_uploads/*

# Reinitialize vector store
python -c "from src.vector_store.faiss_store import FaissVectorStore; store = FaissVectorStore(); store.build_index()"
```