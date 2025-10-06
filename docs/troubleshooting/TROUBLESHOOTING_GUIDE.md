# Troubleshooting Guide

This guide provides solutions to common issues encountered during development and usage of the Local RAG Application.

## Server Issues

### Backend Server Won't Start

#### Error: "Port 8001 already in use"
```bash
# Find process using port 8001
lsof -ti:8001

# Kill the process
kill $(lsof -ti:8001)

# If that doesn't work, force kill
kill -9 $(lsof -ti:8001)

# Verify port is free
lsof -i :8001
```

#### Error: "ModuleNotFoundError"
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Verify activation (should show venv path)
which python

# Install missing dependencies
pip install -r requirements.txt

# If still issues, recreate virtual environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Error: "FAISS not found" or Vector Store Issues
```bash
# Install FAISS
pip install faiss-cpu  # For CPU version
# OR
pip install faiss-gpu  # For GPU version (if CUDA available)

# Rebuild vector store if corrupted
python -c "
from src.vector_store.faiss_store import FaissVectorStore
store = FaissVectorStore()
store.build_index()
print('Vector store rebuilt successfully')
"
```

### Frontend Server Won't Start

#### Error: "Port 8080 already in use"
```bash
# Find and kill process on port 8080
lsof -ti:8080
kill $(lsof -ti:8080)

# Alternative: Use different port
npm run dev -- --port 3000
```

#### Error: "Command not found: npm"
```bash
# Install Node.js (macOS with Homebrew)
brew install node

# Verify installation
node --version
npm --version

# If using nvm (Node Version Manager)
nvm install node
nvm use node
```

#### Error: "Dependencies not installed"
```bash
# Navigate to frontend directory
cd frontend

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# If npm install fails, try yarn
npm install -g yarn
yarn install
```

## API Integration Issues

### Connection Refused / Network Errors

#### Backend Not Reachable
```bash
# Test backend health
curl http://localhost:8001/health

# If fails, check if backend is running
lsof -i :8001

# Check backend logs
tail -f api_server.log

# Restart backend
python api_server.py
```

#### CORS Errors in Browser
**Symptoms**: Console errors about CORS policy
**Solution**: Verify CORS configuration in `api_server.py`
```python
# Should include:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Response Issues

#### Wrong Response Structure
**Symptoms**: Components showing empty data despite successful API calls
**Debug Steps**:
```javascript
// Add logging to component
console.log('API Response:', response);
console.log('Response Data:', response.data);

// Check response structure
// Expected: { data: { requirements: [...] } }
// vs { requirements: [...] }
```

**Common Fix**:
```typescript
// Handle both response structures
const requirements = data?.data?.requirements || data?.requirements || [];
```

#### Session ID Issues
**Symptoms**: "Session not found" errors
**Debug Steps**:
```bash
# Check session creation
curl -X POST "http://localhost:8001/api/upload-rfp" \
  -F "file=@./data/raw/Test_rfp - Sheet1.pdf" \
  -F "description=Test"

# Verify session ID format (should be UUID)
# Example: a6a26923-f634-4e40-9520-84cd9cca7843
```

## File Upload Issues

### File Size Limits
**Error**: "File too large"
**Solutions**:
```python
# Increase limit in api_server.py
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Or configure in FastAPI
from fastapi import UploadFile, File

@app.post("/api/upload-rfp")
async def upload_rfp(
    file: UploadFile = File(..., max_length=50 * 1024 * 1024)  # 50MB
):
```

### Unsupported File Types
**Error**: "Unsupported file format"
**Supported Types**: PDF, Excel (.xlsx, .xls)
**Debug**:
```bash
# Check file type
file ./data/raw/Test_rfp\ -\ Sheet1.pdf

# Verify file extension
ls -la ./data/raw/
```

### Temporary Upload Directory Issues
**Error**: "Cannot write to temp directory"
**Solutions**:
```bash
# Check temp_uploads directory exists
ls -la temp_uploads/

# Create if missing
mkdir -p temp_uploads

# Fix permissions
chmod 755 temp_uploads/

# Clear old files if disk full
rm temp_uploads/*
```

## Component-Specific Issues

### RequirementsManager Not Showing Data

#### Debug Checklist
1. **Session Context**:
   ```javascript
   // Check in browser dev tools
   console.log('Session:', sessionContext.sessionId);
   console.log('Requirements:', sessionContext.requirements);
   ```

2. **API Response**:
   ```javascript
   // Check network tab for /api/requirements/{session_id}
   // Verify response status and data structure
   ```

3. **Component State**:
   ```javascript
   // Add debug logging to RequirementsManager
   useEffect(() => {
     console.log('Component mounted, session:', sessionContext.sessionId);
     console.log('Requirements in context:', sessionContext.requirements);
   }, [sessionContext]);
   ```

#### Common Fixes
```typescript
// Fix 1: Handle loading states
if (isLoading) return <div>Loading requirements...</div>;
if (!sessionContext.sessionId) return <div>No session found</div>;

// Fix 2: Handle empty requirements
if (!requirements || requirements.length === 0) {
  return <div>No requirements extracted yet</div>;
}

// Fix 3: Fix API response parsing
const requirements = useMemo(() => {
  return data?.data?.requirements || data?.requirements || sessionContext.requirements || [];
}, [data, sessionContext.requirements]);
```

### DocumentUpload Component Issues

#### File Not Uploading
**Debug Steps**:
```javascript
// Check FormData creation
const formData = new FormData();
formData.append('file', file);
console.log('FormData entries:', [...formData.entries()]);

// Check file object
console.log('File object:', {
  name: file.name,
  size: file.size,
  type: file.type
});
```

#### Session Not Created
**Debug Steps**:
```javascript
// Check upload response
uploadMutation.mutate(formData, {
  onSuccess: (data) => {
    console.log('Upload success:', data);
    console.log('Session ID:', data.session_id);
  },
  onError: (error) => {
    console.error('Upload error:', error);
  }
});
```

### ChatInterface Issues

#### Using Mock Data Instead of Real API
**Symptoms**: Always returns same response
**Fix**: Verify API integration
```typescript
// Wrong: Mock response
const handleSubmit = async () => {
  setResponse({ response: "Mock answer", quality_score: 85 });
};

// Correct: Real API call
const handleSubmit = async () => {
  const response = await fetch('/api/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: message, top_k: 5 })
  });
  const data = await response.json();
  setResponse(data);
};
```

## Quality Score Issues

### Low Quality Scores
**Symptoms**: Consistently getting scores below 70%
**Debug Steps**:
```bash
# Test vector store
python test_vector_store.py

# Check document indexing
python -c "
from src.vector_store.faiss_store import FaissVectorStore
store = FaissVectorStore()
print(f'Documents in store: {store.get_document_count()}')
"

# Test quality scoring directly
python test_quality_scoring.py
```

**Potential Solutions**:
1. **Rebuild Vector Store**: May be corrupted or outdated
2. **Adjust top_k Parameter**: Try different values (3, 5, 10)
3. **Check Query Relevance**: Ensure questions match document content

### Quality Score Not Displaying
**Debug Steps**:
```javascript
// Check API response structure
console.log('Response with quality score:', response);

// Verify score is number
console.log('Quality score type:', typeof response.quality_score);
console.log('Quality score value:', response.quality_score);
```

## Database/Storage Issues

### Vector Store Corruption
**Symptoms**: Crashes when querying, inconsistent results
**Solution**:
```bash
# Backup current store (if needed)
cp -r test_store/ test_store_backup/

# Remove corrupted store
rm -rf test_store/

# Rebuild from scratch
python -c "
from src.vector_store.faiss_store import FaissVectorStore
from src.ingestion.document_processor import DocumentProcessor

# Initialize components
store = FaissVectorStore()
processor = DocumentProcessor()

# Rebuild index (this may take time)
store.build_index()
print('Vector store rebuilt successfully')
"
```

### Session Storage Issues
**Symptoms**: Sessions lost after restart
**Note**: Currently using in-memory storage
**Future Enhancement**: Implement persistent session storage

## Performance Issues

### Slow Response Times
**Backend Optimization**:
```bash
# Check system resources
top
htop  # If available

# Monitor Python process
ps aux | grep python

# Check available memory
free -h  # Linux
vm_stat  # macOS
```

**Frontend Optimization**:
```bash
# Check bundle size
npm run build
ls -la dist/

# Analyze bundle
npm install -g webpack-bundle-analyzer
npx webpack-bundle-analyzer dist/
```

### High Memory Usage
**Vector Store Optimization**:
```python
# Reduce vector dimensions (if configurable)
# Implement pagination for large result sets
# Use streaming for large file uploads
```

## Development Environment Issues

### Python Environment Problems
```bash
# Check Python version
python --version

# Verify virtual environment
which python
echo $VIRTUAL_ENV

# Recreate environment if corrupted
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Node.js Environment Problems
```bash
# Check Node version compatibility
node --version  # Should be 16+

# Clear npm cache
npm cache clean --force

# Update npm
npm install -g npm@latest

# Fix permission issues (macOS/Linux)
sudo chown -R $(whoami) ~/.npm
```

## Network and Firewall Issues

### Localhost Access Issues
```bash
# Test localhost connectivity
ping localhost
curl http://localhost:8001/health
curl http://localhost:8080

# Check firewall settings (macOS)
sudo pfctl -sr

# Alternative localhost access
curl http://127.0.0.1:8001/health
```

### Browser-Specific Issues
**Chrome**: Check developer tools console
**Safari**: Enable developer tools, check console
**Firefox**: Check browser console and network tab

**Common Browser Fixes**:
1. Clear browser cache
2. Disable browser extensions
3. Try incognito/private mode
4. Check browser console for errors

## Quick Diagnostic Commands

### System Health Check
```bash
#!/bin/bash
echo "=== LOCAL RAG APP DIAGNOSTICS ==="

echo "1. Server Status:"
echo "Backend (8001):" && (lsof -ti:8001 >/dev/null && echo "✅ Running" || echo "❌ Stopped")
echo "Frontend (8080):" && (lsof -ti:8080 >/dev/null && echo "✅ Running" || echo "❌ Stopped")

echo -e "\n2. Environment:"
echo "Python:" && python --version 2>/dev/null || echo "❌ Not found"
echo "Node.js:" && node --version 2>/dev/null || echo "❌ Not found"
echo "Virtual env:" && echo $VIRTUAL_ENV || echo "❌ Not activated"

echo -e "\n3. Files:"
echo "Backend script:" && ls api_server.py >/dev/null 2>&1 && echo "✅ Found" || echo "❌ Missing"
echo "Frontend package:" && ls frontend/package.json >/dev/null 2>&1 && echo "✅ Found" || echo "❌ Missing"
echo "Vector store:" && ls test_store/ >/dev/null 2>&1 && echo "✅ Found" || echo "❌ Missing"

echo -e "\n4. API Health:"
curl -s http://localhost:8001/health >/dev/null 2>&1 && echo "✅ Backend healthy" || echo "❌ Backend unreachable"
curl -s http://localhost:8080 >/dev/null 2>&1 && echo "✅ Frontend accessible" || echo "❌ Frontend unreachable"

echo -e "\n5. Storage:"
echo "Temp uploads:" && ls temp_uploads/ 2>/dev/null | wc -l | xargs echo "files:" || echo "❌ Directory missing"
echo "Vector docs:" && python -c "from src.vector_store.faiss_store import FaissVectorStore; print(f'{FaissVectorStore().get_document_count()} documents')" 2>/dev/null || echo "❌ Cannot access"
```

### Error Log Analysis
```bash
# Backend logs
tail -n 50 api_server.log

# System logs (macOS)
log show --predicate 'process == "python"' --last 1h

# Check disk space
df -h

# Check memory usage
ps aux | head -1; ps aux | grep -E "(python|node)" | head -10
```

## Getting Help

### Debug Information to Collect
When reporting issues, include:

1. **Error Messages**: Exact error text from console/logs
2. **Environment**: OS, Python version, Node.js version
3. **Steps to Reproduce**: Exact sequence that caused the issue
4. **Console Output**: Browser console and terminal output
5. **Server Status**: Output of diagnostic commands above

### Useful Debug Commands
```bash
# Full system state
echo "=== Environment ==="
python --version
node --version
echo $VIRTUAL_ENV

echo -e "\n=== Processes ==="
ps aux | grep -E "(python|node|vite)"

echo -e "\n=== Ports ==="
lsof -i :8001
lsof -i :8080

echo -e "\n=== Recent Logs ==="
tail -n 20 api_server.log 2>/dev/null || echo "No backend logs"
```