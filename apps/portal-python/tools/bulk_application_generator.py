"""Bulk Application Generator

Automatically generates application materials for multiple jobs at once.
Prepares everything for quick submission.
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from tools.resume_generator import ResumeGenerator
from tools.job_application_saver import JobApplicationSaver
from tools.job_models import Job, JobApplication


class BulkApplicationGenerator:
    """Generate application materials for multiple jobs in parallel."""
    
    def __init__(self, base_output_dir: Optional[str] = None):
        """Initialize the bulk generator.
        
        Args:
            base_output_dir: Base directory for saving applications
        """
        self.generator = ResumeGenerator()
        self.saver = JobApplicationSaver(base_output_dir)
        self.results = []
    
    async def generate_for_job(self, job: Job, job_index: int, 
                              total_jobs: int) -> Dict[str, Any]:
        """Generate application materials for a single job.
        
        Args:
            job: Job to generate materials for
            job_index: Index of current job
            total_jobs: Total number of jobs
            
        Returns:
            Dictionary with generation results
        """
        print(f"\n{'='*70}")
        print(f"[{job_index}/{total_jobs}] Generating application for:")
        print(f"  Company: {job.company}")
        print(f"  Role: {job.role}")
        print(f"{'='*70}")
        
        try:
            # Generate materials
            result = await self.generator.generate_full_application(
                job_description=job.description,
                company_name=job.company,
                role_title=job.role,
                output_dir=self.saver.base_dir
            )
            
            # Create application record
            application = JobApplication(
                job=job,
                status="ready",
                resume_path=result.get('resume_path'),
                cover_letter_path=result.get('cover_letter_path')
            )
            
            print(f"✅ Successfully generated materials for {job.company}")
            
            return {
                'job': job,
                'application': application,
                'result': result,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            print(f"❌ Error generating materials for {job.company}: {e}")
            return {
                'job': job,
                'application': None,
                'result': None,
                'success': False,
                'error': str(e)
            }
    
    async def generate_bulk(self, jobs: List[Job], 
                          max_concurrent: int = 3) -> List[Dict[str, Any]]:
        """Generate application materials for multiple jobs.
        
        Args:
            jobs: List of jobs to generate materials for
            max_concurrent: Maximum concurrent generations
            
        Returns:
            List of generation results
        """
        print(f"\n🚀 Starting bulk generation for {len(jobs)} jobs")
        print(f"⚡ Max concurrent: {max_concurrent}")
        print(f"{'='*70}\n")
        
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_with_semaphore(job: Job, index: int) -> Dict[str, Any]:
            async with semaphore:
                return await self.generate_for_job(job, index + 1, len(jobs))
        
        # Generate all in parallel (with concurrency limit)
        tasks = [generate_with_semaphore(job, i) for i, job in enumerate(jobs)]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # Print summary
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        print(f"\n{'='*70}")
        print(f"📊 BULK GENERATION COMPLETE")
        print(f"{'='*70}")
        print(f"  ✅ Successful: {successful}/{len(jobs)}")
        print(f"  ❌ Failed: {failed}/{len(jobs)}")
        print(f"{'='*70}\n")
        
        self.results = results
        return results
    
    def save_summary(self, output_file: Optional[str] = None) -> Path:
        """Save a summary of all generated applications.
        
        Args:
            output_file: Optional output file path
            
        Returns:
            Path to summary file
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{self.saver.base_dir}/bulk_generation_summary_{timestamp}.json"
        
        summary = {
            'generated_at': datetime.now().isoformat(),
            'total_jobs': len(self.results),
            'successful': sum(1 for r in self.results if r['success']),
            'failed': sum(1 for r in self.results if not r['success']),
            'applications': []
        }
        
        for result in self.results:
            job = result['job']
            app_info = {
                'company': job.company,
                'role': job.role,
                'location': job.location,
                'link': job.link,
                'success': result['success'],
                'error': result['error'],
                'status': result['application'].status if result['application'] else None
            }
            summary['applications'].append(app_info)
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2))
        
        print(f"📄 Summary saved to: {output_path}")
        return output_path
    
    def generate_quick_apply_sheet(self, output_file: Optional[str] = None) -> Path:
        """Generate a markdown sheet with all applications ready to submit.
        
        Args:
            output_file: Optional output file path
            
        Returns:
            Path to quick apply sheet
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{self.saver.base_dir}/quick_apply_sheet_{timestamp}.md"
        
        content = f"""# Quick Apply Sheet
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Instructions
1. Click on each job link
2. Copy/paste the resume and cover letter content
3. Submit application
4. Check off when complete

---

"""
        
        for i, result in enumerate(self.results, 1):
            if not result['success']:
                continue
            
            job = result['job']
            app = result['application']
            
            content += f"""
## {i}. {job.company} - {job.role}

- [ ] **Applied**
- **Link**: {job.link}
- **Location**: {job.location}
- **Resume**: `{app.resume_path}`
- **Cover Letter**: `{app.cover_letter_path}`

### Quick Copy Resume
```
See file: {app.resume_path}
```

### Quick Copy Cover Letter
```
See file: {app.cover_letter_path}
```

**Notes**: _____________________

---

"""
        
        output_path = Path(output_file)
        output_path.write_text(content)
        
        print(f"📋 Quick apply sheet saved to: {output_path}")
        return output_path


async def generate_from_job_search(query: str, location: str = "Remote",
                                   max_jobs: int = 10) -> List[Dict[str, Any]]:
    """Generate applications from job search results.
    
    Args:
        query: Job search query
        location: Location filter
        max_jobs: Maximum number of jobs
        
    Returns:
        List of generation results
    """
    from ai.job_search_service import JobSearchService
    
    print(f"🔍 Searching for jobs: '{query}' in {location}")
    
    # Search for jobs
    service = JobSearchService()
    job_results = service.search_jobs(
        query=query,
        location=location,
        num_pages=max_jobs // 10 + 1
    )
    
    # Convert to Job objects
    jobs = []
    for job_data in job_results[:max_jobs]:
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
        jobs.append(job)
    
    print(f"✅ Found {len(jobs)} jobs\n")
    
    # Generate applications
    generator = BulkApplicationGenerator()
    results = await generator.generate_bulk(jobs, max_concurrent=3)
    
    # Save summary and quick apply sheet
    generator.save_summary()
    generator.generate_quick_apply_sheet()
    
    return results


# CLI interface
async def main():
    """CLI interface for bulk application generator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate application materials for multiple jobs'
    )
    
    # Input sources
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--jobs-file', help='JSON file with job listings')
    input_group.add_argument('--search', help='Job search query')
    
    # Search options
    parser.add_argument('--location', default='Remote', 
                       help='Location for job search')
    parser.add_argument('--max-jobs', type=int, default=10,
                       help='Maximum number of jobs to process')
    
    # Generation options
    parser.add_argument('--concurrent', type=int, default=3,
                       help='Maximum concurrent generations')
    parser.add_argument('--output-dir', 
                       help='Custom output directory')
    
    args = parser.parse_args()
    
    if args.search:
        # Generate from search
        await generate_from_job_search(
            query=args.search,
            location=args.location,
            max_jobs=args.max_jobs
        )
    
    elif args.jobs_file:
        # Generate from file
        jobs_path = Path(args.jobs_file)
        
        if not jobs_path.exists():
            print(f"❌ Error: Jobs file not found: {args.jobs_file}")
            return
        
        jobs_data = json.loads(jobs_path.read_text())
        
        # Convert to Job objects
        jobs = []
        for job_data in jobs_data[:args.max_jobs]:
            job = Job(
                role=job_data.get('role', job_data.get('title', '')),
                company=job_data.get('company', ''),
                location=job_data.get('location', ''),
                link=job_data.get('link', job_data.get('url', '')),
                description=job_data.get('description', ''),
                job_id=job_data.get('job_id', job_data.get('id', '')),
                remote=job_data.get('remote', False),
                job_type=job_data.get('job_type', ''),
            )
            jobs.append(job)
        
        # Generate applications
        generator = BulkApplicationGenerator(args.output_dir)
        results = await generator.generate_bulk(jobs, max_concurrent=args.concurrent)
        
        # Save summary and quick apply sheet
        generator.save_summary()
        generator.generate_quick_apply_sheet()
    
    print("\n✅ All done! Check the output directory for your materials.")


if __name__ == "__main__":
    asyncio.run(main())
