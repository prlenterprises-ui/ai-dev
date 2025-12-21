"""
Job Search Service
Searches multiple job boards for positions matching keywords.
"""

import asyncio
import httpx
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class JobSearchResult:
    """Represents a job search result from any board."""
    
    def __init__(
        self,
        title: str,
        company: str,
        location: str,
        description: str,
        url: str,
        posted_date: Optional[str] = None,
        salary: Optional[str] = None,
        source: str = "unknown"
    ):
        self.title = title
        self.company = company
        self.location = location
        self.description = description
        self.url = url
        self.posted_date = posted_date or datetime.now().isoformat()
        self.salary = salary
        self.source = source
        self.raw_data = None  # Store raw API response for later use


class JobSearchService:
    """
    Unified job search service using JSearch API.
    Searches across LinkedIn, Indeed, Glassdoor, ZipRecruiter, and more.
    """
    
    def __init__(self, jsearch_config: Optional[Dict] = None):
        self.timeout = httpx.Timeout(30.0)
        self.jsearch_api_key = os.getenv("JSEARCH_API_KEY")
        self.jsearch_config = jsearch_config or {}
        
    async def search_jobs(
        self,
        keywords: str,
        location: Optional[str] = None,
        limit: int = 100
    ) -> List[JobSearchResult]:
        """
        Search for jobs across multiple boards.
        
        Args:
            keywords: Search keywords/query
            location: Optional location filter
            limit: Maximum number of results to return
            
        Returns:
            List of JobSearchResult objects
        """
        logger.info(f"Searching jobs with keywords='{keywords}', location='{location}'")
        
        # Search JSearch only
        if not self.jsearch_api_key:
            logger.error("JSearch API key not configured. Set JSEARCH_API_KEY env var.")
            return []
        
        # If location is Remote or not specified, enable remote_only filter
        remote_filter = location == "Remote" or location is None or "remote" in (location or "").lower()
        
        all_jobs = await self._search_jsearch(
            keywords, 
            location=location if location and location != "Remote" else None,
            limit=limit,
            remote_only=remote_filter
        )
        
        logger.info(f"Found {len(all_jobs)} jobs from JSearch")
        return all_jobs[:limit]
    
    async def _search_jsearch(self, keywords: str, location: Optional[str] = None, limit: int = 30, date_posted: Optional[str] = None, remote_only: Optional[bool] = None) -> List[JobSearchResult]:
        """
        Search JSearch API (RapidAPI) for jobs from LinkedIn, Indeed, Glassdoor, etc.
        Includes jobs from Amazon, Google, Microsoft, and other major companies.
        
        Get API key from: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
        Free tier: 200 requests/month (basic) or 1,000 requests/month (mega)
        
        Args:
            keywords: Job search query
            location: Location filter (e.g., "Remote", "San Francisco, CA")
            limit: Max results to return (note: API returns ~10 jobs per page)
            date_posted: Filter by date - "today", "3days", "week", "month", "all"
                        If None, uses config value or defaults to "3days"
            remote_only: Filter for remote/work-from-home jobs only
                        If None, uses config value or defaults to True
        """
        if not self.jsearch_api_key:
            logger.warning("JSearch API key not configured")
            return []
        
        # Load parameters from config or use defaults
        if remote_only is None:
            remote_only = self.jsearch_config.get("remote_jobs_only", True)
        if date_posted is None:
            date_posted = self.jsearch_config.get("date_posted", "3days")
        work_from_home = self.jsearch_config.get("work_from_home", True)
        employment_types = self.jsearch_config.get("employment_types", "FULLTIME")
        num_pages = self.jsearch_config.get("num_pages", 1)
        
        logger.info(f"JSearch params: date_posted={date_posted}, remote_only={remote_only}, work_from_home={work_from_home}")
        
        try:
            headers = {
                "X-RapidAPI-Key": self.jsearch_api_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }
            
            # Calculate pages needed: limit/10 jobs per page, max 10 pages
            # Allow config to override, but cap at 10 pages
            pages_needed = min(10, (limit + 9) // 10)
            num_pages_param = min(10, max(1, num_pages or pages_needed))
            
            # Build query with remote keyword if filtering for remote jobs
            search_query = keywords
            if remote_only and "remote" not in keywords.lower():
                search_query = f"{keywords} remote"
            
            params = {
                "query": search_query,
                "page": "1",
                "num_pages": str(num_pages_param),  # Multiple pages in one call
                "date_posted": date_posted,  # e.g., "3days" = last 3 days
            }
            
            # Add remote job filters if requested
            if remote_only:
                params["remote_jobs_only"] = "true"
            
            # Add work from home filter
            if work_from_home:
                params["remote_jobs_only"] = "true"  # JSearch uses this for work from home
            
            # Add employment type filter
            if employment_types:
                params["employment_types"] = employment_types
            
            if location:
                params["location"] = location
            
            logger.info(f"JSearch query: '{search_query}', remote_only={remote_only}, location={location}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    "https://jsearch.p.rapidapi.com/search",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                # Preferred publishers (top 4 major job boards)
                preferred_publishers = self.jsearch_config.get("preferred_publishers", [])
                
                jobs = []
                for job_data in data.get("data", []):
                    # Filter by preferred publishers if configured
                    if preferred_publishers:
                        publisher = job_data.get("job_publisher", "").lower()
                        if not any(pref.lower() in publisher for pref in preferred_publishers):
                            logger.debug(f"Skipping job from {publisher} (not in preferred list)")
                            continue
                    
                    # Extract salary if available
                    salary = None
                    if job_data.get("job_salary_currency") and job_data.get("job_min_salary"):
                        min_sal = job_data.get("job_min_salary", 0)
                        max_sal = job_data.get("job_max_salary", 0)
                        currency = job_data.get("job_salary_currency", "USD")
                        if max_sal:
                            salary = f"{currency} {min_sal:,.0f} - {max_sal:,.0f}"
                        elif min_sal:
                            salary = f"{currency} {min_sal:,.0f}+"
                    
                    job_result = JobSearchResult(
                        title=job_data.get("job_title", ""),
                        company=job_data.get("employer_name", ""),
                        location=job_data.get("job_city", job_data.get("job_country", "Remote")),
                        description=job_data.get("job_description", ""),
                        url=job_data.get("job_apply_link", job_data.get("job_google_link", "")),
                        posted_date=job_data.get("job_posted_at_datetime_utc"),
                        salary=salary,
                        source=f"jsearch-{job_data.get('job_publisher', 'unknown').lower()}"
                    )
                    
                    # Store raw job data for later use
                    job_result.raw_data = job_data
                    jobs.append(job_result)
                    
                    # Stop if we have enough jobs
                    if len(jobs) >= limit:
                        break
                
                logger.info(f"JSearch: Found {len(jobs)} jobs (sources: LinkedIn, Indeed, Glassdoor, ZipRecruiter)")
                return jobs
                
        except Exception as e:
            logger.error(f"JSearch search failed: {e}")
            return []
    
    async def get_job_details(self, job_id: str) -> Optional[Dict]:
        """
        Get detailed job information from JSearch /job-details endpoint.
        
        Args:
            job_id: The job ID from the search results
            
        Returns:
            Dict with detailed job information or None if failed
        """
        if not self.jsearch_api_key:
            logger.warning("JSearch API key not configured")
            return None
        
        try:
            headers = {
                "X-RapidAPI-Key": self.jsearch_api_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }
            
            params = {"job_id": job_id}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    "https://jsearch.p.rapidapi.com/job-details",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"JSearch: Got details for job {job_id}")
                return data
                
        except Exception as e:
            logger.error(f"JSearch job details failed for {job_id}: {e}")
            return None
    
    async def get_estimated_salary(self, job_title: str, location: str = None, radius: int = 100) -> Optional[Dict]:
        """
        Get estimated salary information from JSearch /estimated-salary endpoint.
        
        Args:
            job_title: Job title to estimate salary for
            location: Location for salary estimate
            radius: Search radius in miles (default: 100)
            
        Returns:
            Dict with salary estimates or None if failed
        """
        if not self.jsearch_api_key:
            logger.warning("JSearch API key not configured")
            return None
        
        try:
            headers = {
                "X-RapidAPI-Key": self.jsearch_api_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }
            
            params = {
                "job_title": job_title,
                "radius": str(radius)
            }
            
            if location:
                params["location"] = location
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    "https://jsearch.p.rapidapi.com/estimated-salary",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"JSearch: Got salary estimate for {job_title}")
                return data
                
        except Exception as e:
            logger.error(f"JSearch salary estimate failed for {job_title}: {e}")
            return None
    
    def to_dict(self, job: JobSearchResult) -> Dict:
        """Convert JobSearchResult to dictionary."""
        return {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "url": job.url,
            "posted_date": job.posted_date,
            "salary": job.salary,
            "source": job.source
        }
