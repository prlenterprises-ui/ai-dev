# Resume & Cover Letter Generator Integration

## Overview

The Resume & Cover Letter Generator is now integrated into the ai-dev repository. It uses **LLM Council** for high-quality AI-generated application materials tailored to specific job descriptions.

## How It Works

1. **LLM Council Integration**: Uses multiple LLMs to generate, review, and synthesize the best resume and cover letter
2. **Automatic Storage**: Saves all materials in the `data/oppertunities/applications/` folder
3. **Personal Use**: No Supabase, Stripe, or multi-user setup required - everything runs locally

## Setup

### 1. Configure LLM Council

First, set up your OpenRouter API key for LLM Council:

```bash
cd external/llm-council
echo "OPENROUTER_API_KEY=your-api-key-here" > .env
```

Get your API key at [openrouter.ai](https://openrouter.ai/)

### 2. Configure Council Models (Optional)

Edit `external/llm-council/backend/config.py` to choose which LLMs to use:

```python
COUNCIL_MODELS = [
    "anthropic/claude-sonnet-4.5",
    "openai/gpt-4",
    "google/gemini-pro",
]

CHAIRMAN_MODEL = "anthropic/claude-sonnet-4.5"
```

## Usage

### Command Line Interface

Generate resume and cover letter for a job:

```bash
cd apps/portal-python

# Generate full application (resume + cover letter)
python generate_resume.py \
  --company "Acme Corp" \
  --role "Senior Software Engineer" \
  --job-desc ../../data/oppertunities/_templates/example_job_description.md

# Generate resume only
python generate_resume.py \
  --company "Acme Corp" \
  --role "Senior Software Engineer" \
  --job-desc path/to/job_description.md \
  --resume-only

# Generate cover letter only
python generate_resume.py \
  --company "Acme Corp" \
  --role "Senior Software Engineer" \
  --job-desc path/to/job_description.md \
  --cover-letter-only

# Custom output directory
python generate_resume.py \
  --company "Acme Corp" \
  --role "Senior Software Engineer" \
  --job-desc path/to/job_description.md \
  --output-dir ../../data/oppertunities/3_applied
```

### Python API

Use programmatically in your code:

```python
from tools.resume_generator import ResumeGenerator
import asyncio

async def generate_application():
    generator = ResumeGenerator()
    
    # Generate full application
    result = await generator.generate_full_application(
        job_description="...",
        company_name="Acme Corp",
        role_title="Senior Software Engineer",
        output_dir="data/oppertunities/applications"
    )
    
    print(f"Resume: {result['resume']}")
    print(f"Cover Letter: {result['cover_letter']}")

asyncio.run(generate_application())
```

## Output Structure

All generated materials are saved in:

```
data/oppertunities/applications/
└── Acme_Corp/
    ├── resume_20250120_143022.md
    ├── cover_letter_20250120_143022.md
    ├── job_description_20250120_143022.md
    └── metadata_20250120_143022.json
```

Each generation includes:
- **Tailored Resume** - ATS-optimized markdown resume
- **Cover Letter** - Personalized cover letter
- **Job Description** - Copy of the original job posting
- **Metadata** - Generation timestamp and details

## Features

### LLM Council Process

1. **Stage 1: Multiple Perspectives** - Several LLMs generate their own version
2. **Stage 2: Peer Review** - Each LLM reviews and ranks others' outputs
3. **Stage 3: Synthesis** - Chairman LLM creates the best final version

This multi-LLM approach ensures:
- ✅ High-quality output
- ✅ Multiple perspectives considered
- ✅ Best practices followed
- ✅ ATS-optimized content
- ✅ Natural keyword integration

### Resume Tailoring

- Highlights relevant experience for the specific role
- Uses keywords from job description naturally
- Quantifies achievements where possible
- ATS-friendly formatting
- Clean markdown output

### Cover Letter Generation

- Compelling opening showing genuine interest
- 2-3 key achievements matching the role
- Demonstrates understanding of company/role
- Professional but personable tone
- Strong call to action

## Workflow Integration

Integrate with your job search workflow:

1. **Find Job** → Save to `data/oppertunities/1_interested/`
2. **Qualify Job** → Move to `2_qualified/`
3. **Generate Materials** → Run `generate_resume.py`
4. **Apply** → Materials saved in `applications/` folder
5. **Track** → Update `_tracker.md`

## Example Workflow

```bash
# 1. Save job description
echo "Job details..." > data/oppertunities/2_qualified/acme_job.md

# 2. Generate application materials
cd apps/portal-python
python generate_resume.py \
  --company "Acme Corp" \
  --role "Senior Software Engineer" \
  --job-desc ../../data/oppertunities/2_qualified/acme_job.md

# 3. Review generated materials
ls -la ../../data/oppertunities/applications/Acme_Corp/

# 4. Edit if needed
vim ../../data/oppertunities/applications/Acme_Corp/resume_*.md

# 5. Apply and track
# Update _tracker.md with application details
```

## Tips

1. **Base Resume**: Place your base resume in `data/oppertunities/_templates/resume_base.docx` for better tailoring
2. **Multiple Versions**: Generate multiple versions by running the command multiple times (timestamped)
3. **Manual Edits**: Feel free to edit the generated markdown files manually
4. **Council Selection**: Adjust which LLMs are in your council based on quality/cost preferences
5. **Iterate**: If output isn't perfect, regenerate or manually refine

## Troubleshooting

**"Could not import llm-council"**
- Make sure `external/llm-council` is set up
- Install dependencies: `cd external/llm-council && uv sync`

**"OpenRouter API error"**
- Check your API key in `external/llm-council/.env`
- Ensure you have credits on OpenRouter

**"Base resume not found"**
- Add your resume to `data/oppertunities/_templates/resume_base.docx`
- Or update the path in the code

## Future Enhancements

- [ ] Parse DOCX base resume automatically
- [ ] PDF generation from markdown
- [ ] Integration with job application pipeline
- [ ] Batch processing for multiple jobs
- [ ] Resume version comparison
- [ ] A/B testing different approaches
- [ ] Integration with LinkedIn profile

## Related Documentation

- [LLM Council Documentation](../external/llm-council/README.md)
- [Job Search Tracking](../data/oppertunities/_tracker.md)
- [Application Templates](../data/oppertunities/_templates/)
