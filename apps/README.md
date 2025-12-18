# AI Dev Portal - Apps

This folder contains the unified portal that combines all 5 AI/resume submodules into a cohesive learning application.

## Directory Structure

```
apps/
├── portal-ui/          # React frontend (Vite + JavaScript)
│   ├── src/
│   │   ├── components/    # Shared components (Layout, etc.)
│   │   ├── pages/         # Page components for each module
│   │   ├── lib/           # GraphQL queries, utilities
│   │   └── hooks/         # Custom React hooks
│   └── package.json
│
└── portal-python/      # Python backend (FastAPI + Strawberry GraphQL)
    ├── apis/              # API layer (GraphQL schema, REST routes)
    ├── ai/                # AI/LLM code (clients, council logic)
    ├── python/            # Business logic and services
    └── main.py            # FastAPI entry point
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (port 5173)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  React + Vite + Apollo Client                             │   │
│  │  - Home page with module links                            │   │
│  │  - LLM Council UI                                         │   │
│  │  - Jobbernaut Tailor UI                                   │   │
│  │  - Resume Matcher UI                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                    GraphQL / REST
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                        Backend (port 8000)                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  FastAPI + Strawberry GraphQL                             │   │
│  │  - /graphql          → GraphQL endpoint                   │   │
│  │  - /api/health       → Health check                       │   │
│  │  - /api/upload/*     → File uploads                       │   │
│  │  - /api/stream/*     → Server-sent events                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  AI Layer                                                 │   │
│  │  - OpenRouter (GPT-4, Claude, Gemini, Llama via 1 API)   │   │
│  │  - Ollama (local models for privacy)                      │   │
│  │  - LLM Council (multi-model deliberation)                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Monorepo (recommended)

```bash
# Install JS deps for the whole repo
pnpm -w install

# (Optional) Install Python deps for backend in a venv
python -m venv .venv && source .venv/bin/activate
cd apps/portal-python
python -m pip install -e '.[dev]'
```

Start both (recommended):

```bash
pnpm dev
```

Or run per-package:

### 1. Start the Backend

```bash
cd apps/portal-python

# Run the server (local dev with reload)
uv run python main.py
# or via pnpm workspace helper
pnpm --filter portal-python... dev
```

Backend will be available at:
- http://localhost:8000 - API root
- http://localhost:8000/graphql - GraphQL Playground

### 2. Start the Frontend

```bash
cd apps/portal-ui

# Install dependencies
pnpm install

# Run development server
pnpm run dev
```

Frontend will be available at:
- http://localhost:5173

> Tip: `pnpm dev` runs `portal-python` and `portal-ui` in parallel via Turborepo; `pnpm build` will build the UI and build the backend Docker image.

## Frontend → Backend Communication

### GraphQL (Primary)

Used for most data operations:

```javascript
import { gql, useMutation } from '@apollo/client'

const ASK_COUNCIL = gql`
  mutation AskCouncil($input: CouncilQueryInput!) {
    askCouncil(input: $input) {
      query
      individualResponses { model, content }
      rankings
      finalAnswer
    }
  }
`

// In component:
const [askCouncil, { data, loading }] = useMutation(ASK_COUNCIL)
```

### REST (Specific Use Cases)

Used for:
- File uploads (multipart/form-data)
- Server-sent events (streaming responses)
- Simple health checks

```javascript
// File upload
const formData = new FormData()
formData.append('file', resumeFile)
await fetch('/api/upload/resume', { method: 'POST', body: formData })

// SSE streaming
const eventSource = new EventSource('/api/stream/council')
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data)
  // Handle streaming response
}
```

## Integrated Modules

| Module | Status | Description |
|--------|--------|-------------|
| **LLM Council** | ✅ Active | Multi-model deliberation with peer review |
| **Jobbernaut Tailor** | ✅ Active | Industrial-scale resume tailoring |
| **Resume Matcher** | ✅ Active | Local AI resume analysis with Ollama |
| **ResumeLM** | 🚧 Coming Soon | Full-featured AI resume builder |
| **AIHawk** | 🚧 Coming Soon | Automated job application agent |

## Technology Choices

### Why GraphQL (Strawberry)?

- **Single endpoint** - One URL for all data needs
- **Flexible queries** - Frontend requests exactly what it needs
- **Strong typing** - Strawberry uses Python type hints
- **Great tooling** - Built-in GraphQL Playground
- **Perfect for combining data** - Multiple submodules, one query

### Why OpenRouter?

- **Single API key** - Access GPT-4, Claude, Gemini, Llama, etc.
- **Pay-as-you-go** - No monthly commitments
- **Easy model switching** - Just change the model identifier
- **Great for LLM Council** - Query multiple models with one integration

### Why Ollama for Resume Matcher?

- **Privacy** - Resume data stays on your machine
- **Free** - No API costs for local inference
- **Offline capable** - Works without internet
- **Good enough** - Llama 3 handles resume analysis well

## Development Notes

### Adding a New Module

1. Create page component in `portal-ui/src/pages/NewModulePage.jsx`
2. Add route in `portal-ui/src/App.jsx`
3. Add nav item in `portal-ui/src/components/Layout.jsx`
4. Add GraphQL types/mutations in `portal-python/apis/graphql_schema.py`
5. Implement service logic in `portal-python/python/` or `portal-python/ai/`

### Environment Variables

Backend (`.env`):
```
OPENROUTER_API_KEY=sk-or-v1-...
OPENAI_API_KEY=sk-...          # Optional, for direct OpenAI
ANTHROPIC_API_KEY=sk-ant-...   # Optional, for direct Anthropic
OLLAMA_BASE_URL=http://localhost:11434
```

Frontend uses Vite's proxy - no env vars needed for development.

