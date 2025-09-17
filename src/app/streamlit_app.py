import streamlit as st
from pathlib import Path
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.document_processor import process_document
from retrieval.embeddings import embed_text
from retrieval.vector_store import VectorStore
from retrieval.openai_client import generate_answer

def main():
    st.title("Local RAG Application")
    
    # Create directories if they don't exist
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    
    # Document upload
    uploaded_file = st.file_uploader("Upload a document (PDF or DOCX)", type=['pdf', 'docx'])
    
    if uploaded_file:
        # Save the uploaded file temporarily
        temp_path = Path("data/raw") / uploaded_file.name
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Process the document
        text_chunks = process_document(str(temp_path))
        
        # Initialize vector store
        vector_store = VectorStore(dimension=1536)  # OpenAI embeddings are 1536-dimensional
        
        # Create and store embeddings for each chunk
        embeddings = [embed_text(chunk) for chunk in text_chunks]
        vector_store.add_embeddings(embeddings)
        
        st.success("Document processed and indexed successfully!")
        
        # Query interface
        query = st.text_input("Enter your question about the document:")
        if query:
            # Get query embedding
            query_embedding = embed_text(query)
            
            # Retrieve relevant chunks
            similar_chunks = vector_store.retrieve_similar(query_embedding, top_k=3)
            
            # Create context from similar chunks
            context = "\n".join([text_chunks[int(idx)] for idx, _ in similar_chunks])
            
            # Generate answer using context
            prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
            answer = generate_answer(prompt)
            
            st.write("Answer:", answer)

if __name__ == "__main__":
    main()