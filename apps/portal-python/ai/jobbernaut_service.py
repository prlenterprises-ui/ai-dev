"""
Jobbernaut Tailor Service - Wrapper for job application pipeline
Integrates the 12-step resume tailoring system into the portal backend
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, AsyncGenerator
from datetime import datetime

# Add jobbernaut module to Python path
JOBBERNAUT_PATH = Path(__file__).parent.parent / "jobbernaut" / "src"
sys.path.insert(0, str(JOBBERNAUT_PATH))

try:
    from main import ResumeOptimizationPipeline
    JOBBERNAUT_AVAILABLE = True
except ImportError as e:
    JOBBERNAUT_AVAILABLE = False
    print(f"WARNING: Jobbernaut Tailor module not available: {e}")


class JobbernautService:
    """Service for running Jobbernaut resume tailoring pipeline."""
    
    def __init__(self):
        """Initialize the service."""
        self.pipeline = None
        self.jobbernaut_root = Path(__file__).parent.parent / "jobbernaut"
        self.config_path = self.jobbernaut_root / "config.json"
        self.master_resume_path = self.jobbernaut_root / "profile" / "master_resume.json"
        self.applications_path = self.jobbernaut_root / "data" / "applications.yaml"
        self.outputs_path = self.jobbernaut_root / "outputs"
        
    async def initialize(self) -> bool:
        """Initialize the Jobbernaut pipeline."""
        if not JOBBERNAUT_AVAILABLE:
            return False
            
        try:
            self.pipeline = ResumeOptimizationPipeline()
            return True
        except Exception as e:
            print(f"Failed to initialize Jobbernaut pipeline: {e}")
            return False
    
    async def process_application_stream(
        self,
        job_title: str,
        company: str,
        job_description: str,
        job_url: Optional[str] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        Process a job application and stream progress updates.
        
        Yields progress updates for each step of the 12-step pipeline:
        1. Job Resonance Analysis
        2. Company Research
        3. Storytelling Arc
        4. Resume JSON Generation
        5. Cover Letter Generation
        6. LaTeX Rendering
        7. PDF Compilation
        8-12. Referral documents (if configured)
        
        Args:
            job_title: Job title
            company: Company name
            job_description: Full job description text
            job_url: Optional URL to the job posting
            
        Yields:
            Progress updates with step info, status, and outputs
        """
        if not self.pipeline:
            await self.initialize()
        
        if not self.pipeline:
            yield {
                "step": "initialization",
                "status": "error",
                "message": "Jobbernaut pipeline not available"
            }
            return
        
        # Generate job ID
        job_id = f"{company}_{job_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}".replace(" ", "_")
        
        # Create job dict
        job = {
            "job_id": job_id,
            "job_title": job_title,
            "company_name": company,
            "job_description": job_description,
            "job_url": job_url or "",
            "status": "pending"
        }
        
        # Pipeline steps for progress tracking
        steps = [
            {"id": 1, "name": "Job Resonance Analysis", "stage": "intelligence"},
            {"id": 2, "name": "Company Research", "stage": "intelligence"},
            {"id": 3, "name": "Storytelling Arc", "stage": "intelligence"},
            {"id": 4, "name": "Resume JSON Generation", "stage": "generation"},
            {"id": 5, "name": "Cover Letter Generation", "stage": "generation"},
            {"id": 6, "name": "LaTeX Rendering", "stage": "rendering"},
            {"id": 7, "name": "PDF Compilation", "stage": "rendering"},
        ]
        
        try:
            # Yield start status
            yield {
                "step": "start",
                "status": "started",
                "job_id": job_id,
                "total_steps": len(steps)
            }
            
            # Run pipeline with progress tracking
            # We'll intercept the pipeline's print statements to track progress
            current_step = 0
            
            # Helper to track step progression
            def get_current_step(message: str) -> Optional[int]:
                """Determine current step from log message."""
                if "INTELLIGENCE STEP 1" in message or "Job resonance" in message.lower():
                    return 1
                elif "INTELLIGENCE STEP 2" in message or "Company research" in message.lower():
                    return 2
                elif "INTELLIGENCE STEP 3" in message or "Storytelling arc" in message.lower():
                    return 3
                elif "STEP 1" in message or "Resume JSON" in message:
                    return 4
                elif "STEP 2" in message or "Cover Letter" in message:
                    return 5
                elif "STEP 3" in message or "STEP 4" in message or "LaTeX" in message:
                    return 6
                elif "STEP 5" in message or "STEP 6" in message or "PDF" in message:
                    return 7
                return None
            
            # Run pipeline in background task
            # For now, simulate the process
            for i, step in enumerate(steps, 1):
                yield {
                    "step": step["id"],
                    "name": step["name"],
                    "stage": step["stage"],
                    "status": "running",
                    "progress": (i / len(steps)) * 100
                }
                
                # Simulate processing time
                await asyncio.sleep(2)
                
                yield {
                    "step": step["id"],
                    "name": step["name"],
                    "stage": step["stage"],
                    "status": "completed",
                    "progress": (i / len(steps)) * 100
                }
            
            # TODO: Actually run the pipeline
            # await self.pipeline.process_job(job)
            
            # Yield completion status
            output_dir = self.outputs_path / f"{company}_{job_title}_{job_id}"
            
            yield {
                "step": "complete",
                "status": "success",
                "job_id": job_id,
                "outputs": {
                    "resume_pdf": f"{output_dir}/Resume.pdf",
                    "cover_letter_pdf": f"{output_dir}/Cover_Letter.pdf",
                    "resume_json": f"{output_dir}/Resume.json",
                    "cover_letter_txt": f"{output_dir}/Cover_Letter.txt"
                }
            }
            
        except Exception as e:
            yield {
                "step": "error",
                "status": "failed",
                "message": str(e)
            }
    
    async def get_master_resume(self) -> Optional[Dict]:
        """Load the master resume JSON."""
        if not self.master_resume_path.exists():
            return None
        
        try:
            with open(self.master_resume_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load master resume: {e}")
            return None
    
    async def update_master_resume(self, resume_data: Dict) -> bool:
        """Update the master resume JSON."""
        try:
            with open(self.master_resume_path, "w") as f:
                json.dump(resume_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to update master resume: {e}")
            return False
    
    async def list_applications(self) -> List[Dict]:
        """List all job applications from YAML."""
        # TODO: Implement YAML parsing
        return []
    
    async def get_application_status(self, job_id: str) -> Optional[Dict]:
        """Get the status of a specific job application."""
        # Check output directory
        output_dirs = list(self.outputs_path.glob(f"*{job_id}*"))
        if not output_dirs:
            return None
        
        output_dir = output_dirs[0]
        
        # Check for output files
        has_resume = (output_dir / "Resume.pdf").exists()
        has_cover_letter = (output_dir / "Cover_Letter.pdf").exists()
        
        return {
            "job_id": job_id,
            "status": "completed" if (has_resume and has_cover_letter) else "processing",
            "output_dir": str(output_dir),
            "files": {
                "resume_pdf": has_resume,
                "cover_letter_pdf": has_cover_letter
            }
        }


# Global service instance
_service = None


async def get_jobbernaut_service() -> JobbernautService:
    """Get or create the global Jobbernaut service instance."""
    global _service
    if _service is None:
        _service = JobbernautService()
        await _service.initialize()
    return _service
