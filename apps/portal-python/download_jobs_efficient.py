#!/usr/bin/env python3
"""
Efficient Job Downloader for Limited API Plans
Optimized for JSearch free tier: 200 requests/month

Strategy:
1. Single API call per keyword (3 keywords = 3 API calls)
2. Date filter: last 3 days only
3. Max results per call: ~10 jobs per request (JSearch default)
4. Saves to JSON for later processing
5. Deduplicates results across searches

Usage:
    python download_jobs_efficient.py
    
This will use ~3 API calls and save all results to outputs/jobs_last_3_days.json
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Set
import httpx
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Your search configuration
SEARCH_CONFIG = {
    "job_keywords": [
        "Senior Software Engineer",
        "Staff Software Engineer", 
        "Principal Software Engineer"
    ],
    "location": "Remote",
    "salary_min": 150000,
    "employment_type": "FULLTIME",
}

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
OUTPUT_DIR = Path("outputs")
OUTPUT_FILE = OUTPUT_DIR / f"jobs_last_3_days_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"


async def search_jsearch_optimized(
    keywords: str,
    location: str = None,
    date_posted: str = "3days"
) -> List[Dict]:
    """
    Single optimized JSearch API call.
    
    Args:
        keywords: Job search query
        location: Location filter
        date_posted: "today", "3days", "week", "month", "all"
    
    Returns:
        List of job dictionaries
    """
    if not JSEARCH_API_KEY:
        raise ValueError("JSEARCH_API_KEY not found in environment")
    
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    params = {
        "query": keywords,
        "page": "1",
        "num_pages": "1",  # Only 1 page = 1 API call
        "date_posted": date_posted,
        "employment_types": SEARCH_CONFIG["employment_type"],
        "remote_jobs_only": "true"  # JSearch API parameter for remote/WFH jobs
    }
    
    if location:
        params["location"] = location
    
    print(f"🔍 Searching: {keywords} | Location: {location} | Date: {date_posted}")
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        response = await client.get(
            "https://jsearch.p.rapidapi.com/search",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        data = response.json()
        
        jobs = data.get("data", [])
        print(f"  ✓ Found {len(jobs)} jobs")
        return jobs


def deduplicate_jobs(all_jobs: List[Dict]) -> List[Dict]:
    """Remove duplicate jobs based on URL or title+company."""
    seen_urls: Set[str] = set()
    seen_combos: Set[tuple] = set()
    unique_jobs = []
    
    for job in all_jobs:
        url = job.get("job_apply_link") or job.get("job_google_link", "")
        combo = (job.get("job_title", "").lower(), job.get("employer_name", "").lower())
        
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_jobs.append(job)
        elif not url and combo not in seen_combos:
            seen_combos.add(combo)
            unique_jobs.append(job)
    
    return unique_jobs


def filter_by_salary(jobs: List[Dict], min_salary: int) -> List[Dict]:
    """Filter jobs by minimum salary if available."""
    filtered = []
    for job in jobs:
        min_sal = job.get("job_min_salary")
        if min_sal and min_sal >= min_salary:
            filtered.append(job)
        elif not min_sal:  # Include if salary not specified
            filtered.append(job)
    return filtered


async def download_all_jobs():
    """
    Download jobs for all keywords efficiently.
    Uses minimal API calls by combining search terms.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("🚀 Efficient Job Downloader")
    print("=" * 60)
    print(f"📊 Configuration:")
    print(f"   Keywords: {', '.join(SEARCH_CONFIG['job_keywords'])}")
    print(f"   Location: {SEARCH_CONFIG['location']}")
    print(f"   Salary Min: ${SEARCH_CONFIG['salary_min']:,}")
    print(f"   Date Range: Last 3 days")
    print(f"   API Calls: {len(SEARCH_CONFIG['job_keywords'])} (one per keyword)")
    print("=" * 60)
    
    all_jobs = []
    
    # Strategy 1: Search each keyword separately (3 API calls)
    for keyword in SEARCH_CONFIG["job_keywords"]:
        try:
            jobs = await search_jsearch_optimized(
                keywords=keyword,
                location=SEARCH_CONFIG["location"],
                date_posted="3days"  # Last 3 days only
            )
            all_jobs.extend(jobs)
            
            # Rate limiting - be nice to the API
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"  ✗ Error searching '{keyword}': {e}")
            continue
    
    print("\n" + "=" * 60)
    print(f"📥 Downloaded {len(all_jobs)} total jobs")
    
    # Deduplicate
    unique_jobs = deduplicate_jobs(all_jobs)
    print(f"✨ {len(unique_jobs)} unique jobs after deduplication")
    
    # Filter by salary
    filtered_jobs = filter_by_salary(unique_jobs, SEARCH_CONFIG["salary_min"])
    print(f"💰 {len(filtered_jobs)} jobs meeting salary requirement (${SEARCH_CONFIG['salary_min']:,}+)")
    
    # Add metadata
    result = {
        "downloaded_at": datetime.now().isoformat(),
        "search_config": SEARCH_CONFIG,
        "api_calls_used": len(SEARCH_CONFIG["job_keywords"]),
        "total_jobs": len(all_jobs),
        "unique_jobs": len(unique_jobs),
        "filtered_jobs": len(filtered_jobs),
        "jobs": filtered_jobs
    }
    
    # Save to file
    with open(OUTPUT_FILE, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Saved to: {OUTPUT_FILE}")
    print("=" * 60)
    
    # Print summary stats
    print("\n📊 Job Sources:")
    sources = {}
    for job in filtered_jobs:
        source = job.get("job_publisher", "unknown")
        sources[source] = sources.get(source, 0) + 1
    
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"   {source}: {count}")
    
    print(f"\n✅ Done! API calls used: {len(SEARCH_CONFIG['job_keywords'])}/200")
    print(f"   Remaining this month: {200 - len(SEARCH_CONFIG['job_keywords'])}")
    
    return result


if __name__ == "__main__":
    asyncio.run(download_all_jobs())
