#!/bin/bash

# RFP Response Generator Demo Script
# This script demonstrates how to run the RFP Response Generator

echo "🚀 RFP Response Generator Demo"
echo "==============================="
echo ""

# Check if vector store exists
if [ ! -f "test_store/index.faiss" ]; then
    echo "❌ Vector store not found in test_store/ directory!"
    echo "   Please ensure your knowledge base is properly set up."
    exit 1
fi

echo "✅ Vector store found"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install it first:"
    echo "   brew install ollama"
    echo "   ollama serve"
    echo "   ollama pull llama3"
    exit 1
fi

# Check if Ollama is running
if ! curl -f http://localhost:11434/api/tags &> /dev/null; then
    echo "⚠️  Ollama is not running. Starting it now..."
    echo "   Please run: ollama serve"
    echo "   Then in another terminal: ollama pull llama3"
    echo ""
    echo "📝 Note: This demo requires Ollama to be running with a model (e.g., llama3)"
    exit 1
fi

echo "✅ Ollama is running"

# Check if required dependencies are installed
echo "🔍 Checking dependencies..."

python3 -c "import streamlit, pandas, PyPDF2, sentence_transformers, faiss, requests, openpyxl, reportlab" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ All dependencies are installed"
else
    echo "❌ Some dependencies are missing. Installing them now..."
    pip3 install -r requirements.txt
fi

# Run quick tests
echo ""
echo "🧪 Running system tests..."
python3 quick_test.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed! System is ready."
    echo ""
    echo "🌐 Starting Streamlit application..."
    echo "   Navigate to: http://localhost:8501"
    echo ""
    echo "📋 Workflow:"
    echo "   1. Upload RFP document → Extract requirements"
    echo "   2. Review and edit requirements if needed"
    echo "   3. Generate responses using existing knowledge base"
    echo "   4. Download Excel/PDF files with results"
    echo ""
    echo "💡 The system uses your pre-built knowledge base in test_store/"
    echo ""
    
    # Start Streamlit with simplified app
    python3 -m streamlit run src/app/streamlit_app.py
else
    echo "❌ Tests failed. Please check the error messages above."
    exit 1
fi