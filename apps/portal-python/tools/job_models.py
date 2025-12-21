"""Job Data Models

Data models for job applications, adapted from AIHawk.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class Job:
    """Represents a job posting."""
    
    role: str
    company: str
    location: str = ""
    link: str = ""
    description: str = ""
    job_id: Optional[str] = None
    
    # Application method
    apply_method: str = ""  # e.g., "LinkedIn", "Company Website", "Email"
    
    # Additional details
    salary_range: str = ""
    experience_level: str = ""
    job_type: str = ""  # full_time, contract, part_time, etc.
    remote: bool = False
    
    # Tracking
    posted_date: Optional[str] = None
    found_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Generated materials
    resume_path: Optional[str] = None
    cover_letter_path: Optional[str] = None
    
    # AI analysis
    summary: str = ""
    match_score: Optional[float] = None
    key_requirements: List[str] = field(default_factory=list)
    
    # Recruiter info
    recruiter_name: str = ""
    recruiter_link: str = ""
    
    def formatted_job_information(self) -> str:
        """Format job information as markdown.
        
        Returns:
            Markdown formatted job description
        """
        info = f"""# {self.role} at {self.company}

## Job Information
- **Position**: {self.role}
- **Company**: {self.company}
- **Location**: {self.location or 'Not specified'}
- **Remote**: {'Yes' if self.remote else 'No'}
- **Job Type**: {self.job_type or 'Not specified'}
- **Experience Level**: {self.experience_level or 'Not specified'}
- **Salary Range**: {self.salary_range or 'Not specified'}
- **Application Method**: {self.apply_method or 'Not specified'}
- **Job Link**: {self.link or 'Not available'}
"""
        
        if self.recruiter_name or self.recruiter_link:
            info += f"\n## Recruiter\n"
            if self.recruiter_name:
                info += f"- **Name**: {self.recruiter_name}\n"
            if self.recruiter_link:
                info += f"- **Profile**: {self.recruiter_link}\n"
        
        if self.summary:
            info += f"\n## Summary\n{self.summary}\n"
        
        if self.key_requirements:
            info += f"\n## Key Requirements\n"
            for req in self.key_requirements:
                info += f"- {req}\n"
        
        info += f"\n## Full Description\n{self.description or 'No description provided.'}\n"
        
        if self.match_score is not None:
            info += f"\n## Match Score\n{self.match_score}/10\n"
        
        return info.strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        """Create Job from dictionary.
        
        Args:
            data: Dictionary with job data
            
        Returns:
            Job instance
        """
        return cls(**data)


@dataclass
class JobApplication:
    """Represents a job application."""
    
    job: Job
    
    # Application status
    status: str = "draft"  # draft, submitted, interviewing, rejected, accepted
    applied_date: Optional[str] = None
    
    # Application materials
    resume_path: Optional[str] = None
    cover_letter_path: Optional[str] = None
    
    # Application details
    application_data: Dict[str, Any] = field(default_factory=dict)
    
    # Tracking
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Follow-up
    follow_up_date: Optional[str] = None
    notes: str = ""
    
    # Interview tracking
    interviews: List[Dict[str, Any]] = field(default_factory=list)
    
    def update_status(self, new_status: str, notes: str = ""):
        """Update application status.
        
        Args:
            new_status: New status
            notes: Optional notes
        """
        self.status = new_status
        self.updated_at = datetime.now().isoformat()
        if notes:
            self.notes += f"\n[{self.updated_at}] {notes}"
        
        if new_status == "submitted" and not self.applied_date:
            self.applied_date = self.updated_at
    
    def add_interview(self, interview_type: str, date: str, 
                     interviewer: str = "", notes: str = ""):
        """Add an interview to the application.
        
        Args:
            interview_type: Type of interview (phone, video, onsite, etc.)
            date: Interview date/time
            interviewer: Interviewer name
            notes: Interview notes
        """
        interview = {
            "type": interview_type,
            "date": date,
            "interviewer": interviewer,
            "notes": notes,
            "added_at": datetime.now().isoformat()
        }
        self.interviews.append(interview)
        self.update_status("interviewing", f"Added {interview_type} interview")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        data = asdict(self)
        data['job'] = self.job.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobApplication':
        """Create JobApplication from dictionary.
        
        Args:
            data: Dictionary with application data
            
        Returns:
            JobApplication instance
        """
        job_data = data.pop('job')
        job = Job.from_dict(job_data)
        return cls(job=job, **data)


@dataclass
class JobSearchFilter:
    """Filter criteria for job search."""
    
    # Basic filters
    positions: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    remote: bool = True
    
    # Experience level
    experience_levels: Dict[str, bool] = field(default_factory=dict)
    
    # Job types
    job_types: Dict[str, bool] = field(default_factory=dict)
    
    # Date filter
    date_posted: str = "month"  # all_time, month, week, 24_hours
    
    # Distance (for location-based search)
    distance_miles: int = 50
    
    # Blacklists
    company_blacklist: List[str] = field(default_factory=list)
    title_blacklist: List[str] = field(default_factory=list)
    location_blacklist: List[str] = field(default_factory=list)
    
    # Salary requirements
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    
    def matches_job(self, job: Job) -> bool:
        """Check if a job matches the filter criteria.
        
        Args:
            job: Job to check
            
        Returns:
            True if job matches filter
        """
        # Check blacklists
        if job.company.lower() in [c.lower() for c in self.company_blacklist]:
            return False
        
        if any(blocked.lower() in job.role.lower() 
               for blocked in self.title_blacklist):
            return False
        
        if any(blocked.lower() in job.location.lower() 
               for blocked in self.location_blacklist):
            return False
        
        # Check remote requirement
        if self.remote and not job.remote:
            return False
        
        # Check job type
        if self.job_types and job.job_type:
            if not self.job_types.get(job.job_type, False):
                return False
        
        # Check experience level
        if self.experience_levels and job.experience_level:
            if not self.experience_levels.get(job.experience_level, False):
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return asdict(self)


# Helper functions
def create_job_from_linkedin(job_data: Dict[str, Any]) -> Job:
    """Create Job from LinkedIn job data.
    
    Args:
        job_data: Raw LinkedIn job data
        
    Returns:
        Job instance
    """
    return Job(
        role=job_data.get("title", ""),
        company=job_data.get("company", ""),
        location=job_data.get("location", ""),
        link=job_data.get("link", ""),
        description=job_data.get("description", ""),
        job_id=job_data.get("id", ""),
        apply_method="LinkedIn",
        remote=job_data.get("remote", False),
        job_type=job_data.get("employment_type", ""),
        experience_level=job_data.get("experience_level", ""),
        posted_date=job_data.get("posted_date", "")
    )


def create_job_from_indeed(job_data: Dict[str, Any]) -> Job:
    """Create Job from Indeed job data.
    
    Args:
        job_data: Raw Indeed job data
        
    Returns:
        Job instance
    """
    return Job(
        role=job_data.get("title", ""),
        company=job_data.get("company", ""),
        location=job_data.get("location", ""),
        link=job_data.get("url", ""),
        description=job_data.get("description", ""),
        job_id=job_data.get("job_key", ""),
        apply_method="Indeed",
        remote="remote" in job_data.get("location", "").lower(),
        job_type=job_data.get("job_type", ""),
        salary_range=job_data.get("salary", "")
    )
