import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.ingestion.document_processor import process_document
from src.retrieval.embeddings import embed_text
from src.vector_store.vector_store import FAISSStore

def index_documents(doc_paths, store_dir="test_store"):
    all_chunks = []
    all_embeddings = []
    for doc_path in doc_paths:
        print(f"Processing {doc_path} ...")
        chunks = process_document(str(doc_path))
        embeddings = [embed_text(chunk) for chunk in chunks]
        all_chunks.extend(chunks)
        all_embeddings.extend(embeddings)
    print(f"Total chunks: {len(all_chunks)}")

    # Initialize FAISSStore with correct dimension for MiniLM (384)
    store = FAISSStore(dimension=384)
    doc_ids = store.add_texts(all_chunks, all_embeddings)
    print(f"Indexed {len(doc_ids)} chunks.")

    # Save the store
    store.save(store_dir)
    print(f"Vector store saved to {store_dir}")

if __name__ == "__main__":
    # Example: index all PDF and DOCX files in data/raw
    data_dir = Path("data/raw")
    doc_paths = list(data_dir.glob("*.pdf")) + list(data_dir.glob("*.docx"))
    if not doc_paths:
        print("No PDF or DOCX files found in data/raw.")
    else:
        index_documents(doc_paths)