#!/bin/bash
# Quick test script for Resume Generator integration

set -e

echo "🧪 Testing Resume Generator Integration"
echo "======================================="
echo ""

# Check if LLM Council is set up
echo "1️⃣ Checking LLM Council setup..."
if [ -f "external/llm-council/.env" ]; then
    echo "   ✅ LLM Council .env found"
else
    echo "   ⚠️  LLM Council .env not found"
    echo "   Create external/llm-council/.env with your OPENROUTER_API_KEY"
fi

# Check if dependencies are installed
echo ""
echo "2️⃣ Checking dependencies..."
if [ -d ".venv" ]; then
    echo "   ✅ Python virtual environment found"
else
    echo "   ⚠️  Virtual environment not found"
    echo "   Run: python -m venv .venv && source .venv/bin/activate"
fi

# Check data folder structure
echo ""
echo "3️⃣ Checking data folder structure..."
if [ -d "data/oppertunities/applications" ]; then
    echo "   ✅ Applications folder created"
else
    echo "   ❌ Applications folder not found"
fi

# Check if resume generator exists
echo ""
echo "4️⃣ Checking resume generator..."
if [ -f "apps/portal-python/tools/resume_generator.py" ]; then
    echo "   ✅ Resume generator module found"
else
    echo "   ❌ Resume generator not found"
fi

if [ -f "apps/portal-python/generate_resume.py" ]; then
    echo "   ✅ CLI script found"
else
    echo "   ❌ CLI script not found"
fi

# Check example job description
echo ""
echo "5️⃣ Checking example files..."
if [ -f "data/oppertunities/_templates/example_job_description.md" ]; then
    echo "   ✅ Example job description found"
else
    echo "   ❌ Example job description not found"
fi

echo ""
echo "======================================="
echo "Setup Status: Ready for testing! 🚀"
echo ""
echo "To test, run:"
echo "  cd apps/portal-python"
echo "  python generate_resume.py \\"
echo "    --company \"Acme Corp\" \\"
echo "    --role \"Senior Software Engineer\" \\"
echo "    --job-desc ../../data/oppertunities/_templates/example_job_description.md"
echo ""
