# Resume Generator Integration - Quick Start

## ✅ What's Been Integrated

Resume-LM has been successfully integrated into the ai-dev repository for **personal use only**:

- ✅ **Resume & Cover Letter Generator** using LLM Council
- ✅ **Data folder structure** for storing generated materials
- ✅ **CLI tool** for easy generation
- ✅ **Example templates** and job descriptions
- ✅ **Documentation** in [docs/RESUME_GENERATOR.md](docs/RESUME_GENERATOR.md)

## 🚀 Quick Start (3 Steps)

### 1. Set up LLM Council API Key

```bash
cd external/llm-council
echo "OPENROUTER_API_KEY=your-key-here" > .env
```

Get your key at [openrouter.ai](https://openrouter.ai/)

### 2. Generate Your First Resume

```bash
cd apps/portal-python
python generate_resume.py \
  --company "Acme Corp" \
  --role "Senior Software Engineer" \
  --job-desc ../../data/oppertunities/_templates/example_job_description.md
```

### 3. Find Your Materials

Generated files will be in:
```
data/oppertunities/applications/Acme_Corp/
├── resume_TIMESTAMP.md
├── cover_letter_TIMESTAMP.md
├── job_description_TIMESTAMP.md
└── metadata_TIMESTAMP.json
```

## 📁 What's New

### New Files Created

1. **[apps/portal-python/tools/resume_generator.py](apps/portal-python/tools/resume_generator.py)**
   - Main ResumeGenerator class
   - Integrates with LLM Council
   - Handles resume and cover letter generation

2. **[apps/portal-python/generate_resume.py](apps/portal-python/generate_resume.py)**
   - CLI interface
   - Easy-to-use command-line tool

3. **[data/oppertunities/applications/](data/oppertunities/applications/)**
   - New folder for generated materials
   - Organized by company name
   - Timestamped versions

4. **[docs/RESUME_GENERATOR.md](docs/RESUME_GENERATOR.md)**
   - Complete documentation
   - Usage examples
   - Integration workflows

5. **[data/oppertunities/_templates/example_job_description.md](data/oppertunities/_templates/example_job_description.md)**
   - Example job description for testing

## 🎯 How It Works

1. **LLM Council Multi-Stage Process**:
   - Stage 1: Multiple LLMs generate their version
   - Stage 2: LLMs review and rank each other's work
   - Stage 3: Chairman LLM synthesizes the best final version

2. **Tailored Output**:
   - Resume tailored to job description
   - Cover letter personalized to company/role
   - ATS-optimized formatting
   - Natural keyword integration

3. **Local Storage**:
   - All materials saved in data folder
   - Timestamped for version tracking
   - Includes metadata for organization

## 💡 Usage Examples

### Generate Full Application
```bash
python generate_resume.py \
  --company "Google" \
  --role "Senior Python Engineer" \
  --job-desc path/to/job_description.txt
```

### Resume Only
```bash
python generate_resume.py \
  --company "Meta" \
  --role "ML Engineer" \
  --job-desc path/to/job.txt \
  --resume-only
```

### Custom Output Directory
```bash
python generate_resume.py \
  --company "Tesla" \
  --role "Software Engineer" \
  --job-desc path/to/job.txt \
  --output-dir ../../data/oppertunities/3_applied
```

## 🔧 Configuration

### Choose Your LLM Council

Edit `external/llm-council/backend/config.py`:

```python
COUNCIL_MODELS = [
    "anthropic/claude-sonnet-4.5",  # Best overall
    "openai/gpt-4",                  # Good reasoning
    "google/gemini-pro",             # Fast
]

CHAIRMAN_MODEL = "anthropic/claude-sonnet-4.5"
```

**Recommended models:**
- **Claude Sonnet 4.5** - Excellent writing, great reasoning
- **GPT-4** - Solid all-around performance
- **Gemini Pro** - Fast and cost-effective

### Add Your Base Resume

For better tailoring, add your base resume:
```bash
cp your_resume.docx data/oppertunities/_templates/resume_base.docx
```

## 🔗 Integration with Job Search Workflow

```
1. Find Job → Save to data/oppertunities/1_interested/
2. Qualify → Move to 2_qualified/
3. Generate Materials → Run generate_resume.py
4. Review & Edit → Edit generated .md files as needed
5. Apply → Materials in applications/ folder
6. Track → Update _tracker.md
```

## 📊 What Makes This Different from Resume-LM

| Feature | Resume-LM (Original) | Our Integration |
|---------|---------------------|-----------------|
| Multi-user | ✅ Supabase | ❌ Personal use only |
| Payments | ✅ Stripe | ❌ Free, no limits |
| Storage | ☁️ Database | 📁 Local files |
| AI Backend | Multiple providers | 🤖 LLM Council |
| Setup | Complex | 🚀 Simple |
| Use Case | SaaS product | 🎯 Personal tool |

## ⚡ Benefits

✅ **No External Services**: Everything runs locally  
✅ **No Costs**: No Supabase, Stripe, or database needed  
✅ **Version Control**: All files in git-tracked data folder  
✅ **High Quality**: LLM Council multi-model approach  
✅ **Easy Integration**: Works with existing workflow  
✅ **Customizable**: Edit generated files or regenerate  
✅ **Private**: Your data stays on your machine  

## 📖 Full Documentation

See [docs/RESUME_GENERATOR.md](docs/RESUME_GENERATOR.md) for:
- Detailed API documentation
- Python API usage
- Advanced features
- Troubleshooting guide
- Future enhancements

## 🧪 Test the Integration

Run the test script:
```bash
./test_resume_generator.sh
```

This checks:
- LLM Council setup
- Dependencies
- Data folder structure
- Resume generator files
- Example templates

## ❓ Next Steps

1. **Get OpenRouter API Key**: Sign up at [openrouter.ai](https://openrouter.ai/)
2. **Add API Key**: Create `external/llm-council/.env`
3. **Test Generation**: Use the example job description
4. **Add Your Resume**: Place in `_templates/resume_base.docx`
5. **Customize Council**: Choose your preferred LLMs
6. **Start Applying**: Generate materials for real jobs!

## 🎉 You're All Set!

The Resume Generator is now fully integrated and ready to use. Generate high-quality, tailored application materials using the power of multiple LLMs working together!

---

**Questions?** Check [docs/RESUME_GENERATOR.md](docs/RESUME_GENERATOR.md) or the source code at [apps/portal-python/tools/resume_generator.py](apps/portal-python/tools/resume_generator.py)
