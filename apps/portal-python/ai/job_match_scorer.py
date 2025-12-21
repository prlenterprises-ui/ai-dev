"""Job Match Scoring Service

DEPRECATED: Use ai.matching_service.MatchingService instead.
This module provides backward compatibility.

Calculates how well a job matches user profile and requirements.
"""

from typing import List, Dict
from ai.matching_service import (
    MatchingService,
    UserProfile as _UserProfile,
    MatchResult
)
from ai.user_profile_service import get_user_profile


# Re-export for backward compatibility
class UserProfile(_UserProfile):
    """User profile for job matching.
    
    DEPRECATED: Import from ai.matching_service instead.
    """
    pass


class JobMatchScorer:
    """Calculate match score between job and user profile.
    
    DEPRECATED: Use ai.matching_service.MatchingService instead.
    This class now wraps MatchingService for backward compatibility.
    """
    
    def __init__(self):
        self._service = MatchingService()
    
    @property
    def TECH_SKILLS(self):
        """Backward compatibility for TECH_SKILLS attribute."""
        return self._service.TECH_SKILLS
    
    @property
    def EXPERIENCE_LEVELS(self):
        """Backward compatibility for EXPERIENCE_LEVELS attribute."""
        return self._service.EXPERIENCE_LEVELS
    
    def calculate_match_score(self, job_description: str, job_title: str,
                             user_profile: UserProfile) -> Dict:
        """Calculate comprehensive match score.
        
        Args:
            job_description: Full job description text
            job_title: Job title
            user_profile: User's profile
            
        Returns:
            Dict with overall score and breakdown (legacy format)
        """
        # Use new MatchingService
        result = self._service.calculate_match(job_description, job_title, user_profile)
        
        # Convert to legacy format
        return {
            'overall_score': result.overall_score,
            'breakdown': {
                'skills_match': result.skills_score,
                'experience_match': result.experience_score,
                'role_match': result.role_score,
                'keyword_density': result.keyword_score
            },
            'details': {
                'matched_skills': result.matched_skills,
                'required_skills': self._service.extract_skills(job_description + " " + job_title),
                'experience_level': result.experience_level
            }
        }
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from job text.
        
        DEPRECATED: Use MatchingService.extract_skills instead.
        
        Args:
            text: Job description text
            
        Returns:
            List of identified skills
        """
        return self._service.extract_skills(text)
    
    def extract_experience_level(self, text: str) -> str:
        """Extract experience level from job text.
        
        DEPRECATED: Use MatchingService.extract_experience_level instead.
        
        Args:
            text: Job description text
            
        Returns:
            Experience level (entry, mid, senior, staff, executive)
        """
        return self._service.extract_experience_level(text)


# Legacy helper functions for backward compatibility
def get_default_user_profile():
    """Get default user profile from user_profile_service.
    
    DEPRECATED: Import directly from ai.user_profile_service.
    """
    return get_user_profile()
