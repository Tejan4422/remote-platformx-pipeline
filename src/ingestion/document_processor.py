from typing import List
import PyPDF2
import docx

def process_document(file_path: str, chunk_size: int = 800, chunk_overlap: int = 100) -> List[str]:
    """
    Extracts text from a PDF or DOCX file and splits it into overlapping chunks.
    """
    # Extract all text from the document
    full_text = ""
    if file_path.endswith('.pdf'):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                full_text += paragraph.text.strip() + "\n"
    else:
        raise ValueError("Unsupported file format. Please provide a PDF or DOCX file.")

    # Split text into paragraphs
    paragraphs = [p.strip() for p in full_text.split('\n') if p.strip()]

    # Further split paragraphs into overlapping chunks
    chunks = []
    for para in paragraphs:
        start = 0
        while start < len(para):
            end = min(start + chunk_size, len(para))
            chunk = para[start:end]
            chunks.append(chunk)
            if end == len(para):
                break
            start += chunk_size - chunk_overlap

    return chunks