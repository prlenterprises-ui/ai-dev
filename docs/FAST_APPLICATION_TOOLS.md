# Fast Application Tools - Documentation

Speed up your job application process with automated material generation.

## Overview

These tools dramatically reduce application time while maintaining quality:

| Approach | Time per App | Apps per Hour | Quality | Risk |
|----------|--------------|---------------|---------|------|
| **Manual** | 30-40 min | 2-3 | Highest | None |
| **Our Tools** | 10-12 min | 5-8 | High | None |
| **Full Bot** | 3-4 min | 15-20 | Low | Very High |

## Tools Available

### 1. Bulk Application Generator

Generate materials for multiple jobs in parallel.

**Features:**
- Parallel processing (3-5 jobs at once)
- LLM Council for quality
- Auto-saves all materials
- Summary reports
- Quick-apply sheets

**Usage:**

```bash
cd apps/portal-python

# From job search
python -m tools.bulk_application_generator \
  --search "Python Developer" \
  --location "Remote" \
  --max-jobs 20 \
  --concurrent 3

# From jobs file
python -m tools.bulk_application_generator \
  --jobs-file path/to/jobs.json \
  --max-jobs 50 \
  --concurrent 5
```

**Python API:**

```python
from tools.bulk_application_generator import BulkApplicationGenerator, generate_from_job_search
from tools.job_models import Job
import asyncio

async def bulk_generate():
    # Option 1: From job list
    jobs = [
        Job(role="Engineer", company="Google", description="..."),
        Job(role="Developer", company="Meta", description="..."),
    ]
    
    generator = BulkApplicationGenerator()
    results = await generator.generate_bulk(jobs, max_concurrent=3)
    generator.save_summary()
    generator.generate_quick_apply_sheet()
    
    # Option 2: From search
    results = await generate_from_job_search(
        query="Python Developer",
        location="Remote",
        max_jobs=20
    )

asyncio.run(bulk_generate())
```

**Output:**
```
data/oppertunities/applications/
├── bulk_generation_summary_20250120_143022.json
├── quick_apply_sheet_20250120_143022.md
├── Google/
│   ├── resume_20250120_143022.md
│   ├── cover_letter_20250120_143022.md
│   └── job_description_20250120_143022.md
└── Meta/
    └── ...
```

### 2. One-Click Workflow

Complete end-to-end automation from search to ready-to-submit.

**Features:**
- Automated job search
- Smart filtering
- Bulk generation
- Browser integration
- Daily planning

**Usage:**

```bash
cd apps/portal-python

# Basic workflow
python -m tools.one_click_workflow \
  --positions "Software Engineer" "Python Developer" \
  --locations "Remote" "San Francisco" \
  --max-jobs 20

# With blacklists
python -m tools.one_click_workflow \
  --positions "Backend Engineer" \
  --locations "Remote" \
  --blacklist-companies "BadCorp" \
  --blacklist-titles "junior" "intern" \
  --max-jobs 30

# Open in browser
python -m tools.one_click_workflow \
  --positions "Full Stack Developer" \
  --locations "Remote" \
  --max-jobs 15 \
  --open-browser 5

# Generate application plan
python -m tools.one_click_workflow \
  --generate-plan \
  --plan-days 5 \
  --plan-per-day 10
```

**Python API:**

```python
from tools.one_click_workflow import OneClickApplicationWorkflow
from tools.job_models import JobSearchFilter
import asyncio

async def one_click_apply():
    workflow = OneClickApplicationWorkflow()
    
    # Create filter
    filter = JobSearchFilter(
        positions=["Software Engineer", "Python Developer"],
        locations=["Remote", "San Francisco"],
        remote=True,
        company_blacklist=["BadCorp"],
        title_blacklist=["junior", "intern"]
    )
    
    # Run complete workflow
    results = await workflow.search_and_generate(
        search_filter=filter,
        max_jobs=20
    )
    
    # Open first 5 in browser
    workflow.open_applications_in_browser(results, limit=5)

asyncio.run(one_click_apply())
```

## Workflows

### Quick Start (20 applications in 4 hours)

```bash
# 1. Generate materials (20 min)
python -m tools.one_click_workflow \
  --positions "Software Engineer" \
  --locations "Remote" \
  --max-jobs 20

# 2. Review quick-apply sheet
cat data/oppertunities/applications/quick_apply_sheet_*.md

# 3. Submit applications (3-4 hours at 12 min each)
# Open each link, copy/paste materials, submit
```

### Daily Application Routine (10 apps/day)

```bash
# Monday - Friday
python -m tools.one_click_workflow \
  --positions "Python Developer" "Backend Engineer" \
  --locations "Remote" \
  --max-jobs 10 \
  --open-browser 5

# Takes ~2 hours total:
# - 15 min generation
# - 1h 45min submission (10-11 min each)
```

### Weekend Bulk Generation (100 apps)

```bash
# Saturday morning: Generate
python -m tools.bulk_application_generator \
  --search "Software Engineer" \
  --max-jobs 100 \
  --concurrent 5

# Saturday/Sunday: Submit
# Work through quick-apply sheet
# 10-12 hours total submission time
```

## Time Breakdown

### Per Application

**With Tools:**
- Material generation: 2-3 min (automated)
- Review materials: 1-2 min
- Open job page: 30 sec
- Copy/paste & customize: 3-4 min
- Fill additional fields: 2-3 min
- Submit: 1 min
- **Total: 10-12 minutes**

**Manual:**
- Read job description: 5 min
- Write resume: 10-15 min
- Write cover letter: 10-15 min
- Format and review: 5 min
- Submit: 5 min
- **Total: 35-45 minutes**

**Time Saved: 25-30 min per application!**

### Batch Sizes

| Batch Size | Generation Time | Submission Time | Total Time |
|------------|-----------------|-----------------|------------|
| 10 apps | 15 min | 2 hours | ~2.25 hours |
| 20 apps | 20 min | 4 hours | ~4.5 hours |
| 50 apps | 30 min | 10 hours | ~10.5 hours |
| 100 apps | 45 min | 20 hours | ~21 hours |

## Tips for Maximum Speed

### 1. Optimize Your Setup

```bash
# Create alias for faster access
echo 'alias quick-apply="python -m tools.one_click_workflow"' >> ~/.bashrc
source ~/.bashrc

# Now just:
quick-apply --positions "Engineer" --locations "Remote" --max-jobs 20
```

### 2. Use Browser Extensions

- **Auto-fill**: Use password managers for common fields
- **Multi-tab**: Keep materials in one tab, applications in others
- **Keyboard shortcuts**: Learn platform shortcuts (LinkedIn, Indeed)

### 3. Batch Similar Roles

```bash
# Day 1: Backend roles
quick-apply --positions "Backend Engineer" "Python Developer" --max-jobs 15

# Day 2: Full Stack roles
quick-apply --positions "Full Stack Developer" --max-jobs 15

# Faster to submit similar roles together
```

### 4. Set Time Limits

```bash
# Use a timer - don't spend more than 12 min per app
# Skip if it takes longer (edge cases, complex forms)
```

### 5. Prepare Templates

Save snippets for common questions:
- "Why do you want to work here?"
- "What's your salary expectation?"
- "Why are you leaving your current role?"

## Quick Apply Sheet Guide

The quick apply sheet (`quick_apply_sheet_*.md`) contains:

```markdown
## 1. Google - Software Engineer

- [ ] **Applied**
- **Link**: https://...
- **Location**: Remote
- **Resume**: `path/to/resume.md`
- **Cover Letter**: `path/to/cover_letter.md`

**Notes**: _____________________
```

**Workflow:**
1. Click link
2. Open resume file in split view
3. Copy sections as needed
4. Customize 1-2 lines if needed
5. Paste and submit
6. Check off
7. Move to next

## Comparison with Full Automation

### Our Approach (Recommended)

✅ **Pros:**
- Fast (5-8 apps/hour)
- High quality (LLM Council)
- Safe (no ToS violations)
- Control (you review and submit)
- Flexible (customize as needed)

❌ **Cons:**
- Still requires manual submission (~10 min each)
- Not fully automated

### Full Bot (AIHawk)

✅ **Pros:**
- Very fast (15-20 apps/hour)
- Fully automated

❌ **Cons:**
- Account ban risk
- Low quality (generic)
- Legal/ethical issues
- Fragile (breaks easily)
- No control

## Integration with Other Tools

Works seamlessly with existing tools:

```python
from tools import (
    OneClickApplicationWorkflow,
    JobApplicationSaver,
    Job,
    ConfigValidator
)

# Validate config
config = ConfigValidator.validate_config("config.yaml")

# Run workflow with config
workflow = OneClickApplicationWorkflow()
filter = JobSearchFilter.from_dict(config)
results = await workflow.search_and_generate(filter, max_jobs=20)

# Additional tracking
for result in results:
    if result['success']:
        # Add to tracking system
        tracker.add_application(result['application'])
```

## FAQ

**Q: How many applications can I generate at once?**
A: Practically unlimited, but recommend batches of 20-50 for manageability.

**Q: How long does generation take?**
A: ~3-5 minutes per job with 3-5 parallel. 20 jobs = ~20 minutes.

**Q: Will this get me banned from LinkedIn?**
A: No! This only generates materials. YOU submit manually through official channels.

**Q: Can I customize the generated materials?**
A: Yes! All materials are saved as markdown. Edit before submitting.

**Q: What if a job requires specific formats?**
A: Materials are in markdown. Copy/paste into their format or use converters.

**Q: Is this better than fully automated bots?**
A: Yes - better quality, safer, still 3-4x faster than manual.

## Related Documentation

- [Bulk Application Generator](../apps/portal-python/tools/bulk_application_generator.py)
- [One-Click Workflow](../apps/portal-python/tools/one_click_workflow.py)
- [Resume Generator](RESUME_GENERATOR.md)
- [AIHawk Tools](AIHAWK_TOOLS.md)
- [Full Automation Setup](AIHAWK_AUTOMATION_SETUP.md) (not recommended)
