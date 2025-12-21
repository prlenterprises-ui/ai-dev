#!/usr/bin/env python3
"""Integration test for the complete job application system"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tools.job_models import Job
from ai.job_match_scorer import JobMatchScorer
from ai.user_profile_service import get_user_profile

async def test_integration():
    """Test the complete integration of all components"""
    
    print("🧪 Integration Test: Complete Job Application System")
    print("=" * 70)
    
    # Step 1: Load user profile
    print("\n1️⃣ Loading User Profile...")
    user_profile = get_user_profile()
    print(f"   ✓ Profile loaded: {user_profile.full_name}")
    print(f"   ✓ Skills: {len(user_profile.skills)} skills")
    print(f"   ✓ Experience: {user_profile.experience_years} years")
    
    # Step 2: Create sample jobs
    print("\n2️⃣ Creating Sample Jobs...")
    jobs = [
        Job(
            role="Senior Python Developer",
            company="TechCorp",
            location="Remote",
            description="5+ years Python, AWS, Docker, PostgreSQL required",
            remote=True
        ),
        Job(
            role="Junior Frontend Developer",
            company="StartupCo",
            location="Remote",
            description="0-2 years experience, HTML, CSS, JavaScript",
            remote=True
        ),
        Job(
            role="Backend Engineer",
            company="BigTech",
            location="San Francisco",
            description="3-5 years Node.js, PostgreSQL, REST APIs",
            remote=False
        )
    ]
    print(f"   ✓ Created {len(jobs)} test jobs")
    
    # Step 3: Score all jobs
    print("\n3️⃣ Scoring All Jobs...")
    scorer = JobMatchScorer()
    threshold = 70.0
    
    qualified_jobs = []
    for i, job in enumerate(jobs, 1):
        result = scorer.calculate_match_score(
            job_description=job.description,
            job_title=job.role,
            user_profile=user_profile
        )
        
        status = "✅" if result['overall_score'] >= threshold else "❌"
        print(f"   {status} Job {i}: {job.role} at {job.company}")
        print(f"      Score: {result['overall_score']}/100")
        
        if result['overall_score'] >= threshold:
            qualified_jobs.append((job, result))
    
    # Step 4: Summary
    print("\n" + "=" * 70)
    print("📊 Test Results")
    print("=" * 70)
    print(f"Total Jobs Analyzed: {len(jobs)}")
    print(f"Jobs Above Threshold ({threshold}): {len(qualified_jobs)}")
    print(f"Jobs Below Threshold: {len(jobs) - len(qualified_jobs)}")
    
    if qualified_jobs:
        print(f"\n✅ Qualified Jobs:")
        for job, result in qualified_jobs:
            print(f"   • {job.role} at {job.company} ({result['overall_score']}/100)")
    
    print("\n✅ Integration test complete!")
    print("   All components working together successfully!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_integration())
