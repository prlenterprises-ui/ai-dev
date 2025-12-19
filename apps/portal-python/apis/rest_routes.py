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
from datetime import datetime

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()


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
        text_content = content.decode('utf-8')
    else:
        # For other formats, basic extraction
        try:
            text_content = content.decode('utf-8', errors='ignore')
        except (UnicodeDecodeError, AttributeError):
            text_content = str(content)

    # Basic parsing - extract title from first lines
    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
    title = lines[0] if lines else "Unknown Position"

    # Extract company name (simple heuristic)
    company = "Unknown Company"
    for line in lines[:5]:
        if any(keyword in line.lower() for keyword in ['company:', 'at ', 'join ']):
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

