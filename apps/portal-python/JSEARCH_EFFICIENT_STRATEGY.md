# Optimized Strategy for 200 API Requests/Month

With only **200 JSearch API requests per month**, you need to be strategic. Here's the optimal approach:

## 📊 Your Situation
- **API Limit**: 200 requests/month (free plan)
- **Search Keywords**: 3 (Senior, Staff, Principal Software Engineer)
- **Goal**: Download last 3 days of jobs efficiently

## ✅ Recommended Strategy

### Option 1: Efficient Daily Download (Best for Active Job Search)
```bash
cd /workspaces/ai-dev/apps/portal-python
python download_jobs_efficient.py
```

**Cost**: 3 API calls per run (1 per keyword)
**Returns**: ~30-40 jobs (10-15 per keyword)
**Frequency**: Can run **65 times per month** (195 API calls)
**Best for**: Daily job hunting (run once every 1-2 days)

### Option 2: Weekly Comprehensive Search
```bash
# Modify date_posted to "week" in the script
python download_jobs_efficient.py
```

**Cost**: 3 API calls per run
**Returns**: ~60-80 jobs 
**Frequency**: Can run **65 times per month**
**Best for**: Less frequent checking, broader results

### Option 3: Combined Keywords (Ultra Efficient)
Search all keywords in ONE API call:

```python
# Instead of 3 separate searches, combine:
keywords = "Senior OR Staff OR Principal Software Engineer"
# Cost: 1 API call
# Returns: ~10-15 jobs (all levels combined)
```

**Cost**: 1 API call
**Returns**: ~10-15 jobs
**Frequency**: Can run **200 times per month**
**Best for**: Daily monitoring with maximum API efficiency

## 🎯 Recommended Workflow

### Week 1-4: Daily Monitoring (Total: 12 API calls)
```bash
# Monday, Wednesday, Friday (3x per week)
cd /workspaces/ai-dev/apps/portal-python
python download_jobs_efficient.py
```

- **3 keywords × 3 runs/week × 4 weeks = 36 API calls**
- **Remaining: 164 API calls**

### As Needed: Deep Dive Searches
When you find an interesting company or want more results:
```bash
# Search specific companies
python download_jobs_efficient.py --keywords "Amazon Software Engineer"
python download_jobs_efficient.py --keywords "Google Senior Engineer"
```

## 📦 What You Get Per Run

### download_jobs_efficient.py Output:
```json
{
  "downloaded_at": "2025-12-21T10:30:00",
  "api_calls_used": 3,
  "total_jobs": 38,
  "unique_jobs": 35,
  "filtered_jobs": 28,
  "jobs": [...]
}
```

Each job includes:
- Title, Company, Location
- Full Description
- Application URL
- Salary (if available)
- Posted Date
- Source (LinkedIn, Indeed, Glassdoor, etc.)

## 🚀 Usage Instructions

### 1. Run the efficient downloader:
```bash
cd /workspaces/ai-dev/apps/portal-python
python download_jobs_efficient.py
```

### 2. Check results:
```bash
ls -lh outputs/jobs_last_3_days_*.json
```

### 3. Process downloaded jobs:
```bash
# View summary
cat outputs/jobs_last_3_days_*.json | jq '.filtered_jobs'

# Extract companies
cat outputs/jobs_last_3_days_*.json | jq '.jobs[].employer_name' | sort -u

# Filter high-salary jobs
cat outputs/jobs_last_3_days_*.json | jq '.jobs[] | select(.job_min_salary > 150000)'
```

## 💡 API Efficiency Tips

### 1. **Use date filters** (Already implemented ✓)
```python
date_posted="3days"  # Only recent jobs, less waste
```

### 2. **Combine similar searches**
Instead of:
- ❌ "Senior Software Engineer" (1 call)
- ❌ "Senior SWE" (1 call)  
- ❌ "Sr. Software Engineer" (1 call)

Use:
- ✅ "Senior Software Engineer" (1 call covers all variations)

### 3. **Cache results locally** (Already implemented ✓)
- Don't re-search the same day
- Keep a local database of seen jobs

### 4. **Batch process applications**
- Download jobs once
- Score/match/apply locally (no API calls)
- Apply to multiple jobs from single download

## 📈 API Usage Tracking

Add this to your `.env`:
```bash
# Track your usage
JSEARCH_MONTHLY_LIMIT=200
JSEARCH_CALLS_THIS_MONTH=0
JSEARCH_LAST_RESET=2025-12-01
```

Create a usage tracker:
```bash
echo "0" > /workspaces/ai-dev/apps/portal-python/.jsearch_usage
```

## 🎲 Fallback Options

If you run out of API calls:

### 1. **Use Remotive + Arbeitnow (Free, No Limit)**
```python
# In job_search_service.py, already includes:
await self._search_remotive(keywords, limit=200)
# Returns: ~50-100 remote jobs (tech startups)
```

### 2. **Wait for next month**
- API resets monthly
- Plan your searches

### 3. **Upgrade to paid plan**
- Basic: 500 requests/month ($9.99)
- Pro: 2,500 requests/month ($29.99)
- Ultra: 10,000 requests/month ($99.99)

## 📊 Comparison

| Strategy | API Calls | Jobs/Run | Runs/Month | Total Jobs/Month |
|----------|-----------|----------|------------|------------------|
| **3 Keywords × Last 3 Days** | 3 | ~35 | 65 | 2,275 |
| **Combined Keywords** | 1 | ~12 | 200 | 2,400 |
| **Weekly Search** | 3 | ~80 | 65 | 5,200 |

## 🎯 My Recommendation

For your situation (active job search, 3 keywords):

**Run 3x per week (Mon/Wed/Fri)**:
```bash
# Cron job or manual
cd /workspaces/ai-dev/apps/portal-python && python download_jobs_efficient.py
```

- **Cost**: 36 API calls/month
- **Returns**: ~420 jobs/month
- **Remaining**: 164 API calls for ad-hoc searches
- **Coverage**: All recent jobs (last 3 days, 3 checks per week)

This gives you excellent coverage while preserving 80%+ of your API quota for unexpected searches! 🚀

## 🔍 Next Steps

1. ✅ Run the script: `python download_jobs_efficient.py`
2. ✅ Review results in `outputs/` folder
3. ✅ Set up a schedule (manual or cron)
4. ✅ Track your API usage
5. ✅ Apply to jobs from downloaded data (no extra API calls!)
