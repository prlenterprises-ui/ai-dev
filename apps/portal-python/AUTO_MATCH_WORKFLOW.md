# Auto-Match Workflow - Automatic Resume Generation

## Overview

The **Auto-Match Workflow** automatically generates tailored resumes for jobs that match your profile well. When a job scores above your threshold (default: 70/100), it triggers automatic resume generation using AI.

## How It Works

```
┌─────────────────┐
│  Job Posting    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Match Scoring   │  ← Compare to User Profile
│  (MatchingService)│
└────────┬────────┘
         │
         ▼
    Score >= 70?
         │
    ┌────┴────┐
    │         │
   YES       NO
    │         │
    ▼         ▼
┌────────┐  Skip
│Generate│
│Resume  │
└────────┘
```

## Quick Start

### Basic Usage

```python
from ai.auto_match_workflow import AutoMatchWorkflow

# Create workflow with default threshold (70/100)
workflow = AutoMatchWorkflow(
    match_threshold=70.0,     # Score threshold for auto-generation
    auto_generate=True        # Enable automatic resume generation
)

# Process a single job
result = await workflow.process_job(
    job_description="Senior Python Developer needed...",
    job_title="Senior Python Developer",
    company_name="TechCorp",
    job_url="https://example.com/job/12345"
)

# Check result
if result["resume_generated"]:
    print(f"✅ Resume saved: {result['resume_path']}")
    print(f"   Match score: {result['match_score']}/100")
```

### Batch Processing

```python
# Process multiple jobs
jobs = [
    {
        "job_title": "Senior Python Developer",
        "company_name": "TechCorp",
        "job_description": "...",
        "job_url": "https://..."
    },
    {
        "job_title": "Backend Engineer",
        "company_name": "StartupXYZ",
        "job_description": "...",
        "job_url": "https://..."
    }
]

results = await workflow.process_multiple_jobs(jobs)

# Summary
good_matches = [r for r in results if r["resume_generated"]]
print(f"Generated {len(good_matches)} resumes")
```

## Configuration

### Match Threshold

The `match_threshold` determines when to auto-generate:

```python
# Aggressive (generate more resumes)
workflow = AutoMatchWorkflow(match_threshold=60.0)

# Conservative (only best matches)
workflow = AutoMatchWorkflow(match_threshold=80.0)

# Recommended (balanced)
workflow = AutoMatchWorkflow(match_threshold=70.0)  # Default
```

### Score Ranges

- **80-100**: Excellent match - Perfect fit
- **70-79**: Good match - Strong candidate
- **50-69**: Fair match - Some gaps
- **0-49**: Poor match - Significant mismatch

### Auto-Generate Toggle

```python
# Just score, don't generate resumes
workflow = AutoMatchWorkflow(auto_generate=False)

# Enable auto-generation
workflow = AutoMatchWorkflow(auto_generate=True)  # Default
```

### Custom Output Directory

```python
workflow = AutoMatchWorkflow(
    outputs_dir="/path/to/custom/resumes"
)
```

## Result Format

Each job returns a detailed result:

```python
{
    "job_title": "Senior Python Developer",
    "company_name": "TechCorp",
    "job_url": "https://...",
    "match_score": 74.2,
    
    "match_details": {
        "skills_score": 70.0,
        "experience_score": 100.0,
        "role_score": 100.0,
        "keyword_score": 8.0,
        
        "matched_skills": ["python", "fastapi", "docker", ...],
        "missing_skills": ["kubernetes", "django"],
        "recommendations": [
            "Strong match! Consider applying.",
            "Consider highlighting Docker experience"
        ]
    },
    
    "resume_generated": True,
    "resume_path": "/path/to/resume.md"
}
```

## Scoring Breakdown

### How Scores are Calculated

The match score is a weighted average of 4 components:

1. **Skills Match (40%)**
   - Compares required skills vs. your skills
   - Higher score = more skill overlap

2. **Experience Match (25%)**
   - Compares required experience level vs. yours
   - Penalizes under/over-qualification

3. **Role Match (20%)**
   - Compares job title with desired roles
   - Looks for keyword overlap

4. **Keyword Density (15%)**
   - How often your skills appear in job description
   - Indicates relevance

### Example Calculation

```
Job: Senior Python Developer (5+ years)
Your Profile: 7 years Python, FastAPI, Docker

Skills Match:     8/10 required skills = 80.0/100
Experience Match: 7 years matches "5+ years" = 100.0/100
Role Match:       "Developer" in desired roles = 100.0/100
Keyword Density:  Skills mentioned 12 times = 12.0/100

Overall = (80.0×0.40) + (100.0×0.25) + (100.0×0.20) + (12.0×0.15)
        = 32.0 + 25.0 + 20.0 + 1.8
        = 78.8/100 ✅ Would generate resume!
```

## Generated Resume Format

Resumes are saved as Markdown with metadata:

```markdown
---
Generated: 2025-12-20T14:30:00
Company: TechCorp
Role: Senior Python Developer
Match Score: 78.8/100
Skills Match: 80.0/100
Experience Match: 100.0/100
Matched Skills: python, fastapi, docker, aws, postgresql
---

# Your Name
## Senior Python Developer

### Professional Summary
[AI-generated summary tailored to the job...]

### Experience
[Your experience, highlighted for this role...]

### Skills
[Skills organized by relevance to job...]

### Education
[Your education...]
```

## Testing

### Dry Run (No Resume Generation)

```bash
# Test scoring without generating resumes
python3 test_auto_match.py
```

This shows what the workflow would do:
- ✅ Which jobs would trigger resume generation
- ⚠️ Which jobs need manual review
- ❌ Which jobs are poor matches

### Live Demo (With Resume Generation)

```python
from ai.auto_match_workflow import demo
import asyncio

# Run demo with actual resume generation
results = asyncio.run(demo())
```

## Integration Examples

### With Job Search Service

```python
from ai.auto_match_workflow import AutoMatchWorkflow
from ai.job_search_service import JobSearchService

# Search for jobs
job_search = JobSearchService()
jobs = await job_search.search_jobs(query="Python Developer", limit=10)

# Auto-match and generate resumes
workflow = AutoMatchWorkflow(match_threshold=70.0)
results = await workflow.process_multiple_jobs([
    {
        "job_title": job["title"],
        "company_name": job["company"],
        "job_description": job["description"],
        "job_url": job["url"]
    }
    for job in jobs
])

# Track good matches
for result in results:
    if result["resume_generated"]:
        # Track in application pipeline
        await track_application(result)
```

### With Application Pipeline

```python
from ai.auto_match_workflow import AutoMatchWorkflow
from ai.job_application_pipeline import JobApplicationPipeline

workflow = AutoMatchWorkflow(match_threshold=70.0)
pipeline = JobApplicationPipeline()

# Process job
result = await workflow.process_job(
    job_description=job_desc,
    job_title=title,
    company_name=company
)

if result["resume_generated"]:
    # Add to application pipeline
    await pipeline.add_opportunity(
        company=result["company_name"],
        role=result["job_title"],
        resume_path=result["resume_path"],
        match_score=result["match_score"]
    )
```

## Command Line Usage

Create a CLI script:

```python
#!/usr/bin/env python3
"""Auto-match CLI"""
import asyncio
import argparse
from ai.auto_match_workflow import AutoMatchWorkflow

async def main():
    parser = argparse.ArgumentParser(description='Auto-match jobs')
    parser.add_argument('--threshold', type=float, default=70.0)
    parser.add_argument('--no-generate', action='store_true')
    parser.add_argument('--job-file', required=True, help='JSON file with jobs')
    
    args = parser.parse_args()
    
    workflow = AutoMatchWorkflow(
        match_threshold=args.threshold,
        auto_generate=not args.no_generate
    )
    
    # Load jobs from file
    import json
    with open(args.job_file) as f:
        jobs = json.load(f)
    
    # Process
    results = await workflow.process_multiple_jobs(jobs)
    
    print(f"\n✅ Processed {len(results)} jobs")
    print(f"   Generated {sum(r['resume_generated'] for r in results)} resumes")

if __name__ == "__main__":
    asyncio.run(main())
```

Usage:
```bash
# Auto-match and generate resumes
python auto_match_cli.py --job-file jobs.json

# Just score, don't generate
python auto_match_cli.py --job-file jobs.json --no-generate

# Custom threshold
python auto_match_cli.py --job-file jobs.json --threshold 75
```

## Output Files

Generated resumes are saved to:
```
outputs/auto_matched/
├── 20251220_143000_TechCorp_Senior_Python_Developer_resume.md
├── 20251220_143015_StartupXYZ_Backend_Engineer_resume.md
└── ...
```

Filename format:
```
{timestamp}_{company}_{role}_resume.md
```

## Best Practices

1. **Set Appropriate Threshold**
   - Start with 70 (recommended)
   - Adjust based on quality of generated resumes
   - Higher threshold = fewer but better matches

2. **Review Generated Resumes**
   - Always review before sending
   - AI is good but not perfect
   - Customize based on your preferences

3. **Batch Processing**
   - Process multiple jobs at once
   - More efficient than one-by-one
   - Better for opportunity tracking

4. **Track Results**
   - Save match scores and decisions
   - Analyze what threshold works best
   - Improve over time

5. **Test First**
   - Use `test_auto_match.py` to verify scoring
   - Check matches before generating resumes
   - Adjust threshold based on results

## Troubleshooting

### No Resumes Generated

**Problem**: Score is below threshold for all jobs

**Solutions**:
- Lower the threshold: `match_threshold=60.0`
- Update your user profile with more skills
- Check if jobs match your experience level

### Too Many Resumes

**Problem**: Generating resumes for jobs you're not interested in

**Solutions**:
- Raise the threshold: `match_threshold=80.0`
- Refine your user profile desired_roles
- Use more specific job searches

### Resume Quality Issues

**Problem**: Generated resumes don't look good

**Solutions**:
- Update your base resume template
- Provide more detailed user profile
- Customize the resume generation prompts

## Advanced Usage

### Custom Scoring Weights

Modify the MatchingService weights:

```python
from ai.matching_service import MatchingService

service = MatchingService()

# Adjust weights (must sum to 1.0)
service.WEIGHTS = {
    'skills': 0.50,      # Emphasize skills more
    'experience': 0.20,
    'role': 0.20,
    'keywords': 0.10
}
```

### Custom Resume Template

Provide your own base resume:

```python
from tools.resume_generator import ResumeGenerator

generator = ResumeGenerator(
    base_resume_path="/path/to/your/resume.docx"
)
```

### Hooks and Callbacks

Add custom logic:

```python
class CustomAutoMatchWorkflow(AutoMatchWorkflow):
    async def process_job(self, *args, **kwargs):
        result = await super().process_job(*args, **kwargs)
        
        # Custom logic
        if result["resume_generated"]:
            await self.send_notification(result)
        
        return result
    
    async def send_notification(self, result):
        # Send email, Slack message, etc.
        pass
```

## Summary

✅ **Automatic resume generation** for high-scoring jobs  
✅ **Configurable threshold** (default: 70/100)  
✅ **Batch processing** for efficiency  
✅ **Detailed match breakdown** with recommendations  
✅ **Saved resumes** with metadata  
✅ **Integration ready** for pipelines  

The Auto-Match Workflow saves you time by only generating resumes for jobs that truly match your profile!
