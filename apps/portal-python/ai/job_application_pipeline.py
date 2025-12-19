"""
Automated Job Application Service
Orchestrates the full pipeline: search → analyze → tailor → apply
"""

import asyncio
import uuid
from typing import List, Dict, Optional, AsyncIterator
from datetime import datetime
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from python.database import JobApplication
from ai.job_search_service import JobSearchService, JobSearchResult
from ai.jobbernaut_service import JobbernautService
from ai.llm_clients import get_openrouter_client
from ai.opportunities_manager import OpportunitiesManager

logger = logging.getLogger(__name__)


class JobApplicationPipeline:
    """
    Automated job application pipeline.
    
    Pipeline:
    1. Search for jobs matching keywords
    2. For each job:
       a. Analyze job requirements
       b. Generate tailored resume & cover letter (using Jobbernaut)
       c. Save documents
       d. Track application status
       e. (Optional) Auto-apply if submission endpoint available
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_search = JobSearchService()
        self.jobbernaut = JobbernautService()
        self.opportunities = OpportunitiesManager()
        self.llm_client = None  # Will be initialized when needed
        
    async def run_pipeline(
        self,
        keywords: str,
        location: Optional[str] = None,
        max_applications: int = 10,
        auto_apply: bool = False
    ) -> AsyncIterator[Dict]:
        """
        Run the full automated job application pipeline.
        
        Args:
            keywords: Job search keywords
            location: Optional location filter
            max_applications: Maximum number of applications to generate
            auto_apply: Whether to automatically submit applications (requires external service)
            
        Yields:
            Progress updates as dict with status and data
        """
        yield {
            "stage": "search",
            "status": "started",
            "message": f"Searching for jobs matching '{keywords}'..."
        }
        
        # Step 1: Search for jobs
        try:
            jobs = await self.job_search.search_jobs(
                keywords=keywords,
                location=location,
                limit=max_applications * 2  # Get extra to filter
            )
            
            yield {
                "stage": "search",
                "status": "completed",
                "message": f"Found {len(jobs)} jobs",
                "data": {"job_count": len(jobs)}
            }
        except Exception as e:
            logger.error(f"Job search failed: {e}")
            yield {
                "stage": "search",
                "status": "failed",
                "error": str(e)
            }
            return
        
        if not jobs:
            yield {
                "stage": "pipeline",
                "status": "completed",
                "message": "No jobs found matching criteria"
            }
            return
        
        # Step 2: Filter and rank jobs
        yield {
            "stage": "filter",
            "status": "started",
            "message": "Analyzing and ranking jobs..."
        }
        
        ranked_jobs = await self._rank_jobs(jobs, keywords)
        selected_jobs = ranked_jobs[:max_applications]
        
        yield {
            "stage": "filter",
            "status": "completed",
            "message": f"Selected top {len(selected_jobs)} jobs for application",
            "data": {"selected_count": len(selected_jobs)}
        }
        
        # Step 3: Process each job
        applied_count = 0
        for idx, job in enumerate(selected_jobs, 1):
            yield {
                "stage": "processing",
                "status": "started",
                "message": f"Processing job {idx}/{len(selected_jobs)}: {job.title} at {job.company}",
                "data": {
                    "job_index": idx,
                    "job_title": job.title,
                    "company": job.company
                }
            }
            
            try:
                # Create job application record
                job_app = await self._create_job_application(job)
                
                yield {
                    "stage": "generating",
                    "status": "started",
                    "message": f"Generating tailored resume and cover letter...",
                    "data": {"job_id": job_app.id}
                }
                
                # Generate tailored documents using Jobbernaut
                documents = await self._generate_documents(job, job_app.id)
                
                # Create opportunity folder in data/opportunities/
                try:
                    folder_path = self.opportunities.create_job_folder(
                        company=job.company,
                        role=job.title,
                        stage="qualified",  # Start as qualified since we have generated docs
                        job_url=job.url,
                        job_description=job.description
                    )
                    
                    # Copy documents to opportunity folder
                    if documents.get("resume_path"):
                        self.opportunities.save_documents(
                            str(folder_path),
                            resume_path=documents["resume_path"],
                            cover_letter_path=documents.get("cover_letter_path")
                        )
                    
                    logger.info(f"Created opportunity folder: {folder_path}")
                    
                except Exception as e:
                    logger.warning(f"Failed to create opportunity folder: {e}")
                
                # Update job application with documents
                job_app.resume_url = documents.get("resume_path")
                job_app.cover_letter_url = documents.get("cover_letter_path")
                job_app.match_score = documents.get("match_score", 0.0)
                job_app.status = "completed"
                job_app.updated_at = datetime.now()
                
                self.db.add(job_app)
                await self.db.commit()
                await self.db.refresh(job_app)
                
                applied_count += 1
                
                yield {
                    "stage": "generated",
                    "status": "completed",
                    "message": f"✓ Generated documents for {job.title} at {job.company}",
                    "data": {
                        "job_id": job_app.id,
                        "resume_path": documents.get("resume_path"),
                        "cover_letter_path": documents.get("cover_letter_path"),
                        "match_score": documents.get("match_score")
                    }
                }
                
                # Optional: Auto-apply
                if auto_apply and job.url:
                    yield {
                        "stage": "applying",
                        "status": "started",
                        "message": f"Attempting to submit application...",
                        "data": {"job_url": job.url}
                    }
                    
                    # TODO: Implement actual application submission
                    # This would require integration with job board APIs or browser automation
                    yield {
                        "stage": "applying",
                        "status": "skipped",
                        "message": "Auto-apply not yet implemented. Please apply manually using generated documents.",
                        "data": {"job_url": job.url}
                    }
                
            except Exception as e:
                logger.error(f"Failed to process job {job.title}: {e}")
                yield {
                    "stage": "processing",
                    "status": "failed",
                    "message": f"✗ Failed to process {job.title}",
                    "error": str(e)
                }
                
                # Mark job as failed
                if 'job_app' in locals():
                    job_app.status = "failed"
                    job_app.notes = f"Error: {str(e)}"
                    job_app.updated_at = datetime.now()
                    self.db.add(job_app)
                    await self.db.commit()
        
        # Final summary
        yield {
            "stage": "pipeline",
            "status": "completed",
            "message": f"Pipeline completed: {applied_count}/{len(selected_jobs)} applications generated successfully",
            "data": {
                "total_jobs_found": len(jobs),
                "selected": len(selected_jobs),
                "completed": applied_count,
                "failed": len(selected_jobs) - applied_count
            }
        }
    
    async def _rank_jobs(self, jobs: List[JobSearchResult], keywords: str) -> List[JobSearchResult]:
        """
        Rank jobs by relevance to keywords and freshness.
        Simple scoring for now - can be enhanced with LLM analysis.
        """
        def score_job(job: JobSearchResult) -> float:
            score = 0.0
            
            # Keyword matching in title (highest weight)
            title_lower = job.title.lower()
            for keyword in keywords.lower().split():
                if keyword in title_lower:
                    score += 10.0
            
            # Keyword matching in description
            desc_lower = job.description.lower()
            for keyword in keywords.lower().split():
                if keyword in desc_lower:
                    score += 2.0
            
            # Recency bonus (newer jobs ranked higher)
            try:
                posted_date = datetime.fromisoformat(job.posted_date.replace('Z', '+00:00'))
                days_old = (datetime.now(posted_date.tzinfo) - posted_date).days
                recency_score = max(0, 10 - days_old)  # Bonus for jobs < 10 days old
                score += recency_score
            except:
                pass
            
            return score
        
        # Sort by score descending
        sorted_jobs = sorted(jobs, key=score_job, reverse=True)
        return sorted_jobs
    
    async def _create_job_application(self, job: JobSearchResult) -> JobApplication:
        """Create a job application record in the database."""
        job_app = JobApplication(
            job_title=job.title,
            company=job.company,
            job_description=job.description,
            job_url=job.url,
            status="in_progress",
            notes=f"Source: {job.source}, Posted: {job.posted_date}"
        )
        
        self.db.add(job_app)
        await self.db.commit()
        await self.db.refresh(job_app)
        
        return job_app
    
    async def _generate_documents(self, job: JobSearchResult, job_id: int) -> Dict:
        """
        Generate tailored resume and cover letter using Jobbernaut.
        
        Returns:
            Dict with resume_path, cover_letter_path, and match_score
        """
        # Prepare job data for Jobbernaut
        job_data = {
            "job_id": str(job_id),
            "job_title": job.title,
            "company_name": job.company,
            "job_description": job.description
        }
        
        # Use Jobbernaut service to generate documents
        # This will stream progress updates which we could yield if needed
        result = {"resume_path": None, "cover_letter_path": None, "match_score": 0.0}
        
        async for update in self.jobbernaut.generate_job_documents(job_data):
            if update.get("stage") == "completed":
                result["resume_path"] = update.get("data", {}).get("resume_path")
                result["cover_letter_path"] = update.get("data", {}).get("cover_letter_path")
                # TODO: Calculate actual match score by comparing job requirements to generated resume
                result["match_score"] = 85.0  # Placeholder
        
        return result
    
    async def get_applications(
        self,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[JobApplication]:
        """
        Retrieve job applications from database.
        
        Args:
            status: Filter by status (pending, in_progress, completed, failed)
            limit: Maximum number of results
            
        Returns:
            List of JobApplication records
        """
        query = select(JobApplication)
        
        if status:
            query = query.where(JobApplication.status == status)
        
        query = query.order_by(JobApplication.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        applications = result.scalars().all()
        
        return list(applications)
