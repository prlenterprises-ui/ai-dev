"""Unified Job and Resume Matching Service

Consolidates resume parsing and job matching capabilities:
- Parse resumes to extract skills and experience
- Calculate job-to-profile match scores
- Analyze resume-job compatibility
- Provide improvement recommendations
"""

import re
import json
import logging
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """User profile for job matching."""
    skills: List[str]
    experience_years: int
    desired_roles: List[str]
    locations: List[str]
    desired_salary_min: int = 0
    desired_salary_max: int = 999999
    education_level: str = ""
    full_name: str = ""
    email: str = ""


@dataclass
class MatchResult:
    """Result of job-profile matching."""
    overall_score: float
    skills_score: float
    experience_score: float
    role_score: float
    keyword_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    experience_level: str
    recommendations: List[str]


class MatchingService:
    """
    Unified service for resume parsing and job matching.
    
    Combines capabilities:
    - Resume parsing to extract skills, experience, roles
    - Job description analysis
    - Match scoring between jobs and profiles
    - Improvement recommendations
    """
    
    # Common tech skills for extraction
    TECH_SKILLS = {
        'python', 'java', 'javascript', 'typescript', 'go', 'rust', 'c++', 'c#',
        'react', 'angular', 'vue', 'node', 'django', 'flask', 'fastapi', 'spring',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible',
        'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
        'git', 'ci/cd', 'jenkins', 'github', 'gitlab', 'bitbucket',
        'agile', 'scrum', 'devops', 'microservices', 'rest', 'graphql',
        'machine learning', 'ai', 'data science', 'tensorflow', 'pytorch',
        'html', 'css', 'sass', 'webpack', 'vite', 'nextjs', 'express',
        'nginx', 'apache', 'linux', 'windows', 'macos', 'bash', 'powershell'
    }
    
    # Experience level keywords
    EXPERIENCE_LEVELS = {
        'entry': ['entry', 'junior', 'graduate', '0-2 years', 'early career', 'associate'],
        'mid': ['mid', 'intermediate', '2-5 years', '3-5 years', 'mid-level'],
        'senior': ['senior', 'lead', '5+ years', '5-8 years', 'experienced', 'sr'],
        'staff': ['staff', 'principal', 'architect', '8+ years', '10+ years'],
        'executive': ['director', 'vp', 'head of', 'chief', 'executive', 'manager']
    }
    
    # Scoring weights
    WEIGHTS = {
        'skills': 0.40,
        'experience': 0.25,
        'role': 0.20,
        'keywords': 0.15
    }
    
    def __init__(self):
        """Initialize the matching service."""
        self.logger = logger
    
    # ========================================================================
    # RESUME PARSING
    # ========================================================================
    
    def parse_resume(self, resume_text: str) -> UserProfile:
        """
        Parse a resume to extract user profile information.
        
        Args:
            resume_text: Full text of the resume
            
        Returns:
            UserProfile with extracted information
        """
        skills = self.extract_skills(resume_text)
        experience_years = self.extract_experience_years(resume_text)
        roles = self.extract_roles(resume_text)
        education = self.extract_education_level(resume_text)
        name, email = self.extract_contact_info(resume_text)
        
        return UserProfile(
            skills=skills,
            experience_years=experience_years,
            desired_roles=roles,
            locations=[],  # Could be extracted if needed
            education_level=education,
            full_name=name,
            email=email
        )
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract technical skills from text.
        
        Args:
            text: Resume or job description text
            
        Returns:
            List of identified skills
        """
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.TECH_SKILLS:
            # Match whole words or with boundaries
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        
        return sorted(list(set(found_skills)))
    
    def extract_experience_years(self, text: str) -> int:
        """
        Extract years of experience from resume text.
        
        Args:
            text: Resume text
            
        Returns:
            Estimated years of experience
        """
        # Look for explicit years statements
        patterns = [
            r'(\d+)\+?\s+years?\s+(?:of\s+)?experience',
            r'experience:\s*(\d+)\+?\s+years?',
            r'(\d+)\s+years?\s+(?:in|of)\s+(?:professional|work)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        # Fallback: count work history entries (rough estimate)
        work_entries = len(re.findall(r'\d{4}\s*[-–]\s*(?:\d{4}|present|current)', text, re.IGNORECASE))
        if work_entries > 0:
            return work_entries * 2  # Rough estimate: 2 years per entry
        
        return 0
    
    def extract_roles(self, text: str) -> List[str]:
        """
        Extract job roles/titles from resume.
        
        Args:
            text: Resume text
            
        Returns:
            List of job titles/roles
        """
        roles = []
        role_patterns = [
            r'(?:^|\n)([A-Z][A-Za-z\s]+(?:Engineer|Developer|Manager|Architect|Lead|Designer|Analyst))',
            r'(?:Title|Position|Role):\s*([A-Za-z\s]+)',
        ]
        
        for pattern in role_patterns:
            matches = re.findall(pattern, text)
            roles.extend([m.strip() for m in matches if len(m.strip()) > 5])
        
        return list(set(roles))[:5]  # Top 5 unique roles
    
    def extract_education_level(self, text: str) -> str:
        """
        Extract education level from resume.
        
        Args:
            text: Resume text
            
        Returns:
            Education level (bachelor's, master's, phd, etc.)
        """
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['ph.d', 'phd', 'doctorate', 'doctor of philosophy']):
            return "PhD"
        elif any(keyword in text_lower for keyword in ["master's", 'masters', 'm.s.', 'msc', 'mba']):
            return "Master's"
        elif any(keyword in text_lower for keyword in ["bachelor's", 'bachelors', 'b.s.', 'bsc', 'b.a.']):
            return "Bachelor's"
        elif any(keyword in text_lower for keyword in ['associate', 'a.s.', 'a.a.']):
            return "Associate"
        
        return "Unknown"
    
    def extract_contact_info(self, text: str) -> Tuple[str, str]:
        """
        Extract name and email from resume.
        
        Args:
            text: Resume text
            
        Returns:
            Tuple of (name, email)
        """
        # Email pattern
        email = ""
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            email = email_match.group(0)
        
        # Name (assume first line or first prominent text)
        name = ""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line) < 50 and not '@' in line:
                # Likely a name if it's short and doesn't contain email
                if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$', line):
                    name = line
                    break
        
        return name, email
    
    # ========================================================================
    # JOB MATCHING
    # ========================================================================
    
    def calculate_match(
        self, 
        job_description: str, 
        job_title: str,
        user_profile: UserProfile
    ) -> MatchResult:
        """
        Calculate comprehensive match score between job and profile.
        
        Args:
            job_description: Full job description text
            job_title: Job title
            user_profile: User's profile
            
        Returns:
            MatchResult with scores and recommendations
        """
        # Extract job requirements
        job_skills = self.extract_skills(job_description + " " + job_title)
        job_exp_level = self.extract_experience_level(job_description + " " + job_title)
        
        # Calculate component scores
        skills_score = self._calculate_skills_match(job_skills, user_profile.skills)
        experience_score = self._calculate_experience_match(job_exp_level, user_profile.experience_years)
        role_score = self._calculate_role_match(job_title, user_profile.desired_roles)
        keyword_score = self._calculate_keyword_density(job_description, user_profile.skills)
        
        # Overall weighted score
        overall_score = (
            skills_score * self.WEIGHTS['skills'] +
            experience_score * self.WEIGHTS['experience'] +
            role_score * self.WEIGHTS['role'] +
            keyword_score * self.WEIGHTS['keywords']
        )
        
        # Identify matched and missing skills
        user_skills_lower = [s.lower() for s in user_profile.skills]
        matched = list(set(job_skills) & set(user_skills_lower))
        missing = list(set(job_skills) - set(user_skills_lower))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            skills_score, experience_score, role_score, missing
        )
        
        return MatchResult(
            overall_score=round(overall_score, 1),
            skills_score=round(skills_score, 1),
            experience_score=round(experience_score, 1),
            role_score=round(role_score, 1),
            keyword_score=round(keyword_score, 1),
            matched_skills=matched,
            missing_skills=missing,
            experience_level=job_exp_level,
            recommendations=recommendations
        )
    
    def _calculate_skills_match(self, job_skills: List[str], user_skills: List[str]) -> float:
        """Calculate skills match percentage."""
        if not job_skills:
            return 100.0
        
        user_skills_lower = [s.lower() for s in user_skills]
        matched = len(set(job_skills) & set(user_skills_lower))
        
        return (matched / len(job_skills)) * 100
    
    def _calculate_experience_match(self, job_level: str, user_years: int) -> float:
        """Calculate experience match score."""
        level_years = {
            'entry': (0, 2),
            'mid': (2, 5),
            'senior': (5, 10),
            'staff': (10, 15),
            'executive': (15, 100)
        }
        
        min_years, max_years = level_years.get(job_level, (0, 100))
        
        if min_years <= user_years <= max_years:
            return 100.0
        elif user_years < min_years:
            # Under-qualified
            return max(0, 100 - (min_years - user_years) * 15)
        else:
            # Over-qualified (less penalty)
            return max(70, 100 - (user_years - max_years) * 5)
    
    def _calculate_role_match(self, job_title: str, desired_roles: List[str]) -> float:
        """Calculate role match score."""
        if not desired_roles:
            return 50.0  # Neutral if no preferences
        
        job_title_lower = job_title.lower()
        for role in desired_roles:
            role_lower = role.lower()
            # Check for significant word overlap
            job_words = set(job_title_lower.split())
            role_words = set(role_lower.split())
            overlap = len(job_words & role_words)
            
            if overlap >= 2 or role_lower in job_title_lower or job_title_lower in role_lower:
                return 100.0
        
        return 30.0  # Low match if no role overlap
    
    def _calculate_keyword_density(self, job_description: str, user_skills: List[str]) -> float:
        """Calculate keyword density score."""
        if not user_skills:
            return 0.0
        
        job_lower = job_description.lower()
        total_mentions = 0
        
        for skill in user_skills:
            skill_lower = skill.lower()
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            mentions = len(re.findall(pattern, job_lower))
            total_mentions += mentions
        
        # Normalize by length and number of skills
        density = (total_mentions / len(user_skills)) * 10
        return min(100.0, density)
    
    def extract_experience_level(self, text: str) -> str:
        """
        Extract experience level from job text.
        
        Args:
            text: Job description text
            
        Returns:
            Experience level (entry, mid, senior, staff, executive)
        """
        text_lower = text.lower()
        
        # Check for year patterns first (more specific)
        year_patterns = [
            (r'0[-\s]?2\s+years?', 'entry'),
            (r'[0-2]\+?\s+years?', 'entry'),
            (r'2[-\s]?5\s+years?', 'mid'),
            (r'3[-\s]?5\s+years?', 'mid'),
            (r'5\+?\s+years?', 'senior'),
            (r'5[-\s]?(?:8|10)\s+years?', 'senior'),
            (r'(?:8|10)\+?\s+years?', 'staff'),
            (r'10\+?\s+years?', 'staff'),
        ]
        
        for pattern, level in year_patterns:
            if re.search(pattern, text_lower):
                return level
        
        # Check for keyword patterns
        for level, keywords in self.EXPERIENCE_LEVELS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return level
        
        return 'mid'  # Default to mid-level
    
    def _generate_recommendations(
        self,
        skills_score: float,
        experience_score: float,
        role_score: float,
        missing_skills: List[str]
    ) -> List[str]:
        """Generate actionable recommendations based on match scores."""
        recommendations = []
        
        if skills_score < 70:
            if missing_skills:
                top_missing = missing_skills[:3]
                recommendations.append(
                    f"Consider highlighting or learning: {', '.join(top_missing)}"
                )
            else:
                recommendations.append(
                    "Emphasize your technical skills more prominently in your resume"
                )
        
        if experience_score < 70:
            recommendations.append(
                "Consider roles better aligned with your experience level"
            )
        
        if role_score < 50:
            recommendations.append(
                "This role may not align well with your desired positions"
            )
        
        if not recommendations:
            recommendations.append("Strong match! Consider applying.")
        
        return recommendations
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_match_summary(self, match_result: MatchResult) -> str:
        """Get human-readable summary of match result."""
        score = match_result.overall_score
        
        if score >= 80:
            rating = "Excellent"
        elif score >= 70:
            rating = "Good"
        elif score >= 50:
            rating = "Fair"
        else:
            rating = "Poor"
        
        summary = f"{rating} Match ({score}/100)\n"
        summary += f"Skills: {match_result.skills_score}/100\n"
        summary += f"Experience: {match_result.experience_score}/100\n"
        summary += f"Role: {match_result.role_score}/100\n"
        summary += f"\nMatched Skills: {', '.join(match_result.matched_skills[:5])}\n"
        
        if match_result.missing_skills:
            summary += f"Missing Skills: {', '.join(match_result.missing_skills[:5])}\n"
        
        if match_result.recommendations:
            summary += f"\nRecommendations:\n"
            for rec in match_result.recommendations:
                summary += f"  • {rec}\n"
        
        return summary
