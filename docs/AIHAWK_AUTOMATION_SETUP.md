# AIHawk Automation Setup Guide

For users who want full LinkedIn automation (at your own risk).

## ⚠️ Important Warnings

**Before proceeding, understand the risks:**

1. **Account Ban Risk**: LinkedIn actively detects and bans accounts using bots
2. **Terms of Service**: This violates LinkedIn's ToS
3. **Legal Liability**: Could have legal consequences
4. **Reputation Risk**: Mass applications can damage your professional reputation
5. **Detection**: LinkedIn uses sophisticated bot detection

**Proceed only if you:**
- Accept full responsibility
- Are willing to risk your LinkedIn account
- Understand the ethical implications
- Have read and accepted all risks

## Setup Steps

### 1. Prerequisites

```bash
# Python 3.11+
python --version

# Chrome browser installed
google-chrome --version

# ChromeDriver will be installed automatically
```

### 2. Install AIHawk Dependencies

```bash
cd external/Jobs_Applier_AI_Agent_AIHawk

# Install required packages
pip install -r requirements.txt

# Additional packages if needed
pip install selenium webdriver-manager python-dotenv pyyaml
```

### 3. Configure Data Folder

```bash
# Copy example data folder
cp -r data_folder_example data_folder

# Edit configuration files
cd data_folder
```

### 4. Configure Files

#### `secrets.yaml`
```yaml
# LinkedIn credentials
llm_api_key: "your-openai-api-key"

# Email for notifications (optional)
email:
  sender: "your-email@gmail.com"
  password: "your-app-password"
  recipient: "your-email@gmail.com"
```

#### `config.yaml`
```yaml
# Remote preference
remote: true

# Experience levels you're interested in
experience_level:
  internship: false
  entry: false
  associate: false
  mid_senior_level: true
  director: false
  executive: false

# Job types
job_types:
  full_time: true
  contract: true
  part_time: false
  temporary: false
  internship: false
  other: false
  volunteer: false

# Date posted filter
date:
  all_time: false
  month: true
  week: false
  24_hours: false

# Positions to search for
positions:
  - Software Engineer
  - Python Developer
  - Backend Engineer

# Locations to search
locations:
  - United States
  - Remote

# Search distance (miles)
distance: 50

# Company blacklist (companies to avoid)
company_blacklist:
  - BadCompany Inc
  - Another Bad Company

# Title blacklist (keywords to avoid)
title_blacklist:
  - junior
  - intern
  - unpaid

# Location blacklist
location_blacklist:
  - North Korea
```

#### `plain_text_resume.yaml`
```yaml
personal_information:
  name: "Your Name"
  surname: "Your Surname"
  date_of_birth: "01/01/1990"
  country: "USA"
  city: "San Francisco"
  address: "123 Main St"
  zip_code: "94101"
  phone_prefix: "+1"
  phone: "555-1234"
  email: "your.email@gmail.com"
  github: "https://github.com/yourusername"
  linkedin: "https://linkedin.com/in/yourusername"

self_identification:
  gender: "Male/Female/Other"
  pronouns: "He/Him"
  veteran: "No"
  disability: "No"
  ethnicity: "Prefer not to say"

legal_authorization:
  eu_work_authorization: "Yes"
  us_work_authorization: "Yes"
  requires_us_visa: "No"
  requires_us_sponsorship: "No"
  requires_eu_visa: "No"
  legally_allowed_to_work_in_eu: "Yes"
  legally_allowed_to_work_in_us: "Yes"
  requires_eu_sponsorship: "No"

work_preferences:
  remote_work: "Yes"
  in_person_work: "No"
  open_to_relocation: "No"
  willing_to_complete_assessments: "Yes"
  willing_to_undergo_drug_tests: "Yes"
  willing_to_undergo_background_checks: "Yes"

education_details:
  - education_level: "Bachelor's Degree"
    institution: "University Name"
    field_of_study: "Computer Science"
    final_evaluation_grade: "3.8/4.0"
    start_date: "09/2015"
    year_of_completion: "05/2019"
    exam:
      Algorithms: "A"
      Data Structures: "A"
      Software Engineering: "A-"

experience_details:
  - position: "Senior Software Engineer"
    company: "Tech Company"
    employment_period: "2019-Present"
    location: "San Francisco, CA"
    industry: "Technology"
    key_responsibilities:
      - responsibility_1: "Led development of microservices architecture"
      - responsibility_2: "Mentored junior developers"
      - responsibility_3: "Improved system performance by 40%"
    skills_acquired:
      - "Python"
      - "AWS"
      - "Docker"
      - "Kubernetes"

projects:
  - name: "Open Source Project"
    description: "Description of your project"
    link: "https://github.com/yourusername/project"

languages:
  - language: "English"
    proficiency: "Native"
  - language: "Spanish"
    proficiency: "Professional"
```

### 5. Run AIHawk

```bash
cd external/Jobs_Applier_AI_Agent_AIHawk

# First time (will prompt for LinkedIn credentials)
python main.py

# You'll need to log in to LinkedIn manually in the browser
# The bot will then take over
```

### 6. Monitor Progress

The bot will:
1. Search for jobs based on your criteria
2. Apply filters and blacklists
3. Generate tailored resumes and cover letters
4. Fill out application forms automatically
5. Submit applications
6. Save all data to `job_applications/` folder

## Tips for Safer Usage

### 1. Use Delays
Edit `config.py` to add delays between actions:
```python
MINIMUM_WAIT_TIME_IN_SECONDS = 120  # Wait 2 min between applications
```

### 2. Limit Applications
```python
JOB_MAX_APPLICATIONS = 5  # Apply to max 5 jobs per session
```

### 3. Run in Short Sessions
- Don't run for hours continuously
- Take breaks between sessions
- Spread applications over days/weeks

### 4. Use a Dedicated Account
- Consider using a secondary LinkedIn account
- Don't use your primary professional account

### 5. Monitor and Stop if Detected
- Watch for warning emails from LinkedIn
- Stop immediately if you see suspicious activity warnings
- LinkedIn may ask for phone verification - this is a warning sign

## Alternative: Semi-Automated Approach

**Much safer and still fast:**

```bash
# Use our new tools instead!

# 1. Search and generate 20 applications automatically
python -m tools.one_click_workflow \
  --positions "Software Engineer" "Python Developer" \
  --locations "Remote" \
  --max-jobs 20 \
  --open-browser 5

# 2. Materials are ready - just copy/paste and submit
# Takes ~10 min per application = 3-4 hours for 20 jobs
```

## Comparison

| Approach | Speed | Risk | Quality | Recommendation |
|----------|-------|------|---------|----------------|
| **Full AIHawk Bot** | 17 apps/hour | ⚠️ Very High | Low | Not recommended |
| **Our One-Click** | 6-8 apps/hour | ✅ Very Low | High | **Recommended** |
| **Manual** | 2-3 apps/hour | ✅ None | Highest | For top choices |

## Troubleshooting

### Bot Detected
- **Solution**: Stop immediately, wait 24-48 hours
- Use longer delays
- Reduce applications per day

### ChromeDriver Issues
```bash
# Reinstall ChromeDriver
pip install --upgrade webdriver-manager
```

### LinkedIn Login Issues
- Make sure 2FA is disabled (or handle manually)
- Clear browser cache
- Use incognito mode

### Application Errors
- Check logs in `data_folder/`
- Verify your resume YAML is complete
- Check LinkedIn hasn't changed their UI

## Legal Disclaimer

This guide is for educational purposes only. By using AIHawk automation:

- You accept all risks and liability
- You understand this violates LinkedIn's Terms of Service
- You acknowledge potential account suspension/ban
- You take full responsibility for any consequences
- The authors/maintainers are not liable for any damages

**We strongly recommend using our safer semi-automated tools instead.**

## Better Alternative

Instead of full automation, use our tools:

```bash
# Generate 50 applications in one command
python -m tools.bulk_application_generator \
  --search "Python Developer" \
  --max-jobs 50 \
  --concurrent 5

# Get a quick-apply sheet
# Then spend ~6-8 hours submitting (12 min each)
# Much safer, better quality, still very fast!
```

**Bottom line**: Quality targeted applications >>> Mass automated spam
