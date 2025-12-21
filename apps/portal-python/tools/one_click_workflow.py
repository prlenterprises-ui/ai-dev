"""One-Click Application Workflow

Streamlines the entire application process from job search to ready-to-submit.
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
import webbrowser
from datetime import datetime

from tools.bulk_application_generator import BulkApplicationGenerator
from tools.job_models import Job, JobSearchFilter
from ai.job_search_service import JobSearchService


class OneClickApplicationWorkflow:
    """Automated workflow for rapid job applications."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the workflow.
        
        Args:
            output_dir: Output directory for applications
        """
        self.generator = BulkApplicationGenerator(output_dir)
        self.job_service = JobSearchService()
    
    async def search_and_generate(self, 
                                  search_filter: JobSearchFilter,
                                  max_jobs: int = 20) -> List[Dict[str, Any]]:
        """Search for jobs and generate applications automatically.
        
        Args:
            search_filter: Filter criteria
            max_jobs: Maximum number of jobs to process
            
        Returns:
            List of generation results
        """
        print(f"\n{'='*70}")
        print(f"🚀 ONE-CLICK APPLICATION WORKFLOW")
        print(f"{'='*70}\n")
        
        # Step 1: Search for jobs
        print("📍 Step 1/4: Searching for matching jobs...")
        all_jobs = []
        
        for position in search_filter.positions:
            for location in search_filter.locations:
                print(f"  Searching: {position} in {location}")
                
                results = self.job_service.search_jobs(
                    query=position,
                    location=location,
                    num_pages=2
                )
                
                # Convert to Job objects
                for job_data in results:
                    job = Job(
                        role=job_data.get('job_title', ''),
                        company=job_data.get('employer_name', ''),
                        location=job_data.get('job_location', location),
                        link=job_data.get('job_apply_link', ''),
                        description=job_data.get('job_description', ''),
                        job_id=job_data.get('job_id', ''),
                        remote='remote' in job_data.get('job_location', '').lower(),
                        job_type=job_data.get('job_employment_type', ''),
                        posted_date=job_data.get('job_posted_at', '')
                    )
                    all_jobs.append(job)
        
        print(f"  ✅ Found {len(all_jobs)} total jobs\n")
        
        # Step 2: Filter jobs
        print("🔍 Step 2/4: Filtering jobs based on criteria...")
        filtered_jobs = [job for job in all_jobs if search_filter.matches_job(job)]
        filtered_jobs = filtered_jobs[:max_jobs]
        print(f"  ✅ {len(filtered_jobs)} jobs match your criteria\n")
        
        if not filtered_jobs:
            print("❌ No jobs found matching your criteria. Try adjusting filters.")
            return []
        
        # Step 3: Generate applications
        print(f"⚡ Step 3/4: Generating application materials...")
        print(f"  (This may take a few minutes for {len(filtered_jobs)} jobs)\n")
        
        results = await self.generator.generate_bulk(
            filtered_jobs,
            max_concurrent=3
        )
        
        # Step 4: Create quick-apply resources
        print("📋 Step 4/4: Creating quick-apply resources...")
        summary_path = self.generator.save_summary()
        sheet_path = self.generator.generate_quick_apply_sheet()
        
        print(f"\n{'='*70}")
        print(f"✅ WORKFLOW COMPLETE!")
        print(f"{'='*70}")
        print(f"📁 Applications saved to: {self.generator.saver.base_dir}")
        print(f"📄 Summary: {summary_path}")
        print(f"📋 Quick-apply sheet: {sheet_path}")
        print(f"{'='*70}\n")
        
        return results
    
    def open_applications_in_browser(self, results: List[Dict[str, Any]],
                                    limit: int = 5):
        """Open job application links in browser tabs.
        
        Args:
            results: Generation results
            limit: Maximum tabs to open at once
        """
        print(f"\n🌐 Opening {min(limit, len(results))} job applications in browser...")
        
        opened = 0
        for result in results:
            if not result['success']:
                continue
            
            job = result['job']
            if job.link:
                print(f"  Opening: {job.company} - {job.role}")
                webbrowser.open(job.link)
                opened += 1
                
                if opened >= limit:
                    break
        
        print(f"\n✅ Opened {opened} application pages")
        print("💡 Tip: Use the quick-apply sheet to copy/paste your materials!\n")
    
    def generate_daily_application_plan(self, 
                                       target_per_day: int = 10,
                                       days: int = 5) -> Path:
        """Generate a structured daily application plan.
        
        Args:
            target_per_day: Target applications per day
            days: Number of days to plan for
            
        Returns:
            Path to plan file
        """
        total_needed = target_per_day * days
        
        plan = f"""# {days}-Day Application Plan
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Goal
- **Total Applications**: {total_needed}
- **Per Day**: {target_per_day}
- **Duration**: {days} days

## Daily Schedule

"""
        
        for day in range(1, days + 1):
            plan += f"""### Day {day}
- [ ] Generate {target_per_day} applications
- [ ] Review and customize top 3
- [ ] Submit all {target_per_day} applications
- [ ] Track in spreadsheet
- **Estimated Time**: 2-3 hours

"""
        
        plan += """
## Tips for Speed
1. **Batch Similar Roles**: Group by role type for faster generation
2. **Use Quick-Apply**: Copy/paste from generated materials
3. **Set Timers**: 10-15 min per application maximum
4. **Track Progress**: Check off as you go
5. **Take Breaks**: 5 min break every hour

## Commands

```bash
# Generate 10 applications
python -m tools.one_click_workflow \\
  --positions "Software Engineer" "Python Developer" \\
  --locations "Remote" \\
  --max-jobs 10

# Open first 5 in browser
python -m tools.one_click_workflow \\
  --positions "Software Engineer" \\
  --open-browser 5
```

## Tracking

| Day | Target | Completed | Success Rate | Notes |
|-----|--------|-----------|--------------|-------|
| 1   | 10     |           |              |       |
| 2   | 10     |           |              |       |
| 3   | 10     |           |              |       |
| 4   | 10     |           |              |       |
| 5   | 10     |           |              |       |

---
**Total**: {total_needed} applications in {days} days
"""
        
        plan_path = Path(self.generator.saver.base_dir) / "application_plan.md"
        plan_path.write_text(plan)
        
        print(f"📅 Application plan saved to: {plan_path}")
        return plan_path


# CLI interface
async def main():
    """CLI interface for one-click workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='One-click automated job application workflow'
    )
    
    # Search criteria
    parser.add_argument('--positions', nargs='+', required=True,
                       help='Job positions to search for')
    parser.add_argument('--locations', nargs='+', default=['Remote'],
                       help='Locations to search in')
    parser.add_argument('--remote-only', action='store_true',
                       help='Only remote positions')
    
    # Limits
    parser.add_argument('--max-jobs', type=int, default=20,
                       help='Maximum number of jobs to process')
    
    # Blacklists
    parser.add_argument('--blacklist-companies', nargs='*', default=[],
                       help='Companies to exclude')
    parser.add_argument('--blacklist-titles', nargs='*', default=[],
                       help='Title keywords to exclude')
    
    # Actions
    parser.add_argument('--open-browser', type=int, default=0,
                       help='Open N applications in browser after generation')
    parser.add_argument('--generate-plan', action='store_true',
                       help='Generate a daily application plan')
    parser.add_argument('--plan-days', type=int, default=5,
                       help='Number of days for application plan')
    parser.add_argument('--plan-per-day', type=int, default=10,
                       help='Target applications per day')
    
    # Output
    parser.add_argument('--output-dir', 
                       help='Custom output directory')
    
    args = parser.parse_args()
    
    # Create workflow
    workflow = OneClickApplicationWorkflow(args.output_dir)
    
    # Generate plan if requested
    if args.generate_plan:
        workflow.generate_daily_application_plan(
            target_per_day=args.plan_per_day,
            days=args.plan_days
        )
        return
    
    # Create search filter
    search_filter = JobSearchFilter(
        positions=args.positions,
        locations=args.locations,
        remote=args.remote_only,
        company_blacklist=args.blacklist_companies,
        title_blacklist=args.blacklist_titles
    )
    
    # Run workflow
    results = await workflow.search_and_generate(
        search_filter=search_filter,
        max_jobs=args.max_jobs
    )
    
    # Open in browser if requested
    if args.open_browser > 0:
        workflow.open_applications_in_browser(results, limit=args.open_browser)
    
    print("\n🎉 All done! Your applications are ready to submit.")
    print("💡 Tip: Each application should take ~10-15 minutes to submit.")
    print(f"⏱️  Estimated time to submit all: {len(results) * 12} minutes\n")


if __name__ == "__main__":
    asyncio.run(main())
