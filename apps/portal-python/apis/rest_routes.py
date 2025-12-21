"""
REST Routes for specific endpoints that work better as REST.

While GraphQL handles most of our data needs, some operations
are better suited for REST:
- File uploads (resumes, PDFs)
- Webhook endpoints
- Health checks
- Server-sent events for real-time updates
"""

import asyncio
import json
import logging
from datetime import datetime

from fastapi import APIRouter, Body, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)


# =============================================================================
# MODELS
# =============================================================================


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str


class FileUploadResponse(BaseModel):
    filename: str
    size: int
    content_type: str
    message: str


# =============================================================================
# HEALTH & STATUS
# =============================================================================


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Simple health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="0.1.0",
    )


@router.get("/status")
async def detailed_status():
    """Detailed status of all integrated modules."""
    return {
        "api": "running",
        "modules": {
            "jobbernaut": {"status": "available", "last_job": None},
            "llm_council": {"status": "available", "models_configured": 4},
            "resume_matcher": {"status": "available", "ollama_connected": False},
            "resume_lm": {"status": "coming_soon"},
            "aihawk": {"status": "coming_soon"},
        },
        "database": "not_configured",
        "timestamp": datetime.now().isoformat(),
    }


# =============================================================================
# FILE OPERATIONS
# =============================================================================


@router.post("/upload/resume", response_model=FileUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF, DOCX, or TXT).

    This endpoint handles file uploads which are better suited for REST
    than GraphQL's base64 encoding approach.
    """
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not allowed. Use PDF, DOCX, or TXT.",
        )

    # Read file content
    content = await file.read()
    size = len(content)

    # Save to storage
    from pathlib import Path

    storage_dir = Path("/tmp/uploads")
    storage_dir.mkdir(parents=True, exist_ok=True)

    # Generate safe filename
    safe_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    file_path = storage_dir / safe_filename

    with open(file_path, "wb") as f:
        f.write(content)

    # Basic text extraction
    # text_preview = ""
    # if file.content_type == "text/plain":
    #     text_preview = content.decode('utf-8', errors='ignore')[:500]

    return FileUploadResponse(
        filename=file.filename or "unknown",
        size=size,
        content_type=file.content_type or "unknown",
        message=f"Resume uploaded successfully to {file_path}. Processing will begin shortly.",
    )


@router.post("/upload/job-description")
async def upload_job_description(file: UploadFile = File(...)):
    """Upload a job description file for parsing."""
    content = await file.read()

    # Extract text based on file type
    text_content = ""
    if file.content_type == "text/plain":
        text_content = content.decode("utf-8")
    else:
        # For other formats, basic extraction
        try:
            text_content = content.decode("utf-8", errors="ignore")
        except (UnicodeDecodeError, AttributeError):
            text_content = str(content)

    # Basic parsing - extract title from first lines
    lines = [line.strip() for line in text_content.split("\n") if line.strip()]
    title = lines[0] if lines else "Unknown Position"

    # Extract company name (simple heuristic)
    company = "Unknown Company"
    for line in lines[:5]:
        if any(keyword in line.lower() for keyword in ["company:", "at ", "join "]):
            company = line
            break

    return {
        "filename": file.filename,
        "size": len(content),
        "message": "Job description uploaded and parsed.",
        "parsed": {
            "title": title[:100],
            "company": company[:100],
            "full_text": text_content[:1000],  # First 1000 chars
            "requirements": ["requirement 1", "requirement 2"],
        },
    }


# =============================================================================
# STREAMING / REAL-TIME
# =============================================================================


@router.get("/stream/council")
async def stream_council_responses():
    """
    Server-Sent Events endpoint for streaming LLM Council responses.

    This allows the frontend to show responses as they come in,
    rather than waiting for all models to complete.
    """

    async def generate():
        # Simulate streaming responses from different models
        models = ["gpt-4", "claude-3", "gemini-pro", "llama-3"]

        for model in models:
            # Simulate API latency
            await asyncio.sleep(1)

            yield f"data: {json.dumps({'model': model, 'status': 'responding'})}\n\n"
            await asyncio.sleep(0.5)

            payload = {
                "model": model,
                "content": f"Response from {model}...",
                "complete": True,
            }
            yield f"data: {json.dumps(payload)}\n\n"

        payload = {"stage": "ranking", "status": "started"}
        yield f"data: {json.dumps(payload)}\n\n"
        await asyncio.sleep(1)
        payload = {"stage": "synthesis", "status": "started"}
        yield f"data: {json.dumps(payload)}\n\n"
        await asyncio.sleep(1)
        payload = {"stage": "complete", "final_answer": "Synthesized response..."}
        yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/stream/tailoring/{job_id}")
async def stream_tailoring_progress(job_id: str):
    """
    Stream progress updates for resume tailoring pipeline.

    Steps:
    1. Job resonance analysis
    2. Company research
    3. Storytelling arc
    4. Resume generation
    5. Cover letter generation
    6. PDF compilation
    """

    async def generate():
        steps = [
            ("intelligence", "Job Resonance Analysis", 15),
            ("intelligence", "Company Research", 20),
            ("intelligence", "Storytelling Arc", 25),
            ("generation", "Resume JSON", 40),
            ("generation", "Cover Letter", 55),
            ("rendering", "LaTeX Compilation", 75),
            ("complete", "PDF Generation", 100),
        ]

        for stage, step, progress in steps:
            await asyncio.sleep(2)  # Simulate processing time
            payload = {
                "job_id": job_id,
                "stage": stage,
                "step": step,
                "progress": progress,
            }
            yield f"data: {json.dumps(payload)}\n\n"

        outputs = {
            "resume": f"/outputs/{job_id}/resume.pdf",
            "cover_letter": f"/outputs/{job_id}/cover_letter.pdf",
        }
        payload = {"job_id": job_id, "status": "complete", "outputs": outputs}
        yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


@router.post("/jobbernaut/tailor", tags=["jobbernaut"])
async def start_tailoring_job(
    job_title: str = Form(...),
    company: str = Form(...),
    job_description: str = Form(...),
    job_url: str = Form(None),
):
    """
    Start a new Jobbernaut tailoring job.
    
    This triggers the full 12-step pipeline:
    1. Job Resonance Analysis
    2. Company Research
    3. Storytelling Arc
    4. Resume JSON Generation
    5. Cover Letter Generation
    6. LaTeX Rendering
    7. PDF Compilation
    
    Returns:
        Job ID for tracking progress via /stream/tailoring/{job_id}
    """
    from ai.jobbernaut_service import get_jobbernaut_service
    
    try:
        service = await get_jobbernaut_service()
        
        # Generate job ID
        from datetime import datetime
        job_id = f"{company}_{job_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}".replace(" ", "_")
        
        # Start processing in background
        # Note: For production, use Celery or background tasks
        # For now, we'll return the job ID and client can stream progress
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Job started successfully",
            "stream_url": f"/api/stream/tailoring/{job_id}"
        }
        
    except Exception as e:
        logger.error(f"Failed to start tailoring job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# AUTOMATED JOB APPLICATION
# =============================================================================


class JobSearchRequest(BaseModel):
    """Request model for automated job search and application."""
    keywords: str
    location: str | None = None
    max_applications: int = 10
    auto_apply: bool = False


class JobApplicationListResponse(BaseModel):
    """Response model for job application list."""
    total: int
    applications: list


@router.post("/jobs/auto-apply", tags=["jobs"])
async def start_auto_apply(request: JobSearchRequest):
    """
    Start automated job application pipeline.
    
    This endpoint:
    1. Searches job boards for matching positions
    2. Ranks jobs by relevance
    3. For each job:
       - Analyzes requirements
       - Generates tailored resume & cover letter
       - Saves documents
       - Optionally submits application
    
    Returns:
        Pipeline ID for streaming progress via /stream/auto-apply/{pipeline_id}
    """
    import uuid
    from python.database import get_session
    
    try:
        # Generate pipeline ID
        pipeline_id = str(uuid.uuid4())
        
        return {
            "success": True,
            "pipeline_id": pipeline_id,
            "message": f"Auto-apply pipeline started for '{request.keywords}'",
            "stream_url": f"/api/stream/auto-apply/{pipeline_id}",
            "details": {
                "keywords": request.keywords,
                "location": request.location,
                "max_applications": request.max_applications,
                "auto_apply": request.auto_apply
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to start auto-apply: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream/auto-apply/{pipeline_id}", tags=["jobs"])
async def stream_auto_apply_progress(pipeline_id: str, keywords: str, location: str = None, max_applications: int = 10, auto_apply: bool = False):
    """
    Stream real-time progress updates for automated job application pipeline.
    
    Returns Server-Sent Events with progress updates:
    - Job search results
    - Document generation progress
    - Application submission status
    
    Client should handle events with:
    ```javascript
    const eventSource = new EventSource('/api/stream/auto-apply/{id}?keywords=...');
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data.stage, data.status, data.message);
    };
    ```
    """
    from python.database import async_session_maker, Config
    from ai.job_application_pipeline import JobApplicationPipeline
    from sqlmodel import select
    
    async def generate():
        try:
            async with async_session_maker() as db:
                # Load jsearch config from database
                jsearch_config = None
                result = await db.execute(select(Config).where(Config.name == "auto-apply"))
                config_obj = result.scalar_one_or_none()
                if config_obj:
                    import json as json_lib
                    full_config = json_lib.loads(config_obj.config_json)
                    jsearch_config = full_config.get("jsearch", {})
                
                pipeline = JobApplicationPipeline(db, jsearch_config=jsearch_config)
                
                async for update in pipeline.run_pipeline(
                    keywords=keywords,
                    location=location,
                    max_applications=max_applications,
                    auto_apply=auto_apply
                ):
                    yield f"data: {json.dumps(update)}\n\n"
                    await asyncio.sleep(0.1)  # Small delay for better UX
                    
        except Exception as e:
            logger.error(f"Auto-apply pipeline failed: {e}")
            error_update = {
                "stage": "pipeline",
                "status": "failed",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_update)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


@router.get("/jobs/applications", tags=["jobs"], response_model=JobApplicationListResponse)
async def list_job_applications(status: str = None, limit: int = 100):
    """
    List job applications from database.
    
    Query Parameters:
        status: Filter by status (pending, in_progress, completed, failed)
        limit: Maximum number of results (default: 100)
    
    Returns:
        List of job applications with details
    """
    from python.database import async_session_maker, Config
    from ai.job_application_pipeline import JobApplicationPipeline
    from sqlmodel import select
    
    try:
        async with async_session_maker() as db:
            # Load jsearch config from database
            jsearch_config = None
            result = await db.execute(select(Config).where(Config.name == "auto-apply"))
            config_obj = result.scalar_one_or_none()
            if config_obj:
                import json as json_lib
                full_config = json_lib.loads(config_obj.config_json)
                jsearch_config = full_config.get("jsearch", {})
            
            pipeline = JobApplicationPipeline(db, jsearch_config=jsearch_config)
            applications = await pipeline.get_applications(status=status, limit=limit)
            
            return {
                "total": len(applications),
                "applications": [
                    {
                        "id": app.id,
                        "job_title": app.job_title,
                        "company": app.company,
                        "status": app.status,
                        "match_score": app.match_score,
                        "resume_url": app.resume_url,
                        "cover_letter_url": app.cover_letter_url,
                        "job_url": app.job_url,
                        "created_at": app.created_at.isoformat(),
                        "updated_at": app.updated_at.isoformat(),
                        "notes": app.notes
                    }
                    for app in applications
                ]
            }
    
    except Exception as e:
        logger.error(f"Failed to list applications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/opportunities/{stage}", tags=["jobs"])
async def list_opportunities(stage: str):
    """
    List opportunities from data/opportunities folder structure.
    
    Path Parameters:
        stage: Pipeline stage (interested, qualified, applied, interviewing, offers, archived)
    
    Returns:
        List of opportunities in the specified stage
    """
    from ai.opportunities_manager import OpportunitiesManager
    
    try:
        manager = OpportunitiesManager()
        opportunities = manager.list_opportunities(stage)
        
        return {
            "stage": stage,
            "count": len(opportunities),
            "opportunities": opportunities
        }
    
    except Exception as e:
        logger.error(f"Failed to list opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/opportunities", tags=["jobs"])
async def get_opportunities_summary():
    """
    Get summary of all opportunities across pipeline stages.
    
    Returns:
        Count of opportunities in each stage
    """
    from ai.opportunities_manager import OpportunitiesManager
    
    try:
        manager = OpportunitiesManager()
        counts = manager.get_all_stage_counts()
        
        return {
            "total": sum(counts.values()),
            "stages": counts
        }
    
    except Exception as e:
        logger.error(f"Failed to get opportunities summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/last-search", tags=["jobs"])
async def get_last_search_timestamp():
    """
    Get the timestamp of the last job search.
    
    Returns:
        ISO timestamp of last search, or null if never searched
    """
    from python.database import async_session_maker, Config
    from sqlmodel import select
    
    try:
        async with async_session_maker() as db:
            result = await db.execute(select(Config).where(Config.name == "auto-apply"))
            config_obj = result.scalar_one_or_none()
            
            if config_obj:
                import json as json_lib
                config_data = json_lib.loads(config_obj.config_json)
                last_search = config_data.get("last_search_timestamp")
                
                return {
                    "last_search_timestamp": last_search,
                    "has_searched": last_search is not None
                }
            
            return {
                "last_search_timestamp": None,
                "has_searched": False
            }
    
    except Exception as e:
        logger.error(f"Failed to get last search timestamp: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/search-availability", tags=["jobs"])
async def check_search_availability():
    """
    Check if job search is currently available (24 hour rate limit).
    
    Returns:
        available: bool - whether search is allowed
        reason: str - explanation if not available
        last_search_timestamp: str - ISO timestamp of last search
        hours_since_last_search: float - hours since last search
        hours_until_available: float - hours until next search is allowed
    """
    from python.database import async_session_maker, Config
    from sqlmodel import select
    from dateutil import parser
    from datetime import timedelta
    
    try:
        async with async_session_maker() as db:
            result = await db.execute(select(Config).where(Config.name == "auto-apply"))
            config_obj = result.scalar_one_or_none()
            
            if not config_obj:
                return {
                    "available": True,
                    "reason": "No previous searches",
                    "last_search_timestamp": None,
                    "hours_since_last_search": None,
                    "hours_until_available": 0
                }
            
            import json as json_lib
            config_data = json_lib.loads(config_obj.config_json)
            last_search = config_data.get("last_search_timestamp")
            
            if not last_search:
                return {
                    "available": True,
                    "reason": "No previous searches",
                    "last_search_timestamp": None,
                    "hours_since_last_search": None,
                    "hours_until_available": 0
                }
            
            last_search_dt = parser.isoparse(last_search)
            time_since_last = datetime.now() - last_search_dt.replace(tzinfo=None)
            hours_since = time_since_last.total_seconds() / 3600
            
            if time_since_last < timedelta(hours=24):
                hours_until = 24 - hours_since
                return {
                    "available": False,
                    "reason": f"Rate limited. Last search was {hours_since:.1f} hours ago.",
                    "last_search_timestamp": last_search,
                    "hours_since_last_search": round(hours_since, 2),
                    "hours_until_available": round(hours_until, 2)
                }
            
            return {
                "available": True,
                "reason": "24 hours have passed since last search",
                "last_search_timestamp": last_search,
                "hours_since_last_search": round(hours_since, 2),
                "hours_until_available": 0
            }
    
    except Exception as e:
        logger.error(f"Failed to check search availability: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/jobs/applications/{application_id}/status", tags=["jobs"])
async def update_application_status(
    application_id: str,
    status: str = Body(..., embed=True)
):
    """
    Update status of a job application.
    
    Args:
        application_id: Application ID
        status: New status (applied, interview, offer, rejected)
        
    Returns:
        Updated application
    """
    from ai.opportunities_manager import OpportunitiesManager
    
    valid_statuses = ['ready', 'applied', 'interview', 'offer', 'rejected']
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    try:
        manager = OpportunitiesManager()
        
        # Load application
        application = manager.get_application(application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Update status
        application['status'] = status
        application['updated_at'] = datetime.utcnow().isoformat()
        
        # Save updated application
        manager.update_application(application_id, application)
        
        logger.info(f"Updated application {application_id} status to {status}")
        
        return application
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update application status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
