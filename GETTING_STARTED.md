# Getting Started with AI-Dev Job Application System

Welcome! This guide will help you start using the automated job application system.

## Quick Start (5 Minutes)

### 1. Set Up Your Profile

First, customize your user profile:

```bash
# Edit your profile
vim data/user_profile.json
```

Update these key fields:
- `full_name`: Your actual name
- `email`: Your email address  
- `skills`: Your technical skills
- `experience_years`: Years of experience
- `desired_roles`: Job titles you're targeting
- `desired_salary_min/max`: Salary range

### 2. Test the System

Run the test scripts to verify everything works:

```bash
cd apps/portal-python

# Test match scoring
python test_match_scoring.py

# Test integration
python test_integration.py
```

### 3. Generate Your First Application

```bash
# Generate resume and cover letter for a job
python generate_resume.py \
  --company "Acme Corp" \
  --role "Senior Software Engineer" \
  --job-desc ../../data/oppertunities/_templates/example_job_description.md
```

Results will be saved in `data/oppertunities/applications/Acme_Corp/`

## Features Overview

### 🎯 Match Scoring System
Automatically scores jobs based on:
- Skills match (40%)
- Experience level (25%)
- Role match (20%)
- Keyword density (15%)

**Threshold:** Jobs scoring 70+ are good matches

### 📝 Resume & Cover Letter Generator
Uses LLM Council (multiple AI models) to generate:
- Tailored, ATS-optimized resumes
- Personalized cover letters
- Natural keyword integration

### ⚡ Fast Application Tools
- **Bulk Generator**: Process 20+ jobs in parallel
- **One-Click Workflow**: Search → Score → Generate in one command
- **5-8 applications per hour** (vs 2-3 manual)

## Workflows

### Workflow 1: Single Application (High Quality)

```bash
cd apps/portal-python

# 1. Save job description
echo "Job description here..." > job.txt

# 2. Generate materials
python generate_resume.py \
  --company "Google" \
  --role "Senior Engineer" \
  --job-desc job.txt

# 3. Review and customize
vim ../../data/oppertunities/applications/Google/resume_*.md

# 4. Apply manually using generated materials
```

**Time:** 15-20 min per application  
**Quality:** Highest  
**Best for:** Top choice companies

### Workflow 2: Bulk Applications (Fast)

```bash
cd apps/portal-python

# Generate materials for 20 jobs automatically
python -m tools.one_click_workflow \
  --positions "Software Engineer" "Python Developer" \
  --locations "Remote" \
  --max-jobs 20 \
  --open-browser 5

# Review quick-apply sheet
cat ../../data/oppertunities/applications/quick_apply_sheet_*.md

# Submit applications (10-12 min each)
```

**Time:** 3-4 hours for 20 applications  
**Quality:** High  
**Best for:** Rapid applications to many companies

### Workflow 3: Daily Routine (Sustainable)

```bash
# Morning: Generate 10 applications (15 min)
python -m tools.one_click_workflow \
  --positions "Backend Engineer" \
  --max-jobs 10

# Evening: Submit applications (2 hours)
# Use quick-apply sheet to copy/paste
```

**Daily goal:** 10 applications  
**Weekly goal:** 50 applications  
**Quality:** High  

## Customization

### Adjust Match Scoring

Edit `apps/portal-python/ai/job_match_scorer.py`:

```python
# Change weights
weights = {
    'skills': 0.40,      # Increase for skills-focused
    'experience': 0.25,  # Increase for experience-focused
    'role': 0.20,
    'keywords': 0.15
}

# Change threshold
MATCH_SCORE_THRESHOLD = 75.0  # Increase for stricter matching
```

### Customize LLM Council

Edit `external/llm-council/backend/config.py`:

```python
# Choose your models
COUNCIL_MODELS = [
    "anthropic/claude-sonnet-4.5",  # Best overall
    "openai/gpt-4",                  # Good reasoning
    "google/gemini-pro",             # Fast & cheap
]

CHAIRMAN_MODEL = "anthropic/claude-sonnet-4.5"
```

### Add Skills to Detection

Edit `apps/portal-python/ai/job_match_scorer.py`:

```python
TECH_SKILLS = {
    # Add your skills here
    'your-skill',
    'another-skill',
    # ...existing skills
}
```

## File Structure

```
ai-dev/
├── apps/portal-python/
│   ├── generate_resume.py          # CLI for resume generation
│   ├── test_match_scoring.py       # Test scoring system
│   ├── test_integration.py         # Integration test
│   ├── ai/
│   │   ├── job_match_scorer.py     # Match scoring logic
│   │   └── user_profile_service.py # User profile management
│   └── tools/
│       ├── resume_generator.py     # Resume/cover letter generator
│       ├── bulk_application_generator.py
│       ├── one_click_workflow.py
│       └── job_models.py
├── data/
│   ├── user_profile.json           # YOUR PROFILE - Edit this!
│   └── oppertunities/
│       ├── applications/           # Generated materials here
│       └── _templates/
└── docs/
    ├── RESUME_GENERATOR.md
    ├── FAST_APPLICATION_TOOLS.md
    └── AIHAWK_TOOLS.md
```

## Common Tasks

### Update Your Profile

```bash
vim data/user_profile.json
```

### Test Match Scoring

```bash
cd apps/portal-python
python test_match_scoring.py
```

### Generate 50 Applications

```bash
cd apps/portal-python
python -m tools.bulk_application_generator \
  --search "Python Developer" \
  --max-jobs 50 \
  --concurrent 5
```

### View Generated Applications

```bash
ls -la data/oppertunities/applications/
```

## Tips for Success

1. **Update your profile regularly** - Keep skills and experience current
2. **Adjust match threshold** - Start at 70, increase if too many matches
3. **Batch similar roles** - Generate all "Backend Engineer" jobs together
4. **Use quick-apply sheets** - Copy/paste from generated materials
5. **Set time limits** - Max 12 min per application submission
6. **Track your applications** - Update `data/oppertunities/_tracker.md`

## Performance Benchmarks

| Approach | Apps/Hour | Quality | Risk |
|----------|-----------|---------|------|
| **Manual** | 2-3 | Highest | None |
| **Our Tools** | 5-8 | High | None |
| **Full Bot** | 15-20 | Low | Very High ⚠️ |

**Recommendation:** Use our tools for 80% of applications, manual for top 20%

## Next Steps

1. ✅ Customize `data/user_profile.json`
2. ✅ Run `test_match_scoring.py` to verify scoring
3. ✅ Generate first application with `generate_resume.py`
4. ✅ Try bulk workflow for 10 jobs
5. ✅ Set daily goal (e.g., 10 applications/day)

## Troubleshooting

**Match scores seem wrong?**
- Check your `user_profile.json` - especially skills and experience_years
- Run `test_match_scoring.py` to see examples

**Resume generation fails?**
- Set up LLM Council: `cd external/llm-council && echo "OPENROUTER_API_KEY=your-key" > .env`
- Get key at [openrouter.ai](https://openrouter.ai/)

**No jobs found?**
- Adjust search keywords
- Try broader locations
- Check job search API configuration

## Support & Documentation

- [Resume Generator Guide](docs/RESUME_GENERATOR.md)
- [Fast Application Tools](docs/FAST_APPLICATION_TOOLS.md)
- [Job Search Tracking](data/oppertunities/_tracker.md)
- [Full Documentation](README.md)

## Success Story Template

Track your progress:

```
Week 1: 50 applications → 5 responses (10% response rate)
Week 2: 50 applications → 7 responses (14% response rate)
Week 3: 40 applications → 6 responses (15% response rate)
Week 4: 30 applications → 8 interviews → 2 offers! 🎉
```

---

**Ready to get started?** Run these three commands:

```bash
# 1. Update your profile
vim data/user_profile.json

# 2. Test the system
cd apps/portal-python && python test_integration.py

# 3. Generate your first application
python generate_resume.py \
  --company "YourTarget" \
  --role "Your Role" \
  --job-desc path/to/job.txt
```

Good luck! 🚀
