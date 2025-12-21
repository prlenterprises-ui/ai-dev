"""
Job Search and Application API routes.
"""

import asyncio
import logging
from typing import Optional, AsyncIterator
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timedelta
from pathlib import Path
import json

from python.database import get_session, JobApplication, Config
from ai.job_search_service import JobSearchService
from ai.matching_service import MatchingService, UserProfile
from ai.user_profile_service import get_user_profile
from ai.jobbernaut_service import JobbernautService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jobs", tags=["jobs"])

# Tracking file path
TRACKING_FILE = Path(".jsearch_tracking.json")


@router.get("/search-status")
async def get_search_status():
    """
    Get the status of the last job search.
    Returns tracking info including when last search was run.
    
    Returns:
        - can_search: bool - Whether search is allowed (24+ hours since last run)
        - last_run: datetime - When the last search was performed
        - hours_since_last_run: float - Hours since last search
        - hours_until_next: float - Hours until next search is allowed
        - total_api_calls: int - Total API calls used
        - message: str - Human-readable status message
    """
    try:
        # Check if tracking file exists
        if not TRACKING_FILE.exists():
            return {
                "can_search": True,
                "last_run": None,
                "hours_since_last_run": None,
                "hours_until_next": 0,
                "total_api_calls": 0,
                "message": "No previous searches. Ready to search!"
            }
        
        # Load tracking data
        with open(TRACKING_FILE, "r") as f:
            tracking = json.load(f)
        
        last_run_str = tracking.get("last_run")
        if not last_run_str:
            return {
                "can_search": True,
                "last_run": None,
                "hours_since_last_run": None,
                "hours_until_next": 0,
                "total_api_calls": tracking.get("total_api_calls", 0),
                "message": "No previous searches. Ready to search!"
            }
        
        # Calculate time since last run
        last_run = datetime.fromisoformat(last_run_str)
        now = datetime.now()
        time_diff = now - last_run
        hours_since = time_diff.total_seconds() / 3600
        
        # Check if 24 hours have passed
        can_search = hours_since >= 24
        hours_until_next = max(0, 24 - hours_since)
        
        # Create message
        if can_search:
            message = f"Ready to search! Last search was {hours_since:.1f} hours ago."
        else:
            message = f"Please wait {hours_until_next:.1f} more hours. Last search was {hours_since:.1f} hours ago."
        
        return {
            "can_search": can_search,
            "last_run": last_run.isoformat(),
            "hours_since_last_run": round(hours_since, 1),
            "hours_until_next": round(hours_until_next, 1),
            "total_api_calls": tracking.get("total_api_calls", 0),
            "runs_count": len(tracking.get("runs", [])),
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Failed to get search status: {e}")
        # On error, allow search to proceed
        return {
            "can_search": True,
            "last_run": None,
            "hours_since_last_run": None,
            "hours_until_next": 0,
            "total_api_calls": 0,
            "message": "Status check failed. Search is allowed."
        }


@router.post("/find")
async def find_jobs(session: AsyncSession = Depends(get_session)):
    """
    Find jobs based on auto-apply configuration.
    Streams progress updates using Server-Sent Events.
    
    Returns:
        StreamingResponse with job search progress
    """
    
    async def generate_events():
        """Generate Server-Sent Events for job search progress."""
        try:
            # Load auto-apply config
            yield f"data: {json.dumps({'stage': 'config', 'status': 'loading', 'message': 'Loading configuration...'})}\n\n"
            
            result = await session.execute(
                select(Config).where(Config.name == "auto-apply")
            )
            config_obj = result.scalar_one_or_none()
            
            if not config_obj:
                yield f"data: {json.dumps({'stage': 'config', 'status': 'error', 'message': 'Auto-apply configuration not found'})}\n\n"
                return
                
            config = json.loads(config_obj.config_json)
            yield f"data: {json.dumps({'stage': 'config', 'status': 'loaded', 'message': 'Configuration loaded'})}\n\n"
            
            # Get JSearch configuration (now centralized)
            jsearch_config = config.get("jsearch", {})
            jsearch_api_key = jsearch_config.get("X-RapidAPI-Key")
            jsearch_queries = jsearch_config.get("queries", ["Software Engineer"])
            jsearch_location = jsearch_config.get("location", "Remote")
            jsearch_remote_only = jsearch_config.get("remote_jobs_only", True)
            jsearch_date_posted = jsearch_config.get("date_posted", "3days")
            
            # Get matching/scoring configuration
            score_config = config.get("score_matching", {})
            match_threshold = score_config.get("match_threshold", 70)
            max_applications = config.get("max_applications", 20)
            auto_generate_resume = score_config.get("auto_generate_resume", True)
            
            # Initialize services
            job_search = JobSearchService(jsearch_api_key=jsearch_api_key)
            matching_service = MatchingService()
            user_profile = get_user_profile()
            
            # Search for jobs sequentially - LIMIT TO 100 JOBS TOTAL
            MAX_JOBS = 100
            all_jobs = []
            seen_urls = set()  # Deduplicate as we go
            
            for query_idx, query in enumerate(jsearch_queries, 1):
                # Stop if we already have 100 jobs
                if len(all_jobs) >= MAX_JOBS:
                    yield f"data: {json.dumps({'stage': 'search', 'status': 'limit_reached', 'message': f'Reached limit of {MAX_JOBS} jobs, stopping search'})}\n\n"
                    break
                
                yield f"data: {json.dumps({'stage': 'search', 'status': 'started', 'message': f'Query {query_idx}/{len(jsearch_queries)}: {query} in {jsearch_location}...'})}\n\n"
                
                # Search this query
                jobs = await job_search.search_jobs(
                    keywords=query,
                    location=jsearch_location,
                    limit=MAX_JOBS  # Request up to max (API will return ~10 per page)
                )
                
                # Add unique jobs only
                query_unique = 0
                query_duplicates = 0
                for job in jobs:
                    if len(all_jobs) >= MAX_JOBS:
                        break  # Stop at 100 jobs
                    if job.url not in seen_urls:
                        seen_urls.add(job.url)
                        all_jobs.append(job)
                        query_unique += 1
                    else:
                        query_duplicates += 1
                
                yield f"data: {json.dumps({'stage': 'search', 'status': 'query_completed', 'message': f'Query {query_idx}: Found {len(jobs)} jobs ({query_unique} new, {query_duplicates} duplicates). Total: {len(all_jobs)}/{MAX_JOBS}', 'data': {'query': query, 'found': len(jobs), 'unique': query_unique, 'total': len(all_jobs)}})}\n\n"
            
            yield f"data: {json.dumps({'stage': 'search', 'status': 'completed', 'message': f'Search complete: {len(all_jobs)} unique jobs from {query_idx} queries', 'data': {'count': len(all_jobs), 'queries_processed': query_idx}})}\n\n"
            
            if not all_jobs:
                yield f"data: {json.dumps({'stage': 'complete', 'status': 'done', 'message': 'No jobs found matching criteria'})}\n\n"
                return
            
            jobs = all_jobs
            
            # Check for existing jobs to avoid duplicates
            existing_urls = set()
            existing_result = await session.execute(
                select(JobApplication.job_url).where(JobApplication.job_url.isnot(None))
            )
            for row in existing_result:
                if row[0]:
                    existing_urls.add(row[0])
            
            # Process each job
            processed_count = 0
            matched_count = 0
            skipped_count = 0
            
            for idx, job in enumerate(jobs, 1):
                # Check for duplicate
                if job.url in existing_urls:
                    skipped_count += 1
                    yield f"data: {json.dumps({'stage': 'processing', 'status': 'skipped', 'message': f'Skipped duplicate: {job.title} at {job.company}', 'data': {'index': idx, 'total': len(jobs)}})}\n\n"
                    continue
                
                yield f"data: {json.dumps({'stage': 'processing', 'status': 'analyzing', 'message': f'Analyzing {idx}/{len(jobs)}: {job.title} at {job.company}', 'data': {'index': idx, 'total': len(jobs), 'job_title': job.title, 'company': job.company}})}\n\n"
                
                # Calculate match score
                match_result = matching_service.calculate_match(
                    job_description=job.description,
                    job_title=job.title,
                    user_profile=user_profile
                )
                
                match_score = match_result.overall_score
                yield f"data: {json.dumps({'stage': 'processing', 'status': 'scored', 'message': f'Match score: {match_score}%', 'data': {'match_score': match_score, 'threshold': match_threshold}})}\n\n"
                
                # STORE COMPLETE JSEARCH JSON - This is the source of truth
                # The raw_data contains the ENTIRE job object from JSearch with all fields
                jsearch_search_data = None
                
                # Store complete JSON for this job (contains 30+ fields from JSearch)
                if hasattr(job, 'raw_data') and job.raw_data:
                    # This is the COMPLETE job data - contains everything JSearch returned
                    jsearch_search_data = json.dumps(job.raw_data)
                else:
                    # Fallback: create JSON from extracted fields if raw_data not available
                    jsearch_search_data = json.dumps({
                        "job_title": job.title,
                        "employer_name": job.company,
                        "job_description": job.description,
                        "job_apply_link": job.url,
                        "job_city": job.location,
                        "job_posted_at_datetime_utc": job.posted_date,
                        "job_publisher": job.source.replace("jsearch-", "")
                    })
                
                # Skip job-details and salary API calls in initial download
                # These can be fetched later for specific jobs to save API quota
                jsearch_details_data = None
                jsearch_salary_data = None
                
                # Create job application with COMPLETE JSON stored
                # Basic fields (job_title, company, job_url) are extracted for indexing only
                # ALWAYS use jsearch_search_response JSON as the source of truth
                job_app = JobApplication(
                    # Indexed fields (for search/queries only)
                    job_title=job.title,
                    company=job.company,
                    job_url=job.url,
                    source=job.source,
                    
                    # Status and metadata
                    status="pending",
                    match_score=match_score / 100.0,
                    notes=f"Location: {job.location}\nSalary: {job.salary or 'Not specified'}\nPosted: {job.posted_date}",
                    
                    # SOURCE OF TRUTH: Complete JSearch API responses
                    jsearch_search_response=jsearch_search_data,  # COMPLETE job data (30+ fields)
                    jsearch_details_response=jsearch_details_data,  # COMPLETE details response
                    jsearch_salary_response=jsearch_salary_data,  # COMPLETE salary response
                    
                    # Deprecated field (kept for compatibility)
                    job_description=job.description[:1000] if job.description else None  # Truncated
                )
                
                session.add(job_app)
                await session.commit()
                await session.refresh(job_app)
                
                existing_urls.add(job.url)
                processed_count += 1
                
                # Check if match score meets threshold
                if match_score >= match_threshold:
                    matched_count += 1
                    
                    if auto_generate_resume:
                        yield f"data: {json.dumps({'stage': 'generating', 'status': 'started', 'message': f'Generating resume and cover letter for {job.title}...', 'data': {'job_id': job_app.id}})}\n\n"
                        
                        try:
                            # Generate tailored resume and cover letter
                            jobbernaut = JobbernautService()
                            result = await jobbernaut.generate_tailored_resume(
                                job_description=job.description,
                                job_title=job.title,
                                company=job.company
                            )
                            
                            if result:
                                job_app.resume_url = result.get("resume_path")
                                job_app.cover_letter_url = result.get("cover_letter_path")
                                job_app.status = "in_progress"
                                await session.commit()
                                
                                yield f"data: {json.dumps({'stage': 'generating', 'status': 'completed', 'message': f'Resume and cover letter generated', 'data': {'job_id': job_app.id}})}\n\n"
                            else:
                                yield f"data: {json.dumps({'stage': 'generating', 'status': 'failed', 'message': f'Failed to generate documents', 'data': {'job_id': job_app.id}})}\n\n"
                                
                        except Exception as e:
                            logger.error(f"Failed to generate documents for job {job_app.id}: {e}")
                            yield f"data: {json.dumps({'stage': 'generating', 'status': 'error', 'message': f'Error: {str(e)}', 'data': {'job_id': job_app.id}})}\n\n"
                    else:
                        # Just mark as pending for manual review
                        yield f"data: {json.dumps({'stage': 'processing', 'status': 'matched', 'message': f'Good match! Added to pending applications', 'data': {'job_id': job_app.id, 'match_score': match_score}})}\n\n"
                else:
                    yield f"data: {json.dumps({'stage': 'processing', 'status': 'low_match', 'message': f'Match score below threshold ({match_score}% < {match_threshold}%)', 'data': {'match_score': match_score}})}\n\n"
                
                # Stop if we've processed enough
                if matched_count >= max_applications:
                    yield f"data: {json.dumps({'stage': 'complete', 'status': 'limit_reached', 'message': f'Reached maximum applications limit ({max_applications})'})}\n\n"
                    break
            
            # Final summary
            yield f"data: {json.dumps({'stage': 'complete', 'status': 'done', 'message': 'Job search completed', 'data': {'processed': processed_count, 'matched': matched_count, 'skipped': skipped_count}})}\n\n"
            
            # Update tracking file for 24-hour cooldown
            try:
                tracking = {}
                if TRACKING_FILE.exists():
                    with open(TRACKING_FILE, "r") as f:
                        tracking = json.load(f)
                
                # Calculate API calls used based on queries searched
                # Each query uses num_pages API calls (calculated in job_search_service)
                num_queries_searched = query_idx  # Number of queries actually searched
                # Estimate: ~10 pages per query to get up to 100 jobs
                estimated_calls_per_query = min(10, (MAX_JOBS + 9) // 10)
                api_calls_used = num_queries_searched * estimated_calls_per_query
                
                tracking["last_run"] = datetime.now().isoformat()
                tracking["total_api_calls"] = tracking.get("total_api_calls", 0) + api_calls_used
                tracking["runs"] = tracking.get("runs", [])
                tracking["runs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "api_calls": api_calls_used,
                    "queries_searched": num_queries_searched,
                    "jobs_found": len(all_jobs),
                    "jobs_processed": processed_count,
                    "jobs_matched": matched_count,
                    "date_filter": jsearch_date_posted
                })
                
                with open(TRACKING_FILE, "w") as f:
                    json.dump(tracking, f, indent=2)
                    
                logger.info(f"Updated tracking: {api_calls_used} API calls ({num_queries_searched} queries), total: {tracking['total_api_calls']}")
            except Exception as track_error:
                logger.error(f"Failed to update tracking: {track_error}")
            
        except Exception as e:
            logger.error(f"Job search failed: {e}")
            yield f"data: {json.dumps({'stage': 'error', 'status': 'failed', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/applications")
async def list_applications(
    status: Optional[str] = None,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
):
    """
    List job applications from database.
    
    Query Parameters:
        status: Filter by status (pending, in_progress, completed, failed)
        limit: Maximum number of results (default: 100)
    """
    try:
        query = select(JobApplication).order_by(JobApplication.created_at.desc())
        
        if status:
            query = query.where(JobApplication.status == status)
        
        query = query.limit(limit)
        
        result = await session.execute(query)
        applications = result.scalars().all()
        
        return {
            "total": len(applications),
            "applications": [
                {
                    "id": app.id,
                    "job_title": app.job_title,
                    "company": app.company,
                    "job_description": app.job_description,
                    "status": app.status,
                    "match_score": app.match_score,
                    "resume_url": app.resume_url,
                    "cover_letter_url": app.cover_letter_url,
                    "job_url": app.job_url,
                    "source": app.source,
                    "created_at": app.created_at.isoformat(),
                    "updated_at": app.updated_at.isoformat(),
                    "notes": app.notes
                }
                for app in applications
            ]
        }
    
    except Exception as e:
        logger.error(f"Failed to list applications: {e}")
        raise HTTPException(status_code=500, detail=str(e))
