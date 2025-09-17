import numpy as np
from vector_store import FAISSStore

def test_vector_store():
    # Initialize store
    store = FAISSStore(dimension=3)  # Using small dimension for testing
    
    # Test data
    texts = [
        "This is the first document",
        "This is the second document",
        "This is the third document"
    ]
    
    # Create mock embeddings (normally these would come from an embedding model)
    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ]
    
    # Add texts and embeddings
    doc_ids = store.add_texts(texts, embeddings)
    print(f"Added documents with IDs: {doc_ids}")
    
    # Test similarity search
    query_embedding = [1.0, 0.1, 0.1]  # Should be closest to first document
    results = store.similarity_search(query_embedding, k=2)
    
    print("\nSearch results:")
    for doc_id, text, score in results:
        print(f"ID: {doc_id}, Score: {score:.4f}")
        print(f"Text: {text}\n")
    
    # Test save and load
    store.save("test_store")
    loaded_store = FAISSStore.load("test_store")
    
    # Verify loaded store works
    loaded_results = loaded_store.similarity_search(query_embedding, k=2)
    print("\nResults from loaded store:")
    for doc_id, text, score in loaded_results:
        print(f"ID: {doc_id}, Score: {score:.4f}")
        print(f"Text: {text}\n")

if __name__ == "__main__":
    test_vector_store()