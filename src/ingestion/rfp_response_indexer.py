import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import tempfile
import os
import sys
from datetime import datetime

# Add the current directory to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from retrieval.embeddings import embed_text
from vector_store.vector_store import FAISSStore

class RFPResponseIndexer:
    """
    Handles indexing of RFP response documents to add them to the vector store.
    Expected format: Excel files with 'Requirement' and 'Response' columns
    """
    
    def __init__(self, vector_store_path: str = "test_store"):
        """
        Initialize the RFP Response Indexer
        
        Args:
            vector_store_path (str): Path to the vector store directory
        """
        self.vector_store_path = vector_store_path
        self.texts = []  # For compatibility with existing code
        
    def detect_columns(self, df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
        """
        Detect requirement and response columns in the DataFrame
        
        Args:
            df (pd.DataFrame): The input DataFrame
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (requirement_column, response_column)
        """
        # Common variations for requirement columns
        requirement_variations = [
            'requirement', 'requirements', 'question', 'questions', 
            'query', 'queries', 'item', 'items', 'task', 'tasks',
            'rfp_requirement', 'rfp_question', 'description'
        ]
        
        # Common variations for response columns
        response_variations = [
            'response', 'responses', 'answer', 'answers', 'reply', 'replies',
            'solution', 'solutions', 'description', 'details', 'content',
            'rfp_response', 'our_response', 'proposal_response'
        ]
        
        columns_lower = [col.lower().strip() for col in df.columns]
        
        # Find requirement column
        requirement_col = None
        for var in requirement_variations:
            for i, col in enumerate(columns_lower):
                if var in col or col in var:
                    requirement_col = df.columns[i]
                    break
            if requirement_col:
                break
        
        # Find response column
        response_col = None
        for var in response_variations:
            for i, col in enumerate(columns_lower):
                if var in col or col in var:
                    # Make sure it's not the same as requirement column
                    if df.columns[i] != requirement_col:
                        response_col = df.columns[i]
                        break
            if response_col:
                break
        
        return requirement_col, response_col
    
    def process_rfp_responses(self, file_path: str) -> Dict:
        """
        Process an RFP response file and extract requirement-response pairs
        
        Args:
            file_path (str): Path to the Excel file
            
        Returns:
            Dict: Processing results with extracted data and metadata
        """
        try:
            # Load the Excel file
            df = pd.read_excel(file_path)
            
            # Detect columns
            req_col, resp_col = self.detect_columns(df)
            
            if not req_col or not resp_col:
                return {
                    'success': False,
                    'error': 'Could not detect requirement and response columns',
                    'available_columns': list(df.columns),
                    'detected_requirement_col': req_col,
                    'detected_response_col': resp_col
                }
            
            # Filter out empty rows
            df = df.dropna(subset=[req_col, resp_col])
            df = df[df[req_col].astype(str).str.strip() != '']
            df = df[df[resp_col].astype(str).str.strip() != '']
            
            # Extract requirement-response pairs
            rfp_pairs = []
            for _, row in df.iterrows():
                requirement = str(row[req_col]).strip()
                response = str(row[resp_col]).strip()
                
                if requirement and response:
                    rfp_pairs.append({
                        'requirement': requirement,
                        'response': response
                    })
            
            return {
                'success': True,
                'rfp_pairs': rfp_pairs,
                'requirement_column': req_col,
                'response_column': resp_col,
                'total_pairs': len(rfp_pairs),
                'dataframe': df
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error processing file: {str(e)}"
            }
    
    def create_indexable_documents(self, rfp_pairs: List[Dict]) -> List[str]:
        """
        Create documents suitable for indexing from RFP pairs
        
        Args:
            rfp_pairs (List[Dict]): List of requirement-response pairs
            
        Returns:
            List[str]: List of formatted documents for indexing
        """
        documents = []
        
        for i, pair in enumerate(rfp_pairs, 1):
            # Create a comprehensive document that includes both requirement and response
            # This allows the RAG system to retrieve relevant responses based on similar requirements
            document = f"""RFP Response #{i}

Requirement: {pair['requirement']}

Response: {pair['response']}

---
This is a historical RFP response that demonstrates how our organization has addressed similar requirements in the past. The response can be used as reference for generating responses to similar future requirements."""
            
            documents.append(document)
        
        return documents
    
    def add_to_vector_store(self, documents: List[str], metadata: Dict = None) -> Dict:
        """
        Add documents to the existing vector store
        
        Args:
            documents (List[str]): List of documents to add
            metadata (Dict): Optional metadata about the indexing operation
            
        Returns:
            Dict: Results of the indexing operation
        """
        try:
            # Generate embeddings for documents
            embeddings = [embed_text(doc) for doc in documents]
            
            # Load existing vector store or create new one
            vector_store_exists = (Path(self.vector_store_path) / "index.faiss").exists()
            
            if vector_store_exists:
                # Load existing vector store
                store = FAISSStore.load(self.vector_store_path)
                initial_count = len(store.document_map)
            else:
                # Create new vector store
                store = FAISSStore()
                initial_count = 0
            
            # Add new documents
            doc_ids = store.add_texts(documents, embeddings)
            
            # Save updated vector store
            store.save(self.vector_store_path)
            
            return {
                'success': True,
                'documents_added': len(documents),
                'document_ids': doc_ids,
                'initial_document_count': initial_count,
                'final_document_count': len(store.document_map),
                'vector_store_path': self.vector_store_path,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error adding to vector store: {str(e)}"
            }
    
    def index_rfp_responses(self, file_path: str) -> Dict:
        """
        Complete workflow to index RFP responses from a file
        
        Args:
            file_path (str): Path to the Excel file containing RFP responses
            
        Returns:
            Dict: Complete results of the indexing operation
        """
        # Step 1: Process the file
        processing_result = self.process_rfp_responses(file_path)
        
        if not processing_result['success']:
            return processing_result
        
        # Step 2: Create indexable documents
        documents = self.create_indexable_documents(processing_result['rfp_pairs'])
        
        # Step 3: Add to vector store
        indexing_result = self.add_to_vector_store(documents, processing_result)
        
        # Combine results
        return {
            **processing_result,
            **indexing_result,
            'indexable_documents': len(documents)
        }
    
    def get_vector_store_info(self) -> Dict:
        """
        Get information about the current vector store
        
        Returns:
            Dict: Information about the vector store
        """
        try:
            vector_store_exists = (Path(self.vector_store_path) / "index.faiss").exists()
            
            if not vector_store_exists:
                return {
                    'exists': False,
                    'path': self.vector_store_path
                }
            
            store = FAISSStore.load(self.vector_store_path)
            
            return {
                'exists': True,
                'path': self.vector_store_path,
                'total_documents': len(store.document_map),
                'vector_dimension': store.dimension,
                'index_size': store.index.ntotal
            }
            
        except Exception as e:
            return {
                'exists': False,
                'error': f"Error reading vector store: {str(e)}"
            }