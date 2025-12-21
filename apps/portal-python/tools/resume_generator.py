"""Resume and Cover Letter Generator using LLM Council.

This module generates tailored resumes and cover letters based on job descriptions
using the LLM Council approach for high-quality output.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime

# Add external/llm-council to path
council_path = Path(__file__).parent.parent.parent.parent / "external" / "llm-council"
sys.path.insert(0, str(council_path))

try:
    from backend.council import stage1_collect_responses, stage2_collect_rankings, stage3_synthesize_final
    from backend.config import COUNCIL_MODELS, CHAIRMAN_MODEL
except ImportError:
    print("Warning: Could not import llm-council. Make sure it's set up correctly.")
    COUNCIL_MODELS = []
    CHAIRMAN_MODEL = None


class ResumeGenerator:
    """Generate tailored resumes and cover letters using LLM Council."""
    
    def __init__(self, base_resume_path: Optional[str] = None):
        """Initialize the resume generator.
        
        Args:
            base_resume_path: Path to the base resume template
        """
        self.base_resume_path = base_resume_path or self._get_default_resume_path()
        self.base_resume_content = self._load_base_resume()
        
    def _get_default_resume_path(self) -> str:
        """Get the default base resume path."""
        return str(Path(__file__).parent.parent.parent.parent / 
                  "data" / "oppertunities" / "_templates" / "resume_base.docx")
    
    def _load_base_resume(self) -> str:
        """Load base resume content."""
        if not os.path.exists(self.base_resume_path):
            return "No base resume found. Please provide your resume details."
        
        # For now, return a placeholder. In production, you'd parse the DOCX
        return """
# [Your Name]
## [Current Title]

### Experience
- [Your experience details]

### Skills
- [Your skills]

### Education
- [Your education]
"""
    
    async def generate_resume(self, job_description: str, company_name: str, 
                             role_title: str) -> str:
        """Generate a tailored resume using LLM Council.
        
        Args:
            job_description: The full job description
            company_name: Name of the company
            role_title: Title of the role
            
        Returns:
            The tailored resume content
        """
        prompt = f"""You are an expert resume writer. Given the following base resume and job description, 
create a tailored, ATS-optimized resume that highlights the most relevant experience and skills.

**Job Details:**
Company: {company_name}
Role: {role_title}

**Job Description:**
{job_description}

**Base Resume:**
{self.base_resume_content}

**Instructions:**
1. Tailor the resume to match the job description's requirements
2. Use keywords from the job description naturally
3. Highlight the most relevant experience first
4. Keep it concise and ATS-friendly
5. Use strong action verbs and quantifiable achievements
6. Format in clean Markdown

Please generate the tailored resume now:"""

        # Stage 1: Collect responses from all council members
        print("🤖 Stage 1: Gathering perspectives from LLM Council...")
        stage1_results = await stage1_collect_responses(prompt, "resume-generation")
        
        # Stage 2: Collect rankings
        print("📊 Stage 2: Council members reviewing each other's work...")
        stage2_results = await stage2_collect_rankings(prompt, stage1_results)
        
        # Stage 3: Synthesize final response
        print("✨ Stage 3: Chairman synthesizing final resume...")
        final_resume = await stage3_synthesize_final(prompt, stage1_results, stage2_results)
        
        return final_resume
    
    async def generate_cover_letter(self, job_description: str, company_name: str,
                                   role_title: str, resume_content: str) -> str:
        """Generate a tailored cover letter using LLM Council.
        
        Args:
            job_description: The full job description
            company_name: Name of the company
            role_title: Title of the role
            resume_content: The tailored resume content
            
        Returns:
            The cover letter content
        """
        prompt = f"""You are an expert at writing compelling cover letters. Given the job description 
and tailored resume, create a professional cover letter that demonstrates enthusiasm and fit.

**Job Details:**
Company: {company_name}
Role: {role_title}

**Job Description:**
{job_description}

**Tailored Resume:**
{resume_content}

**Instructions:**
1. Write a compelling opening that shows genuine interest
2. Highlight 2-3 key achievements that match the role
3. Show understanding of the company and role
4. Express enthusiasm and cultural fit
5. Keep it concise (3-4 paragraphs)
6. Professional but personable tone
7. Strong closing with call to action

Please generate the cover letter now:"""

        # Stage 1: Collect responses
        print("🤖 Stage 1: Gathering cover letter drafts from LLM Council...")
        stage1_results = await stage1_collect_responses(prompt, "cover-letter-generation")
        
        # Stage 2: Collect rankings
        print("📊 Stage 2: Council members reviewing each other's work...")
        stage2_results = await stage2_collect_rankings(prompt, stage1_results)
        
        # Stage 3: Synthesize final response
        print("✨ Stage 3: Chairman synthesizing final cover letter...")
        final_cover_letter = await stage3_synthesize_final(prompt, stage1_results, stage2_results)
        
        return final_cover_letter
    
    async def generate_full_application(self, job_description: str, company_name: str,
                                       role_title: str, output_dir: Optional[str] = None) -> Dict[str, str]:
        """Generate both resume and cover letter for a job application.
        
        Args:
            job_description: The full job description
            company_name: Name of the company
            role_title: Title of the role
            output_dir: Directory to save the outputs (optional)
            
        Returns:
            Dictionary with 'resume' and 'cover_letter' keys
        """
        print(f"\n{'='*60}")
        print(f"🎯 Generating Application Materials")
        print(f"Company: {company_name}")
        print(f"Role: {role_title}")
        print(f"{'='*60}\n")
        
        # Generate resume
        print("📄 GENERATING TAILORED RESUME\n")
        resume = await self.generate_resume(job_description, company_name, role_title)
        
        # Generate cover letter
        print("\n" + "="*60)
        print("💌 GENERATING COVER LETTER\n")
        cover_letter = await self.generate_cover_letter(job_description, company_name, 
                                                        role_title, resume)
        
        # Save to files if output_dir provided
        if output_dir:
            self._save_application_materials(output_dir, company_name, role_title, 
                                            resume, cover_letter, job_description)
        
        print("\n" + "="*60)
        print("✅ Application materials generated successfully!")
        print("="*60 + "\n")
        
        return {
            'resume': resume,
            'cover_letter': cover_letter,
            'company': company_name,
            'role': role_title,
            'generated_at': datetime.now().isoformat()
        }
    
    def _save_application_materials(self, output_dir: str, company_name: str, 
                                   role_title: str, resume: str, cover_letter: str,
                                   job_description: str):
        """Save application materials to the data folder structure."""
        # Create company folder
        safe_company_name = company_name.replace(' ', '_').replace('/', '_')
        company_dir = Path(output_dir) / safe_company_name
        company_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save resume
        resume_path = company_dir / f"resume_{timestamp}.md"
        resume_path.write_text(resume)
        print(f"  ✓ Resume saved: {resume_path}")
        
        # Save cover letter
        cover_letter_path = company_dir / f"cover_letter_{timestamp}.md"
        cover_letter_path.write_text(cover_letter)
        print(f"  ✓ Cover letter saved: {cover_letter_path}")
        
        # Save job description
        job_desc_path = company_dir / f"job_description_{timestamp}.md"
        job_desc_path.write_text(f"# {role_title} at {company_name}\n\n{job_description}")
        print(f"  ✓ Job description saved: {job_desc_path}")
        
        # Save metadata
        metadata = {
            'company': company_name,
            'role': role_title,
            'generated_at': datetime.now().isoformat(),
            'files': {
                'resume': str(resume_path.name),
                'cover_letter': str(cover_letter_path.name),
                'job_description': str(job_desc_path.name)
            }
        }
        metadata_path = company_dir / f"metadata_{timestamp}.json"
        metadata_path.write_text(json.dumps(metadata, indent=2))
        print(f"  ✓ Metadata saved: {metadata_path}")


# CLI interface
async def main():
    """CLI interface for resume generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate tailored resumes and cover letters')
    parser.add_argument('--company', required=True, help='Company name')
    parser.add_argument('--role', required=True, help='Role title')
    parser.add_argument('--job-desc', required=True, help='Path to job description file')
    parser.add_argument('--output-dir', default='data/oppertunities/2_qualified',
                       help='Output directory (default: data/oppertunities/2_qualified)')
    parser.add_argument('--resume-only', action='store_true', help='Generate resume only')
    parser.add_argument('--cover-letter-only', action='store_true', help='Generate cover letter only')
    
    args = parser.parse_args()
    
    # Load job description
    job_desc_path = Path(args.job_desc)
    if not job_desc_path.exists():
        print(f"❌ Error: Job description file not found: {args.job_desc}")
        sys.exit(1)
    
    job_description = job_desc_path.read_text()
    
    # Initialize generator
    generator = ResumeGenerator()
    
    # Generate materials
    if args.resume_only:
        resume = await generator.generate_resume(job_description, args.company, args.role)
        print("\n" + "="*60)
        print("GENERATED RESUME")
        print("="*60 + "\n")
        print(resume)
    elif args.cover_letter_only:
        # Need resume first
        resume = await generator.generate_resume(job_description, args.company, args.role)
        cover_letter = await generator.generate_cover_letter(job_description, args.company, 
                                                             args.role, resume)
        print("\n" + "="*60)
        print("GENERATED COVER LETTER")
        print("="*60 + "\n")
        print(cover_letter)
    else:
        # Generate full application
        await generator.generate_full_application(
            job_description, args.company, args.role, args.output_dir
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
