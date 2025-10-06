# Documentation Index

This directory contains comprehensive documentation for the Local RAG Application development and usage.

## 📁 Documentation Structure

### 🚀 Setup & Configuration
- **[SERVER_MANAGEMENT.md](./setup/SERVER_MANAGEMENT.md)** - Complete guide for starting, stopping, and managing frontend/backend servers
- **[DEVELOPMENT_WORKFLOW.md](./setup/DEVELOPMENT_WORKFLOW.md)** - Development workflows, API integration, and testing procedures
- **[LOCAL_DEVELOPMENT_GUIDE.md](./setup/LOCAL_DEVELOPMENT_GUIDE.md)** - Local development environment setup

### 🔌 API Documentation
- **[API_DOCUMENTATION.md](./api/API_DOCUMENTATION.md)** - Complete API documentation with TypeScript interfaces

### 🎨 Frontend Documentation
- **[INTEGRATION_GUIDE.md](./frontend/INTEGRATION_GUIDE.md)** - Frontend integration guide
- **[FRONTEND_MISSING_FEATURES.md](./frontend/FRONTEND_MISSING_FEATURES.md)** - Missing features and roadmap
- **[FRONTEND_INTEGRATION_README.md](./frontend/FRONTEND_INTEGRATION_README.md)** - Frontend setup and integration

### 📊 Implementation Details
- **[IMPLEMENTATION_SUMMARY.md](./implementation/IMPLEMENTATION_SUMMARY.md)** - Technical implementation summary

### 🚨 Troubleshooting
- **[TROUBLESHOOTING_GUIDE.md](./troubleshooting/TROUBLESHOOTING_GUIDE.md)** - Solutions to common issues, debugging steps, and diagnostic commands

### 📊 Features
- **[RFP_INDEXING_FEATURE.md](./RFP_INDEXING_FEATURE.md)** - RFP document processing and indexing capabilities
- **[DIRECT_QUERY_FEATURE.md](./DIRECT_QUERY_FEATURE.md)** - Direct query interface for AI responses

## 🎯 Quick Start Guide

### For Developers Starting Fresh

1. **Read Server Management** 📖
   - [SERVER_MANAGEMENT.md](./setup/SERVER_MANAGEMENT.md) - Learn how to start/stop servers
   - Follow the "Recommended Startup Order" section

2. **Understand the Workflow** 🔄
   - [DEVELOPMENT_WORKFLOW.md](./setup/DEVELOPMENT_WORKFLOW.md) - Complete RFP processing pipeline
   - Review "Frontend Workflow Components" section

3. **API Integration** 🔌
   - [API_DOCUMENTATION.md](./api/API_DOCUMENTATION.md) - All endpoints and TypeScript interfaces
   - Reference "Core Workflow Endpoints" in Development Workflow

4. **When Things Go Wrong** 🚨
   - [TROUBLESHOOTING_GUIDE.md](./troubleshooting/TROUBLESHOOTING_GUIDE.md) - Debug common issues
   - Use "Quick Diagnostic Commands" for system health

### For Frontend Developers

**Essential Reading Order:**
1. [SERVER_MANAGEMENT.md](./setup/SERVER_MANAGEMENT.md) → Frontend Server section
2. [DEVELOPMENT_WORKFLOW.md](./setup/DEVELOPMENT_WORKFLOW.md) → Frontend Workflow Components
3. [API_DOCUMENTATION.md](./api/API_DOCUMENTATION.md) → TypeScript interfaces
4. [frontend/](./frontend/) → Component-specific documentation

### For Backend Developers

**Essential Reading Order:**
1. [SERVER_MANAGEMENT.md](./setup/SERVER_MANAGEMENT.md) → Backend Server section
2. [DEVELOPMENT_WORKFLOW.md](./setup/DEVELOPMENT_WORKFLOW.md) → API Endpoints Reference
3. [API_DOCUMENTATION.md](./api/API_DOCUMENTATION.md) → Complete API specification
4. [api/](./api/) → Backend implementation guides

## 🛠️ Common Tasks

### Starting Development
```bash
# Quick server startup (from project root)
source venv/bin/activate && python api_server.py &
cd frontend && npm run dev
```

### Debugging Issues
```bash
# Quick health check
lsof -ti:8001 && echo "Backend ✅" || echo "Backend ❌"
lsof -ti:8080 && echo "Frontend ✅" || echo "Frontend ❌"
```

### Testing Workflow
```bash
# Test API upload
curl -X POST "http://localhost:8001/api/upload-rfp" \
  -F "file=@./data/raw/Test_rfp - Sheet1.pdf"
```

## 📋 Documentation Standards

### File Naming Convention
- **ALL_CAPS**: Main documentation files
- **lowercase**: Supporting files and examples
- **PascalCase**: Component-specific documentation

### Structure Guidelines
- **Overview**: Brief description and purpose
- **Quick Reference**: Commands and key information
- **Detailed Sections**: Step-by-step instructions
- **Troubleshooting**: Common issues and solutions
- **Examples**: Code snippets and usage patterns

## 🔄 Document Updates

### When to Update Documentation

**SERVER_MANAGEMENT.md** - Update when:
- Server startup procedures change
- New ports or configurations added
- Deployment scripts modified

**DEVELOPMENT_WORKFLOW.md** - Update when:
- New API endpoints added
- Frontend components modified
- Workflow steps change

**TROUBLESHOOTING_GUIDE.md** - Update when:
- New common issues discovered
- Solutions found for existing problems
- Diagnostic commands improved

**API_DOCUMENTATION.md** - Update when:
- API endpoints added/modified/removed
- Response structures change
- New TypeScript interfaces added

### Documentation Review Checklist
- [ ] Commands tested on clean environment
- [ ] All file paths verified and absolute
- [ ] Code examples functional
- [ ] Screenshots updated (if applicable)
- [ ] Cross-references valid
- [ ] Version-specific information noted

## 🎯 Key Information Summary

### Server Information
- **Backend**: FastAPI on port 8001
- **Frontend**: React/Vite on port 8080
- **Health Check**: `curl http://localhost:8001/health`
- **API Docs**: http://localhost:8001/docs

### Development Environment
- **Python**: 3.8+ with virtual environment
- **Node.js**: 16+ with npm
- **Vector Store**: FAISS with 83 documents
- **File Support**: PDF, Excel (.xlsx, .xls)

### Workflow Overview
1. **Upload** → 2. **Extract** → 3. **Process** → 4. **Download**
- Session-based state management
- Quality scoring (80-95% typical)
- Excel export functionality

### Critical Files
- `api_server.py` - Backend server
- `frontend/src/App.tsx` - Main frontend app
- `docs/setup/SERVER_MANAGEMENT.md` - Server operations
- `API_DOCUMENTATION.md` - Complete API reference

## 📞 Support & Contribution

### Getting Help
1. **Check Documentation**: Start with relevant guide above
2. **Run Diagnostics**: Use troubleshooting diagnostic commands
3. **Check Logs**: Backend logs in `api_server.log`
4. **Browser Console**: Check for frontend errors

### Contributing to Documentation
1. **Test Changes**: Verify all commands work
2. **Follow Standards**: Use established formatting
3. **Update Index**: Add new documents to this index
4. **Cross-Reference**: Link related documentation

### Documentation Maintenance
- **Monthly Review**: Check for outdated information
- **Issue Tracking**: Note common questions for documentation
- **Version Updates**: Update when dependencies change
- **User Feedback**: Incorporate suggestions and clarifications

---

**Last Updated**: October 2025
**Maintained By**: Development Team
**Review Schedule**: Monthly or on major changes