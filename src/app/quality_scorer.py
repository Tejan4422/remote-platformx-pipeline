"""
RFP Response Quality Scoring System

This module evaluates the quality of generated RFP responses across multiple dimensions:
- Completeness: Does the response fully address the requirement?
- Clarity: Is the response clear and well-structured?
- Professionalism: Does it use appropriate business language?
- Relevance: How well does it match the requirement context?
"""

import re
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class QualityScore:
    """Represents the quality score for an RFP response"""
    overall_score: float  # 0-100
    completeness: float   # 0-100
    clarity: float       # 0-100
    professionalism: float  # 0-100
    relevance: float     # 0-100
    feedback: List[str]  # Specific improvement suggestions
    status: str          # "Excellent", "Good", "Needs Review", "Poor"


class RFPQualityScorer:
    """Evaluates the quality of RFP responses using multiple scoring algorithms"""
    
    def __init__(self):
        # Professional language indicators
        self.professional_phrases = {
            'positive': [
                'demonstrated experience', 'proven track record', 'comprehensive approach',
                'industry best practices', 'established methodology', 'quality assurance',
                'client satisfaction', 'measurable results', 'continuous improvement',
                'subject matter expertise', 'strategic partnership', 'value proposition'
            ],
            'negative': [
                'maybe', 'might', 'probably', 'i think', 'in my opinion',
                'not sure', 'could be', 'sort of', 'kind of'
            ]
        }
        
        # Clarity indicators
        self.clarity_patterns = {
            'good': [
                r'\b(first|second|third|finally)\b',  # Sequential indicators
                r'\b(however|therefore|furthermore|additionally)\b',  # Logical connectors
                r'\b(specifically|for example|such as)\b',  # Clarifying phrases
            ],
            'poor': [
                r'\b(uh|um|er)\b',  # Filler words
                r'\.{3,}',  # Multiple dots
                r'\b(thing|stuff|whatever)\b',  # Vague terms
            ]
        }
    
    def score_response(self, requirement: str, response: str) -> QualityScore:
        """
        Score a single RFP response across all quality dimensions
        
        Args:
            requirement: The original requirement text
            response: The generated response text
            
        Returns:
            QualityScore object with detailed scoring and feedback
        """
        if not response or not response.strip():
            return QualityScore(
                overall_score=0,
                completeness=0,
                clarity=0,
                professionalism=0,
                relevance=0,
                feedback=["Response is empty or missing"],
                status="Poor"
            )
        
        # Calculate individual scores
        completeness = self._score_completeness(requirement, response)
        clarity = self._score_clarity(response)
        professionalism = self._score_professionalism(response)
        relevance = self._score_relevance(requirement, response)
        
        # Calculate weighted overall score
        overall = (
            completeness * 0.3 +     # 30% weight on completeness
            clarity * 0.25 +         # 25% weight on clarity
            professionalism * 0.25 + # 25% weight on professionalism
            relevance * 0.2          # 20% weight on relevance
        )
        
        # Generate feedback
        feedback = self._generate_feedback(
            completeness, clarity, professionalism, relevance, response
        )
        
        # Determine status
        status = self._determine_status(overall)
        
        return QualityScore(
            overall_score=round(overall, 1),
            completeness=round(completeness, 1),
            clarity=round(clarity, 1),
            professionalism=round(professionalism, 1),
            relevance=round(relevance, 1),
            feedback=feedback,
            status=status
        )
    
    def _score_completeness(self, requirement: str, response: str) -> float:
        """Score how completely the response addresses the requirement"""
        if len(response.strip()) < 50:
            return 30.0  # Too short to be complete
        
        # Check for key elements
        score = 60.0  # Base score for having a response
        
        # Length appropriateness (responses should be substantial)
        req_words = len(requirement.split())
        resp_words = len(response.split())
        
        if resp_words >= req_words * 0.5:  # At least half as long as requirement
            score += 15.0
        
        if resp_words >= req_words:  # At least as long as requirement
            score += 10.0
        
        # Check for question addressing
        req_questions = len(re.findall(r'\?', requirement))
        if req_questions > 0:
            # Look for answers or acknowledgment of questions
            answer_indicators = len(re.findall(
                r'\b(yes|no|we will|we can|we provide|our approach|we have)\b', 
                response.lower()
            ))
            if answer_indicators >= req_questions:
                score += 15.0
        else:
            score += 15.0  # No questions to answer
        
        return min(score, 100.0)
    
    def _score_clarity(self, response: str) -> float:
        """Score the clarity and structure of the response"""
        score = 70.0  # Base score
        
        # Check for good structure indicators
        for pattern in self.clarity_patterns['good']:
            matches = len(re.findall(pattern, response.lower()))
            score += min(matches * 5, 15)  # Up to 15 points for good patterns
        
        # Penalize poor clarity indicators
        for pattern in self.clarity_patterns['poor']:
            matches = len(re.findall(pattern, response.lower()))
            score -= matches * 10
        
        # Check sentence structure
        sentences = response.split('.')
        avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])
        
        if 10 <= avg_sentence_length <= 25:  # Optimal sentence length
            score += 10
        elif avg_sentence_length > 40:  # Too long
            score -= 15
        
        # Check for bullet points or numbering (good structure)
        if re.search(r'^\s*[-•\d+]\s', response, re.MULTILINE):
            score += 10
        
        return max(min(score, 100.0), 0.0)
    
    def _score_professionalism(self, response: str) -> float:
        """Score the professional language and tone"""
        score = 70.0  # Base score
        
        # Positive professional language
        for phrase in self.professional_phrases['positive']:
            if phrase in response.lower():
                score += 3  # Up to significant bonus for professional terms
        
        # Negative unprofessional language
        for phrase in self.professional_phrases['negative']:
            if phrase in response.lower():
                score -= 10
        
        # Check for proper business writing
        if re.search(r'\b(I|we)\b', response):  # Uses first person appropriately
            score += 5
        
        # Check for passive voice overuse (should be balanced)
        passive_indicators = len(re.findall(r'\b(is|are|was|were)\s+\w+ed\b', response))
        total_words = len(response.split())
        if total_words > 0:
            passive_ratio = passive_indicators / total_words
            if passive_ratio > 0.3:  # Too much passive voice
                score -= 15
        
        # Check capitalization and basic formatting
        if response[0].isupper():  # Starts with capital
            score += 5
        
        return max(min(score, 100.0), 0.0)
    
    def _score_relevance(self, requirement: str, response: str) -> float:
        """Score how relevant the response is to the requirement"""
        # Simple keyword overlap scoring
        req_words = set(re.findall(r'\b\w+\b', requirement.lower()))
        resp_words = set(re.findall(r'\b\w+\b', response.lower()))
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        req_words = req_words - stop_words
        resp_words = resp_words - stop_words
        
        if not req_words:
            return 70.0  # Neutral score if no meaningful words in requirement
        
        # Calculate overlap
        overlap = len(req_words & resp_words)
        overlap_ratio = overlap / len(req_words)
        
        # Base score on overlap ratio
        base_score = 50 + (overlap_ratio * 50)
        
        # Bonus for addressing specific terms
        technical_terms = len([w for w in req_words if len(w) > 6])  # Longer words likely more specific
        addressed_technical = len([w for w in req_words & resp_words if len(w) > 6])
        
        if technical_terms > 0:
            technical_ratio = addressed_technical / technical_terms
            base_score += technical_ratio * 20
        
        return min(base_score, 100.0)
    
    def _generate_feedback(self, completeness: float, clarity: float, 
                          professionalism: float, relevance: float, response: str) -> List[str]:
        """Generate specific feedback for improving the response"""
        feedback = []
        
        if completeness < 70:
            feedback.append("Response seems incomplete. Consider providing more detailed information.")
        
        if clarity < 70:
            feedback.append("Response could be clearer. Try using bullet points or numbered lists.")
        
        if professionalism < 70:
            feedback.append("Consider using more professional business language.")
        
        if relevance < 70:
            feedback.append("Response doesn't fully address the requirement. Include more specific details.")
        
        if len(response.split()) < 30:
            feedback.append("Response is too brief. Provide more comprehensive information.")
        
        # Positive feedback for good scores
        if all(score >= 80 for score in [completeness, clarity, professionalism, relevance]):
            feedback.append("Excellent response! Ready for submission.")
        elif all(score >= 70 for score in [completeness, clarity, professionalism, relevance]):
            feedback.append("Good response with minor room for improvement.")
        
        return feedback if feedback else ["Response meets basic quality standards."]
    
    def _determine_status(self, overall_score: float) -> str:
        """Determine the overall status based on score"""
        if overall_score >= 85:
            return "Excellent"
        elif overall_score >= 75:
            return "Good"
        elif overall_score >= 60:
            return "Needs Review"
        else:
            return "Poor"
    
    def score_batch(self, requirements_responses: List[Tuple[str, str]]) -> List[QualityScore]:
        """Score a batch of requirement-response pairs"""
        return [
            self.score_response(req, resp) 
            for req, resp in requirements_responses
        ]
    
    def get_batch_summary(self, scores: List[QualityScore]) -> Dict:
        """Get summary statistics for a batch of scores"""
        if not scores:
            return {}
        
        overall_scores = [s.overall_score for s in scores]
        status_counts = {}
        for score in scores:
            status_counts[score.status] = status_counts.get(score.status, 0) + 1
        
        return {
            'total_responses': len(scores),
            'average_score': round(np.mean(overall_scores), 1),
            'min_score': min(overall_scores),
            'max_score': max(overall_scores),
            'status_distribution': status_counts,
            'excellent_count': status_counts.get('Excellent', 0),
            'good_count': status_counts.get('Good', 0),
            'needs_review_count': status_counts.get('Needs Review', 0),
            'poor_count': status_counts.get('Poor', 0),
        }