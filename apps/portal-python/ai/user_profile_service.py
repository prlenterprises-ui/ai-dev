"""User Profile Service

Manages user profile for job matching and customization.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class UserProfile:
    """User profile for job matching."""
    # Skills
    skills: List[str]
    
    # Experience
    experience_years: int
    desired_roles: List[str]
    
    # Location preferences
    locations: List[str]
    remote_ok: bool = True
    
    # Compensation
    desired_salary_min: int = 0
    desired_salary_max: int = 999999
    
    # Education
    education_level: str = "Bachelor"
    
    # Personal info (for resume generation)
    full_name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""
    
    # Job search preferences
    job_types: List[str] = None  # full-time, part-time, contract
    company_sizes: List[str] = None  # startup, small, medium, large, enterprise
    industries: List[str] = None
    
    def __post_init__(self):
        if self.job_types is None:
            self.job_types = ['full-time']
        if self.company_sizes is None:
            self.company_sizes = []
        if self.industries is None:
            self.industries = []


class UserProfileService:
    """Service for managing user profile."""
    
    def __init__(self, profile_path: Optional[str] = None):
        """Initialize user profile service.
        
        Args:
            profile_path: Path to user profile JSON file
        """
        if profile_path is None:
            # Default to workspace data folder
            profile_path = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', '..', 
                'data', 
                'user_profile.json'
            )
        
        self.profile_path = Path(profile_path).resolve()
        self._profile: Optional[UserProfile] = None
    
    def load_profile(self) -> UserProfile:
        """Load user profile from file.
        
        Returns:
            UserProfile instance
        """
        if not self.profile_path.exists():
            # Create default profile
            profile = self._create_default_profile()
            self.save_profile(profile)
            return profile
        
        try:
            with open(self.profile_path, 'r') as f:
                data = json.load(f)
            
            self._profile = UserProfile(**data)
            return self._profile
        
        except Exception as e:
            print(f"Error loading profile: {e}. Using default.")
            return self._create_default_profile()
    
    def save_profile(self, profile: UserProfile):
        """Save user profile to file.
        
        Args:
            profile: UserProfile to save
        """
        # Ensure directory exists
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        with open(self.profile_path, 'w') as f:
            json.dump(asdict(profile), f, indent=2)
        
        self._profile = profile
        print(f"Profile saved to {self.profile_path}")
    
    def get_profile(self) -> UserProfile:
        """Get current user profile (cached).
        
        Returns:
            UserProfile instance
        """
        if self._profile is None:
            self._profile = self.load_profile()
        return self._profile
    
    def update_profile(self, **kwargs) -> UserProfile:
        """Update specific profile fields.
        
        Args:
            **kwargs: Fields to update
            
        Returns:
            Updated UserProfile
        """
        profile = self.get_profile()
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        # Save
        self.save_profile(profile)
        
        return profile
    
    def _create_default_profile(self) -> UserProfile:
        """Create default user profile.
        
        Returns:
            Default UserProfile
        """
        return UserProfile(
            skills=[
                'Python', 'JavaScript', 'React', 'Node.js', 
                'Docker', 'AWS', 'PostgreSQL', 'FastAPI', 
                'Git', 'REST API'
            ],
            experience_years=5,
            desired_roles=[
                'Software Engineer',
                'Backend Engineer',
                'Full Stack Developer',
                'Python Developer',
                'Senior Developer'
            ],
            locations=['Remote', 'San Francisco', 'New York'],
            remote_ok=True,
            desired_salary_min=120000,
            desired_salary_max=200000,
            education_level='Bachelor',
            full_name='Your Name',
            email='your.email@example.com',
            phone='555-0100',
            linkedin='https://linkedin.com/in/yourprofile',
            github='https://github.com/yourusername',
            website='https://yourwebsite.com',
            job_types=['full-time'],
            company_sizes=['startup', 'medium', 'large'],
            industries=['Technology', 'Software', 'AI/ML']
        )


# Global instance
_profile_service = None


def get_profile_service() -> UserProfileService:
    """Get global user profile service instance.
    
    Returns:
        UserProfileService instance
    """
    global _profile_service
    if _profile_service is None:
        _profile_service = UserProfileService()
    return _profile_service


def get_user_profile() -> UserProfile:
    """Get user profile (convenience function).
    
    Returns:
        UserProfile instance
    """
    return get_profile_service().get_profile()
