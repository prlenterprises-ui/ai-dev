"""Auto-Match Workflow - Automatically generate resumes for high-scoring jobs

This service combines job matching and resume generation:
1. Match jobs against user profile
2. When match score is high (70+), automatically generate tailored resume
3. Save resume and track the opportunity
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import asyncio

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.matching_service import MatchingService, UserProfile, MatchResult
from ai.user_profile_service import get_user_profile
from tools.resume_generator import ResumeGenerator


class AutoMatchWorkflow:
    """
    Automatically generate tailored resumes for jobs that match well.
    
    Workflow:
    1. Score job against user profile
    2. If score >= threshold, automatically generate resume
    3. Save resume to outputs directory
    4. Track opportunity in data folder
    """
    
    def __init__(self, 
                 match_threshold: float = 70.0,
                 auto_generate: bool = True,
                 outputs_dir: Optional[str] = None):
        """
        Initialize the auto-match workflow.
        
        Args:
            match_threshold: Minimum match score to trigger resume generation (default: 70)
            auto_generate: Whether to automatically generate resumes (default: True)
            outputs_dir: Directory to save generated resumes
        """
        self.match_threshold = match_threshold
        self.auto_generate = auto_generate
        self.matching_service = MatchingService()
        self.resume_generator = ResumeGenerator()
        
        # Setup output directory
        if outputs_dir:
            self.outputs_dir = Path(outputs_dir)
        else:
            self.outputs_dir = Path(__file__).parent.parent / "outputs" / "auto_matched"
        
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
    
    async def process_job(
        self,
        job_description: str,
        job_title: str,
        company_name: str,
        user_profile: Optional[UserProfile] = None,
        job_url: Optional[str] = None
    ) -> Dict:
        """
        Process a job posting - match and optionally generate resume.
        
        Args:
            job_description: Full job description text
            job_title: Job title
            company_name: Company name
            user_profile: User profile (uses default if not provided)
            job_url: Optional URL to the job posting
            
        Returns:
            Dict with match result and resume info (if generated)
        """
        # Get user profile
        if user_profile is None:
            user_profile = get_user_profile()
        
        # Calculate match score
        print(f"\n🎯 Analyzing: {job_title} at {company_name}")
        match_result = self.matching_service.calculate_match(
            job_description, job_title, user_profile
        )
        
        print(f"   Match Score: {match_result.overall_score}/100")
        
        # Prepare result
        result = {
            "job_title": job_title,
            "company_name": company_name,
            "job_url": job_url,
            "match_score": match_result.overall_score,
            "match_details": {
                "skills_score": match_result.skills_score,
                "experience_score": match_result.experience_score,
                "role_score": match_result.role_score,
                "keyword_score": match_result.keyword_score,
                "matched_skills": match_result.matched_skills,
                "missing_skills": match_result.missing_skills,
                "recommendations": match_result.recommendations
            },
            "resume_generated": False,
            "resume_path": None
        }
        
        # Check if match is good enough
        if match_result.overall_score >= self.match_threshold:
            print(f"   ✅ Excellent match! (>= {self.match_threshold})")
            
            if self.auto_generate:
                print("   📄 Generating tailored resume...")
                resume_path = await self._generate_and_save_resume(
                    job_description, job_title, company_name, match_result
                )
                result["resume_generated"] = True
                result["resume_path"] = str(resume_path)
                print(f"   ✅ Resume saved: {resume_path.name}")
            else:
                print("   💡 Auto-generation disabled. Resume not created.")
        else:
            print(f"   ⚠️  Match score below threshold ({self.match_threshold})")
            print(f"   💡 Recommendations:")
            for rec in match_result.recommendations[:3]:
                print(f"      • {rec}")
        
        return result
    
    async def _generate_and_save_resume(
        self,
        job_description: str,
        job_title: str,
        company_name: str,
        match_result: MatchResult
    ) -> Path:
        """Generate tailored resume and save to file."""
        
        # Generate resume using LLM Council
        resume_content = await self.resume_generator.generate_resume(
            job_description, company_name, job_title
        )
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_company = company_name.replace(" ", "_").replace("/", "-")[:30]
        safe_title = job_title.replace(" ", "_").replace("/", "-")[:30]
        filename = f"{timestamp}_{safe_company}_{safe_title}_resume.md"
        
        resume_path = self.outputs_dir / filename
        
        # Save resume with metadata
        metadata = f"""---
Generated: {datetime.now().isoformat()}
Company: {company_name}
Role: {job_title}
Match Score: {match_result.overall_score}/100
Skills Match: {match_result.skills_score}/100
Experience Match: {match_result.experience_score}/100
Matched Skills: {', '.join(match_result.matched_skills[:10])}
---

"""
        
        with open(resume_path, 'w') as f:
            f.write(metadata)
            f.write(resume_content)
        
        return resume_path
    
    async def process_multiple_jobs(
        self,
        jobs: List[Dict],
        user_profile: Optional[UserProfile] = None
    ) -> List[Dict]:
        """
        Process multiple jobs and generate resumes for good matches.
        
        Args:
            jobs: List of job dicts with keys: job_description, job_title, company_name, job_url
            user_profile: User profile (uses default if not provided)
            
        Returns:
            List of results for each job
        """
        print(f"\n{'='*70}")
        print(f"🚀 Auto-Match Workflow: Processing {len(jobs)} jobs")
        print(f"   Match Threshold: {self.match_threshold}/100")
        print(f"   Auto-Generate: {'Enabled' if self.auto_generate else 'Disabled'}")
        print(f"{'='*70}")
        
        results = []
        
        for i, job in enumerate(jobs, 1):
            print(f"\n[{i}/{len(jobs)}] Processing...")
            
            result = await self.process_job(
                job_description=job.get("job_description", ""),
                job_title=job.get("job_title", "Unknown Role"),
                company_name=job.get("company_name", "Unknown Company"),
                user_profile=user_profile,
                job_url=job.get("job_url")
            )
            
            results.append(result)
        
        # Summary
        print(f"\n{'='*70}")
        print("📊 Summary")
        print(f"{'='*70}")
        
        good_matches = [r for r in results if r["match_score"] >= self.match_threshold]
        resumes_generated = [r for r in results if r["resume_generated"]]
        
        print(f"Total Jobs: {len(results)}")
        print(f"Good Matches (>= {self.match_threshold}): {len(good_matches)}")
        print(f"Resumes Generated: {len(resumes_generated)}")
        
        if resumes_generated:
            print(f"\n✅ Generated Resumes:")
            for r in resumes_generated:
                print(f"   • {r['company_name']} - {r['job_title']} ({r['match_score']}/100)")
        
        print(f"{'='*70}\n")
        
        return results
    
    def get_match_summary(self, match_result: MatchResult) -> str:
        """Get human-readable match summary."""
        return self.matching_service.get_match_summary(match_result)


async def demo():
    """Demo the auto-match workflow."""
    
    workflow = AutoMatchWorkflow(
        match_threshold=70.0,
        auto_generate=True  # Set to False to just score without generating
    )
    
    # Sample jobs
    jobs = [
        {
            "job_title": "Senior Python Developer",
            "company_name": "TechCorp",
            "job_description": """
            Senior Python Developer needed with 5+ years experience.
            
            Requirements:
            - Expert in Python, FastAPI, Django
            - AWS, Docker, Kubernetes experience
            - PostgreSQL and REST APIs
            - Strong problem-solving skills
            
            Responsibilities:
            - Build scalable backend services
            - Design REST APIs
            - Mentor junior developers
            """,
            "job_url": "https://example.com/job/12345"
        },
        {
            "job_title": "Java Developer",
            "company_name": "Enterprise Inc",
            "job_description": """
            Senior Java Developer with Spring Boot experience.
            
            Requirements:
            - 8+ years Java development
            - Spring Boot, Microservices
            - AWS experience helpful
            - SQL databases
            """,
            "job_url": "https://example.com/job/67890"
        },
        {
            "job_title": "Full Stack Engineer",
            "company_name": "StartupXYZ",
            "job_description": """
            Full Stack Engineer to join our growing team.
            
            Requirements:
            - Python and JavaScript/React
            - 3-5 years experience
            - Docker, Git, REST APIs
            - AWS or cloud experience
            
            Bonus:
            - FastAPI or Django knowledge
            - DevOps experience
            """,
            "job_url": "https://example.com/job/11111"
        }
    ]
    
    # Process all jobs
    results = await workflow.process_multiple_jobs(jobs)
    
    return results


if __name__ == "__main__":
    print("🤖 Auto-Match Workflow Demo\n")
    results = asyncio.run(demo())
