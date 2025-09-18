# local-rag-app README.md

# Local RAG Application

This project is a local implementation of a Retrieval-Augmented Generation (RAG) pipeline using the OpenAI API, FAISS or ChromaDB for vector indexing, and a modular structure. The application allows users to ingest documents, process them, and retrieve relevant information using embeddings.

## Project Structure

# RFP Response Generator

An intelligent system that extracts requirements from RFP documents and generates professional responses using Retrieval-Augmented Generation (RAG) with local language models.

## Features

- **📄 Document Processing**: Upload PDF/DOCX files containing RFP requirements
- **🧠 Intelligent Extraction**: Automatically extract individual requirements from documents
- **🔍 RAG Pipeline**: Use your knowledge base to generate contextual responses
- **📊 Multiple Output Formats**: Export results as Excel, PDF, or CSV
- **🎛️ Interactive Interface**: User-friendly Streamlit web interface
- **⚡ Batch Processing**: Process multiple requirements efficiently

## System Architecture

```
RFP Document → Requirement Extraction → RAG Processing → Response Generation → Output Files
     ↓                    ↓                   ↓                    ↓               ↓
   PDF/DOCX         Pattern Matching    Vector Search      Ollama LLM        Excel/PDF/CSV
```

## Installation

1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Install Ollama** (if not already installed):
   ```bash
   # On macOS
   brew install ollama
   
   # Start Ollama service
   ollama serve
   
   # Pull a model (e.g., llama3)
   ollama pull llama3
   ```

## Usage

### Running the Streamlit Application

```bash
streamlit run src/app/streamlit_app.py
```

Then navigate to `http://localhost:8501` in your web browser.

### Workflow

1. **Upload & Extract** tab:
   - Upload your RFP document (PDF or DOCX)
   - Review automatically extracted requirements
   - Edit requirements if needed

2. **Build Knowledge Base** tab:
   - Upload documents containing information to answer requirements
   - Build vector store for RAG retrieval

3. **Generate Responses** tab:
   - Configure RAG parameters (context chunks, model)
   - Generate responses for all requirements
   - Review generated responses

4. **Download Results** tab:
   - Export results in Excel, PDF, or CSV format
   - Download files for submission or review

## System Components

### Core Modules

- **`requirement_extractor.py`**: Extracts requirements from documents
- **`rag_pipeline.py`**: Main RAG processing pipeline
- **`output_generator.py`**: Excel and CSV generation
- **`pdf_generator.py`**: PDF report generation
- **`streamlit_app.py`**: Web interface

### Supporting Modules

- **`document_processor.py`**: Text extraction and chunking
- **`embeddings.py`**: Text embedding generation
- **`vector_store.py`**: FAISS vector storage

## Testing

Run the test suite:

```bash
python3 test_system.py
```

## Dependencies

- **streamlit**: Web interface
- **pandas**: Data manipulation
- **PyPDF2**: PDF processing
- **python-docx**: DOCX processing
- **sentence-transformers**: Text embeddings
- **faiss-cpu**: Vector similarity search
- **requests**: Ollama API communication
- **openpyxl**: Excel file generation
- **reportlab**: PDF generation

