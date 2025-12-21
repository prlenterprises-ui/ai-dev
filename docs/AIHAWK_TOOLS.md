# AIHawk Tools Integration

The following tools have been extracted and adapted from AIHawk into standalone utilities in the `tools/` folder.

## Tools Converted

### 1. Job Application Saver ([job_application_saver.py](../apps/portal-python/tools/job_application_saver.py))

**Purpose**: Save job applications with structured file organization.

**Features**:
- Organized by company name
- Saves resume, cover letter, job description
- Metadata tracking with JSON
- List and query saved applications

**Usage**:
```bash
cd apps/portal-python

# Save an application
python -m tools.job_application_saver \
  --company "Google" \
  --role "Software Engineer" \
  --job-desc path/to/job.txt \
  --resume path/to/resume.md \
  --cover-letter path/to/cover_letter.md

# List all applications
python -m tools.job_application_saver --list
```

**Python API**:
```python
from tools.job_application_saver import JobApplicationSaver

saver = JobApplicationSaver()
app_dir = saver.save_application(
    company="Google",
    role="Software Engineer",
    job_description="...",
    resume_content="...",
    cover_letter_content="..."
)
```

### 2. Job Data Models ([job_models.py](../apps/portal-python/tools/job_models.py))

**Purpose**: Structured data models for jobs and applications.

**Classes**:
- **`Job`**: Represents a job posting with all details
- **`JobApplication`**: Tracks application status and materials
- **`JobSearchFilter`**: Filter criteria for job searches

**Usage**:
```python
from tools.job_models import Job, JobApplication, JobSearchFilter

# Create a job
job = Job(
    role="Senior Python Engineer",
    company="Acme Corp",
    location="Remote",
    link="https://...",
    description="...",
    remote=True,
    job_type="full_time"
)

# Format as markdown
print(job.formatted_job_information())

# Create application
application = JobApplication(
    job=job,
    resume_path="path/to/resume.pdf"
)

# Update status
application.update_status("submitted", "Applied via LinkedIn")
application.add_interview("phone", "2025-01-15", "Jane Smith", "Technical screen")

# Search filter
filter = JobSearchFilter(
    positions=["Software Engineer", "Python Developer"],
    locations=["Remote", "San Francisco"],
    remote=True,
    company_blacklist=["Bad Company"],
    title_blacklist=["junior", "intern"]
)

if filter.matches_job(job):
    print("Job matches criteria!")
```

### 3. Config Validator ([config_validator.py](../apps/portal-python/tools/config_validator.py))

**Purpose**: Validate YAML configuration files for job search settings.

**Features**:
- Validates experience levels, job types, locations
- Checks blacklists and filters
- Email validation
- Comprehensive error messages

**Usage**:
```bash
cd apps/portal-python

# Validate config file
python -m tools.config_validator path/to/config.yaml

# Verbose output
python -m tools.config_validator path/to/config.yaml --verbose
```

**Config File Example**:
```yaml
# job_search_config.yaml
remote: true

experience_level:
  entry: false
  mid_senior_level: true
  director: false

job_types:
  full_time: true
  contract: true
  part_time: false

date:
  all_time: false
  month: true
  week: false

positions:
  - Software Engineer
  - Python Developer
  - Backend Engineer

locations:
  - Remote
  - San Francisco, CA
  - New York, NY

distance: 50

company_blacklist:
  - BadCompany Inc
  
title_blacklist:
  - junior
  - intern

min_salary: 120000
max_salary: 200000
```

**Python API**:
```python
from tools.config_validator import ConfigValidator
from pathlib import Path

try:
    config = ConfigValidator.validate_config(Path("config.yaml"))
    print("✅ Valid configuration")
except ConfigError as e:
    print(f"❌ Error: {e}")
```

## Integration with Resume Generator

These tools work seamlessly with the Resume Generator:

```python
from tools.resume_generator import ResumeGenerator
from tools.job_application_saver import JobApplicationSaver
from tools.job_models import Job, JobApplication
import asyncio

async def full_workflow():
    # 1. Create job object
    job = Job(
        role="Senior Software Engineer",
        company="Acme Corp",
        location="Remote",
        description="...",
        remote=True
    )
    
    # 2. Generate materials
    generator = ResumeGenerator()
    result = await generator.generate_full_application(
        job_description=job.description,
        company_name=job.company,
        role_title=job.role
    )
    
    # 3. Save application
    saver = JobApplicationSaver()
    app_dir = saver.save_application(
        company=job.company,
        role=job.role,
        job_description=job.description,
        resume_content=result['resume'],
        cover_letter_content=result['cover_letter']
    )
    
    # 4. Create application record
    application = JobApplication(
        job=job,
        resume_path=str(app_dir / "resume.md"),
        cover_letter_path=str(app_dir / "cover_letter.md")
    )
    application.update_status("submitted")
    
    print(f"✅ Complete workflow finished! Saved to {app_dir}")

asyncio.run(full_workflow())
```

## Differences from Original AIHawk

| Feature | AIHawk Original | Our Tools |
|---------|----------------|-----------|
| **Automation** | Selenium bot for auto-applying | Manual/scripted |
| **Focus** | Volume (1000s of applications) | Quality (targeted) |
| **LinkedIn** | Automated LinkedIn bot | No automation |
| **Dependencies** | Heavy (Selenium, browser drivers) | Lightweight |
| **Use Case** | Spray and pray | Thoughtful applications |
| **Integration** | Standalone tool | Part of ai-dev ecosystem |

## File Structure

```
apps/portal-python/tools/
├── __init__.py
├── resume_generator.py        # Resume & cover letter with LLM Council
├── job_application_saver.py   # Save applications (from AIHawk)
├── job_models.py              # Data models (from AIHawk)
└── config_validator.py        # Config validation (from AIHawk)
```

## Benefits

✅ **Modular**: Each tool works independently  
✅ **Type-Safe**: Dataclasses with proper typing  
✅ **CLI + API**: Use from command line or Python  
✅ **Documented**: Clear docstrings and examples  
✅ **Integrated**: Works with existing workflow  
✅ **Lightweight**: No heavy dependencies  
✅ **Testable**: Easy to unit test  

## Example Workflow

```bash
# 1. Validate your search config
python -m tools.config_validator data/job_search_config.yaml

# 2. Generate resume and cover letter
python generate_resume.py \
  --company "Acme Corp" \
  --role "Senior Engineer" \
  --job-desc path/to/job.txt

# 3. Application is auto-saved via resume generator

# 4. List all applications
python -m tools.job_application_saver --list
```

## Future Enhancements

- [ ] Job scraper tool (without Selenium automation)
- [ ] Application tracker dashboard
- [ ] Email template generator
- [ ] Interview prep tool
- [ ] Salary negotiation assistant
- [ ] Network graph of applications
- [ ] Analytics and reporting

## Related Documentation

- [Resume Generator](RESUME_GENERATOR.md)
- [Job Search Workflow](../data/oppertunities/_tracker.md)
- [External Tools](../EXTERNAL_APPS.md)
