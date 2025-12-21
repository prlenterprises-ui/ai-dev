# Generated Application Materials

This folder contains AI-generated resumes and cover letters for job applications.

## Structure

Each application is stored in a company-specific folder:

```
applications/
├── Company_Name/
│   ├── resume_20250120_143022.md
│   ├── cover_letter_20250120_143022.md
│   ├── job_description_20250120_143022.md
│   └── metadata_20250120_143022.json
└── Another_Company/
    └── ...
```

## Files

- **resume_*.md** - Tailored resume generated using LLM Council
- **cover_letter_*.md** - Personalized cover letter
- **job_description_*.md** - Original job description
- **metadata_*.json** - Generation metadata (timestamp, company, role)

## Usage

Generate application materials using the CLI:

```bash
# From the portal-python directory
python -m ai.resume_generator \
  --company "Company Name" \
  --role "Senior Software Engineer" \
  --job-desc path/to/job_description.txt \
  --output-dir data/oppertunities/applications
```

## Notes

- All materials are generated using LLM Council for high-quality output
- Files are timestamped to track versions
- Metadata JSON contains generation details
- Materials are optimized for ATS (Applicant Tracking Systems)
