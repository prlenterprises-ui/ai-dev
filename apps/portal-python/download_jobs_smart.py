#!/usr/bin/env python3
"""
Smart Job Downloader with Timestamp Tracking
Automatically adjusts date range based on when it was last run

First run: Searches last 3 days
Subsequent runs: Searches since last run (1 day, 3 days, or week)

This maximizes efficiency - you never download the same jobs twice!

Usage:
    # Run it - it figures out the rest!
    python download_jobs_smart.py
    
    # Force specific date range
    python download_jobs_smart.py --force-date 3days
    
    # Reset tracking (start fresh)
    python download_jobs_smart.py --reset
"""

import asyncio
import json
import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Set, Tuple
import httpx
from dotenv import load_dotenv

# Load environment
load_dotenv()

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
OUTPUT_DIR = Path("outputs")
TRACKING_FILE = Path(".jsearch_tracking.json")


def load_tracking() -> Dict:
    """Load tracking data from file."""
    if TRACKING_FILE.exists():
        with open(TRACKING_FILE, "r") as f:
            return json.load(f)
    return {
        "last_run": None,
        "total_api_calls": 0,
        "runs": []
    }


def save_tracking(data: Dict):
    """Save tracking data to file."""
    with open(TRACKING_FILE, "w") as f:
        json.dump(data, f, indent=2)


def calculate_date_filter(last_run: str = None) -> Tuple[str, str]:
    """
    Calculate optimal date filter based on last run.
    
    Returns:
        (date_posted_value, description)
    """
    if not last_run:
        # First run
        return ("3days", "Last 3 days (first run)")
    
    last_dt = datetime.fromisoformat(last_run)
    now = datetime.now()
    hours_since = (now - last_dt).total_seconds() / 3600
    days_since = hours_since / 24
    
    if days_since < 1:
        return ("today", f"Today only (last run {hours_since:.1f} hours ago)")
    elif days_since < 3:
        return ("3days", f"Last 3 days (last run {days_since:.1f} days ago)")
    elif days_since < 7:
        return ("week", f"Last week (last run {days_since:.1f} days ago)")
    else:
        return ("month", f"Last month (last run {days_since:.0f} days ago)")


async def search_jsearch_smart(
    keywords: str,
    location: str = None,
    date_posted: str = "3days",
    num_pages: int = 1
) -> List[Dict]:
    """Search JSearch with smart parameters."""
    if not JSEARCH_API_KEY:
        raise ValueError("JSEARCH_API_KEY not found in environment")
    
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    params = {
        "query": keywords,
        "page": "1",
        "num_pages": str(num_pages),
        "date_posted": date_posted,
        "employment_types": "FULLTIME",
        "remote_jobs_only": "true"  # JSearch API parameter for remote/WFH jobs
    }
    
    if location:
        params["location"] = location
    
    print(f"🔍 {keywords}")
    print(f"   📅 Date filter: {date_posted}")
    print(f"   📄 Pages: {num_pages} (API calls: {num_pages})")
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.get(
            "https://jsearch.p.rapidapi.com/search",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        data = response.json()
        
        jobs = data.get("data", [])
        print(f"   ✓ Found {len(jobs)} jobs")
        return jobs


def deduplicate_jobs(all_jobs: List[Dict]) -> List[Dict]:
    """Remove duplicate jobs."""
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
    """Filter jobs by minimum salary."""
    filtered = []
    for job in jobs:
        min_sal = job.get("job_min_salary")
        if min_sal and min_sal >= min_salary:
            filtered.append(job)
        elif not min_sal:  # Include if salary not specified
            filtered.append(job)
    return filtered


def remove_already_seen(jobs: List[Dict], tracking: Dict) -> List[Dict]:
    """Remove jobs we've already downloaded in previous runs."""
    seen_ids = set()
    for run in tracking.get("runs", []):
        seen_ids.update(run.get("job_ids", []))
    
    new_jobs = []
    for job in jobs:
        job_id = job.get("job_id")
        if job_id and job_id not in seen_ids:
            new_jobs.append(job)
        elif not job_id:
            new_jobs.append(job)  # Keep if no ID
    
    return new_jobs


async def download_jobs_smart(
    keywords_list: List[str] = None,
    location: str = "Remote",
    num_pages: int = 1,
    min_salary: int = 150000,
    force_date: str = None,
    reset: bool = False
):
    """Smart job downloader with timestamp tracking."""
    
    # Default keywords
    if not keywords_list:
        keywords_list = [
            "Senior Software Engineer",
            "Staff Software Engineer",
            "Principal Software Engineer"
        ]
    
    # Load tracking
    tracking = {} if reset else load_tracking()
    last_run = tracking.get("last_run")
    
    # Calculate optimal date filter
    if force_date:
        date_posted = force_date
        date_description = f"{force_date} (forced)"
    else:
        date_posted, date_description = calculate_date_filter(last_run)
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    total_api_calls = len(keywords_list) * num_pages
    
    print("=" * 70)
    print("🧠 Smart Job Downloader")
    print("=" * 70)
    
    if last_run:
        last_dt = datetime.fromisoformat(last_run)
        time_since = datetime.now() - last_dt
        hours = time_since.total_seconds() / 3600
        print(f"⏱️  Last run: {last_dt.strftime('%Y-%m-%d %H:%M')} ({hours:.1f} hours ago)")
        print(f"📊 Total API calls used: {tracking.get('total_api_calls', 0)}")
        print(f"🔄 Total runs: {len(tracking.get('runs', []))}")
    else:
        print(f"🆕 First run! Starting fresh.")
    
    print()
    print(f"📊 This Run:")
    print(f"   Keywords: {', '.join(keywords_list)}")
    print(f"   Location: {location}")
    print(f"   Date Filter: {date_description}")
    print(f"   Pages/keyword: {num_pages}")
    print(f"   API Calls: {total_api_calls}")
    print(f"   Salary Min: ${min_salary:,}")
    print("=" * 70)
    
    all_jobs = []
    
    for keyword in keywords_list:
        try:
            jobs = await search_jsearch_smart(
                keywords=keyword,
                location=location,
                date_posted=date_posted,
                num_pages=num_pages
            )
            all_jobs.extend(jobs)
            await asyncio.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue
    
    print("\n" + "=" * 70)
    print(f"📥 Downloaded {len(all_jobs)} total jobs")
    
    # Deduplicate
    unique_jobs = deduplicate_jobs(all_jobs)
    print(f"✨ {len(unique_jobs)} unique jobs (after dedup)")
    
    # Remove already seen jobs
    new_jobs = remove_already_seen(unique_jobs, tracking)
    if len(new_jobs) < len(unique_jobs):
        print(f"🔍 {len(new_jobs)} new jobs (removed {len(unique_jobs) - len(new_jobs)} already seen)")
    
    # Filter by salary
    filtered_jobs = filter_by_salary(new_jobs, min_salary)
    print(f"💰 {len(filtered_jobs)} jobs meeting criteria (${min_salary:,}+ salary)")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = OUTPUT_DIR / f"jobs_smart_{timestamp}.json"
    
    result = {
        "downloaded_at": datetime.now().isoformat(),
        "search_config": {
            "keywords": keywords_list,
            "location": location,
            "date_posted": date_posted,
            "date_description": date_description,
            "num_pages": num_pages,
            "min_salary": min_salary
        },
        "api_calls_used": total_api_calls,
        "total_jobs": len(all_jobs),
        "unique_jobs": len(unique_jobs),
        "new_jobs": len(new_jobs),
        "filtered_jobs": len(filtered_jobs),
        "jobs": filtered_jobs
    }
    
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Saved to: {output_file}")
    
    # Update tracking
    job_ids = [job.get("job_id") for job in filtered_jobs if job.get("job_id")]
    
    new_tracking = {
        "last_run": datetime.now().isoformat(),
        "total_api_calls": tracking.get("total_api_calls", 0) + total_api_calls,
        "runs": tracking.get("runs", []) + [{
            "timestamp": datetime.now().isoformat(),
            "api_calls": total_api_calls,
            "jobs_found": len(filtered_jobs),
            "date_filter": date_posted,
            "job_ids": job_ids
        }]
    }
    
    save_tracking(new_tracking)
    print(f"📝 Updated tracking: {TRACKING_FILE}")
    
    print("=" * 70)
    
    # Stats
    print("\n📊 Summary:")
    sources = {}
    for job in filtered_jobs:
        source = job.get("job_publisher", "unknown")
        sources[source] = sources.get(source, 0) + 1
    
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {source}: {count}")
    
    print(f"\n✅ Done!")
    print(f"   API Calls (this run): {total_api_calls}")
    print(f"   API Calls (total): {new_tracking['total_api_calls']}/200")
    print(f"   Remaining: {200 - new_tracking['total_api_calls']}")
    print(f"   Jobs per API call: {len(filtered_jobs) / total_api_calls:.1f}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if len(filtered_jobs) == 0:
        print(f"   ⚠️  No new jobs found. Try running less frequently.")
    elif len(filtered_jobs) > 50:
        print(f"   ✓ Lots of new jobs! Consider running more frequently.")
    
    return result


def show_tracking():
    """Show current tracking status."""
    tracking = load_tracking()
    
    print("=" * 70)
    print("📊 JSearch API Usage Tracking")
    print("=" * 70)
    
    if not tracking.get("last_run"):
        print("No runs recorded yet.")
        return
    
    last_dt = datetime.fromisoformat(tracking["last_run"])
    print(f"Last Run: {last_dt.strftime('%Y-%m-%d %H:%M')}")
    print(f"Total API Calls: {tracking['total_api_calls']}/200")
    print(f"Remaining: {200 - tracking['total_api_calls']}")
    print(f"Total Runs: {len(tracking['runs'])}")
    
    print("\n📜 Recent Runs:")
    for run in tracking["runs"][-5:]:
        dt = datetime.fromisoformat(run["timestamp"])
        print(f"  {dt.strftime('%Y-%m-%d %H:%M')} | "
              f"{run['api_calls']} calls | "
              f"{run['jobs_found']} jobs | "
              f"filter: {run['date_filter']}")
    
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Smart JSearch Job Downloader with Timestamp Tracking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Just run it - automatically figures out date range!
  python download_jobs_smart.py
  
  # Force specific date range
  python download_jobs_smart.py --force-date week
  
  # Check tracking status
  python download_jobs_smart.py --status
  
  # Reset tracking (start fresh)
  python download_jobs_smart.py --reset
        """
    )
    
    parser.add_argument(
        "--keywords",
        nargs="+",
        help="Job keywords (default: Senior/Staff/Principal SE)"
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
        help="Pages per keyword (default: 1)"
    )
    parser.add_argument(
        "--min-salary",
        type=int,
        default=150000,
        help="Minimum salary (default: 150000)"
    )
    parser.add_argument(
        "--force-date",
        choices=["today", "3days", "week", "month", "all"],
        help="Force specific date filter (overrides smart detection)"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset tracking (start fresh)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show tracking status and exit"
    )
    
    args = parser.parse_args()
    
    if args.status:
        show_tracking()
        return
    
    if args.reset:
        if TRACKING_FILE.exists():
            TRACKING_FILE.unlink()
            print(f"✅ Reset tracking: {TRACKING_FILE}")
    
    asyncio.run(download_jobs_smart(
        keywords_list=args.keywords,
        location=args.location,
        num_pages=args.pages,
        min_salary=args.min_salary,
        force_date=args.force_date,
        reset=args.reset
    ))


if __name__ == "__main__":
    main()
