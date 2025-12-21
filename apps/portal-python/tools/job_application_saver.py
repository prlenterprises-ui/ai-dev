"""Job Application Saver Tool

Saves job application materials in a structured format.
Adapted from AIHawk's ApplicationSaver with improvements for our workflow.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class JobApplicationSaver:
    """Saves job applications with resume, cover letter, and job description."""
    
    def __init__(self, base_dir: Optional[str] = None):
        """Initialize the application saver.
        
        Args:
            base_dir: Base directory for saving applications
        """
        self.base_dir = base_dir or self._get_default_base_dir()
        Path(self.base_dir).mkdir(parents=True, exist_ok=True)
    
    def _get_default_base_dir(self) -> str:
        """Get the default base directory for applications."""
        return str(Path(__file__).parent.parent.parent.parent / 
                  "data" / "oppertunities" / "applications")
    
    def create_application_directory(self, company: str, role: str, 
                                    job_id: Optional[str] = None) -> Path:
        """Create a directory for a job application.
        
        Args:
            company: Company name
            role: Role title
            job_id: Optional job ID
            
        Returns:
            Path to the created directory
        """
        # Sanitize names for filesystem
        safe_company = self._sanitize_filename(company)
        safe_role = self._sanitize_filename(role)
        
        # Create directory name
        if job_id:
            dir_name = f"{job_id}_{safe_company}_{safe_role}"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dir_name = f"{safe_company}_{safe_role}_{timestamp}"
        
        dir_path = Path(self.base_dir) / safe_company / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        
        return dir_path
    
    def save_application(self, company: str, role: str, 
                        job_description: str,
                        resume_path: Optional[str] = None,
                        cover_letter_path: Optional[str] = None,
                        resume_content: Optional[str] = None,
                        cover_letter_content: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None,
                        job_id: Optional[str] = None) -> Path:
        """Save a complete job application.
        
        Args:
            company: Company name
            role: Role title
            job_description: Job description text
            resume_path: Path to resume file (PDF/DOCX)
            cover_letter_path: Path to cover letter file (PDF/DOCX)
            resume_content: Resume content as markdown/text
            cover_letter_content: Cover letter content as markdown/text
            metadata: Additional metadata to save
            job_id: Optional job ID
            
        Returns:
            Path to the application directory
        """
        # Create directory
        app_dir = self.create_application_directory(company, role, job_id)
        
        # Save job description
        job_desc_path = app_dir / "job_description.md"
        job_desc_path.write_text(f"# {role} at {company}\n\n{job_description}")
        
        # Save resume
        if resume_content:
            resume_md_path = app_dir / "resume.md"
            resume_md_path.write_text(resume_content)
        if resume_path and os.path.exists(resume_path):
            ext = Path(resume_path).suffix
            shutil.copy(resume_path, app_dir / f"resume{ext}")
        
        # Save cover letter
        if cover_letter_content:
            cover_letter_md_path = app_dir / "cover_letter.md"
            cover_letter_md_path.write_text(cover_letter_content)
        if cover_letter_path and os.path.exists(cover_letter_path):
            ext = Path(cover_letter_path).suffix
            shutil.copy(cover_letter_path, app_dir / f"cover_letter{ext}")
        
        # Save metadata
        app_metadata = {
            "company": company,
            "role": role,
            "job_id": job_id,
            "created_at": datetime.now().isoformat(),
            "files": {
                "job_description": "job_description.md",
                "resume_md": "resume.md" if resume_content else None,
                "cover_letter_md": "cover_letter.md" if cover_letter_content else None,
            }
        }
        
        if metadata:
            app_metadata.update(metadata)
        
        metadata_path = app_dir / "application_metadata.json"
        metadata_path.write_text(json.dumps(app_metadata, indent=2))
        
        print(f"✅ Application saved to: {app_dir}")
        return app_dir
    
    def save_job_details(self, job_details: Dict[str, Any], 
                        app_dir: Optional[Path] = None) -> Path:
        """Save detailed job information as JSON.
        
        Args:
            job_details: Dictionary with job details
            app_dir: Application directory (if None, creates new one)
            
        Returns:
            Path to the saved JSON file
        """
        if app_dir is None:
            company = job_details.get("company", "Unknown")
            role = job_details.get("role", "Unknown")
            app_dir = self.create_application_directory(company, role)
        
        job_json_path = app_dir / "job_details.json"
        job_json_path.write_text(json.dumps(job_details, indent=2))
        
        return job_json_path
    
    def save_application_response(self, app_dir: Path, 
                                  response_data: Dict[str, Any]):
        """Save application response/confirmation data.
        
        Args:
            app_dir: Application directory
            response_data: Response data from application submission
        """
        response_path = app_dir / "application_response.json"
        response_data["saved_at"] = datetime.now().isoformat()
        response_path.write_text(json.dumps(response_data, indent=2))
    
    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Sanitize a string for use in filenames.
        
        Args:
            name: String to sanitize
            
        Returns:
            Sanitized string safe for filesystem
        """
        # Replace spaces and special characters
        safe_name = name.replace(" ", "_")
        safe_name = "".join(c for c in safe_name if c.isalnum() or c in "_-")
        # Limit length
        return safe_name[:100]
    
    def list_applications(self, company: Optional[str] = None) -> list:
        """List all saved applications.
        
        Args:
            company: Optional company name to filter by
            
        Returns:
            List of application directories
        """
        base_path = Path(self.base_dir)
        
        if company:
            safe_company = self._sanitize_filename(company)
            company_path = base_path / safe_company
            if company_path.exists():
                return [d for d in company_path.iterdir() if d.is_dir()]
            return []
        
        # List all applications
        applications = []
        for company_dir in base_path.iterdir():
            if company_dir.is_dir():
                applications.extend([d for d in company_dir.iterdir() if d.is_dir()])
        
        return applications
    
    def get_application_summary(self, app_dir: Path) -> Dict[str, Any]:
        """Get a summary of an application.
        
        Args:
            app_dir: Application directory
            
        Returns:
            Dictionary with application summary
        """
        metadata_path = app_dir / "application_metadata.json"
        
        if metadata_path.exists():
            return json.loads(metadata_path.read_text())
        
        # Fallback: construct from directory name
        return {
            "directory": str(app_dir),
            "name": app_dir.name,
            "created_at": datetime.fromtimestamp(app_dir.stat().st_ctime).isoformat()
        }


# CLI interface
def main():
    """CLI interface for job application saver."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Save job application materials'
    )
    parser.add_argument('--company', required=True, help='Company name')
    parser.add_argument('--role', required=True, help='Role title')
    parser.add_argument('--job-desc', required=True, 
                       help='Path to job description file')
    parser.add_argument('--resume', help='Path to resume markdown file')
    parser.add_argument('--cover-letter', help='Path to cover letter markdown file')
    parser.add_argument('--resume-pdf', help='Path to resume PDF')
    parser.add_argument('--cover-letter-pdf', help='Path to cover letter PDF')
    parser.add_argument('--job-id', help='Job ID')
    parser.add_argument('--output-dir', help='Custom output directory')
    parser.add_argument('--list', action='store_true', 
                       help='List all applications')
    
    args = parser.parse_args()
    
    saver = JobApplicationSaver(args.output_dir)
    
    if args.list:
        apps = saver.list_applications()
        print(f"\n📁 Found {len(apps)} applications:\n")
        for app in apps:
            summary = saver.get_application_summary(app)
            print(f"  • {summary.get('company', 'Unknown')} - {summary.get('role', 'Unknown')}")
            print(f"    Created: {summary.get('created_at', 'Unknown')}")
            print(f"    Path: {app}\n")
        return
    
    # Load content
    job_desc = Path(args.job_desc).read_text() if args.job_desc else ""
    resume_content = Path(args.resume).read_text() if args.resume else None
    cover_letter_content = Path(args.cover_letter).read_text() if args.cover_letter else None
    
    # Save application
    app_dir = saver.save_application(
        company=args.company,
        role=args.role,
        job_description=job_desc,
        resume_path=args.resume_pdf,
        cover_letter_path=args.cover_letter_pdf,
        resume_content=resume_content,
        cover_letter_content=cover_letter_content,
        job_id=args.job_id
    )
    
    print(f"\n✅ Application saved successfully!")
    print(f"📂 Location: {app_dir}\n")


if __name__ == "__main__":
    main()
