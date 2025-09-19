#!/usr/bin/env python3
"""
Quick test for the new Quality Scoring feature
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app.quality_scorer import RFPQualityScorer

def test_quality_scoring():
    """Test the quality scoring system"""
    scorer = RFPQualityScorer()
    
    # Test cases
    test_cases = [
        {
            "requirement": "Describe your company's experience with cloud migration projects",
            "response": "Our company has demonstrated experience in cloud migration projects over the past 5 years. We have successfully migrated over 50 enterprise applications to AWS and Azure platforms. Our proven track record includes comprehensive approach to planning, execution, and post-migration support. We follow industry best practices and maintain quality assurance throughout the process.",
            "expected_status": "Excellent"
        },
        {
            "requirement": "What is your approach to data security?",
            "response": "We take security seriously and have good practices in place.",
            "expected_status": "Needs Review"
        },
        {
            "requirement": "Provide details about your project management methodology",
            "response": "",
            "expected_status": "Poor"
        }
    ]
    
    print("🧪 Testing RFP Quality Scoring System\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(f"Requirement: {test['requirement']}")
        print(f"Response: {test['response']}")
        
        score = scorer.score_response(test['requirement'], test['response'])
        
        print(f"Overall Score: {score.overall_score}/100")
        print(f"Status: {score.status}")
        print(f"Breakdown:")
        print(f"  - Completeness: {score.completeness}")
        print(f"  - Clarity: {score.clarity}")
        print(f"  - Professionalism: {score.professionalism}")
        print(f"  - Relevance: {score.relevance}")
        print(f"Feedback: {', '.join(score.feedback)}")
        
        # Check if result matches expectation
        status_match = "✅" if score.status == test['expected_status'] else "❌"
        print(f"Expected: {test['expected_status']} | Got: {score.status} {status_match}")
        print("-" * 80)
        print()

    # Test batch processing
    print("🔥 Testing Batch Processing:")
    batch_data = [(test['requirement'], test['response']) for test in test_cases]
    batch_scores = scorer.score_batch(batch_data)
    batch_summary = scorer.get_batch_summary(batch_scores)
    
    print(f"Batch Summary:")
    print(f"  Total Responses: {batch_summary['total_responses']}")
    print(f"  Average Score: {batch_summary['average_score']}")
    print(f"  Status Distribution: {batch_summary['status_distribution']}")
    print(f"  Excellent: {batch_summary['excellent_count']}")
    print(f"  Good: {batch_summary['good_count']}")
    print(f"  Needs Review: {batch_summary['needs_review_count']}")
    print(f"  Poor: {batch_summary['poor_count']}")

if __name__ == "__main__":
    test_quality_scoring()