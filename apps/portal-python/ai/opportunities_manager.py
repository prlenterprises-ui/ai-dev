"""
Opportunities Folder Manager
Manages job applications in the data/opportunities/ folder structure
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class OpportunitiesManager:
    """
    Manages job opportunities in the file-based folder structure:
    - 1_interested/
    - 2_qualified/
    - 3_applied/
    - 4_interviewing/
    - 5_offers/
    - 6_archived/
    """
    
    def __init__(self, base_path: str = "/workspaces/ai-dev/data/oppertunities"):
        self.base_path = Path(base_path)
        self.templates_path = self.base_path / "_templates"
        
        self.stages = {
            "interested": self.base_path / "1_interested",
            "qualified": self.base_path / "2_qualified",
            "applied": self.base_path / "3_applied",
            "interviewing": self.base_path / "4_interviewing",
            "offers": self.base_path / "5_offers",
            "archived": self.base_path / "6_archived"
        }
    
    def create_job_folder(
        self,
        company: str,
        role: str,
        stage: str = "qualified",
        job_url: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> Path:
        """
        Create a new job folder in the appropriate stage.
        
        Args:
            company: Company name
            role: Job role/title
            stage: One of: interested, qualified, applied, interviewing, offers, archived
            job_url: URL to the job posting
            job_description: Full job description text
            
        Returns:
            Path to created folder
        """
        if stage not in self.stages:
            raise ValueError(f"Invalid stage: {stage}. Must be one of: {list(self.stages.keys())}")
        
        # Create safe folder name
        safe_company = self._sanitize_name(company)
        safe_role = self._sanitize_name(role)
        folder_name = f"{safe_company} - {safe_role}"
        
        job_folder = self.stages[stage] / folder_name
        job_folder.mkdir(parents=True, exist_ok=True)
        
        # Create job.md with details
        self._create_job_file(job_folder, company, role, job_url, job_description)
        
        logger.info(f"Created job folder: {job_folder}")
        return job_folder
    
    def save_application_documents(
        self,
        company: str,
        role: str,
        resume_path: Optional[str] = None,
        cover_letter_path: Optional[str] = None,
        stage: str = "applied"
    ) -> Dict[str, Path]:
        """
        Save application documents to the job folder.
        
        Args:
            company: Company name
            role: Job role
            resume_path: Path to resume PDF
            cover_letter_path: Path to cover letter PDF
            stage: Stage to save in (default: applied)
            
        Returns:
            Dict with paths to saved documents
        """
        job_folder = self._get_or_create_job_folder(company, role, stage)
        
        saved_paths = {}
        
        # Copy resume
        if resume_path and os.path.exists(resume_path):
            dest_resume = job_folder / "resume.pdf"
            shutil.copy2(resume_path, dest_resume)
            saved_paths["resume"] = dest_resume
            logger.info(f"Saved resume to {dest_resume}")
        
        # Copy cover letter
        if cover_letter_path and os.path.exists(cover_letter_path):
            dest_cover = job_folder / "cover_letter.pdf"
            shutil.copy2(cover_letter_path, dest_cover)
            saved_paths["cover_letter"] = dest_cover
            logger.info(f"Saved cover letter to {dest_cover}")
        
        return saved_paths
    
    def create_application_log(
        self,
        company: str,
        role: str,
        applied_date: Optional[str] = None,
        confirmation_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Path:
        """
        Create application log from template.
        
        Args:
            company: Company name
            role: Job role
            applied_date: Date applied (defaults to today)
            confirmation_id: Application confirmation ID
            notes: Additional notes
            
        Returns:
            Path to created application log
        """
        job_folder = self._get_or_create_job_folder(company, role, "applied")
        
        # Read template
        template_path = self.templates_path / "application_log_template.md"
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Fill in template
        applied_date = applied_date or datetime.now().strftime("%Y-%m-%d")
        log_content = template.replace("{Company}", company).replace("{Role}", role)
        log_content = log_content.replace("YYYY-MM-DD", applied_date, 1)  # Only first occurrence
        
        if confirmation_id:
            log_content = log_content.replace("**Confirmation ID** | |", f"**Confirmation ID** | {confirmation_id} |")
        
        if notes:
            log_content += f"\n\n### Additional Notes\n\n{notes}\n"
        
        # Save log
        log_path = job_folder / "application_log.md"
        with open(log_path, 'w') as f:
            f.write(log_content)
        
        logger.info(f"Created application log: {log_path}")
        return log_path
    
    def move_job_stage(
        self,
        company: str,
        role: str,
        from_stage: str,
        to_stage: str
    ) -> Optional[Path]:
        """
        Move a job folder from one stage to another.
        
        Args:
            company: Company name
            role: Job role
            from_stage: Current stage
            to_stage: Target stage
            
        Returns:
            New path if successful, None if not found
        """
        if from_stage not in self.stages or to_stage not in self.stages:
            raise ValueError(f"Invalid stage")
        
        safe_company = self._sanitize_name(company)
        safe_role = self._sanitize_name(role)
        folder_name = f"{safe_company} - {safe_role}"
        
        old_path = self.stages[from_stage] / folder_name
        new_path = self.stages[to_stage] / folder_name
        
        if old_path.exists():
            shutil.move(str(old_path), str(new_path))
            logger.info(f"Moved job from {from_stage} to {to_stage}: {folder_name}")
            return new_path
        else:
            logger.warning(f"Job folder not found: {old_path}")
            return None
    
    def update_tracker(self):
        """
        Update the _tracker.md file with current counts.
        This could be enhanced to automatically scan folders and update counts.
        """
        # Count jobs in each stage
        counts = {}
        for stage_name, stage_path in self.stages.items():
            if stage_path.exists():
                counts[stage_name] = len([d for d in stage_path.iterdir() if d.is_dir() and not d.name.startswith('.')])
            else:
                counts[stage_name] = 0
        
        logger.info(f"Stage counts: {counts}")
        return counts
    
    def _get_or_create_job_folder(self, company: str, role: str, stage: str) -> Path:
        """Get existing job folder or create new one."""
        safe_company = self._sanitize_name(company)
        safe_role = self._sanitize_name(role)
        folder_name = f"{safe_company} - {safe_role}"
        
        job_folder = self.stages[stage] / folder_name
        
        if not job_folder.exists():
            return self.create_job_folder(company, role, stage)
        
        return job_folder
    
    def _create_job_file(
        self,
        job_folder: Path,
        company: str,
        role: str,
        job_url: Optional[str],
        job_description: Optional[str]
    ):
        """Create job.md file with details."""
        job_md = f"""# {role} at {company}

## Job Details

**Company:** {company}
**Role:** {role}
**Posted:** {datetime.now().strftime("%Y-%m-%d")}
**Status:** Active
"""
        
        if job_url:
            job_md += f"**Job URL:** {job_url}\n"
        
        job_md += "\n---\n\n## Job Description\n\n"
        
        if job_description:
            job_md += f"{job_description}\n"
        else:
            job_md += "_Add job description here_\n"
        
        job_md += "\n---\n\n## Match Analysis\n\n_To be filled in_\n\n"
        job_md += "## Application Strategy\n\n_To be filled in_\n"
        
        job_file = job_folder / "job.md"
        with open(job_file, 'w') as f:
            f.write(job_md)
    
    def _sanitize_name(self, name: str) -> str:
        """Convert name to safe folder name."""
        # Remove/replace invalid characters
        safe = name.replace('/', '-').replace('\\', '-').replace(':', '-')
        safe = ''.join(c for c in safe if c.isalnum() or c in ' -_')
        return safe.strip()
