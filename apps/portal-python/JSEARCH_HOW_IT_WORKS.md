# How JSearch API Works

## 🎯 TL;DR
**One API call returns FULL job details** - No second call needed!

## 📊 API Call Structure

### One Call = One Page = ~10 Complete Jobs

```
Single API Request
      ↓
JSearch searches: LinkedIn + Indeed + Glassdoor + ZipRecruiter
      ↓
Returns ~10 jobs with FULL details
      ↓
{
  "data": [
    {
      "job_id": "abc123",
      "job_title": "Senior Software Engineer",
      "employer_name": "Google",
      "job_description": "FULL description (2000+ words)...",
      "job_apply_link": "https://linkedin.com/jobs/...",
      "job_salary_min": 150000,
      "job_salary_max": 250000,
      "job_posted_at_datetime_utc": "2025-12-21T00:00:00Z",
      ...30+ other fields
    },
    ...9 more jobs
  ]
}
```

## ✅ What You Get in ONE Call

Each job includes:

### Basic Info
- ✓ Job ID
- ✓ Job Title
- ✓ Company Name
- ✓ Company Logo URL

### Location
- ✓ City, State, Country
- ✓ Latitude/Longitude
- ✓ Is Remote flag

### Job Details
- ✓ **FULL Job Description** (complete text, not truncated!)
- ✓ Employment Type (full-time, part-time, contract)
- ✓ Application Link (direct URL)
- ✓ Job Publisher (LinkedIn, Indeed, etc.)

### Salary (if available)
- ✓ Min Salary
- ✓ Max Salary
- ✓ Currency (USD, EUR, etc.)
- ✓ Period (YEAR, HOUR, etc.)

### Timeline
- ✓ Posted Date (timestamp & datetime)
- ✓ Expiration Date (if available)

### Requirements (if available)
- ✓ Required Skills
- ✓ Required Experience
- ✓ Education Level

### Highlights (if available)
- ✓ Qualifications
- ✓ Responsibilities
- ✓ Benefits

## 🔄 No Second Call Required!

Unlike some APIs (e.g., job boards that return IDs first), JSearch gives you **everything in one shot**:

```python
# ✅ JSearch: ONE call gets everything
response = requests.get("https://jsearch.p.rapidapi.com/search", params={
    "query": "Senior Software Engineer",
    "num_pages": "1"
})
jobs = response.json()["data"]
# Each job already has FULL description, salary, apply link, etc.

# ❌ Some other APIs: TWO calls needed
# Call 1: Get job IDs
ids = api.search("Senior Engineer")  # Returns: ["id1", "id2", ...]
# Call 2: Get details for each ID
for job_id in ids:
    details = api.get_job(job_id)  # Need separate call per job!
```

## 💰 API Usage Calculation

### Example Scenario
```
Query: "Senior Software Engineer Remote"
num_pages: 1
```

**API Calls Used**: 1 ✓
**Jobs Returned**: ~10 jobs with COMPLETE details
**Additional calls needed**: 0 ✓

### Multiple Pages
```
Query: "Senior Software Engineer Remote"
num_pages: 3
```

**API Calls Used**: 3 (one per page)
**Jobs Returned**: ~30 jobs with COMPLETE details
**Additional calls needed**: 0 ✓

## 📈 Efficiency Comparison

| API Type | Initial Call | Detail Calls | Total Calls | Your Scenario |
|----------|--------------|--------------|-------------|---------------|
| **JSearch** | 1 | 0 | **1** | ✅ 1 call = 10 complete jobs |
| LinkedIn API | 1 | 10 | 11 | ❌ 1 search + 10 detail calls |
| Indeed API | 1 | 10 | 11 | ❌ 1 search + 10 detail calls |

## 🎯 Your Current Setup

```python
# In job_search_service.py
params = {
    "query": keywords,
    "page": "1",
    "num_pages": "1",  # 1 page = 1 API call
    "date_posted": "3days"
}

response = await client.get("https://jsearch.p.rapidapi.com/search", ...)
data = response.json()

# data["data"] already contains FULL job details!
for job in data["data"]:
    title = job["job_title"]
    company = job["employer_name"]
    description = job["job_description"]  # FULL text!
    apply_link = job["job_apply_link"]    # Direct link!
    salary = job["job_min_salary"]        # Already included!
```

## 💡 Key Points for Your 200 API Limit

1. **Each search = 1 API call** (not 1 + 10 + 10...)
2. **Each call returns ~10 complete jobs**
3. **No need to fetch details separately**
4. **3 keywords × 1 call each = 3 API calls total** ✓

### Example Usage
```bash
# Run your efficient downloader
python download_jobs_efficient.py

# This uses:
# - 1 call for "Senior Software Engineer"
# - 1 call for "Staff Software Engineer"  
# - 1 call for "Principal Software Engineer"
# = 3 API calls total

# Returns: ~30 jobs with FULL details
# No additional calls needed!
```

## 🚀 Best Practices

### ✅ DO: Use `num_pages=1` for efficiency
```python
params = {
    "query": "Senior Engineer",
    "num_pages": "1"  # Just 1 page = 1 API call
}
```

### ✅ DO: Use date filters to reduce irrelevant results
```python
params = {
    "date_posted": "3days"  # Fresh jobs only
}
```

### ❌ DON'T: Request multiple pages if not needed
```python
params = {
    "num_pages": "10"  # This uses 10 API calls!
}
```

### ❌ DON'T: Make separate calls for job details
```python
# You already have everything! No need for:
for job in jobs:
    details = fetch_job_details(job["job_id"])  # Unnecessary!
```

## 📝 Real Example

Here's what ONE API call returns (abbreviated):

```json
{
  "status": "OK",
  "data": [
    {
      "job_id": "Gj12345abcde",
      "employer_name": "Google",
      "job_title": "Senior Software Engineer",
      "job_description": "We are seeking a talented Senior Software Engineer to join our team... (FULL 2000+ word description)",
      "job_apply_link": "https://www.google.com/about/careers/applications/...",
      "job_city": "Mountain View",
      "job_state": "CA",
      "job_country": "US",
      "job_posted_at_datetime_utc": "2025-12-21T08:30:00.000Z",
      "job_min_salary": 150000,
      "job_max_salary": 250000,
      "job_salary_currency": "USD",
      "job_salary_period": "YEAR",
      "job_employment_type": "FULLTIME",
      "job_publisher": "LinkedIn",
      "job_required_skills": ["Python", "Java", "AWS", "Kubernetes"],
      "job_highlights": {
        "Qualifications": ["BS in CS", "5+ years experience"],
        "Responsibilities": ["Design systems", "Lead projects"],
        "Benefits": ["Health insurance", "401k", "Stock options"]
      }
    },
    {
      "job_id": "Indeed789xyz",
      "employer_name": "Amazon",
      "job_title": "Staff Software Engineer",
      ...
    }
    // ...8 more complete jobs
  ]
}
```

## 🎯 Summary

**JSearch is super efficient:**
- ✅ **One call = Full details for ~10 jobs**
- ✅ **No additional API calls needed**
- ✅ **Perfect for limited API quotas**
- ✅ **Your 200 calls/month = up to 2,000 complete job listings!**

That's why your `download_jobs_efficient.py` script works so well - each of your 3 keywords uses just 1 API call and returns everything you need! 🚀
