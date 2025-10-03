# 🚀 RFP Response Generator - Full-Stack Monorepo

A comprehensive AI-powered RFP (Request for Proposal) response generation system built with FastAPI backend and React frontend.

## 📁 Project Structure

```
rfp-response-generator/
├── README.md                          # This file
├── .gitignore                         # Git ignore patterns
├── requirements.txt                   # Backend dependencies
├── .env                              # Backend environment variables
├── 
├── api_server.py                     # Main FastAPI application
├── src/                              # Backend source code
│   ├── app/                          # Application logic
│   ├── config/                       # Configuration
│   ├── ingestion/                    # Document processing
│   ├── retrieval/                    # Vector search & embeddings
│   └── vector_store/                 # Vector database
├── data/                             # Data storage
├── tests/                            # Backend tests
├── docs/                             # Backend documentation
│
├── frontend/                         # React + TypeScript Frontend
│   ├── package.json                  # Node.js dependencies
│   ├── vite.config.ts               # Vite configuration
│   ├── .env.local                   # Frontend environment variables
│   ├── src/                         # Source code
│   │   ├── components/              # React components
│   │   ├── hooks/                   # Custom React hooks
│   │   ├── lib/                     # Utilities & API client
│   │   ├── contexts/                # React contexts
│   │   └── pages/                   # Page components
│   └── public/                      # Static assets
│
└── frontend-integration/            # Integration files for frontend
    ├── api-client.ts                # Type-safe API client
    ├── useAPI.ts                    # React Query hooks
    ├── DocumentUpload.tsx           # Enhanced upload component
    ├── ChatInterface.tsx            # Real-time chat interface
    ├── KnowledgeBase.tsx            # Knowledge management
    ├── SessionContext.tsx           # Session state management
    └── INTEGRATION_GUIDE.md         # Integration instructions
```

## 🛠️ Technology Stack

### Backend (Python + FastAPI + RAG)
- **FastAPI** - Modern, fast web framework
- **LangChain** - RAG (Retrieval Augmented Generation)
- **FAISS** - Vector similarity search
- **OpenAI/Ollama** - Language models
- **PyPDF2** - PDF processing
- **pandas** - Data manipulation

### Frontend (React + TypeScript)
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **shadcn/ui** - UI component library
- **Tailwind CSS** - Utility-first styling
- **React Query** - Server state management

