# External Applications Reference

This document describes the external applications that are available but **not consolidated** into the main repository, as they are standalone applications rather than reusable libraries.

## Resume-LM

**Type**: Next.js Frontend Application  
**Location**: `external/resume-lm/`  
**Description**: Full-featured resume builder with React UI  
**Tech Stack**: Next.js 15, React 19, Tailwind CSS  

**Status**: Standalone application. Not integrated into portal-ui as it is a complete application on its own. Could potentially be merged into our frontend in the future.

**How to Use**:
```bash
cd external/resume-lm
pnpm install
pnpm dev
# Visit http://localhost:3001
```

## AIHawk (Jobs_Applier_AI_Agent_AIHawk)

**Type**: Python Automation Bot  
**Location**: `external/Jobs_Applier_AI_Agent_AIHawk/`  
**Description**: Automated job application bot using AI  
**Tech Stack**: Python with LLM integration  

**Status**: Standalone automation script. Runs independently with its own config. Could be integrated as a service in the future, but requires significant refactoring.

**How to Use**:
```bash
cd external/Jobs_Applier_AI_Agent_AIHawk
pip install -r requirements.txt
# Configure data_folder/ with your profile
python main.py
```

## Why Not Consolidated?

Unlike **Jobbernaut** and **Resume Matcher** which are reusable modules:
- **Resume-LM** is a complete frontend application (would duplicate our portal-ui)
- **AIHawk** is a standalone automation script (not a library/service)

Both remain in `external/` for reference and potential future integration.
