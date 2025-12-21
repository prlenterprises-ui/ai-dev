#!/usr/bin/env python3
"""Test the unified MatchingService"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from ai.matching_service import MatchingService, UserProfile

def test_resume_parsing():
    """Test resume parsing functionality"""
    print("=" * 70)
    print("🧪 Testing Resume Parsing")
    print("=" * 70)
    
    service = MatchingService()
    
    # Sample resume
    resume_text = """
    John Doe
    john.doe@example.com
    
    Senior Python Developer
    
    Professional with 7 years of experience in backend development.
    
    EXPERIENCE:
    Senior Python Developer at Tech Corp (2020 - Present)
    - Built scalable APIs using FastAPI and Django
    - Deployed services on AWS with Docker and Kubernetes
    - Implemented CI/CD pipelines using GitHub Actions
    
    Mid-Level Developer at StartupXYZ (2018 - 2020)
    - Developed REST APIs with Python and PostgreSQL
    - Used React for admin dashboards
    
    EDUCATION:
    Bachelor's in Computer Science, MIT (2017)
    
    SKILLS:
    Python, JavaScript, FastAPI, Django, React, AWS, Docker, 
    Kubernetes, PostgreSQL, Git, REST, GraphQL, CI/CD
    """
    
    profile = service.parse_resume(resume_text)
    
    print(f"\n✅ Name: {profile.full_name}")
    print(f"✅ Email: {profile.email}")
    print(f"✅ Experience: {profile.experience_years} years")
    print(f"✅ Education: {profile.education_level}")
    print(f"✅ Skills ({len(profile.skills)}): {', '.join(profile.skills[:10])}")
    if len(profile.skills) > 10:
        print(f"   ... and {len(profile.skills) - 10} more")
    print(f"✅ Roles: {', '.join(profile.desired_roles)}")


def test_job_matching():
    """Test job matching functionality"""
    print("\n" + "=" * 70)
    print("🎯 Testing Job Matching")
    print("=" * 70)
    
    service = MatchingService()
    
    # Create test profile
    profile = UserProfile(
        full_name="John Doe",
        email="john.doe@example.com",
        skills=['python', 'fastapi', 'django', 'aws', 'docker', 'kubernetes', 
                'postgresql', 'git', 'react', 'rest'],
        experience_years=7,
        desired_roles=['Senior Python Developer', 'Backend Engineer'],
        locations=['Remote'],
        education_level="Bachelor's"
    )
    
    # Test Job 1: Perfect Match
    print("\n📋 Test Job 1: Senior Python Developer (Perfect Match)")
    job1_desc = """
    Senior Python Developer - Remote
    
    We're looking for a Senior Python Developer with 5+ years of experience.
    
    Requirements:
    - Expert in Python, FastAPI, and Django
    - Experience with AWS, Docker, and Kubernetes
    - Strong knowledge of PostgreSQL and REST APIs
    - Git proficiency required
    - Experience with React is a plus
    
    Responsibilities:
    - Build scalable backend services
    - Design REST APIs
    - Mentor team members
    """
    
    result1 = service.calculate_match(job1_desc, "Senior Python Developer", profile)
    print(f"\n   Overall Score: {result1.overall_score}/100")
    print(f"   Skills: {result1.skills_score}/100")
    print(f"   Experience: {result1.experience_score}/100")
    print(f"   Role: {result1.role_score}/100")
    print(f"   Keywords: {result1.keyword_score}/100")
    print(f"   Matched: {', '.join(result1.matched_skills[:5])}")
    if result1.missing_skills:
        print(f"   Missing: {', '.join(result1.missing_skills[:5])}")
    print(f"\n   Recommendations:")
    for rec in result1.recommendations:
        print(f"      • {rec}")
    
    # Test Job 2: Partial Match
    print("\n📋 Test Job 2: Java Developer (Partial Match)")
    job2_desc = """
    Senior Java Developer - San Francisco
    
    Requirements:
    - 8+ years Java development
    - Spring Boot, Microservices
    - AWS experience
    - Docker and Kubernetes
    - SQL databases
    """
    
    result2 = service.calculate_match(job2_desc, "Senior Java Developer", profile)
    print(f"\n   Overall Score: {result2.overall_score}/100")
    print(f"   Skills: {result2.skills_score}/100")
    print(f"   Experience: {result2.experience_score}/100")
    print(f"   Role: {result2.role_score}/100")
    print(f"   Keywords: {result2.keyword_score}/100")
    print(f"   Matched: {', '.join(result2.matched_skills) if result2.matched_skills else 'None'}")
    print(f"   Missing: {', '.join(result2.missing_skills[:5])}")
    print(f"\n   Recommendations:")
    for rec in result2.recommendations:
        print(f"      • {rec}")
    
    # Test Job 3: Poor Match
    print("\n📋 Test Job 3: Junior Frontend Developer (Poor Match)")
    job3_desc = """
    Junior Frontend Developer - Entry Level
    
    Requirements:
    - 0-2 years experience
    - HTML, CSS, JavaScript
    - Basic React knowledge
    - No backend experience needed
    """
    
    result3 = service.calculate_match(job3_desc, "Junior Frontend Developer", profile)
    print(f"\n   Overall Score: {result3.overall_score}/100")
    print(f"   Skills: {result3.skills_score}/100")
    print(f"   Experience: {result3.experience_score}/100")
    print(f"   Role: {result3.role_score}/100")
    print(f"   Keywords: {result3.keyword_score}/100")
    print(f"   Matched: {', '.join(result3.matched_skills) if result3.matched_skills else 'None'}")
    print(f"\n   Recommendations:")
    for rec in result3.recommendations:
        print(f"      • {rec}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Summary")
    print("=" * 70)
    print(f"Job 1 (Perfect): {result1.overall_score}/100 {'✅' if result1.overall_score >= 70 else '❌'}")
    print(f"Job 2 (Partial): {result2.overall_score}/100 {'⚠️' if result2.overall_score >= 50 else '❌'}")
    print(f"Job 3 (Poor):    {result3.overall_score}/100 {'❌'}")
    print(f"\nRecommended threshold: 70+ for good matches")


def test_get_summary():
    """Test summary generation"""
    print("\n" + "=" * 70)
    print("📝 Testing Summary Generation")
    print("=" * 70)
    
    service = MatchingService()
    
    profile = UserProfile(
        skills=['python', 'fastapi', 'docker'],
        experience_years=5,
        desired_roles=['Backend Developer'],
        locations=['Remote']
    )
    
    job_desc = "Senior Python Developer needed with FastAPI and Docker experience (5+ years)"
    result = service.calculate_match(job_desc, "Senior Python Developer", profile)
    
    summary = service.get_match_summary(result)
    print(f"\n{summary}")


if __name__ == "__main__":
    print("🚀 Unified Matching Service Tests\n")
    
    test_resume_parsing()
    test_job_matching()
    test_get_summary()
    
    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)
