# RFP Response Generator API Documentation
## For Frontend Integration (Lovable UI)

### 🌐 **Base Configuration**
- **Base URL**: `http://localhost:8001`
- **Content-Type**: `application/json` (for POST requests)
- **CORS**: Enabled for all origins
- **API Documentation**: Available at `http://localhost:8001/docs` (Swagger UI)

---

## 📋 **API Endpoints Overview**

| Category | Endpoint | Method | Purpose |
|----------|----------|--------|---------|
| **Health** | `/health` | GET | Check API server status |
| **Vector Store** | `/api/vector-store/status` | GET | Check knowledge base status |
| **Vector Store** | `/api/vector-store/stats` | GET | Get detailed vector store statistics |
| **Document Upload** | `/api/upload-rfp` | POST | Upload RFP document and extract requirements |
| **Requirements** | `/api/requirements/{session_id}` | GET | Get extracted requirements for a session |
| **Direct Query** | `/api/query` | POST | Direct query to knowledge base |
| **Response Generation** | `/api/generate-responses` | POST | Generate responses for requirements |
| **Response Retrieval** | `/api/responses/{session_id}` | GET | Get generated responses for a session |
| **Knowledge Base** | `/api/index-responses` | POST | Index historical RFP responses |
| **Knowledge Base** | `/api/upload-historical-data` | POST | Batch upload historical data |
| **Session Management** | `/api/session/{session_id}` | DELETE | Clean up session data |

---

## 🔍 **Detailed API Documentation**

### 1. Health Check API

#### `GET /health`
**Purpose**: Check if the API server is running and healthy.

**Request**:
```bash
curl http://localhost:8001/health
```

**Response**:
```json
{
  "success": true,
  "message": "RFP Response Generator API is running",
  "data": {
    "timestamp": "2025-10-04T14:07:33.795108",
    "version": "1.0.0",
    "status": "healthy"
  },
  "session_id": null
}
```

**Frontend Usage**:
```typescript
const checkHealth = async () => {
  const response = await fetch('http://localhost:8001/health');
  const data = await response.json();
  return data.success; // true if healthy
};
```

---

### 2. Vector Store Status API

#### `GET /api/vector-store/status`
**Purpose**: Check if the knowledge base exists and is ready for queries.

**Request**:
```bash
curl http://localhost:8001/api/vector-store/status
```

**Response**:
```json
{
  "success": true,
  "message": "Vector store status retrieved",
  "data": {
    "exists": true,
    "total_documents": 83,
    "vector_store_path": "test_store",
    "ready_for_queries": true
  },
  "session_id": null
}
```

**Frontend Usage**:
```typescript
interface VectorStoreStatus {
  exists: boolean;
  total_documents: number;
  vector_store_path: string;
  ready_for_queries: boolean;
}

const getVectorStoreStatus = async (): Promise<VectorStoreStatus> => {
  const response = await fetch('http://localhost:8001/api/vector-store/status');
  const data = await response.json();
  return data.data;
};
```

---

### 3. Document Upload API

#### `POST /api/upload-rfp`
**Purpose**: Upload an RFP document (PDF, DOCX, Excel) and extract requirements automatically.

**Request**:
```bash
curl -X POST http://localhost:8001/api/upload-rfp \
  -F "file=@document.pdf"
```

**Response**:
```json
{
  "success": true,
  "message": "Successfully extracted 10 requirements from document.pdf",
  "session_id": "f914da9b-9789-4473-9467-8383edde23e3",
  "requirements": [
    "G1: Is the platform cloud based?",
    "G2: Is the platform web-based?",
    "G3: Will the platform retrieve data in real time?"
  ],
  "extraction_metadata": null,
  "file_info": {
    "filename": "document.pdf",
    "size": 1024000,
    "type": "application/pdf",
    "extension": ".pdf"
  }
}
```

**Frontend Usage**:
```typescript
interface UploadResponse {
  success: boolean;
  message: string;
  session_id: string;
  requirements: string[];
  extraction_metadata?: any;
  file_info: {
    filename: string;
    size: number;
    type: string;
    extension: string;
  };
}

const uploadRFPDocument = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8001/api/upload-rfp', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
};
```

---

### 4. Requirements API

#### `GET /api/requirements/{session_id}`
**Purpose**: Get detailed requirements for a specific session.

**Request**:
```bash
curl http://localhost:8001/api/requirements/f914da9b-9789-4473-9467-8383edde23e3
```

**Response**:
```json
{
  "success": true,
  "message": "Requirements retrieved successfully",
  "session_id": "f914da9b-9789-4473-9467-8383edde23e3",
  "data": {
    "requirements": [
      "G1: Is the platform cloud based?",
      "G2: Is the platform web-based?"
    ],
    "extraction_metadata": null,
    "file_info": {
      "filename": "document.pdf",
      "file_type": ".pdf",
      "upload_time": "2025-10-04T14:05:00.000000"
    },
    "total_requirements": 10
  }
}
```

**Frontend Usage**:
```typescript
interface RequirementsResponse {
  requirements: string[];
  extraction_metadata?: any;
  file_info: {
    filename: string;
    file_type: string;
    upload_time: string;
  };
  total_requirements: number;
}

const getRequirements = async (sessionId: string): Promise<RequirementsResponse> => {
  const response = await fetch(`http://localhost:8001/api/requirements/${sessionId}`);
  const data = await response.json();
  return data.data;
};
```

---

### 5. Direct Query API

#### `POST /api/query`
**Purpose**: Query the knowledge base directly without uploading documents.

**Request**:
```bash
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are your data security measures?",
    "top_k": 3,
    "model": "llama3"
  }'
```

**Response**:
```json
{
  "success": true,
  "message": "Query executed successfully",
  "data": {
    "query": "What are your data security measures?",
    "answer": "Our organization takes data security extremely seriously...",
    "context": "RFP Response #2\n\nRequirement: How do you ensure data security?...",
    "quality_score": 92.5,
    "quality_status": "Excellent",
    "parameters": {
      "top_k": 3,
      "model": "llama3"
    }
  },
  "session_id": null
}
```

**Frontend Usage**:
```typescript
interface QueryRequest {
  query: string;
  top_k?: number; // Default: 3, Range: 1-10
  model?: string; // Options: "llama3", "llama2", "mistral", "codellama"
}

interface QueryResponse {
  query: string;
  answer: string;
  context: string;
  quality_score: number;
  quality_status: string; // "Excellent", "Good", "Fair", "Poor"
  parameters: {
    top_k: number;
    model: string;
  };
}

const directQuery = async (queryData: QueryRequest): Promise<QueryResponse> => {
  const response = await fetch('http://localhost:8001/api/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      top_k: 3,
      model: 'llama3',
      ...queryData
    })
  });
  
  const data = await response.json();
  return data.data;
};
```

---

### 6. Response Generation API

#### `POST /api/generate-responses`
**Purpose**: Generate responses for multiple requirements using the RAG pipeline.

**Request**:
```bash
curl -X POST http://localhost:8001/api/generate-responses \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": [
      "Is the platform cloud based?",
      "What are your security measures?"
    ],
    "top_k": 3,
    "model": "llama3",
    "session_id": "f914da9b-9789-4473-9467-8383edde23e3"
  }'
```

**Response**:
```json
{
  "success": true,
  "message": "Generated responses for 2/2 requirements",
  "session_id": "f914da9b-9789-4473-9467-8383edde23e3",
  "data": {
    "responses": [
      {
        "requirement_index": 0,
        "requirement": "Is the platform cloud based?",
        "answer": "The platform is hosting location-agnostic...",
        "quality_score": 92.5,
        "quality_status": "Excellent",
        "status": "success"
      }
    ],
    "summary": {
      "total_requirements": 2,
      "successful_responses": 2,
      "failed_responses": 0,
      "success_rate": 100.0
    },
    "parameters": {
      "top_k": 3,
      "model": "llama3"
    }
  }
}
```

**Frontend Usage**:
```typescript
interface GenerateRequest {
  requirements: string[];
  top_k?: number;
  model?: string;
  session_id: string;
}

interface ResponseItem {
  requirement_index: number;
  requirement: string;
  answer: string;
  quality_score?: number;
  quality_status?: string;
  status: 'success' | 'error';
  error?: string;
}

interface GenerateResponse {
  responses: ResponseItem[];
  summary: {
    total_requirements: number;
    successful_responses: number;
    failed_responses: number;
    success_rate: number;
  };
  parameters: {
    top_k: number;
    model: string;
  };
}

const generateResponses = async (requestData: GenerateRequest): Promise<GenerateResponse> => {
  const response = await fetch('http://localhost:8001/api/generate-responses', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      top_k: 3,
      model: 'llama3',
      ...requestData
    })
  });
  
  const data = await response.json();
  return data.data;
};
```

---

### 7. Response Retrieval API

#### `GET /api/responses/{session_id}`
**Purpose**: Get generated responses for a specific session.

**Request**:
```bash
curl http://localhost:8001/api/responses/f914da9b-9789-4473-9467-8383edde23e3
```

**Response**:
```json
{
  "success": true,
  "message": "Responses retrieved successfully",
  "session_id": "f914da9b-9789-4473-9467-8383edde23e3",
  "data": {
    "responses": [
      {
        "requirement_index": 0,
        "requirement": "Is the platform cloud based?",
        "answer": "The platform is hosting location-agnostic...",
        "quality_score": 92.5,
        "quality_status": "Excellent",
        "status": "success"
      }
    ],
    "summary": {
      "total_requirements": 2,
      "total_responses": 2,
      "successful_responses": 2,
      "success_rate": 100.0
    },
    "generation_info": {
      "response_generation_time": "2025-10-04T14:10:00.000000",
      "upload_time": "2025-10-04T14:05:00.000000"
    }
  }
}
```

**Frontend Usage**:
```typescript
const getResponses = async (sessionId: string): Promise<GenerateResponse> => {
  const response = await fetch(`http://localhost:8001/api/responses/${sessionId}`);
  const data = await response.json();
  return data.data;
};
```

---

### 8. Session Cleanup API

#### `DELETE /api/session/{session_id}`
**Purpose**: Clean up session data and temporary files.

**Request**:
```bash
curl -X DELETE http://localhost:8001/api/session/f914da9b-9789-4473-9467-8383edde23e3
```

**Response**:
```json
{
  "success": true,
  "message": "Session cleaned up successfully",
  "session_id": "f914da9b-9789-4473-9467-8383edde23e3"
}
```

**Frontend Usage**:
```typescript
const cleanupSession = async (sessionId: string): Promise<boolean> => {
  const response = await fetch(`http://localhost:8001/api/session/${sessionId}`, {
    method: 'DELETE'
  });
  const data = await response.json();
  return data.success;
};
```

---

## 🎯 **Complete Workflow Example**

Here's how to implement the complete RFP processing workflow:

```typescript
// Step 1: Check if system is ready
const vectorStatus = await getVectorStoreStatus();
if (!vectorStatus.ready_for_queries) {
  // Show warning that knowledge base is not ready
}

// Step 2: Upload RFP document
const uploadResult = await uploadRFPDocument(file);
const sessionId = uploadResult.session_id;
const requirements = uploadResult.requirements;

// Step 3: Get detailed requirements (optional)
const detailedRequirements = await getRequirements(sessionId);

// Step 4: Generate responses
const generateResult = await generateResponses({
  requirements: requirements,
  top_k: 3,
  model: 'llama3',
  session_id: sessionId
});

// Step 5: Get final responses
const finalResponses = await getResponses(sessionId);

// Step 6: Clean up when done
await cleanupSession(sessionId);
```

---

## 🚨 **Error Handling**

### Common Error Responses:
```json
{
  "success": false,
  "message": "Error description",
  "data": null,
  "session_id": null
}
```

### HTTP Status Codes:
- **200**: Success
- **400**: Bad Request (invalid file type, missing parameters)
- **404**: Not Found (session not found, vector store not found)
- **500**: Internal Server Error

### Frontend Error Handling:
```typescript
const handleAPICall = async <T>(apiCall: () => Promise<T>): Promise<T | null> => {
  try {
    return await apiCall();
  } catch (error) {
    if (error instanceof Response) {
      const errorData = await error.json();
      console.error('API Error:', errorData.message);
      // Show user-friendly error message
    }
    return null;
  }
};
```

---

## 📊 **Quality Score Interpretation**

### Quality Score Ranges:
- **90-100**: Excellent (🟢)
- **70-89**: Good (🔵) 
- **50-69**: Fair (🟡)
- **Below 50**: Poor (🔴)

### Quality Status Values:
- `"Excellent"`: High confidence, comprehensive answer
- `"Good"`: Good match with minor gaps
- `"Fair"`: Adequate answer but may need review
- `"Poor"`: Low confidence, may need manual review

---

## 🔧 **Configuration Options**

### RAG Parameters:
- **top_k**: Number of context chunks (1-10, default: 3)
- **model**: AI model ("llama3", "llama2", "mistral", "codellama")

### File Support:
- **PDF**: Supported ✅
- **DOCX**: Supported ✅ 
- **XLSX/XLS**: Supported ✅
- **Max File Size**: Check with backend team

### Performance Notes:
- **Direct Queries**: 10-25 seconds per query
- **Response Generation**: 3-5 seconds per requirement
- **Large Batches**: Consider showing progress for >10 requirements

This documentation provides everything needed for frontend integration with the RFP Response Generator API!