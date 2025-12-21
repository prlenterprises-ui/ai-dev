#!/usr/bin/env python3
"""
Resume & Cover Letter Generator CLI

Generate tailored resumes and cover letters using LLM Council.
"""

import sys
import os
from pathlib import Path

# Add portal-python to path
portal_python_path = Path(__file__).parent.parent
sys.path.insert(0, str(portal_python_path))

from tools.resume_generator import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
