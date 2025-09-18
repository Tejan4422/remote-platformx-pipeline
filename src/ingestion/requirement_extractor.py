import re
from typing import List, Dict, Any
import PyPDF2
import pandas as pd

class RequirementExtractor:
    """Extract requirements from PDF, CSV, or XLSX documents"""
    
    def __init__(self):
        # Column names that typically contain requirements/questions
        self.requirement_column_names = [
            'requirement', 'requirements', 'question', 'questions', 'query', 'queries',
            'item', 'items', 'description', 'task', 'tasks', 'deliverable', 'deliverables',
            'specification', 'specifications', 'criteria', 'criterion', 'objective', 'objectives'
        ]
    
    def extract_from_file(self, file_path: str) -> List[str]:
        """Extract requirements from PDF, CSV, or XLSX files"""
        file_path_lower = file_path.lower()
        
        if file_path_lower.endswith('.pdf'):
            return self._extract_from_pdf(file_path)
        elif file_path_lower.endswith(('.xlsx', '.xls')):
            return self._extract_from_excel(file_path)
        elif file_path_lower.endswith('.csv'):
            return self._extract_from_csv(file_path)
        else:
            raise ValueError("Unsupported file format. Please provide a PDF, XLSX, XLS, or CSV file.")
    
    def extract_with_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract requirements with metadata for structured processing"""
        file_path_lower = file_path.lower()
        
        if file_path_lower.endswith('.pdf'):
            requirements = self._extract_from_pdf(file_path)
            return {
                'requirements': requirements,
                'source_type': 'pdf',
                'has_structure': False,
                'column_name': None
            }
        elif file_path_lower.endswith(('.xlsx', '.xls', '.csv')):
            return self._extract_from_structured_file(file_path)
        else:
            raise ValueError("Unsupported file format. Please provide a PDF, XLSX, XLS, or CSV file.")
    
    def _extract_from_pdf(self, file_path: str) -> List[str]:
        """Extract numbered questions from a PDF file"""
        # Extract text content from PDF
        text_content = self._extract_text_from_pdf(file_path)
        
        # Extract numbered questions
        questions = self._extract_numbered_questions(text_content)
        
        return questions
    
    def _extract_from_excel(self, file_path: str) -> List[str]:
        """Extract requirements from Excel file"""
        try:
            # Try to read the Excel file
            df = pd.read_excel(file_path)
            return self._extract_from_dataframe(df)
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")
    
    def _extract_from_csv(self, file_path: str) -> List[str]:
        """Extract requirements from CSV file"""
        try:
            # Try to read the CSV file
            df = pd.read_csv(file_path)
            return self._extract_from_dataframe(df)
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")
    
    def _extract_from_structured_file(self, file_path: str) -> Dict[str, Any]:
        """Extract requirements from structured file with metadata"""
        try:
            # Read the file
            if file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Find the requirements column
            column_name = self._find_requirements_column(df)
            
            if column_name:
                # Extract requirements from the identified column
                requirements = df[column_name].dropna().astype(str).tolist()
                # Clean up requirements
                requirements = [req.strip() for req in requirements if req.strip() and len(req.strip()) > 5]
                
                return {
                    'requirements': requirements,
                    'source_type': 'excel' if file_path.lower().endswith(('.xlsx', '.xls')) else 'csv',
                    'has_structure': True,
                    'column_name': column_name,
                    'dataframe': df  # Include for response generation
                }
            else:
                # Fallback: extract from all text columns
                requirements = self._extract_from_dataframe(df)
                return {
                    'requirements': requirements,
                    'source_type': 'excel' if file_path.lower().endswith(('.xlsx', '.xls')) else 'csv',
                    'has_structure': False,
                    'column_name': None
                }
        except Exception as e:
            raise ValueError(f"Error reading structured file: {str(e)}")
    
    def _extract_from_dataframe(self, df: pd.DataFrame) -> List[str]:
        """Extract requirements from any columns in a dataframe"""
        requirements = []
        
        # First, try to find a requirements column
        column_name = self._find_requirements_column(df)
        
        if column_name:
            # Extract from the specific column
            requirements = df[column_name].dropna().astype(str).tolist()
        else:
            # Extract from all text columns
            for column in df.columns:
                if df[column].dtype == 'object':  # Text columns
                    column_requirements = df[column].dropna().astype(str).tolist()
                    requirements.extend(column_requirements)
        
        # Clean up requirements
        cleaned_requirements = []
        for req in requirements:
            req = req.strip()
            if len(req) > 5 and not self._is_header_like(req):
                cleaned_requirements.append(req)
        
        return cleaned_requirements
    
    def _find_requirements_column(self, df: pd.DataFrame) -> str:
        """Find the column that likely contains requirements"""
        # Check column names (case-insensitive) - prioritize exact matches first
        exact_matches = []
        partial_matches = []
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            for req_name in self.requirement_column_names:
                if req_name == col_lower:
                    exact_matches.append((col, req_name))
                elif req_name in col_lower:
                    partial_matches.append((col, req_name))
        
        # Prefer exact matches
        if exact_matches:
            return exact_matches[0][0]
        
        # Then prefer longer partial matches (more specific)
        if partial_matches:
            # Sort by length of the requirement name (longer = more specific)
            partial_matches.sort(key=lambda x: len(x[1]), reverse=True)
            return partial_matches[0][0]
        
        # If no name-based matches, look for columns with question-like content
        best_column = None
        best_score = 0
        
        for col in df.columns:
            if df[col].dtype == 'object':  # Text columns
                sample_values = df[col].dropna().head(10).astype(str)
                if len(sample_values) == 0:
                    continue
                
                # Score based on content characteristics
                score = 0
                for val in sample_values:
                    val_lower = val.lower()
                    # Questions
                    if '?' in val:
                        score += 3
                    # Question words
                    if any(word in val_lower for word in ['what', 'how', 'describe', 'explain', 'provide', 'please']):
                        score += 2
                    # Business terms
                    if any(word in val_lower for word in ['experience', 'approach', 'company', 'service', 'support']):
                        score += 1
                    # Length check (requirements are usually substantial)
                    if len(val) > 20:
                        score += 1
                
                # Average score per sample
                avg_score = score / len(sample_values)
                if avg_score > best_score:
                    best_score = avg_score
                    best_column = col
        
        # Only return if we have a reasonable confidence
        if best_score >= 1.5:  # Threshold for confidence
            return best_column
        
        return None
    
    def _is_header_like(self, text: str) -> bool:
        """Check if text looks like a header rather than a requirement"""
        text_lower = text.lower().strip()
        
        # Short, all caps text is likely a header
        if len(text) < 30 and text.isupper():
            return True
        
        # Common header words
        header_words = ['id', 'number', 'index', 'row', 'column', 'header', 'title', 'name']
        if any(word == text_lower for word in header_words):
            return True
        
        return False
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from PDF file"""
        if not file_path.endswith('.pdf'):
            raise ValueError("Only PDF files are supported for this simple extractor")
        
        full_text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
        
        return full_text
    
    def _extract_numbered_questions(self, text: str) -> List[str]:
        """Extract numbered questions from text"""
        questions = []
        lines = text.split('\n')
        
        current_question = ""
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check if this line starts a new numbered question
            # Patterns: "1.", "G1:", "A1:", "Question 1:", etc.
            if self._is_question_start(line):
                # Save previous question if it exists
                if current_question.strip():
                    questions.append(current_question.strip())
                
                # Start new question
                current_question = line
            else:
                # Continue current question (multi-line)
                if current_question:
                    current_question += " " + line
        
        # Don't forget the last question
        if current_question.strip():
            questions.append(current_question.strip())
        
        # Clean up questions
        cleaned_questions = []
        for q in questions:
            if len(q.strip()) > 10:  # Minimum length check
                cleaned_questions.append(q.strip())
        
        return cleaned_questions
    
    def _is_question_start(self, line: str) -> bool:
        """Check if a line starts a new numbered question"""
        # Simple patterns for numbered questions
        patterns = [
            r'^\d+\.',          # 1., 2., 3., etc.
            r'^[A-Z]\d+:',      # G1:, A1:, B2:, etc.
            r'^Question\s+\d+', # Question 1, Question 2, etc.
            r'^Q\d+',           # Q1, Q2, etc.
            r'^\(\d+\)',        # (1), (2), etc.
            r'^\d+\)',          # 1), 2), etc.
        ]
        
        for pattern in patterns:
            if re.match(pattern, line):
                return True
        
        return False
def extract_requirements_from_file(file_path: str) -> List[str]:
    """Convenience function to extract requirements from a file"""
    extractor = RequirementExtractor()
    return extractor.extract_from_file(file_path)