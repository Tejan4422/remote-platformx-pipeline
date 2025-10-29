import requests
import json
import re
import pandas as pd
from typing import List, Optional, Dict, Tuple
import openpyxl

class RequirementClassifier:
    """Classifies requirements into predefined categories using LLM"""
    
    # Predefined categories
    CATEGORIES = [
        "Tech",
        "Security", 
        "Compliance",
        "Functional",
        "Non-Functional",
        "BI Tool",
        "Gen AI or AI",
        "Machine Learning",
    ]
    
    def __init__(self, ollama_url="http://localhost:11434", model="llama3"):
        self.ollama_url = ollama_url
        self.model = model
    
    def classify_requirement(self, requirement: str) -> str:
        """
        Classify a single requirement into one of the predefined categories
        
        Args:
            requirement (str): The requirement text to classify
            
        Returns:
            str: One of the predefined categories or "Unknown" if classification fails
        """
        prompt = f"""You are a requirement classifier. Your job is to classify the given requirement into EXACTLY ONE of these categories:

Categories:
- Tech: Technical requirements related to technology stack, infrastructure, APIs, databases, etc.
- Security: Requirements related to data security, access control, authentication, encryption, etc.
- Compliance: Requirements related to regulatory compliance, standards, audit trails, etc.
- Functional: Requirements describing what the system should do, features, business logic, etc.
- Non-Functional: Requirements about performance, scalability, usability, reliability, etc.
- BI Tool: Requirements specifically about Business Intelligence tools, reporting, analytics, dashboards, etc.
- Gen AI or AI: Requirements related to Generative AI capabilities, models, or applications.
- Machine Learning: Requirements related to machine learning models, training, inference, or data processing.

IMPORTANT RULES:
1. Respond with ONLY the category name - nothing else
2. The response must be exactly one of: Tech, Security, Compliance, Functional, Non-Functional, BI Tool, Gen AI or AI, Machine Learning
3. Do not add any explanation, punctuation, or additional text
4. If unsure, choose the most relevant category

Requirement to classify: {requirement}

Category:"""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistent classification
                        "top_p": 0.9
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            raw_response = response.json()["response"].strip()
            
            # Clean and validate the response
            category = self._clean_and_validate_category(raw_response)
            return category
            
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Ollama for classification: {e}")
            return "Unknown"
        except KeyError:
            print("Error: Invalid response from Ollama for classification")
            return "Unknown"
        except Exception as e:
            print(f"Unexpected error during classification: {e}")
            return "Unknown"
    
    def _clean_and_validate_category(self, raw_response: str) -> str:
        """
        Clean the LLM response and validate it's a valid category
        
        Args:
            raw_response (str): Raw response from LLM
            
        Returns:
            str: Valid category name or "Unknown"
        """
        # Remove extra whitespace and newlines
        cleaned = raw_response.strip().replace('\n', '').replace('\r', '')
        
        # Remove common prefixes that LLM might add
        prefixes_to_remove = [
            "Category:",
            "The category is:",
            "Classification:",
            "Answer:",
            "Response:",
            "Result:"
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
        
        # Check if the cleaned response matches any of our categories (case-insensitive)
        for category in self.CATEGORIES:
            if cleaned.lower() == category.lower():
                return category
        
        # Try partial matching for common variations
        category_variations = {
            "technical": "Tech",
            "technology": "Tech",
            "functional": "Functional",
            "non-functional": "Non-Functional",
            "nonfunctional": "Non-Functional",
            "security": "Security",
            "compliance": "Compliance",
            "bi tool": "BI Tool",
            "bi": "BI Tool",
            "business intelligence": "BI Tool",
            "gen ai": "Gen AI or AI",
            "ai": "Gen AI or AI",
            "machine learning": "Machine Learning",
            "ml": "Machine Learning"
        }
        
        for variation, category in category_variations.items():
            if variation in cleaned.lower():
                return category
        
        print(f"Warning: Unrecognized category response: '{cleaned}'. Defaulting to 'Unknown'")
        return "Unknown"
    
    def classify_requirements_batch(self, requirements: List[str]) -> List[dict]:
        """
        Classify multiple requirements in batch
        
        Args:
            requirements (List[str]): List of requirement texts
            
        Returns:
            List[dict]: List of dictionaries with requirement and category
        """
        results = []
        total_requirements = len(requirements)
        
        print(f"Classifying {total_requirements} requirements...")
        
        for i, requirement in enumerate(requirements):
            print(f"Classifying requirement {i+1}/{total_requirements}")
            
            try:
                category = self.classify_requirement(requirement)
                results.append({
                    "requirement": requirement,
                    "category": category,
                    "status": "success"
                })
            except Exception as e:
                print(f"Error classifying requirement {i+1}: {e}")
                results.append({
                    "requirement": requirement,
                    "category": "Unknown",
                    "status": "error"
                })
        
        return results
    
    def process_multi_sheet_rfp(self, file_path: str, requirement_columns: List[str] = None) -> Dict[str, List[dict]]:
        """
        Process an Excel file with multiple sheets for RFP requirements
        
        Args:
            file_path (str): Path to the Excel file
            requirement_columns (List[str]): Column names that contain requirements
                                           If None, will try to auto-detect
            
        Returns:
            Dict[str, List[dict]]: Dictionary with sheet names as keys and 
                                  classified requirements as values
        """
        if requirement_columns is None:
            requirement_columns = ['requirement', 'requirements', 'description', 'details', 'specification']
        
        try:
            # Read all sheets from Excel file
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            print(f"Found {len(sheet_names)} sheets: {sheet_names}")
            
            all_results = {}
            
            for sheet_name in sheet_names:
                print(f"\nProcessing sheet: {sheet_name}")
                
                # Read the specific sheet
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Extract requirements from this sheet
                requirements = self._extract_requirements_from_dataframe(df, requirement_columns)
                
                if not requirements:
                    print(f"No requirements found in sheet '{sheet_name}'")
                    all_results[sheet_name] = []
                    continue
                
                print(f"Found {len(requirements)} requirements in sheet '{sheet_name}'")
                
                # Classify requirements for this sheet
                classified_results = self.classify_requirements_batch(requirements)
                
                # Add sheet information to each result
                for result in classified_results:
                    result['sheet_name'] = sheet_name
                
                all_results[sheet_name] = classified_results
            
            return all_results
            
        except Exception as e:
            print(f"Error processing multi-sheet RFP file: {e}")
            return {}
    
    def _extract_requirements_from_dataframe(self, df: pd.DataFrame, requirement_columns: List[str]) -> List[str]:
        """
        Extract requirements text from a DataFrame
        
        Args:
            df (pd.DataFrame): DataFrame containing the data
            requirement_columns (List[str]): Possible column names for requirements
            
        Returns:
            List[str]: List of requirement texts
        """
        requirements = []
        
        # Find the column that contains requirements
        requirement_column = None
        df_columns_lower = [col.lower() for col in df.columns]
        
        for req_col in requirement_columns:
            if req_col.lower() in df_columns_lower:
                # Get the actual column name (preserving case)
                actual_col_index = df_columns_lower.index(req_col.lower())
                requirement_column = df.columns[actual_col_index]
                break
        
        if requirement_column is None:
            print(f"No requirement column found. Available columns: {list(df.columns)}")
            return requirements
        
        print(f"Using column '{requirement_column}' for requirements")
        
        # Extract non-empty requirements
        for idx, row in df.iterrows():
            req_text = str(row[requirement_column]).strip()
            if req_text and req_text.lower() not in ['nan', 'none', '']:
                requirements.append(req_text)
        
        return requirements
    
    def export_results_to_excel(self, results: Dict[str, List[dict]], output_path: str):
        """
        Export classified results back to Excel with multiple sheets
        
        Args:
            results (Dict[str, List[dict]]): Results from process_multi_sheet_rfp
            output_path (str): Path for the output Excel file
        """
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                
                # Create a summary sheet
                summary_data = []
                for sheet_name, sheet_results in results.items():
                    if sheet_results:
                        category_counts = {}
                        for result in sheet_results:
                            category = result['category']
                            category_counts[category] = category_counts.get(category, 0) + 1
                        
                        for category, count in category_counts.items():
                            summary_data.append({
                                'Sheet': sheet_name,
                                'Category': category,
                                'Count': count
                            })
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Create individual sheets for each original sheet
                for sheet_name, sheet_results in results.items():
                    if sheet_results:
                        df_data = []
                        for result in sheet_results:
                            df_data.append({
                                'Requirement': result['requirement'],
                                'Category': result['category'],
                                'Status': result['status']
                            })
                        
                        df = pd.DataFrame(df_data)
                        # Truncate sheet name if too long (Excel limit is 31 characters)
                        safe_sheet_name = sheet_name[:31] if len(sheet_name) > 31 else sheet_name
                        df.to_excel(writer, sheet_name=f"{safe_sheet_name}_Classified", index=False)
            
            print(f"Results exported to: {output_path}")
            
        except Exception as e:
            print(f"Error exporting results to Excel: {e}")
    
    def get_classification_summary(self, results: Dict[str, List[dict]]) -> Dict[str, Dict[str, int]]:
        """
        Get a summary of classifications by sheet and category
        
        Args:
            results (Dict[str, List[dict]]): Results from process_multi_sheet_rfp
            
        Returns:
            Dict[str, Dict[str, int]]: Summary with counts by sheet and category
        """
        summary = {}
        
        for sheet_name, sheet_results in results.items():
            summary[sheet_name] = {}
            
            for result in sheet_results:
                category = result['category']
                summary[sheet_name][category] = summary[sheet_name].get(category, 0) + 1
        
        return summary
    
    def get_sheet_names(self, file_path: str) -> List[str]:
        """
        Get list of sheet names from an Excel file without processing them
        
        Args:
            file_path (str): Path to the Excel file
            
        Returns:
            List[str]: List of sheet names
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception as e:
            print(f"Error reading sheet names from file: {e}")
            return []
    
    def preview_sheet_data(self, file_path: str, sheet_name: str, max_rows: int = 5) -> Dict:
        """
        Preview data from a specific sheet without processing
        
        Args:
            file_path (str): Path to the Excel file
            sheet_name (str): Name of the sheet to preview
            max_rows (int): Maximum number of rows to preview
            
        Returns:
            Dict: Preview information including columns and sample data
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            preview_data = {
                'sheet_name': sheet_name,
                'total_rows': len(df),
                'columns': list(df.columns),
                'sample_data': df.head(max_rows).to_dict('records')
            }
            
            return preview_data
            
        except Exception as e:
            print(f"Error previewing sheet '{sheet_name}': {e}")
            return {}

def test_classifier():
    """Test function to verify the classifier works"""
    classifier = RequirementClassifier()
    
    # Test requirements for each category
    test_requirements = [
        "The system must use PostgreSQL database and REST APIs",  # Tech
        "All user data must be encrypted at rest and in transit",  # Security
        "The system must comply with GDPR regulations",  # Compliance
        "Users should be able to create and edit customer profiles",  # Functional
        "The system must respond to queries within 2 seconds",  # Non-Functional
        "Generate monthly sales reports with charts and dashboards"  # BI Tool
    ]
    
    print("Testing Requirement Classifier...")
    print("=" * 50)
    
    for i, requirement in enumerate(test_requirements, 1):
        category = classifier.classify_requirement(requirement)
        print(f"{i}. Requirement: {requirement}")
        print(f"   Category: {category}")
        print()

def test_multi_sheet_processing():
    """Test function for multi-sheet RFP processing"""
    classifier = RequirementClassifier()
    
    print("Testing Multi-Sheet RFP Processing...")
    print("=" * 60)
    
    # Example: Test with a hypothetical multi-sheet file
    # In practice, you would use an actual file path
    sample_file_path = "sample_rfp.xlsx"
    
    # Check if we can read sheet names (for demo purposes)
    try:
        # This is just an example - in practice you'd have an actual file
        print("Example of how to use multi-sheet processing:")
        print("\n1. Get sheet names from Excel file:")
        print("   sheet_names = classifier.get_sheet_names(file_path)")
        
        print("\n2. Preview data from specific sheet:")
        print("   preview = classifier.preview_sheet_data(file_path, 'Sheet1')")
        
        print("\n3. Process all sheets:")
        print("   results = classifier.process_multi_sheet_rfp(file_path)")
        
        print("\n4. Get classification summary:")
        print("   summary = classifier.get_classification_summary(results)")
        
        print("\n5. Export results to Excel:")
        print("   classifier.export_results_to_excel(results, 'output.xlsx')")
        
        # Demonstrate the expected structure
        print("\nExpected Results Structure:")
        print("results = {")
        print("    'Technical_Requirements': [")
        print("        {'requirement': 'System must use REST APIs', 'category': 'Tech', 'status': 'success', 'sheet_name': 'Technical_Requirements'},")
        print("        ...")
        print("    ],")
        print("    'Security_Requirements': [")
        print("        {'requirement': 'Data must be encrypted', 'category': 'Security', 'status': 'success', 'sheet_name': 'Security_Requirements'},")
        print("        ...")
        print("    ]")
        print("}")
        
    except Exception as e:
        print(f"Note: This is a demonstration. To test with real files, provide a valid Excel file path.")

def process_rfp_file_example(file_path: str):
    """
    Example of how to process a real multi-sheet RFP file
    
    Args:
        file_path (str): Path to the Excel file with multiple sheets
    """
    classifier = RequirementClassifier()
    
    print(f"Processing RFP file: {file_path}")
    print("=" * 60)
    
    # Step 1: Get sheet names
    sheet_names = classifier.get_sheet_names(file_path)
    print(f"Found sheets: {sheet_names}")
    
    # Step 2: Preview each sheet
    for sheet_name in sheet_names:
        print(f"\nPreviewing sheet: {sheet_name}")
        preview = classifier.preview_sheet_data(file_path, sheet_name, max_rows=3)
        if preview:
            print(f"  Rows: {preview['total_rows']}")
            print(f"  Columns: {preview['columns']}")
    
    # Step 3: Process all sheets
    print("\nProcessing all sheets...")
    results = classifier.process_multi_sheet_rfp(
        file_path=file_path,
        requirement_columns=['requirement', 'description', 'specification', 'details']
    )
    
    # Step 4: Display summary
    if results:
        summary = classifier.get_classification_summary(results)
        print("\nClassification Summary:")
        print("-" * 40)
        
        total_requirements = 0
        for sheet_name, categories in summary.items():
            sheet_total = sum(categories.values())
            total_requirements += sheet_total
            print(f"\nSheet: {sheet_name} ({sheet_total} requirements)")
            for category, count in categories.items():
                print(f"  {category}: {count}")
        
        print(f"\nTotal requirements processed: {total_requirements}")
        
        # Step 5: Export results
        output_path = file_path.replace('.xlsx', '_classified.xlsx')
        classifier.export_results_to_excel(results, output_path)
        print(f"Results exported to: {output_path}")
    
    return results

if __name__ == "__main__":
    # Run the original test
    test_classifier()
    
    print("\n" + "="*80 + "\n")
    
    # Run the multi-sheet test
    test_multi_sheet_processing()
    
    # Example: Uncomment and modify the following line to test with a real file
    # process_rfp_file_example("/path/to/your/multi_sheet_rfp.xlsx")