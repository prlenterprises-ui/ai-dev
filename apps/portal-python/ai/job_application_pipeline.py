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

from python.database import JobApplication, Config
from ai.job_search_service import JobSearchService, JobSearchResult
from ai.jobbernaut_service import JobbernautService
from ai.llm_clients import get_openrouter_client
from ai.opportunities_manager import OpportunitiesManager
from ai.job_match_scorer import JobMatchScorer, get_default_user_profile
from ai.user_profile_service import get_user_profile

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
    
    def __init__(self, db: AsyncSession, jsearch_config: Optional[Dict] = None):
        self.db = db
        self.jsearch_config = jsearch_config or {}
        self.job_search = JobSearchService(jsearch_config=self.jsearch_config)
        self.jobbernaut = JobbernautService()
        self.opportunities = OpportunitiesManager()
        self.llm_client = None  # Will be initialized when needed
        self.match_scorer = JobMatchScorer()
        self.user_profile = get_user_profile()
        
    async def _is_search_allowed(self) -> tuple[bool, Optional[str]]:
        """Check if search is allowed (24 hours must pass between searches).
        
        Returns:
            tuple: (is_allowed, reason_if_not_allowed)
        """
        try:
            result = await self.db.execute(select(Config).where(Config.name == "auto-apply"))
            config_obj = result.scalar_one_or_none()
            if config_obj:
                import json as json_lib
                from dateutil import parser
                from datetime import timedelta
                
                config_data = json_lib.loads(config_obj.config_json)
                last_search = config_data.get("last_search_timestamp")
                
                if not last_search:
                    return True, None
                
                last_search_dt = parser.isoparse(last_search)
                time_since_last = datetime.now() - last_search_dt.replace(tzinfo=None)
                
                if time_since_last < timedelta(hours=24):
                    hours_remaining = 24 - (time_since_last.total_seconds() / 3600)
                    return False, f"Search rate limited. Last search was {time_since_last.total_seconds() / 3600:.1f} hours ago. Please wait {hours_remaining:.1f} more hours."
                
                return True, None
            return True, None
        except Exception as e:
            logger.error(f"Failed to check search rate limit: {e}")
            return True, None  # Allow search if check fails
    
    async def _check_and_adjust_search_window(self):
        """Check last_search_timestamp and adjust date_posted if needed."""
        try:
            result = await self.db.execute(select(Config).where(Config.name == "auto-apply"))
            config_obj = result.scalar_one_or_none()
            if config_obj:
                import json as json_lib
                config_data = json_lib.loads(config_obj.config_json)
                last_search = config_data.get("last_search_timestamp")
                
                if not last_search:
                    # No previous search - use 7 days ("week")
                    self.jsearch_config["date_posted"] = "week"
                    logger.info("No previous search found, searching last 7 days (week)")
                else:
                    logger.info(f"Last search was at {last_search}")
        except Exception as e:
            logger.error(f"Failed to check last_search_timestamp: {e}")
    
    async def _update_last_search_timestamp(self):
        """Update last_search_timestamp in auto-apply config."""
        try:
            result = await self.db.execute(select(Config).where(Config.name == "auto-apply"))
            config_obj = result.scalar_one_or_none()
            if config_obj:
                import json as json_lib
                config_data = json_lib.loads(config_obj.config_json)
                config_data["last_search_timestamp"] = datetime.now().isoformat()
                config_obj.config_json = json_lib.dumps(config_data)
                config_obj.updated_at = datetime.now()
                await self.db.commit()
                logger.info(f"Updated last_search_timestamp to {config_data['last_search_timestamp']}")
        except Exception as e:
            logger.error(f"Failed to update last_search_timestamp: {e}")
        
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
        # Check rate limit (24 hours between searches)
        is_allowed, rate_limit_message = await self._is_search_allowed()
        if not is_allowed:
            yield {
                "stage": "search",
                "status": "rate_limited",
                "error": rate_limit_message,
                "message": rate_limit_message
            }
            return
        
        yield {
            "stage": "search",
            "status": "started",
            "message": f"Searching for jobs matching '{keywords}'..."
        }
        
        # Check and adjust search window based on last search timestamp
        await self._check_and_adjust_search_window()
        
        # Update job search service with adjusted config
        self.job_search.jsearch_config = self.jsearch_config
        
        # Step 1: Search for jobs
        try:
            jobs = await self.job_search.search_jobs(
                keywords=keywords,
                location=location,
                limit=max_applications * 2  # Get extra to filter
            )
            
            # Update last search timestamp
            await self._update_last_search_timestamp()
            
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
        # Use Jobbernaut service to generate documents
        # This will stream progress updates which we could yield if needed
        result = {"resume_path": None, "cover_letter_path": None, "match_score": 0.0}
        
        async for update in self.jobbernaut.process_application_stream(
            job_title=job.title,
            company=job.company,
            job_description=job.description,
            job_url=job.url
        ):
            if update.get("step") == "complete" and update.get("status") == "success":
                outputs = update.get("outputs", {})
                result["resume_path"] = outputs.get("resume_pdf")
                result["cover_letter_path"] = outputs.get("cover_letter_pdf")
                
                # Calculate actual match score
                match_result = self.match_scorer.calculate_match_score(
                    job_description=job.description,
                    job_title=job.title,
                    user_profile=self.user_profile
                )
                result["match_score"] = match_result["overall_score"]
                result["match_breakdown"] = match_result["breakdown"]
                result["match_details"] = match_result["details"]
        
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
