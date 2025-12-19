"""
Job Search Service
Searches multiple job boards for positions matching keywords.
"""

import asyncio
import httpx
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


class JobSearchService:
    """
    Unified job search service supporting multiple job boards.
    Currently supports: Remotive (remote jobs), Arbeitnow (remote jobs), JSearch API.
    """
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)
        
    async def search_jobs(
        self,
        keywords: str,
        location: Optional[str] = None,
        limit: int = 50
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
        
        # Search multiple sources in parallel
        tasks = [
            self._search_remotive(keywords, limit=20),
            self._search_arbeitnow(keywords, limit=20),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten and deduplicate results
        all_jobs = []
        seen_urls = set()
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Job search error: {result}")
                continue
            
            for job in result:
                if job.url not in seen_urls:
                    seen_urls.add(job.url)
                    all_jobs.append(job)
        
        # Sort by posted date (most recent first)
        all_jobs.sort(key=lambda j: j.posted_date, reverse=True)
        
        logger.info(f"Found {len(all_jobs)} unique jobs")
        return all_jobs[:limit]
    
    async def _search_remotive(self, keywords: str, limit: int = 20) -> List[JobSearchResult]:
        """
        Search Remotive API for remote jobs.
        https://remotive.com/api/remote-jobs
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    "https://remotive.com/api/remote-jobs",
                    params={"search": keywords, "limit": limit}
                )
                response.raise_for_status()
                data = response.json()
                
                jobs = []
                for job_data in data.get("jobs", [])[:limit]:
                    jobs.append(JobSearchResult(
                        title=job_data.get("title", ""),
                        company=job_data.get("company_name", ""),
                        location=job_data.get("candidate_required_location", "Remote"),
                        description=job_data.get("description", ""),
                        url=job_data.get("url", ""),
                        posted_date=job_data.get("publication_date"),
                        salary=job_data.get("salary"),
                        source="remotive"
                    ))
                
                logger.info(f"Remotive: Found {len(jobs)} jobs")
                return jobs
                
        except Exception as e:
            logger.error(f"Remotive search failed: {e}")
            return []
    
    async def _search_arbeitnow(self, keywords: str, limit: int = 20) -> List[JobSearchResult]:
        """
        Search Arbeitnow API for remote jobs.
        https://arbeitnow.com/api/job-board-api
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    "https://www.arbeitnow.com/api/job-board-api",
                )
                response.raise_for_status()
                data = response.json()
                
                jobs = []
                # Filter by keywords in title or company
                for job_data in data.get("data", []):
                    title = job_data.get("title", "").lower()
                    company = job_data.get("company_name", "").lower()
                    description = job_data.get("description", "").lower()
                    
                    # Simple keyword matching
                    if any(kw.lower() in title or kw.lower() in company or kw.lower() in description 
                           for kw in keywords.split()):
                        jobs.append(JobSearchResult(
                            title=job_data.get("title", ""),
                            company=job_data.get("company_name", ""),
                            location=job_data.get("location", "Remote"),
                            description=job_data.get("description", ""),
                            url=job_data.get("url", ""),
                            posted_date=job_data.get("created_at"),
                            salary=None,
                            source="arbeitnow"
                        ))
                        
                        if len(jobs) >= limit:
                            break
                
                logger.info(f"Arbeitnow: Found {len(jobs)} jobs")
                return jobs
                
        except Exception as e:
            logger.error(f"Arbeitnow search failed: {e}")
            return []
    
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
