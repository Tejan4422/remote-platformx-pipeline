# 🚀 Phase 6: Frontend Integration - Complete Guide

## Overview

This guide provides everything you need to integrate your Lovable frontend with the RFP Response Generator backend API. The integration maintains your existing UI design while adding powerful backend functionality.

## 📁 Project Structure

```
frontend-integration/
├── api-client.ts              # Main API client with all endpoints
├── useAPI.ts                  # React Query hooks for API calls
├── DocumentUpload.tsx         # Enhanced upload component
├── ChatInterface.tsx          # Real-time chat with backend
├── KnowledgeBase.tsx          # Knowledge base management
├── SessionContext.tsx         # Session state management
├── INTEGRATION_GUIDE.md       # Step-by-step instructions
└── README.md                  # This file
```

## 🔧 Quick Start

### 1. Copy Files to Your Frontend

```bash
# In your Lovable frontend project root
mkdir -p src/lib src/hooks src/contexts

# Copy API integration files
cp frontend-integration/api-client.ts src/lib/
cp frontend-integration/useAPI.ts src/hooks/
cp frontend-integration/SessionContext.tsx src/contexts/

# Replace existing components
cp frontend-integration/DocumentUpload.tsx src/components/
cp frontend-integration/ChatInterface.tsx src/components/
cp frontend-integration/KnowledgeBase.tsx src/components/
```

### 2. Environment Setup

Create `.env.local` in your frontend root:
```env
VITE_API_BASE_URL=http://localhost:8001
VITE_API_TIMEOUT=30000
```

### 3. Update App.tsx

```typescript
import { SessionProvider } from '@/contexts/SessionContext';

const App = () => (
  <QueryClientProvider client={queryClient}>
    <SessionProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          {/* Your existing routes */}
        </BrowserRouter>
      </TooltipProvider>
    </SessionProvider>
  </QueryClientProvider>
);
```

### 4. Start Both Servers

Backend:
```bash
cd /path/to/backend
source venv/bin/activate
python api_server.py
```

Frontend:
```bash
cd /path/to/frontend
npm run dev
```

## 🎯 Features Implemented

### ✅ DocumentUpload Component
- **Real file upload** to backend API
- **Session management** with unique IDs
- **Progress indicators** and loading states
- **Error handling** with toast notifications
- **Requirements extraction** display
- **Vector store status** integration

### ✅ ChatInterface Component
- **Direct queries** to AI backend
- **Real-time responses** with streaming
- **Quality scoring** display
- **System readiness** checks
- **Loading states** and error handling
- **Quick question** templates

### ✅ KnowledgeBase Component
- **Document indexing** for RFP responses
- **Bulk upload** for historical data
- **Vector store statistics** monitoring
- **Processing status** tracking
- **System capabilities** display
- **Drag & drop** file upload

### ✅ Session Management
- **Persistent sessions** across page reloads
- **Session cleanup** functionality
- **Context provider** for global state
- **Local storage** integration

## 🔌 API Integration Details

### Endpoints Connected

| Component | Method | Endpoint | Purpose |
|-----------|--------|----------|---------|
| Health | GET | `/health` | System status check |
| DocumentUpload | POST | `/api/upload-rfp` | Upload RFP documents |
| ChatInterface | POST | `/api/query` | Direct AI queries |
| ResponseDashboard | POST | `/api/generate-responses` | Bulk response generation |
| ResponseDashboard | GET | `/api/responses/{session_id}` | Get generated responses |
| KnowledgeBase | POST | `/api/index-responses` | Index RFP responses |
| KnowledgeBase | POST | `/api/upload-historical-data` | Bulk document upload |
| All Components | GET | `/api/vector-store/stats` | Vector store statistics |

### Data Flow

1. **Upload RFP** → Extract requirements → Store in session
2. **Direct Query** → Send to AI → Display response with quality score
3. **Generate Responses** → Process requirements → Store responses in session
4. **Knowledge Base** → Index documents → Update vector store
5. **Session Management** → Track workflow → Enable cleanup

## 🛠️ Customization Options

### API Configuration

```typescript
// In src/lib/api-client.ts
const apiClient = new APIClient('http://your-custom-backend.com');
```

### Request Timeouts

```typescript
// Add timeout configuration
const config: RequestInit = {
  headers: { 'Content-Type': 'application/json' },
  signal: AbortSignal.timeout(30000), // 30 second timeout
  ...options,
};
```

### Error Handling

```typescript
// Custom error handling in hooks
onError: (error: Error) => {
  // Custom error logging
  console.error('API Error:', error);
  
  // Custom toast notification
  toast({
    title: "Custom Error Title",
    description: error.message,
    variant: "destructive",
  });
}
```

## 🚀 Testing the Integration

### 1. Basic Workflow Test
1. Upload an RFP document (PDF/Excel)
2. Verify requirements extraction
3. Try direct queries in chat
4. Upload knowledge base documents
5. Generate responses for requirements

### 2. Error Handling Test
- Upload invalid file formats
- Try queries without vector store
- Test network disconnection
- Verify error messages display

### 3. Session Management Test
- Upload document and refresh page
- Verify session persistence
- Test cleanup functionality
- Check localStorage behavior

## 📊 Performance Considerations

### React Query Configuration

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: 3,
      refetchOnWindowFocus: false,
    },
  },
});
```

### File Upload Optimization

- **Chunked uploads** for large files
- **Progress tracking** for user feedback
- **File validation** before upload
- **Automatic retry** on failure

## 🔒 Security Features

- **CORS configuration** for cross-origin requests
- **Input validation** on frontend
- **Error message sanitization**
- **Session cleanup** to prevent memory leaks

## 🐛 Troubleshooting

### Common Issues

**1. CORS Errors**
```typescript
// Backend: Update CORS in api_server.py
allow_origins=["http://localhost:5173", "your-frontend-domain"]
```

**2. File Upload Fails**
- Check file size limits
- Verify supported formats
- Check network connectivity
- Review backend logs

**3. Queries Not Working**
- Ensure vector store has documents
- Check backend is running
- Verify API endpoints
- Review console errors

**4. Session Not Persisting**
- Check localStorage permissions
- Verify session context setup
- Review browser dev tools

### Debug Mode

Enable debug logging:
```typescript
// In api-client.ts
const DEBUG = import.meta.env.VITE_DEBUG === 'true';

if (DEBUG) {
  console.log('API Request:', url, config);
  console.log('API Response:', response);
}
```

## 📈 Production Deployment

### Environment Variables

```env
# Production .env
VITE_API_BASE_URL=https://api.your-domain.com
VITE_API_TIMEOUT=60000
VITE_DEBUG=false
```

### Backend CORS Update

```python
# Update api_server.py for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🎉 Success Metrics

After integration, you should see:
- ✅ Real-time document processing
- ✅ AI-powered response generation
- ✅ Knowledge base management
- ✅ Session-based workflow
- ✅ Professional error handling
- ✅ Responsive loading states
- ✅ Toast notifications
- ✅ Progress indicators

## 🤝 Support

If you encounter issues:
1. Check the console for errors
2. Review network requests in dev tools
3. Verify backend server is running
4. Check API endpoint responses
5. Review the integration guide steps

The integration maintains your beautiful Lovable UI while adding powerful backend functionality! 🚀