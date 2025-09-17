import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.retrieval.embeddings import embed_text
from src.vector_store.vector_store import FAISSStore

def test_query(query, store_dir="test_store"):
    # Load the vector store
    store = FAISSStore.load(store_dir)
    # Embed the query
    query_embedding = embed_text(query)
    # Search for top 3 similar chunks
    results = store.similarity_search(query_embedding, 3)
    print("Top results:")
    for i, chunk in enumerate(results):
        print(f"\nResult {i+1}:\n{chunk}")

if __name__ == "__main__":
    query = input("Enter your query: ")
    test_query(query)