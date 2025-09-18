import re
from typing import List
import PyPDF2

class RequirementExtractor:
    """Simple extractor for numbered questions from PDF documents"""
    
    def __init__(self):
        pass
    
    def extract_from_file(self, file_path: str) -> List[str]:
        """Extract numbered questions from a PDF file"""
        # Extract text content from PDF
        text_content = self._extract_text_from_pdf(file_path)
        
        # Extract numbered questions
        questions = self._extract_numbered_questions(text_content)
        
        return questions
    
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