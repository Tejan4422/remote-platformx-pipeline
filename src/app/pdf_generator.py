from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from typing import List, Dict
from pathlib import Path
from datetime import datetime
import io

class PDFGenerator:
    """Generate PDF reports for RAG pipeline results"""
    
    def __init__(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Requirement style
        self.requirement_style = ParagraphStyle(
            'RequirementStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            spaceBefore=6,
            leftIndent=20,
            fontName='Helvetica-Bold'
        )
        
        # Response style
        self.response_style = ParagraphStyle(
            'ResponseStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=20,
            leftIndent=30,
            rightIndent=20
        )
        
        # Header style
        self.header_style = ParagraphStyle(
            'HeaderStyle',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.darkblue
        )
    
    def generate_pdf(self, results: List[Dict], filename: str = None, title: str = "RFP Response Document") -> str:
        """Generate PDF file with requirements and responses"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rfp_responses_{timestamp}.pdf"
        
        output_path = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        # Build content
        story = []
        
        # Add title
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 20))
        
        # Add generation date
        date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        story.append(Paragraph(f"Generated on: {date_str}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add summary
        total_reqs = len(results)
        successful_reqs = sum(1 for r in results if r.get("status", "success") == "success")
        
        summary_text = f"Total Requirements: {total_reqs}<br/>Successfully Processed: {successful_reqs}"
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Add requirements and responses
        for i, result in enumerate(results, 1):
            # Requirement header
            req_header = f"Requirement {i}"
            story.append(Paragraph(req_header, self.header_style))
            
            # Requirement text
            req_text = result["requirement"].replace('\n', '<br/>')
            story.append(Paragraph(req_text, self.requirement_style))
            
            # Response header
            story.append(Paragraph("Response:", self.styles['Heading3']))
            
            # Response text
            response_text = result["response"].replace('\n', '<br/>')
            story.append(Paragraph(response_text, self.response_style))
            
            # Add status if not successful
            if result.get("status") != "success":
                status_text = f"<b>Status:</b> {result.get('status', 'unknown')}"
                story.append(Paragraph(status_text, self.styles['Normal']))
            
            # Add separator line except for last item
            if i < len(results):
                story.append(Spacer(1, 10))
                story.append(Paragraph("_" * 80, self.styles['Normal']))
                story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story)
        
        return str(output_path)
    
    def generate_pdf_bytes(self, results: List[Dict], title: str = "RFP Response Document") -> bytes:
        """Generate PDF file as bytes for Streamlit download"""
        # Create PDF document in memory
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        # Build content
        story = []
        
        # Add title
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 20))
        
        # Add generation date
        date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        story.append(Paragraph(f"Generated on: {date_str}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add summary
        total_reqs = len(results)
        successful_reqs = sum(1 for r in results if r.get("status", "success") == "success")
        
        summary_text = f"Total Requirements: {total_reqs}<br/>Successfully Processed: {successful_reqs}"
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Add requirements and responses
        for i, result in enumerate(results, 1):
            # Requirement header
            req_header = f"Requirement {i}"
            story.append(Paragraph(req_header, self.header_style))
            
            # Requirement text
            req_text = result["requirement"].replace('\n', '<br/>')
            story.append(Paragraph(req_text, self.requirement_style))
            
            # Response header
            story.append(Paragraph("Response:", self.styles['Heading3']))
            
            # Response text
            response_text = result["response"].replace('\n', '<br/>')
            story.append(Paragraph(response_text, self.response_style))
            
            # Add status if not successful
            if result.get("status") != "success":
                status_text = f"<b>Status:</b> {result.get('status', 'unknown')}"
                story.append(Paragraph(status_text, self.styles['Normal']))
            
            # Add separator line except for last item
            if i < len(results):
                story.append(Spacer(1, 10))
                story.append(Paragraph("_" * 80, self.styles['Normal']))
                story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story)
        
        # Get the value and reset buffer position
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_summary_table_pdf(self, results: List[Dict], filename: str = None) -> str:
        """Generate a table-style PDF with requirements and responses"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rfp_summary_{timestamp}.pdf"
        
        output_path = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        story = []
        
        # Add title
        story.append(Paragraph("RFP Response Summary", self.title_style))
        story.append(Spacer(1, 20))
        
        # Prepare table data
        table_data = [['#', 'Requirement', 'Response', 'Status']]
        
        for i, result in enumerate(results, 1):
            # Truncate long texts for table display
            req_text = result["requirement"][:200] + "..." if len(result["requirement"]) > 200 else result["requirement"]
            resp_text = result["response"][:300] + "..." if len(result["response"]) > 300 else result["response"]
            status = result.get("status", "success")
            
            table_data.append([str(i), req_text, resp_text, status])
        
        # Create table
        table = Table(table_data, colWidths=[0.5*inch, 2.5*inch, 3.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(table)
        
        # Build PDF
        doc.build(story)
        
        return str(output_path)