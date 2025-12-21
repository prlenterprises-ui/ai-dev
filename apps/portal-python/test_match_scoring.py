#!/usr/bin/env python3
"""Test match scoring system"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from ai.job_match_scorer import JobMatchScorer, get_default_user_profile
from ai.user_profile_service import get_user_profile

def test_match_scoring():
    """Test the match scoring system with sample jobs"""
    
    print("🧪 Testing Match Scoring System")
    print("=" * 70)
    
    # Load user profile
    print("\n1️⃣ Loading user profile...")
    user_profile = get_user_profile()
    print(f"   Name: {user_profile.full_name}")
    print(f"   Skills: {', '.join(user_profile.skills[:5])}...")
    print(f"   Experience: {user_profile.experience_years} years")
    print(f"   Desired roles: {', '.join(user_profile.desired_roles[:3])}")
    
    # Create scorer
    scorer = JobMatchScorer()
    
    # Test Job 1: Perfect match
    print("\n2️⃣ Testing Job 1: Perfect Match (Senior Python Developer)")
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
    - Mentor junior developers
    - Design REST APIs
    """
    
    job1_title = "Senior Python Developer"
    result1 = scorer.calculate_match_score(job1_desc, job1_title, user_profile)
    
    print(f"\n   Overall Score: {result1['overall_score']}/100")
    print(f"   Skills Match: {result1['breakdown']['skills_match']}/100")
    print(f"   Experience Match: {result1['breakdown']['experience_match']}/100")
    print(f"   Role Match: {result1['breakdown']['role_match']}/100")
    print(f"   Keyword Density: {result1['breakdown']['keyword_density']}/100")
    print(f"\n   Matched Skills: {', '.join(result1['details']['matched_skills'])}")
    
    # Test Job 2: Partial match
    print("\n3️⃣ Testing Job 2: Partial Match (Java Developer)")
    job2_desc = """
    Senior Java Developer - San Francisco
    
    Looking for a Java expert with Spring Boot experience.
    
    Requirements:
    - 8+ years Java development
    - Spring Boot, Microservices
    - AWS experience
    - Docker and Kubernetes
    - SQL databases
    """
    
    job2_title = "Senior Java Developer"
    result2 = scorer.calculate_match_score(job2_desc, job2_title, user_profile)
    
    print(f"\n   Overall Score: {result2['overall_score']}/100")
    print(f"   Skills Match: {result2['breakdown']['skills_match']}/100")
    print(f"   Experience Match: {result2['breakdown']['experience_match']}/100")
    print(f"   Role Match: {result2['breakdown']['role_match']}/100")
    print(f"   Keyword Density: {result2['breakdown']['keyword_density']}/100")
    print(f"\n   Matched Skills: {', '.join(result2['details']['matched_skills'])}")
    
    # Test Job 3: Poor match
    print("\n4️⃣ Testing Job 3: Poor Match (Junior Frontend Developer)")
    job3_desc = """
    Junior Frontend Developer - Entry Level
    
    Looking for someone just starting their career.
    
    Requirements:
    - 0-2 years experience
    - HTML, CSS, JavaScript
    - Basic React knowledge
    - No backend experience needed
    """
    
    job3_title = "Junior Frontend Developer"
    result3 = scorer.calculate_match_score(job3_desc, job3_title, user_profile)
    
    print(f"\n   Overall Score: {result3['overall_score']}/100")
    print(f"   Skills Match: {result3['breakdown']['skills_match']}/100")
    print(f"   Experience Match: {result3['breakdown']['experience_match']}/100")
    print(f"   Role Match: {result3['breakdown']['role_match']}/100")
    print(f"   Keyword Density: {result3['breakdown']['keyword_density']}/100")
    print(f"\n   Matched Skills: {', '.join(result3['details']['matched_skills'])}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Match Score Summary")
    print("=" * 70)
    print(f"Job 1 (Perfect Match):  {result1['overall_score']}/100 ✅")
    print(f"Job 2 (Partial Match):  {result2['overall_score']}/100 ⚠️")
    print(f"Job 3 (Poor Match):     {result3['overall_score']}/100 ❌")
    print("\nRecommended threshold: 70+ for good matches")
    print("=" * 70)

if __name__ == "__main__":
    test_match_scoring()
