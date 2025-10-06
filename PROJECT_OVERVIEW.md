# Project Documentation Overview

This document provides a complete overview of the Local RAG Application project documentation and serves as the central reference point for all project information.

## 📖 Complete Documentation Map

### 🔥 **Essential Quick Start**
- **[docs/setup/SERVER_MANAGEMENT.md](docs/setup/SERVER_MANAGEMENT.md)** - How to start/stop servers
- **[docs/api/API_DOCUMENTATION.md](docs/api/API_DOCUMENTATION.md)** - Complete API reference with TypeScript interfaces
- **[docs/setup/DEVELOPMENT_WORKFLOW.md](docs/setup/DEVELOPMENT_WORKFLOW.md)** - Complete development workflow guide

### 📚 **All Documentation Files**

#### Root Level Documentation
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** ← *This document*
- **[README.md](README.md)** - Project introduction and basic setup

#### Setup & Configuration
- **[docs/setup/SERVER_MANAGEMENT.md](docs/setup/SERVER_MANAGEMENT.md)** - **[CRITICAL]** Server startup/shutdown procedures
- **[docs/setup/DEVELOPMENT_WORKFLOW.md](docs/setup/DEVELOPMENT_WORKFLOW.md)** - Complete workflow documentation
- **[docs/setup/LOCAL_DEVELOPMENT_GUIDE.md](docs/setup/LOCAL_DEVELOPMENT_GUIDE.md)** - Local development setup

#### API Documentation
- **[docs/api/API_DOCUMENTATION.md](docs/api/API_DOCUMENTATION.md)** - Complete API endpoints and TypeScript interfaces

#### Features & Capabilities  
- **[docs/RFP_INDEXING_FEATURE.md](docs/RFP_INDEXING_FEATURE.md)** - RFP document processing
- **[docs/DIRECT_QUERY_FEATURE.md](docs/DIRECT_QUERY_FEATURE.md)** - Direct query interface

#### Frontend Documentation
- **[docs/frontend/INTEGRATION_GUIDE.md](docs/frontend/INTEGRATION_GUIDE.md)** - Frontend integration guide
- **[docs/frontend/FRONTEND_MISSING_FEATURES.md](docs/frontend/FRONTEND_MISSING_FEATURES.md)** - Missing features and roadmap
- **[docs/frontend/FRONTEND_INTEGRATION_README.md](docs/frontend/FRONTEND_INTEGRATION_README.md)** - Frontend integration README

#### Implementation Details
- **[docs/implementation/IMPLEMENTATION_SUMMARY.md](docs/implementation/IMPLEMENTATION_SUMMARY.md)** - Technical implementation summary

#### Troubleshooting & Support
- **[docs/troubleshooting/TROUBLESHOOTING_GUIDE.md](docs/troubleshooting/TROUBLESHOOTING_GUIDE.md)** - **[CRITICAL]** Complete troubleshooting guide
- **[docs/README.md](docs/README.md)** - Documentation index and navigation

## 🎯 **Documentation for Different Roles**

### 👩‍💻 **New Developers (Start Here)**

**Required Reading Order:**
1. **[docs/setup/SERVER_MANAGEMENT.md](docs/setup/SERVER_MANAGEMENT.md)** - Learn server operations
2. **[docs/api/API_DOCUMENTATION.md](docs/api/API_DOCUMENTATION.md)** - Understand API structure  
3. **[docs/setup/DEVELOPMENT_WORKFLOW.md](docs/setup/DEVELOPMENT_WORKFLOW.md)** - Complete workflow understanding
4. **[docs/troubleshooting/TROUBLESHOOTING_GUIDE.md](docs/troubleshooting/TROUBLESHOOTING_GUIDE.md)** - Debugging knowledge

**Quick Start Commands:**
```bash
# 1. Start backend
cd /Users/tejan/Documents/Projects/Local-RAG-App/local-rag-app
source venv/bin/activate
python api_server.py

# 2. Start frontend (new terminal)
cd /Users/tejan/Documents/Projects/Local-RAG-App/local-rag-app/frontend
npm run dev

# 3. Test health
curl http://localhost:8001/health
```

### 🎨 **Frontend Developers**

**Focus Areas:**
- **[docs/setup/DEVELOPMENT_WORKFLOW.md](docs/setup/DEVELOPMENT_WORKFLOW.md)** → "Frontend Workflow Components"
- **[docs/api/API_DOCUMENTATION.md](docs/api/API_DOCUMENTATION.md)** → "TypeScript Interfaces"
- **[docs/frontend/](docs/frontend/)** → Component documentation

**Key Components:**
- `DocumentUpload.tsx` - File upload and requirement extraction
- `RequirementsManager.tsx` - Requirements display and management
- `ChatInterface.tsx` - Direct query interface
- `SessionContext.tsx` - Global state management

### ⚙️ **Backend Developers**

**Focus Areas:**
- **[docs/setup/DEVELOPMENT_WORKFLOW.md](docs/setup/DEVELOPMENT_WORKFLOW.md)** → "API Endpoints Reference"
- **[docs/api/API_DOCUMENTATION.md](docs/api/API_DOCUMENTATION.md)** → Complete API specification
- **[docs/api/](docs/api/)** → Backend implementation guides

**Key Files:**
- `api_server.py` - Main FastAPI server
- `src/app/rag_pipeline.py` - RAG processing logic
- `src/vector_store/` - Vector store management
- `src/ingestion/` - Document processing

### 🔧 **DevOps/Deployment**

**Focus Areas:**
- **[docs/setup/SERVER_MANAGEMENT.md](docs/setup/SERVER_MANAGEMENT.md)** → Production considerations
- **[docs/troubleshooting/TROUBLESHOOTING_GUIDE.md](docs/troubleshooting/TROUBLESHOOTING_GUIDE.md)** → System diagnostics
- **[docs/setup/LOCAL_DEVELOPMENT_GUIDE.md](docs/setup/LOCAL_DEVELOPMENT_GUIDE.md)** → Environment setup

## 🚀 **Application Overview**

### **What This Application Does**
The Local RAG Application is a complete document processing pipeline that:

1. **Uploads RFP Documents** (PDF/Excel) → 2. **Extracts Requirements** → 3. **Processes with AI** → 4. **Generates Responses** → 5. **Exports to Excel**

### **Technical Stack**
- **Backend**: FastAPI (Python) on port 8001
- **Frontend**: React/TypeScript/Vite on port 8080  
- **AI**: LLaMA3 model with RAG pipeline
- **Vector Store**: FAISS with 83 indexed documents
- **Quality Scoring**: 80-95% typical range

### **Key Features**
- **Complete RFP Workflow**: Upload → Extract → Process → Export
- **Direct Query Interface**: Ask questions without uploading documents
- **Session Management**: Track workflow progress across components
- **Quality Scoring**: AI response quality assessment
- **Excel Export**: Formatted results download

## 📊 **Project Status & Progress**

### **Current State**
- ✅ **Backend API**: Fully functional with all endpoints
- ✅ **Frontend Components**: Complete workflow implementation
- ✅ **Integration**: Frontend-backend connectivity established
- ✅ **Documentation**: Comprehensive guides created
- ✅ **Debugging**: Major component issues resolved

### **Recent Major Fixes**
- **RequirementsManager**: Fixed data display and API response parsing
- **DocumentUpload**: Enhanced session management and extraction workflow
- **ChatInterface**: Converted from mock to real API integration
- **SessionContext**: Improved state management across components

### **Testing Status**
- **Backend Workflow**: 100% success rate on test documents
- **API Endpoints**: All endpoints tested and functional
- **Quality Scoring**: Consistent 80-95% scores on relevant content
- **Frontend Integration**: Components debugged and ready for testing

## 🔍 **Common Development Scenarios**

### **"I need to start the application"**
→ **[docs/setup/SERVER_MANAGEMENT.md](docs/setup/SERVER_MANAGEMENT.md)** - Complete startup procedures

### **"Something is broken"**
→ **[docs/troubleshooting/TROUBLESHOOTING_GUIDE.md](docs/troubleshooting/TROUBLESHOOTING_GUIDE.md)** - Comprehensive debugging guide

### **"I need to understand the API"**
→ **[docs/api/API_DOCUMENTATION.md](docs/api/API_DOCUMENTATION.md)** - Complete API reference with examples

### **"I'm working on frontend components"**
→ **[docs/setup/DEVELOPMENT_WORKFLOW.md](docs/setup/DEVELOPMENT_WORKFLOW.md)** - Frontend workflow and components

### **"I need to test the complete workflow"**
→ **[docs/setup/DEVELOPMENT_WORKFLOW.md](docs/setup/DEVELOPMENT_WORKFLOW.md)** - Manual testing procedures

### **"I want to understand the codebase"**
→ **[docs/implementation/IMPLEMENTATION_SUMMARY.md](docs/implementation/IMPLEMENTATION_SUMMARY.md)** - Technical implementation details

## 🔧 **Critical Information**

### **Essential Commands**
```bash
# Server health check
echo "Backend:" && (lsof -ti:8001 && echo "✅ Running" || echo "❌ Stopped")
echo "Frontend:" && (lsof -ti:8080 && echo "✅ Running" || echo "❌ Stopped")

# Start backend
source venv/bin/activate && python api_server.py

# Start frontend  
cd frontend && npm run dev

# Kill servers
kill $(lsof -ti:8001) $(lsof -ti:8080) 2>/dev/null
```

### **Important File Locations**
- **Backend Server**: `/api_server.py`
- **Frontend App**: `/frontend/src/App.tsx`
- **API Documentation**: `/docs/api/API_DOCUMENTATION.md`
- **Server Management**: `/docs/setup/SERVER_MANAGEMENT.md`
- **Vector Store**: `/test_store/`
- **Uploads**: `/temp_uploads/`

### **Development Ports**
- **Backend API**: http://localhost:8001
- **Frontend UI**: http://localhost:8080  
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 📝 **Documentation Maintenance**

### **When to Update Which Document**

**[docs/setup/SERVER_MANAGEMENT.md](docs/setup/SERVER_MANAGEMENT.md)** - Update when:
- Server configuration changes
- New startup/shutdown procedures
- Port or environment changes

**[docs/api/API_DOCUMENTATION.md](docs/api/API_DOCUMENTATION.md)** - Update when:
- API endpoints added/modified/removed
- Request/response structures change
- New TypeScript interfaces added

**[docs/setup/DEVELOPMENT_WORKFLOW.md](docs/setup/DEVELOPMENT_WORKFLOW.md)** - Update when:
- Workflow steps change
- New components added
- Testing procedures modified

**[docs/troubleshooting/TROUBLESHOOTING_GUIDE.md](docs/troubleshooting/TROUBLESHOOTING_GUIDE.md)** - Update when:
- New issues discovered
- Solutions found
- Diagnostic commands improved

### **Documentation Review Schedule**
- **Weekly**: Check for outdated commands
- **Monthly**: Full documentation review
- **On Major Changes**: Update affected documents immediately
- **Before Releases**: Comprehensive documentation validation

## 🎯 **Next Steps & Future Development**

### **Immediate Priorities**
1. **End-to-End Testing**: Complete workflow validation with debugged components
2. **Performance Optimization**: Monitor and improve response times
3. **Error Handling**: Enhanced error states and user feedback

### **Planned Enhancements**
1. **Persistent Sessions**: Database storage for session management
2. **User Authentication**: Multi-user support
3. **Advanced Export**: Multiple format support
4. **Deployment**: Production environment setup

### **Documentation Roadmap**
1. **Component Documentation**: Detailed frontend component guides
2. **API Examples**: More comprehensive usage examples
3. **Deployment Guide**: Production setup documentation
4. **User Manual**: End-user operation guide

---

**📞 Need Help?**
1. **Start Here**: [docs/README.md](docs/README.md) - Documentation index
2. **Server Issues**: [docs/setup/SERVER_MANAGEMENT.md](docs/setup/SERVER_MANAGEMENT.md)
3. **Debugging**: [docs/troubleshooting/TROUBLESHOOTING_GUIDE.md](docs/troubleshooting/TROUBLESHOOTING_GUIDE.md)
4. **API Questions**: [docs/api/API_DOCUMENTATION.md](docs/api/API_DOCUMENTATION.md)

**Last Updated**: October 2025 | **Next Review**: November 2025