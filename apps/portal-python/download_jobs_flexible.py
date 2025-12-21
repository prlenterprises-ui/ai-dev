#!/usr/bin/env python3
"""
Flexible Job Downloader - Get More Jobs with JSearch
Supports different strategies based on your API budget

To get 250 jobs, you need: num_pages = 25 (25 API calls)

Usage:
    # Conservative (default): 3 API calls total
    python download_jobs_flexible.py
    
    # Aggressive: Get 250 jobs per keyword (75 API calls total)
    python download_jobs_flexible.py --pages 25
    
    # Medium: Get 50 jobs per keyword (15 API calls total)
    python download_jobs_flexible.py --pages 5
    
    # Single keyword with 250 jobs (25 API calls)
    python download_jobs_flexible.py --keywords "Senior Software Engineer" --pages 25
"""

import asyncio
import json
import os
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set
import httpx
from dotenv import load_dotenv

# Load environment
load_dotenv()

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
OUTPUT_DIR = Path("outputs")


async def search_jsearch_with_pages(
    keywords: str,
    location: str = None,
    num_pages: int = 1,
    date_posted: str = "3days"
) -> List[Dict]:
    """
    Search JSearch with multiple pages.
    
    Args:
        keywords: Job search query
        location: Location filter
        num_pages: Number of pages to fetch (each page = 1 API call, ~10 jobs)
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
        "num_pages": str(num_pages),  # JSearch will fetch multiple pages
        "date_posted": date_posted,
        "employment_types": "FULLTIME",
        "remote_jobs_only": "true"  # JSearch API parameter for remote/WFH jobs
    }
    
    if location:
        params["location"] = location
    
    print(f"🔍 Searching: {keywords}")
    print(f"   Location: {location}")
    print(f"   Pages: {num_pages} (= {num_pages} API calls)")
    print(f"   Expected jobs: ~{num_pages * 10}")
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.get(
            "https://jsearch.p.rapidapi.com/search",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        data = response.json()
        
        jobs = data.get("data", [])
        print(f"  ✓ Returned {len(jobs)} jobs")
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


async def download_jobs(
    keywords_list: List[str],
    location: str = "Remote",
    num_pages: int = 1,
    date_posted: str = "3days",
    min_salary: int = 150000
):
    """Download jobs with flexible page settings."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    total_api_calls = len(keywords_list) * num_pages
    
    print("=" * 70)
    print("🚀 Flexible Job Downloader")
    print("=" * 70)
    print(f"📊 Configuration:")
    print(f"   Keywords: {', '.join(keywords_list)}")
    print(f"   Location: {location}")
    print(f"   Pages per keyword: {num_pages}")
    print(f"   Date Range: {date_posted}")
    print(f"   Salary Min: ${min_salary:,}")
    print(f"   Total API Calls: {total_api_calls}")
    print(f"   Expected Jobs: ~{total_api_calls * 10}")
    
    if total_api_calls > 50:
        print(f"\n⚠️  WARNING: This will use {total_api_calls} API calls!")
        print(f"   With 200 calls/month, you can run this {200 // total_api_calls} times")
        response = input("   Continue? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    print("=" * 70)
    
    all_jobs = []
    
    for keyword in keywords_list:
        try:
            jobs = await search_jsearch_with_pages(
                keywords=keyword,
                location=location,
                num_pages=num_pages,
                date_posted=date_posted
            )
            all_jobs.extend(jobs)
            
            # Rate limiting
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"  ✗ Error searching '{keyword}': {e}")
            continue
    
    print("\n" + "=" * 70)
    print(f"📥 Downloaded {len(all_jobs)} total jobs")
    
    # Deduplicate
    unique_jobs = deduplicate_jobs(all_jobs)
    print(f"✨ {len(unique_jobs)} unique jobs after deduplication")
    
    # Filter by salary
    filtered_jobs = filter_by_salary(unique_jobs, min_salary)
    print(f"💰 {len(filtered_jobs)} jobs meeting salary requirement (${min_salary:,}+)")
    
    # Save results
    output_file = OUTPUT_DIR / f"jobs_{num_pages}pages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    result = {
        "downloaded_at": datetime.now().isoformat(),
        "search_config": {
            "keywords": keywords_list,
            "location": location,
            "num_pages": num_pages,
            "date_posted": date_posted,
            "min_salary": min_salary
        },
        "api_calls_used": total_api_calls,
        "api_remaining_this_month": f"{200 - total_api_calls} (if starting fresh)",
        "total_jobs": len(all_jobs),
        "unique_jobs": len(unique_jobs),
        "filtered_jobs": len(filtered_jobs),
        "jobs": filtered_jobs
    }
    
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Saved to: {output_file}")
    print("=" * 70)
    
    # Print summary stats
    print("\n📊 Job Sources:")
    sources = {}
    for job in filtered_jobs:
        source = job.get("job_publisher", "unknown")
        sources[source] = sources.get(source, 0) + 1
    
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {source}: {count}")
    
    print(f"\n✅ Done! API calls used: {total_api_calls}/200")
    print(f"   Jobs per API call: {len(filtered_jobs) / total_api_calls:.1f}")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Flexible JSearch Job Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Conservative (3 API calls):
  python download_jobs_flexible.py
  
  # Get 250 jobs per keyword (75 API calls):
  python download_jobs_flexible.py --pages 25
  
  # Single keyword, 250 jobs (25 API calls):
  python download_jobs_flexible.py --keywords "Senior Software Engineer" --pages 25
  
  # Last week's jobs (more results):
  python download_jobs_flexible.py --pages 10 --date week
        """
    )
    
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=["Senior Software Engineer", "Staff Software Engineer", "Principal Software Engineer"],
        help="Job keywords to search (default: Senior/Staff/Principal SE)"
    )
    parser.add_argument(
        "--location",
        default="Remote",
        help="Location filter (default: Remote)"
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Pages per keyword (1 page = ~10 jobs = 1 API call). For 250 jobs, use 25 pages (default: 1)"
    )
    parser.add_argument(
        "--date",
        choices=["today", "3days", "week", "month", "all"],
        default="3days",
        help="Date filter (default: 3days)"
    )
    parser.add_argument(
        "--min-salary",
        type=int,
        default=150000,
        help="Minimum salary filter (default: 150000)"
    )
    
    args = parser.parse_args()
    
    asyncio.run(download_jobs(
        keywords_list=args.keywords if isinstance(args.keywords, list) else [args.keywords],
        location=args.location,
        num_pages=args.pages,
        date_posted=args.date,
        min_salary=args.min_salary
    ))


if __name__ == "__main__":
    main()
