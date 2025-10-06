# Server Management Guide

This guide provides comprehensive instructions for starting, stopping, and managing both the frontend and backend servers for the Local RAG Application.

## Quick Reference

### Check Server Status
```bash
# Check both servers at once
echo "=== SERVER STATUS CHECK ==="
echo "Frontend (port 8080):"
(lsof -ti:8080 && echo "✅ Running" || echo "❌ Stopped")
echo "Backend (port 8001):"
(lsof -ti:8001 && echo "✅ Running" || echo "❌ Stopped")
```

### Health Check
```bash
# Backend health check
curl -s http://localhost:8001/health | grep -o "healthy" && echo " - Backend server is running ✅"

# Frontend check (if running)
curl -s http://localhost:8080 > /dev/null && echo "Frontend accessible ✅" || echo "Frontend not accessible ❌"
```

## Backend Server (FastAPI)

### Starting the Backend Server

#### Method 1: Direct Python (Recommended)
```bash
# Navigate to project root
cd /Users/tejan/Documents/Projects/Local-RAG-App/local-rag-app

# Activate virtual environment
source venv/bin/activate

# Start the server
python api_server.py
```

#### Method 2: Using uvicorn directly
```bash
# From project root with venv activated
uvicorn api_server:app --host 0.0.0.0 --port 8001 --reload
```

### Stopping the Backend Server

#### Method 1: Graceful shutdown (if running in terminal)
- Press `Ctrl+C` in the terminal where the server is running

#### Method 2: Kill by port (if running in background)
```bash
# Find process on port 8001
lsof -ti:8001

# Kill the process
kill $(lsof -ti:8001)

# Force kill if needed
kill -9 $(lsof -ti:8001)
```

#### Method 3: Kill by process name
```bash
# Find python processes
ps aux | grep api_server.py

# Kill specific process (replace XXXX with actual PID)
kill XXXX
```

### Backend Server Information
- **Port**: 8001
- **Health Endpoint**: http://localhost:8001/health
- **API Documentation**: http://localhost:8001/docs (Swagger UI)
- **Log Location**: `api_server.log` (if logging enabled)

## Frontend Server (React/Vite)

### Starting the Frontend Server

```bash
# Navigate to frontend directory
cd /Users/tejan/Documents/Projects/Local-RAG-App/local-rag-app/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

### Frontend Server Options

#### Development Mode (Default)
```bash
npm run dev
```

#### Production Build
```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Stopping the Frontend Server

#### Method 1: Graceful shutdown (if running in terminal)
- Press `Ctrl+C` in the terminal where the server is running

#### Method 2: Kill by port
```bash
# Find process on port 8080
lsof -ti:8080

# Kill the process
kill $(lsof -ti:8080)

# Force kill if needed
kill -9 $(lsof -ti:8080)
```

### Frontend Server Information
- **Port**: 8080 (default for Vite)
- **URL**: http://localhost:8080
- **Hot Reload**: Enabled in development mode
- **Build Output**: `dist/` directory

## Startup Sequence

### Recommended Startup Order
1. **Start Backend First** (dependency for frontend)
   ```bash
   cd /Users/tejan/Documents/Projects/Local-RAG-App/local-rag-app
   source venv/bin/activate
   python api_server.py
   ```

2. **Wait for Backend** (verify it's running)
   ```bash
   curl -s http://localhost:8001/health
   ```

3. **Start Frontend** (in new terminal)
   ```bash
   cd /Users/tejan/Documents/Projects/Local-RAG-App/local-rag-app/frontend
   npm run dev
   ```

### Complete Startup Script
```bash
#!/bin/bash
echo "🚀 Starting Local RAG Application..."

# Start backend
echo "📡 Starting backend server..."
cd /Users/tejan/Documents/Projects/Local-RAG-App/local-rag-app
source venv/bin/activate
python api_server.py &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 3
until curl -s http://localhost:8001/health > /dev/null; do
  echo "Waiting for backend..."
  sleep 1
done
echo "✅ Backend ready!"

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "🎉 Application started!"
echo "📡 Backend: http://localhost:8001"
echo "🎨 Frontend: http://localhost:8080"
echo "📚 API Docs: http://localhost:8001/docs"
```

## Shutdown Sequence

### Graceful Shutdown
```bash
#!/bin/bash
echo "🛑 Shutting down Local RAG Application..."

# Stop frontend
echo "🎨 Stopping frontend server..."
kill $(lsof -ti:8080) 2>/dev/null || echo "Frontend not running"

# Stop backend
echo "📡 Stopping backend server..."
kill $(lsof -ti:8001) 2>/dev/null || echo "Backend not running"

echo "✅ Application stopped!"
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Error: Port 8001 already in use
lsof -ti:8001
kill $(lsof -ti:8001)

# Error: Port 8080 already in use
lsof -ti:8080
kill $(lsof -ti:8080)
```

#### Backend Won't Start
1. Check if virtual environment is activated
2. Verify Python dependencies: `pip install -r requirements.txt`
3. Check for port conflicts
4. Review error logs in terminal

#### Frontend Won't Start
1. Check if Node.js is installed: `node --version`
2. Install dependencies: `npm install`
3. Clear cache: `npm cache clean --force`
4. Check for port conflicts

#### Connection Refused
1. Verify backend is running: `curl http://localhost:8001/health`
2. Check firewall settings
3. Verify correct ports are being used

### Process Management

#### List All Related Processes
```bash
# Find all related processes
ps aux | grep -E "(api_server|vite|node.*dev)"

# Find processes by port
lsof -i :8001  # Backend
lsof -i :8080  # Frontend
```

#### Clean Kill All
```bash
# Nuclear option - kill all related processes
pkill -f api_server
pkill -f "vite.*dev"
```

## Environment Requirements

### Backend Requirements
- Python 3.8+
- Virtual environment activated
- Required packages from `requirements.txt`
- FastAPI, Uvicorn, etc.

### Frontend Requirements
- Node.js 16+
- npm or yarn
- Dependencies from `package.json`

## Development Notes

### API Server Features
- **Auto-reload**: Enabled with `--reload` flag
- **CORS**: Configured for frontend on port 8080
- **Logging**: Available in `api_server.log`
- **Health Check**: `/health` endpoint
- **API Documentation**: Auto-generated at `/docs`

### Frontend Features
- **Hot Module Replacement**: Instant updates during development
- **TypeScript**: Full type checking
- **Build Optimization**: Vite bundling for production
- **Development Tools**: React DevTools compatible

### Session Management
- Backend maintains session state
- Frontend uses SessionContext for state management
- Upload sessions persist across page refreshes
- Session data stored in backend memory/database

## Quick Commands Reference

```bash
# Status check
lsof -ti:8001 && echo "Backend ✅" || echo "Backend ❌"
lsof -ti:8080 && echo "Frontend ✅" || echo "Frontend ❌"

# Start backend
cd /path/to/project && source venv/bin/activate && python api_server.py

# Start frontend
cd /path/to/project/frontend && npm run dev

# Kill both
kill $(lsof -ti:8001) $(lsof -ti:8080) 2>/dev/null

# Health check
curl -s http://localhost:8001/health && curl -s http://localhost:8080 > /dev/null
```
