# local-rag-app README.md

# Local RAG Application

This project is a local implementation of a Retrieval-Augmented Generation (RAG) pipeline using the OpenAI API, FAISS or ChromaDB for vector indexing, and a modular structure. The application allows users to ingest documents, process them, and retrieve relevant information using embeddings.

## Project Structure

```
local-rag-app
├── src
│   ├── ingestion          # Module for data ingestion
│   │   ├── __init__.py
│   │   ├── excel_loader.py # Functions to load data from Excel files
│   │   └── document_processor.py # Handles text extraction and chunking
│   ├── retrieval          # Module for data retrieval
│   │   ├── __init__.py
│   │   ├── embeddings.py   # Functions for embedding text using OpenAI API
│   │   ├── vector_store.py  # Manages storage and retrieval of embeddings
│   │   └── openai_client.py # Interacts with the OpenAI API
│   ├── app                # Streamlit application
│   │   ├── __init__.py
│   │   ├── streamlit_app.py # Streamlit app code
│   │   └── utils.py        # Utility functions for the app
│   └── config             # Configuration settings
│       ├── __init__.py
│       └── settings.py     # API keys and constants
├── data                   # Data directories
│   ├── processed          # Processed data files
│   └── raw                # Raw data files
├── tests                  # Unit tests
│   ├── __init__.py
│   ├── test_ingestion.py  # Tests for ingestion module
│   └── test_retrieval.py  # Tests for retrieval module
├── requirements.txt       # Project dependencies
├── .env                   # Environment variables
├── .gitignore             # Git ignore file
└── README.md              # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd local-rag-app
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add your API keys and other configuration settings.

5. **Run the Streamlit app:**
   ```bash
   streamlit run src/app/streamlit_app.py
   ```

## Usage

- Upload documents through the Streamlit interface.
- The application will process the documents and allow you to query relevant information using the OpenAI API.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.