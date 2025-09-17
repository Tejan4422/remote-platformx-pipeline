import unittest
from src.retrieval.embeddings import embed_text
from src.retrieval.vector_store import VectorStore
from src.retrieval.openai_client import generate_answer

class TestRetrieval(unittest.TestCase):

    def test_embed_text(self):
        text = "This is a test sentence."
        embeddings = embed_text(text)
        self.assertIsInstance(embeddings, list)
        self.assertGreater(len(embeddings), 0)

    def test_vector_store(self):
        vector_store = VectorStore()
        test_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        vector_store.add_embeddings(test_embeddings)

        query_embedding = [0.1, 0.2, 0.3]
        results = vector_store.retrieve_similar(query_embedding, top_k=1)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_generate_answer(self):
        prompt = "What is the capital of France?"
        answer = generate_answer(prompt)
        self.assertIsInstance(answer, str)
        self.assertGreater(len(answer), 0)

if __name__ == '__main__':
    unittest.main()