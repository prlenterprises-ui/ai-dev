# Find Jobs Flow - Updated Strategy

## Overview
Updated the auto job apply flow to be more efficient with the 200 API calls/month limit by:
1. Limiting to **100 jobs maximum** per search
2. Processing queries **sequentially** (complete first query before moving to second)
3. **Skipping** job-details and salary API calls in initial download
4. Maintaining **24-hour cooldown** between searches

## Flow Details

### 1. Sequential Query Processing
**Before:** All queries searched in parallel, then deduplicated
**After:** Queries processed one at a time, deduplicating as we go

```
Query 1: Senior Software Engineer → 30 jobs found (30 new)
Query 2: Staff Software Engineer → 25 jobs found (18 new, 7 duplicates)  
Query 3: Principal Software Engineer → 20 jobs found (15 new, 5 duplicates)
...continues until 100 jobs reached
```

**Benefits:**
- Stops early if 100 jobs reached (saves API calls)
- Real-time deduplication (no wasted processing)
- Clear progress reporting per query

### 2. 100 Job Limit
Hard limit of 100 jobs per "Find Jobs" run.

**Rationale:**
- Each query can return up to 100 jobs (10 pages × 10 jobs/page)
- With 3 queries, worst case = 30 API calls (3 queries × 10 pages)
- With 200 calls/month, you can run ~6-7 full searches
- Most queries will exhaust results before 10 pages

**Implementation:**
- `MAX_JOBS = 100` constant
- Loop breaks when limit reached
- Jobs deduplicated inline

### 3. API Call Optimization
**Skipped in initial download:**
- ❌ `/job-details` endpoint (1 call per job)
- ❌ `/estimated-salary` endpoint (1 call per job)

**What we still call:**
- ✅ `/search` endpoint (multiple pages per query)

**Savings Example:**
- Before: 10 jobs = 1 search + 10 details + 10 salary = **21 API calls**
- After: 100 jobs = 30 search only = **30 API calls**
- Old way for 100 jobs would use: 1 + 100 + 100 = **201 calls** (over limit!)

### 4. Smart Pagination
The `job_search_service.py` now calculates optimal pages:

```python
# Request 100 jobs → 10 pages
num_pages = min(10, (limit + 9) // 10)
```

- Automatically requests the right number of pages
- Stops if fewer jobs returned (end of results)
- Each page = 1 API call, ~10 jobs

### 5. 24-Hour Cooldown (Unchanged)
**Status check:** `/api/jobs/search-status`
- Checks `.jsearch_tracking.json` 
- Returns `can_search: false` if < 24 hours since last run
- UI disables "Find Jobs" button with countdown

**Tracking updates:**
```json
{
  "last_run": "2025-12-21T10:30:00",
  "total_api_calls": 45,
  "runs": [
    {
      "timestamp": "2025-12-21T10:30:00",
      "api_calls": 30,
      "queries_searched": 3,
      "jobs_found": 95,
      "jobs_processed": 95,
      "jobs_matched": 42,
      "date_filter": "3days"
    }
  ]
}
```

## API Call Budget

### Scenario: 3 Queries with 100 Job Limit

| Scenario | Queries | API Calls | Jobs | Searches/Month |
|----------|---------|-----------|------|----------------|
| Best case (few results) | 3 | 9 | 27 | ~22 |
| Average case | 3 | 18 | 65 | ~11 |
| Worst case (max pages) | 3 | 30 | 100 | ~6 |

### Adding More Queries

With 100 job limit, additional queries may not execute if limit reached:

| Queries | Jobs/Query | Likely API Calls | Searches/Month |
|---------|------------|------------------|----------------|
| 3 queries | ~33 each | 9-18 | 11-22 |
| 5 queries | ~20 each | 15-30 | 6-13 |
| 10 queries | ~10 each | 10-50 | 4-20 |

## Configuration Example

```json
{
  "jsearch": {
    "X-RapidAPI-Key": "your-key-here",
    "location": "Remote",
    "remote_jobs_only": true,
    "date_posted": "3days",
    "queries": [
      "Senior Software Engineer",
      "Staff Software Engineer",
      "Principal Software Engineer"
    ]
  }
}
```

## UI Behavior

### Before Search
1. Check `/api/jobs/search-status`
2. If `can_search: false`, disable button and show:
   ```
   ⚠️ Last search was X hours ago. 
   Button will be enabled in Y hours.
   ```

### During Search
Real-time SSE updates:
```
🔍 Query 1/3: Senior Software Engineer in Remote...
✓ Query 1: Found 30 jobs (30 new, 0 duplicates). Total: 30/100
🔍 Query 2/3: Staff Software Engineer in Remote...
✓ Query 2: Found 25 jobs (18 new, 7 duplicates). Total: 48/100
...
✓ Search complete: 95 unique jobs from 3 queries
```

### After Search
Button disabled for 24 hours, tracking file updated.

## Key Files Modified

1. **[jobs_routes.py](apis/jobs_routes.py#L150-L200)**
   - Sequential query processing with 100 job limit
   - Inline deduplication
   - Enhanced tracking updates

2. **[job_search_service.py](ai/job_search_service.py#L105-L115)**
   - Smart `num_pages` calculation
   - Supports up to 100 jobs per query (10 pages)

3. **[database.py](python/database.py)**
   - Stores complete JSON responses (unchanged)
   - job-details and salary fields remain NULL initially

## Future Enhancements

### Option 1: On-Demand Details Fetch
Add button in UI: "Get Full Details" for specific jobs
- Fetches `/job-details` and `/estimated-salary` on demand
- Only uses API calls for jobs user is interested in

### Option 2: Smart Details Fetch
Automatically fetch details for high-match jobs (>80% score)
- Uncomment code in `jobs_routes.py` lines 252-263
- Only fetches for matched jobs, not all 100

### Option 3: Weekly Full Scan
Different strategies for different frequencies:
- Daily: 100 jobs, search only (30 calls)
- Weekly: 50 jobs with details (150 calls)
- Monthly: 25 jobs with full data (75 calls)

## Testing

```bash
# Check status (should show can_search: true initially)
curl http://localhost:8000/api/jobs/search-status

# Run search
curl -X POST http://localhost:8000/api/jobs/find

# Check status again (should show can_search: false for 24 hours)
curl http://localhost:8000/api/jobs/search-status

# View tracking file
cat .jsearch_tracking.json
```

## Summary

✅ **Efficient:** Uses 9-30 API calls per search (down from potential 201+)
✅ **Smart:** Stops at 100 jobs or when queries exhausted
✅ **Sequential:** Processes queries in order with live feedback
✅ **Protected:** 24-hour cooldown prevents over-use
✅ **Extensible:** Can add on-demand details fetching later
