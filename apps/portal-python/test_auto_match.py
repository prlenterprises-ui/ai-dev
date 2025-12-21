#!/usr/bin/env python3
"""Test the auto-match workflow (dry run without LLM calls)"""

import sys
from pathlib import Path
import asyncio

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from ai.matching_service import MatchingService, UserProfile
from ai.user_profile_service import get_user_profile


async def test_auto_match_scoring():
    """Test automatic matching and scoring without resume generation."""
    
    print("=" * 70)
    print("🤖 Auto-Match Workflow Test (Scoring Only)")
    print("=" * 70)
    
    # Get user profile
    user_profile = get_user_profile()
    matching_service = MatchingService()
    
    # Sample jobs
    jobs = [
        {
            "title": "Senior Python Developer",
            "company": "TechCorp",
            "description": """
            Senior Python Developer needed with 5+ years experience.
            
            Requirements:
            - Expert in Python, FastAPI, Django
            - AWS, Docker, Kubernetes experience
            - PostgreSQL and REST APIs
            - Git proficiency required
            - React experience is a plus
            
            Responsibilities:
            - Build scalable backend services
            - Design REST APIs
            - Mentor junior developers
            """
        },
        {
            "title": "Java Developer",
            "company": "Enterprise Inc",
            "description": """
            Senior Java Developer with Spring Boot experience.
            
            Requirements:
            - 8+ years Java development
            - Spring Boot, Microservices
            - AWS experience helpful
            - SQL databases
            """
        },
        {
            "title": "Full Stack Engineer",
            "company": "StartupXYZ",
            "description": """
            Full Stack Engineer to join our growing team.
            
            Requirements:
            - Python and JavaScript/React
            - 3-5 years experience
            - Docker, Git, REST APIs
            - AWS or cloud experience
            
            Bonus:
            - FastAPI or Django knowledge
            - DevOps experience
            """
        }
    ]
    
    print(f"\n📋 Processing {len(jobs)} jobs...")
    print(f"🎯 Match Threshold: 70/100 (auto-generate if >= 70)")
    print(f"👤 User Profile: {user_profile.full_name}")
    print(f"   Skills: {len(user_profile.skills)} skills")
    print(f"   Experience: {user_profile.experience_years} years")
    print()
    
    results = []
    
    for i, job in enumerate(jobs, 1):
        print(f"\n{'='*70}")
        print(f"[{i}/{len(jobs)}] {job['title']} at {job['company']}")
        print('='*70)
        
        # Calculate match
        match_result = matching_service.calculate_match(
            job["description"],
            job["title"],
            user_profile
        )
        
        # Display results
        print(f"\n📊 Match Score: {match_result.overall_score}/100")
        print(f"   Skills:     {match_result.skills_score}/100")
        print(f"   Experience: {match_result.experience_score}/100")
        print(f"   Role:       {match_result.role_score}/100")
        print(f"   Keywords:   {match_result.keyword_score}/100")
        
        if match_result.matched_skills:
            print(f"\n✅ Matched Skills ({len(match_result.matched_skills)}):")
            print(f"   {', '.join(match_result.matched_skills[:8])}")
            if len(match_result.matched_skills) > 8:
                print(f"   ... and {len(match_result.matched_skills) - 8} more")
        
        if match_result.missing_skills:
            print(f"\n⚠️  Missing Skills ({len(match_result.missing_skills)}):")
            print(f"   {', '.join(match_result.missing_skills[:5])}")
            if len(match_result.missing_skills) > 5:
                print(f"   ... and {len(match_result.missing_skills) - 5} more")
        
        # Auto-generate decision
        print(f"\n🤖 Auto-Generate Decision:")
        if match_result.overall_score >= 70:
            print(f"   ✅ YES - Score {match_result.overall_score} >= 70")
            print(f"   📄 Would generate tailored resume automatically")
            action = "GENERATE RESUME"
        else:
            print(f"   ❌ NO - Score {match_result.overall_score} < 70")
            print(f"   💡 Score too low for automatic resume generation")
            action = "SKIP"
        
        # Recommendations
        if match_result.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in match_result.recommendations:
                print(f"   • {rec}")
        
        # Store result
        results.append({
            "job": f"{job['title']} at {job['company']}",
            "score": match_result.overall_score,
            "action": action
        })
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 SUMMARY")
    print(f"{'='*70}")
    
    good_matches = [r for r in results if r["score"] >= 70]
    fair_matches = [r for r in results if 50 <= r["score"] < 70]
    poor_matches = [r for r in results if r["score"] < 50]
    
    print(f"\nTotal Jobs Analyzed: {len(results)}")
    print(f"  ✅ Excellent Matches (>=70): {len(good_matches)}")
    print(f"  ⚠️  Fair Matches (50-69):    {len(fair_matches)}")
    print(f"  ❌ Poor Matches (<50):       {len(poor_matches)}")
    
    if good_matches:
        print(f"\n🎯 Would auto-generate resumes for:")
        for r in good_matches:
            print(f"   • {r['job']} ({r['score']}/100)")
    
    if fair_matches:
        print(f"\n⚠️  Manual review recommended for:")
        for r in fair_matches:
            print(f"   • {r['job']} ({r['score']}/100)")
    
    print(f"\n{'='*70}")
    print("✅ Test Complete!")
    print(f"{'='*70}\n")
    
    print("💡 To actually generate resumes, use:")
    print("   from ai.auto_match_workflow import AutoMatchWorkflow")
    print("   workflow = AutoMatchWorkflow(match_threshold=70.0)")
    print("   await workflow.process_job(...)")
    print()


if __name__ == "__main__":
    asyncio.run(test_auto_match_scoring())
