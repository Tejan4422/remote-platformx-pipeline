#!/usr/bin/env python3
"""
Test Excel export with quality scores
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app.output_generator import OutputGenerator
from src.app.quality_scorer import RFPQualityScorer

def test_excel_with_quality():
    """Test Excel generation with quality scores"""
    
    # Create sample results with quality scores
    scorer = RFPQualityScorer()
    
    # Sample requirement-response pairs
    test_data = [
        {
            "requirement": "Describe your company's experience with cloud migration projects",
            "response": "Our company has demonstrated experience in cloud migration projects over the past 5 years. We have successfully migrated over 50 enterprise applications to AWS and Azure platforms. Our proven track record includes comprehensive approach to planning, execution, and post-migration support."
        },
        {
            "requirement": "What is your approach to data security?",
            "response": "We take security seriously and have good practices in place."
        }
    ]
    
    # Generate results with quality scores
    results = []
    for i, data in enumerate(test_data, 1):
        quality_score = scorer.score_response(data["requirement"], data["response"])
        
        result = {
            "requirement": data["requirement"],
            "response": data["response"],
            "status": "success",
            "quality_score": quality_score.overall_score,
            "quality_status": quality_score.status,
            "quality_breakdown": {
                "completeness": quality_score.completeness,
                "clarity": quality_score.clarity,
                "professionalism": quality_score.professionalism,
                "relevance": quality_score.relevance
            },
            "quality_feedback": quality_score.feedback
        }
        results.append(result)
    
    # Generate Excel file
    output_gen = OutputGenerator()
    excel_path = output_gen.generate_excel(results, "test_quality_scores.xlsx")
    
    print(f"✅ Excel file generated: {excel_path}")
    print(f"📊 The file now includes quality scoring columns:")
    print(f"   - Quality Score (0-100)")
    print(f"   - Quality Status (Excellent/Good/Needs Review/Poor)")
    print(f"   - Completeness, Clarity, Professionalism, Relevance scores")
    print(f"   - Quality Feedback suggestions")
    
    # Also test CSV
    csv_path = output_gen.generate_csv(results, "test_quality_scores.csv")
    print(f"✅ CSV file generated: {csv_path}")
    
    print(f"\n🎯 Client Value: Export files now show quality metrics for every response!")

if __name__ == "__main__":
    test_excel_with_quality()