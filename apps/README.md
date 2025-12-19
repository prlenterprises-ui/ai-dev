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

---

## Containers & Production

We provide Dockerfiles and docker-compose setups for local dev and production parity.

### Build & run locally

```bash
# Build backend image
docker build -t portal-python:local ./apps/portal-python

docker run --rm --env-file apps/portal-python/.env -p 8000:8000 portal-python:local

# Build UI image
docker build -t portal-ui:local ./apps/portal-ui

docker run --rm -p 5173:5173 portal-ui:local
```

### Convenience: Makefile

We've added a `Makefile` at the repo root with convenient targets. Example usage:

```bash
# Install dependencies for the monorepo
make install

# Start both services locally via turbo
make dev

# Run lint and tests
make lint
make test

# Build Docker images locally
make docker-build
make docker-build-ui

# Start docker-compose (dev)
make compose-up
```

---

### Automated releases

This repo uses **Release Drafter** to generate draft release notes automatically when changes are pushed to `main`. The configuration is stored at `.github/release-drafter.yml`. When you're ready to publish a release, create a tag (e.g., `v1.2.3`) and push it — CI already builds artifacts and uploads the wheel for tag pushes.

### Docker Compose (dev)

```bash
docker compose -f docker-compose.dev.yml up --build
```

### Docker Compose (prod)

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

### Publish to GHCR

We push Docker images to GitHub Container Registry (`ghcr.io/<org>/ai-dev/<service>`).

- To allow pushes from GitHub Actions, ensure the repository's workflow permissions allow the `packages: write` permission (already configured in CI workflow).
- If you want to push manually, create a Personal Access Token with `write:packages` scope and run:

```bash
echo $GHCR_PAT | docker login ghcr.io -u <username> --password-stdin
docker tag portal-python:local ghcr.io/<org>/ai-dev/portal-python:latest
docker push ghcr.io/<org>/ai-dev/portal-python:latest
```

---

## CI

We run the following in CI (GitHub Actions):
- `pnpm -w install` and `pnpm -w build` (Turbo)
- Frontend lint & build
- Python lint (ruff) & tests (pytest)
- Build Python wheel and upload as an artifact
- Build Docker images and push to GHCR on `main` (and on tags)

Make sure to add any required secrets to the repository settings under `Settings` > `Secrets` > `Actions`:

- `GHCR_PAT` (optional) — a Personal Access Token with `write:packages` scope if you prefer using a PAT for GHCR pushes instead of `GITHUB_TOKEN`. The CI will use `GHCR_PAT` if present, otherwise it falls back to `GITHUB_TOKEN`.

Additionally, note that the CI **enforces** frontend (ESLint) and backend (ruff) linting; failing lint will fail the workflow. If you want non-blocking lint for a while, tell me and I can relax this enforcement.

---

## Branch protection (recommended)

A branch protection workflow has been added to help you enforce best practices on `main`. It is a manual workflow (run-once via `workflow_dispatch`) that configures the following for the `main` branch:

- Require status checks to pass (the `CI` workflow)
- Enforce admin protections
- Require at least 1 approving review for PRs

To enable it, go to the Actions tab, select **Configure Branch Protection**, and click **Run workflow**. The workflow will attempt to configure protection using the `GITHUB_TOKEN`; if your org restricts that, you may need to run it with a token that has admin privileges.


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

