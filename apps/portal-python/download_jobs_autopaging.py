#!/usr/bin/env python3
"""
Auto-Paging Job Downloader - Stops When No More Jobs Found

This script automatically pages through results until JSearch has no more jobs.
It detects the end by checking if fewer jobs than expected are returned.

Usage:
    # Page until no more results
    python download_jobs_autopaging.py
    
    # Set max pages as safety limit
    python download_jobs_autopaging.py --max-pages 10
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set
import httpx
from dotenv import load_dotenv

# Load environment
load_dotenv()

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
OUTPUT_DIR = Path("outputs")
JOBS_PER_PAGE = 10  # JSearch returns ~10 jobs per page


async def search_jsearch_page(
    keywords: str,
    location: str = "Remote",
    page: int = 1,
    date_posted: str = "3days",
    remote_only: bool = True
) -> tuple[List[Dict], bool]:
    """
    Search a single page and detect if more pages exist.
    
    Returns:
        (jobs, has_more) - jobs list and whether more pages likely exist
    """
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    params = {
        "query": keywords,
        "page": str(page),
        "num_pages": "1",
        "date_posted": date_posted,
    }
    
    if remote_only:
        params["remote_jobs_only"] = "true"
    
    if location:
        params["location"] = location
    
    print(f"   📄 Page {page}...", end=" ", flush=True)
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.get(
            "https://jsearch.p.rapidapi.com/search",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        data = response.json()
        
        jobs = data.get("data", [])
        
        # If we got fewer than JOBS_PER_PAGE, no more pages exist
        has_more = len(jobs) >= JOBS_PER_PAGE
        
        print(f"✓ {len(jobs)} jobs{'' if has_more else ' (last page)'}")
        return jobs, has_more


async def search_all_pages(
    keywords: str,
    location: str = "Remote",
    date_posted: str = "3days",
    max_pages: int = 25,  # Safety limit
    remote_only: bool = True
) -> List[Dict]:
    """
    Keep paging until no more results or max_pages reached.
    
    Args:
        keywords: Search query
        location: Location filter
        date_posted: Date range filter
        max_pages: Maximum pages to fetch (safety limit)
        remote_only: Filter for remote jobs only
        
    Returns:
        List of all jobs found
    """
    all_jobs = []
    page = 1
    api_calls = 0
    
    print(f"🔍 Searching: {keywords}")
    print(f"   Location: {location}")
    print(f"   Date: {date_posted}")
    print(f"   Remote Only: {remote_only}")
    
    while page <= max_pages:
        try:
            jobs, has_more = await search_jsearch_page(
                keywords=keywords,
                location=location,
                page=page,
                date_posted=date_posted,
                remote_only=remote_only
            )
            
            all_jobs.extend(jobs)
            api_calls += 1
            
            if not has_more:
                print(f"   ✓ No more pages (stopped at page {page})")
                break
            
            if page >= max_pages:
                print(f"   ⚠️  Reached max pages limit ({max_pages})")
                break
            
            page += 1
            
            # Rate limiting - small delay between requests
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"   ✗ Error on page {page}: {e}")
            break
    
    print(f"   📊 Total: {len(all_jobs)} jobs from {api_calls} API calls")
    return all_jobs


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


async def download_jobs(
    keywords_list: List[str],
    location: str = "Remote",
    max_pages: int = 25,
    date_posted: str = "3days",
    remote_only: bool = True
):
    """Download jobs with auto-pagination."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("🚀 Auto-Paging Job Downloader")
    print("=" * 70)
    print(f"📊 Configuration:")
    print(f"   Keywords: {', '.join(keywords_list)}")
    print(f"   Location: {location}")
    print(f"   Date Range: {date_posted}")
    print(f"   Max Pages: {max_pages} (safety limit)")
    print(f"   Remote Only: {remote_only}")
    print(f"   Max API Calls: {len(keywords_list) * max_pages}")
    print(f"\n💡 Auto-paging: Will stop when no more jobs are found")
    print("=" * 70)
    
    all_jobs = []
    total_api_calls = 0
    
    for keyword in keywords_list:
        try:
            jobs = await search_all_pages(
                keywords=keyword,
                location=location,
                date_posted=date_posted,
                max_pages=max_pages,
                remote_only=remote_only
            )
            all_jobs.extend(jobs)
            
            # Count API calls (each page = 1 call)
            # We can estimate from jobs returned
            total_api_calls += (len(jobs) + JOBS_PER_PAGE - 1) // JOBS_PER_PAGE
            
        except Exception as e:
            print(f"✗ Error searching '{keyword}': {e}")
            continue
    
    print(f"\n📥 Downloaded {len(all_jobs)} total jobs")
    
    # Deduplicate
    unique_jobs = deduplicate_jobs(all_jobs)
    duplicates = len(all_jobs) - len(unique_jobs)
    if duplicates > 0:
        print(f"🔄 Removed {duplicates} duplicates → {len(unique_jobs)} unique jobs")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"jobs_autopaged_{timestamp}.json"
    
    with open(output_file, "w") as f:
        json.dump({
            "downloaded_at": datetime.now().isoformat(),
            "keywords": keywords_list,
            "location": location,
            "date_posted": date_posted,
            "remote_only": remote_only,
            "api_calls_used": total_api_calls,
            "total_jobs": len(all_jobs),
            "unique_jobs": len(unique_jobs),
            "duplicates_removed": duplicates,
            "jobs": unique_jobs
        }, f, indent=2)
    
    print(f"\n💾 Saved to: {output_file}")
    
    # Summary stats
    print("\n" + "=" * 70)
    print("📈 Summary:")
    print(f"   API Calls: {total_api_calls} / 200 remaining this month")
    print(f"   Total Jobs: {len(all_jobs)}")
    print(f"   Unique Jobs: {len(unique_jobs)}")
    print(f"   Duplicates: {duplicates}")
    
    # Company breakdown
    companies = {}
    for job in unique_jobs:
        company = job.get("employer_name", "Unknown")
        companies[company] = companies.get(company, 0) + 1
    
    print(f"\n🏢 Top Companies ({len(companies)} total):")
    for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {company}: {count}")
    
    print("=" * 70)


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-paging job downloader")
    parser.add_argument("--keywords", nargs="+", help="Search keywords")
    parser.add_argument("--location", default="Remote", help="Location filter")
    parser.add_argument("--date", default="3days", 
                       choices=["today", "3days", "week", "month", "all"],
                       help="Date posted filter")
    parser.add_argument("--max-pages", type=int, default=25,
                       help="Maximum pages per keyword (safety limit)")
    parser.add_argument("--no-remote", action="store_true",
                       help="Don't filter for remote only")
    
    args = parser.parse_args()
    
    # Load config from database first, fallback to config.json
    jsearch_config = {}
    try:
        # Try database first
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from python.database import Config, get_session, init_db
        from sqlmodel import select
        
        async def load_config_from_db():
            await init_db()
            async for session in get_session():
                result = await session.execute(
                    select(Config).where(Config.name == "auto-apply")
                )
                config_obj = result.scalar_one_or_none()
                if config_obj:
                    return json.loads(config_obj.config_json)
                return None
        
        db_config = await load_config_from_db()
        if db_config:
            jsearch_config = db_config.get("jsearch", {})
            print("✅ Loaded config from database")
    except Exception as e:
        print(f"⚠️  Could not load from database: {e}")
    
    # Fallback to config.json if database fails
    if not jsearch_config:
        config_path = Path(__file__).parent.parent / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                jsearch_config = config.get("jsearch", {})
            print("✅ Loaded config from config.json (fallback)")
        else:
            jsearch_config = {}
            print("⚠️  No config found, using defaults")
    
    # Use args or config
    keywords = args.keywords or jsearch_config.get("queries", [
        "Senior Software Engineer",
        "Staff Software Engineer", 
        "Principal Software Engineer"
    ])
    
    location = args.location or jsearch_config.get("location", "Remote")
    remote_only = not args.no_remote and jsearch_config.get("remote_jobs_only", True)
    
    await download_jobs(
        keywords_list=keywords,
        location=location,
        max_pages=args.max_pages,
        date_posted=args.date,
        remote_only=remote_only
    )


if __name__ == "__main__":
    asyncio.run(main())
