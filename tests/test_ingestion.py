import unittest
import pandas as pd
from src.ingestion.excel_loader import load_excel
from src.ingestion.document_processor import process_document

class TestIngestion(unittest.TestCase):

    def test_load_excel(self):
        # Assuming there's a sample Excel file in the test data
        df = load_excel('data/raw/sample_data.xlsx')
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)

    def test_process_document(self):
        # Assuming there's a sample document in the test data
        chunks = process_document('data/raw/sample_document.txt')
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)

if __name__ == '__main__':
    unittest.main()