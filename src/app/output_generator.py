import pandas as pd
from typing import List, Dict
from pathlib import Path
import io
from datetime import datetime

class OutputGenerator:
    """Generate output files in various formats for RAG pipeline results"""
    
    def __init__(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_excel(self, results: List[Dict], filename: str = None) -> str:
        """Generate Excel file with requirements and responses"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rfp_responses_{timestamp}.xlsx"
        
        # Prepare data for DataFrame
        data = []
        for i, result in enumerate(results, 1):
            data.append({
                "ID": i,
                "Requirement": result["requirement"],
                "Response": result["response"],
                "Status": result.get("status", "success")
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Save to Excel file
        output_path = self.output_dir / filename
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='RFP Responses', index=False)
            
            # Get the workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['RFP Responses']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                # Set reasonable column widths
                if column_letter == 'A':  # ID column
                    adjusted_width = 5
                elif column_letter == 'B':  # Requirement column
                    adjusted_width = min(max_length + 2, 80)
                elif column_letter == 'C':  # Response column
                    adjusted_width = min(max_length + 2, 100)
                else:  # Status column
                    adjusted_width = min(max_length + 2, 15)
                
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Enable text wrapping for requirement and response columns
            from openpyxl.styles import Alignment
            wrap_alignment = Alignment(wrap_text=True, vertical='top')
            
            for row in worksheet.iter_rows(min_row=2):  # Skip header row
                row[1].alignment = wrap_alignment  # Requirement column
                row[2].alignment = wrap_alignment  # Response column
        
        return str(output_path)
    
    def generate_excel_bytes(self, results: List[Dict]) -> bytes:
        """Generate Excel file as bytes for Streamlit download"""
        # Prepare data for DataFrame
        data = []
        for i, result in enumerate(results, 1):
            data.append({
                "ID": i,
                "Requirement": result["requirement"],
                "Response": result["response"],
                "Status": result.get("status", "success")
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='RFP Responses', index=False)
            
            # Get the workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['RFP Responses']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                # Set reasonable column widths
                if column_letter == 'A':  # ID column
                    adjusted_width = 5
                elif column_letter == 'B':  # Requirement column
                    adjusted_width = min(max_length + 2, 80)
                elif column_letter == 'C':  # Response column
                    adjusted_width = min(max_length + 2, 100)
                else:  # Status column
                    adjusted_width = min(max_length + 2, 15)
                
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Enable text wrapping for requirement and response columns
            from openpyxl.styles import Alignment
            wrap_alignment = Alignment(wrap_text=True, vertical='top')
            
            for row in worksheet.iter_rows(min_row=2):  # Skip header row
                row[1].alignment = wrap_alignment  # Requirement column
                row[2].alignment = wrap_alignment  # Response column
        
        output.seek(0)
        return output.getvalue()
    
    def generate_csv(self, results: List[Dict], filename: str = None) -> str:
        """Generate CSV file with requirements and responses"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rfp_responses_{timestamp}.csv"
        
        # Prepare data for DataFrame
        data = []
        for i, result in enumerate(results, 1):
            data.append({
                "ID": i,
                "Requirement": result["requirement"],
                "Response": result["response"],
                "Status": result.get("status", "success")
            })
        
        # Create DataFrame and save as CSV
        df = pd.DataFrame(data)
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False)
        
        return str(output_path)
    
    def generate_csv_bytes(self, results: List[Dict]) -> bytes:
        """Generate CSV file as bytes for Streamlit download"""
        # Prepare data for DataFrame
        data = []
        for i, result in enumerate(results, 1):
            data.append({
                "ID": i,
                "Requirement": result["requirement"],
                "Response": result["response"],
                "Status": result.get("status", "success")
            })
        
        # Create DataFrame and convert to CSV bytes
        df = pd.DataFrame(data)
        return df.to_csv(index=False).encode('utf-8')