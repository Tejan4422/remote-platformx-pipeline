# Local RAG Application

This project is a local implementation of a Retrieval-Augmented Generation (RAG) pipeline that extracts requirements from RFP documents and generates professional responses using local language models.

## Project Structure

```
local-rag-app/
├── README.md
├── requirements.txt
├── demo.sh
├── quick_test.py
├── debug_extraction.py
├── show_improvement.py
├── test_real_pdf.py
├── test_system.py
├── test_vector_store.py
├── data/
│   ├── processed/
│   └── raw/
│       └── Test_rfp - Sheet1.pdf
├── output/
├── src/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── index_documents.py
│   │   ├── output_generator.py
│   │   ├── pdf_generator.py
│   │   ├── rag_pipeline.py
│   │   ├── streamlit_app_simple.py
│   │   ├── streamlit_app.py
│   │   ├── test_retrieval.py
│   │   └── utils.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── document_processor.py
│   │   ├── excel_loader.py
│   │   ├── requirement_extractor.py
│   │   └── advanced/
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── embeddings.py
│   │   ├── openai_client.py
│   │   └── vector_store.py
│   └── vector_store/
│       ├── __init__.py
│       ├── test_vector_store.py
│       └── vector_store.py
├── test_store/
│   ├── docstore.pkl
│   └── index.faiss
└── tests/
    ├── __init__.py
    ├── test_enhanced_extraction.py
    ├── test_ingestion.py
    └── test_retrieval.py
```

## Core Components

### Application Layer (`src/app/`)
- **`streamlit_app.py`**: Main web interface for RFP processing
- **`rag_pipeline.py`**: Core RAG processing pipeline
- **`output_generator.py`**: Excel and CSV file generation
- **`pdf_generator.py`**: PDF report generation

### Ingestion Layer (`src/ingestion/`)
- **`requirement_extractor.py`**: Extracts requirements from PDF/Excel/CSV files
- **`document_processor.py`**: Text extraction and document chunking
- **`excel_loader.py`**: Excel and CSV file processing

### Retrieval Layer (`src/retrieval/`)
- **`embeddings.py`**: Text embedding generation
- **`vector_store.py`**: FAISS vector storage and similarity search
- **`openai_client.py`**: Language model integration

### Configuration (`src/config/`)
- **`settings.py`**: Application configuration and constants

