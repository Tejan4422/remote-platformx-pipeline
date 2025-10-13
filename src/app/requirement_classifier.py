import requests
import json
import re
from typing import List, Optional

class RequirementClassifier:
    """Classifies requirements into predefined categories using LLM"""
    
    # Predefined categories
    CATEGORIES = [
        "Tech",
        "Security", 
        "Compliance",
        "Functional",
        "Non-Functional",
        "BI Tool"
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

IMPORTANT RULES:
1. Respond with ONLY the category name - nothing else
2. The response must be exactly one of: Tech, Security, Compliance, Functional, Non-Functional, BI Tool
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

if __name__ == "__main__":
    test_classifier()