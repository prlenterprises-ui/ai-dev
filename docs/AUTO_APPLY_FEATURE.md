# Automated Job Application Feature

## Overview

The Auto-Apply feature combines job search, resume tailoring, and application generation into a single automated pipeline. It searches multiple job boards, analyzes requirements, and generates perfectly matched resumes and cover letters for each position.

## Architecture

### Backend Components

1. **Job Search Service** (`ai/job_search_service.py`)
   - Searches multiple job boards (Remotive, Arbeitnow)
   - Returns unified job results
   - Can be extended with additional job board integrations

2. **Job Application Pipeline** (`ai/job_application_pipeline.py`)
   - Orchestrates the full automation workflow
   - Ranks jobs by relevance
   - Integrates with Jobbernaut for document generation
   - Tracks application status in database
   - Streams real-time progress updates

3. **REST API Endpoints** (`apis/rest_routes.py`)
   - `POST /api/jobs/auto-apply` - Start the pipeline
   - `GET /api/stream/auto-apply/{id}` - Stream progress via SSE
   - `GET /api/jobs/applications` - List generated applications

### Frontend Component

- **AutoJobApply Page** (`apps/portal-ui/src/pages/AutoJobApply.tsx`)
  - Job search form with keywords, location, limits
  - Real-time progress tracking
  - Activity log with stage-by-stage updates
  - List of generated applications with download links

## Pipeline Flow

```
1. User Input
   ↓
2. Job Search (Multiple boards in parallel)
   ↓
3. Rank & Filter Jobs
   ↓
4. For Each Job:
   a. Analyze Requirements
   b. Generate Tailored Resume (Jobbernaut)
   c. Generate Cover Letter (Jobbernaut)
   d. Save Documents
   e. Track in Database
   ↓
5. Return Results
```

## Usage

### Via UI

1. Navigate to "Auto Apply" in the navigation
2. Enter job keywords (e.g., "Senior Software Engineer, Python")
3. Optionally specify location
4. Set maximum number of applications
5. Click "Start Auto-Apply"
6. Watch real-time progress
7. Download generated documents

### Via API

```bash
# Start pipeline
curl -X POST http://localhost:8000/api/jobs/auto-apply \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "Senior Software Engineer",
    "location": "Remote",
    "max_applications": 10,
    "auto_apply": false
  }'

# Stream progress (Server-Sent Events)
curl -N http://localhost:8000/api/stream/auto-apply/{pipeline_id}?keywords=...

# List applications
curl http://localhost:8000/api/jobs/applications?status=completed
```

## Database Schema

```sql
CREATE TABLE job_applications (
    id INTEGER PRIMARY KEY,
    job_title TEXT NOT NULL,
    company TEXT NOT NULL,
    job_description TEXT,
    job_url TEXT,
    status TEXT DEFAULT 'pending',  -- pending, in_progress, completed, failed
    resume_url TEXT,
    cover_letter_url TEXT,
    match_score REAL,
    notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Job Board Integrations

### Current Integrations

1. **Remotive** (https://remotive.com/api)
   - Remote jobs worldwide
   - Tech-focused positions
   - Free API, no rate limits

2. **Arbeitnow** (https://arbeitnow.com/api)
   - Remote jobs in Europe & US
   - Multiple industries
   - Free API, no authentication

### Adding New Job Boards

To add a new job board:

1. Create a new method in `JobSearchService`:
```python
async def _search_newboard(self, keywords: str, limit: int = 20) -> List[JobSearchResult]:
    # Implementation here
    pass
```

2. Add it to the parallel search in `search_jobs()`:
```python
tasks = [
    self._search_remotive(keywords, limit=20),
    self._search_arbeitnow(keywords, limit=20),
    self._search_newboard(keywords, limit=20),  # Add here
]
```

## Jobbernaut Integration

The pipeline uses the existing Jobbernaut service for document generation:

- **12-Step Pipeline**: Job analysis → Company research → Resume tailoring → PDF generation
- **AI-Powered**: Uses LLM council for intelligent matching
- **LaTeX Templates**: Professional, ATS-optimized formatting
- **Streaming Progress**: Real-time updates during generation

## Future Enhancements

### Phase 1 (Current)
- ✅ Multi-board job search
- ✅ Resume/cover letter generation
- ✅ Progress tracking
- ✅ Document storage

### Phase 2 (Planned)
- [ ] Automatic application submission (requires browser automation)
- [ ] LinkedIn integration
- [ ] Indeed API integration
- [ ] Email notifications
- [ ] Application follow-up reminders

### Phase 3 (Future)
- [ ] Interview scheduling
- [ ] Offer tracking
- [ ] Salary negotiation insights
- [ ] Career analytics dashboard

## Configuration

### Environment Variables

```bash
# Job Search
JOB_SEARCH_TIMEOUT=30  # Request timeout in seconds
JOB_SEARCH_MAX_RESULTS=50  # Max results per search

# Jobbernaut (for document generation)
POE_API_KEY=your_poe_api_key
MASTER_RESUME_PATH=path/to/resume.json

# Database
DATABASE_URL=sqlite+aiosqlite:///./portal.db  # or PostgreSQL for production
```

## Limitations

1. **Auto-Submit**: Currently generates documents only; manual submission required
2. **Job Boards**: Limited to boards with public APIs (no LinkedIn/Indeed scraping)
3. **Rate Limits**: Respects API rate limits; may take time for large batches
4. **ATS Compatibility**: Generated documents are ATS-optimized but not guaranteed to pass all systems

## Testing

```bash
# Run backend tests
cd apps/portal-python
pytest test_integration.py -k "job_application"

# Manual API test
python -c "
import asyncio
from ai.job_search_service import JobSearchService

async def test():
    service = JobSearchService()
    jobs = await service.search_jobs('Python Developer', limit=5)
    for job in jobs:
        print(f'{job.title} at {job.company}')

asyncio.run(test())
"
```

## Support

For issues or feature requests:
- Check logs in `apps/portal-python/logs/`
- Review activity log in UI for pipeline errors
- Ensure POE API key is configured for document generation
- Verify job board APIs are accessible

## Credits

Built on top of:
- **Jobbernaut** - Resume tailoring engine
- **Resume Matcher** - ATS analysis
- **Remotive** & **Arbeitnow** - Job board APIs
- **AIHawk** - Inspiration for automation workflow
