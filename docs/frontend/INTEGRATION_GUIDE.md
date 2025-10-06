# Phase 6: Frontend Integration Guide

## 🚀 Complete Integration Implementation

### **Step 1: Install the API Files**

1. **Copy the API Client** to your frontend:
   ```bash
   # In your Lovable frontend project
   cp api-client.ts src/lib/api-client.ts
   cp useAPI.ts src/hooks/useAPI.ts
   ```

2. **Update your existing components**:
   ```bash
   # Replace existing components with enhanced versions
   cp DocumentUpload.tsx src/components/DocumentUpload.tsx
   cp ChatInterface.tsx src/components/ChatInterface.tsx
   cp KnowledgeBase.tsx src/components/KnowledgeBase.tsx
   ```

### **Step 2: Environment Configuration**

Create a `.env.local` file in your frontend root:
```env
VITE_API_BASE_URL=http://localhost:8001
VITE_API_TIMEOUT=30000
```

Update your API client to use environment variables:
```typescript
// In src/lib/api-client.ts - update the constructor
constructor(baseURL: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001') {
  this.baseURL = baseURL;
}
```

### **Step 3: Enhanced Components Overview**

#### **DocumentUpload Component** 
- ✅ Real file upload to `/api/upload-rfp` endpoint
- ✅ Session management with backend
- ✅ Progress indicators and error handling
- ✅ Vector store status integration
- ✅ Requirements extraction display

#### **ChatInterface Component**
- ✅ Direct queries to `/api/query` endpoint  
- ✅ Real-time response generation
- ✅ Quality scoring display
- ✅ Vector store readiness checks
- ✅ Loading states and error handling

#### **KnowledgeBase Component**
- ✅ Document indexing via `/api/index-responses`
- ✅ Bulk upload via `/api/upload-historical-data`
- ✅ Vector store statistics display
- ✅ Real-time processing status
- ✅ System capabilities monitoring

### **Step 4: ResponseDashboard Integration**

Update your ResponseDashboard component to use real data:

```typescript
// In src/components/ResponseDashboard.tsx - add these imports
import { useRequirements, useResponses, useGenerateResponses } from "@/hooks/useAPI";
import { useState, useEffect } from "react";

// Replace mock data with real API calls
export const ResponseDashboard = () => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  // Get session ID from localStorage or context
  useEffect(() => {
    const savedSessionId = localStorage.getItem('currentSessionId');
    setSessionId(savedSessionId);
  }, []);

  const { data: requirementsData } = useRequirements(sessionId);
  const { data: responsesData } = useResponses(sessionId);
  const generateMutation = useGenerateResponses();

  const requirements = requirementsData?.data?.requirements || [];
  const responses = responsesData?.data?.responses || [];
  
  // ... rest of component logic
};
```

### **Step 5: Session Management**

Add a session context provider:

```typescript
// Create src/contexts/SessionContext.tsx
import { createContext, useContext, useState, ReactNode } from 'react';

interface SessionContextType {
  sessionId: string | null;
  setSessionId: (id: string | null) => void;
  clearSession: () => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export const SessionProvider = ({ children }: { children: ReactNode }) => {
  const [sessionId, setSessionIdState] = useState<string | null>(
    localStorage.getItem('currentSessionId')
  );

  const setSessionId = (id: string | null) => {
    setSessionIdState(id);
    if (id) {
      localStorage.setItem('currentSessionId', id);
    } else {
      localStorage.removeItem('currentSessionId');
    }
  };

  const clearSession = () => setSessionId(null);

  return (
    <SessionContext.Provider value={{ sessionId, setSessionId, clearSession }}>
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within SessionProvider');
  }
  return context;
};
```

Update your App.tsx:
```typescript
import { SessionProvider } from '@/contexts/SessionContext';

const App = () => (
  <QueryClientProvider client={queryClient}>
    <SessionProvider>
      <TooltipProvider>
        {/* ... rest of your app */}
      </TooltipProvider>
    </SessionProvider>
  </QueryClientProvider>
);
```

### **Step 6: Error Handling & Loading States**

The components now include:
- **Loading spinners** during API calls
- **Error messages** with proper toast notifications  
- **Success feedback** for completed operations
- **Disabled states** when vector store isn't ready
- **Progress indicators** for long operations

### **Step 7: Testing the Integration**

1. **Start your backend server**:
   ```bash
   cd /path/to/backend
   source venv/bin/activate
   python api_server.py
   ```

2. **Start your frontend**:
   ```bash
   cd /path/to/frontend
   npm run dev
   ```

3. **Test the workflow**:
   - Upload an RFP document
   - Check that requirements are extracted
   - Try direct queries in ChatInterface
   - Upload documents to Knowledge Base
   - Generate responses for requirements

### **Step 8: API Endpoint Summary**

Your frontend now integrates with these backend endpoints:

| Component | Endpoint | Purpose |
|-----------|----------|---------|
| Health Check | `GET /health` | System status |
| DocumentUpload | `POST /api/upload-rfp` | RFP document upload |
| ChatInterface | `POST /api/query` | Direct AI queries |
| ResponseDashboard | `POST /api/generate-responses` | Bulk response generation |
| KnowledgeBase | `POST /api/index-responses` | Document indexing |
| KnowledgeBase | `POST /api/upload-historical-data` | Bulk document upload |
| All | `GET /api/vector-store/stats` | Vector store statistics |

### **Step 9: Production Considerations**

For production deployment:

1. **Update CORS settings** in your backend:
   ```python
   # In api_server.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend-domain.com"],  # Update this
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Environment variables**:
   ```env
   # Frontend .env.production
   VITE_API_BASE_URL=https://your-backend-api.com
   ```

3. **Error monitoring** and logging
4. **Authentication** if needed
5. **Rate limiting** consideration

### **🎉 Integration Complete!**

Your frontend is now fully integrated with the backend API, providing:
- Real-time document processing
- AI-powered query responses  
- Knowledge base management
- Session-based workflow
- Comprehensive error handling
- Production-ready architecture

The integration maintains your existing Lovable UI design while adding powerful backend functionality!