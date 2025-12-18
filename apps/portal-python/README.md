# Portal Python - AI Dev Portal Backend

Unified Python backend that combines all AI/resume tools into a single GraphQL + REST API.

## Quick Start

```bash
# Install dependencies
uv sync

# Copy environment template and add your API keys
cp .env.example .env
# Edit .env with your keys

# Run the server
uv run python main.py
# Or with auto-reload:
uv run uvicorn main:app --reload --port 8000
```

## API Endpoints

| Endpoint | Type | Description |
|----------|------|-------------|
| `/graphql` | GraphQL | Main API - queries and mutations |
| `/api/health` | REST | Health check |
| `/api/upload/resume` | REST | File upload for resumes |
| `/api/stream/council` | SSE | Real-time LLM Council responses |
| `/api/stream/tailoring/{id}` | SSE | Real-time resume tailoring progress |

## Environment Variables

Create a `.env` file with:

```env
# Required: OpenRouter for LLM Council (access to many models)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Optional: Direct provider keys
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Server
PORT=8000
DEBUG=true

# LLM Council
COUNCIL_MODELS=openai/gpt-4o,anthropic/claude-3-5-sonnet,google/gemini-2.0-flash-exp
CHAIRMAN_MODEL=google/gemini-2.0-flash-thinking-exp

# Local AI (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## Directory Structure

```
portal-python/
├── main.py              # FastAPI app entry point
├── apis/                # API layer
│   ├── graphql_schema.py   # Strawberry GraphQL schema
│   └── rest_routes.py      # REST endpoints
├── ai/                  # AI/LLM code
│   ├── llm_clients.py      # Unified LLM client wrappers
│   └── council.py          # LLM Council implementation
└── python/              # Business logic
    └── config.py           # Settings management
```

## GraphQL Schema

### Queries

```graphql
query {
  health {
    status
    timestamp
    version
  }
  
  modules {
    id
    name
    description
    status
    route
  }
  
  applications(status: "pending") {
    id
    jobTitle
    company
    status
  }
}
```

### Mutations

```graphql
mutation {
  askCouncil(input: {
    query: "What is the best programming language for beginners?"
    models: ["openai/gpt-4o", "anthropic/claude-3-5-sonnet"]
  }) {
    individualResponses {
      model
      content
    }
    rankings
    finalAnswer
  }
  
  matchResume(input: {
    resumeText: "..."
    jobDescription: "..."
  }) {
    overallScore
    keywordMatch
    suggestions
  }
}
```

## Integrated Modules

1. **Jobbernaut Tailor** - Industrial-scale resume tailoring
2. **LLM Council** - Multi-model deliberation with peer review
3. **Resume Matcher** - Local AI resume analysis
4. **ResumeLM** - Full-featured resume builder (coming soon)
5. **AIHawk** - Automated job applications (coming soon)

