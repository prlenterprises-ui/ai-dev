# AI Dev Portal

Unified backend for AI-powered career development tools, combining resume generation, LLM council deliberation, and job application automation.

## Features

- **LLM Council**: Multi-model deliberation system using GPT-4, Claude 3.5, Gemini 2.0, and Llama 3.3
- **Resume Matching**: AI-powered resume analysis and ATS compatibility checking
- **Job Applications**: Automated application tracking and document generation
- **GraphQL API**: Modern GraphQL API with Strawberry
- **REST Endpoints**: Traditional REST APIs for file uploads and streaming

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- pnpm 8+ (for monorepo management)
- Docker & Docker Compose (optional)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/prlenterprises-ui/ai-dev.git
   cd ai-dev
   ```

2. **Install dependencies**
   ```bash
   # Install pnpm globally if needed
   npm install -g pnpm

   # Install all workspace dependencies
   pnpm install
   ```

3. **Set up Python environment**
   ```bash
   cd apps/portal-python
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```

4. **Configure environment variables**
   ```bash
   cp apps/portal-python/.env.example apps/portal-python/.env
   # Edit .env and add your API keys
   ```

5. **Run the backend**
   ```bash
   cd apps/portal-python
   uvicorn main:app --reload --port 8000
   ```

6. **Run the frontend**
   ```bash
   cd apps/portal-ui
   pnpm dev
   ```

7. **Access the services**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - GraphQL Playground: http://localhost:8000/graphql
   - API Documentation: http://localhost:8000/docs

### Docker Setup

```bash
# Development
docker-compose -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.prod.yml up -d
```

## Project Structure

```
ai-dev/
├── apps/
│   ├── portal-python/          # FastAPI backend
│   │   ├── ai/                 # AI/LLM integrations
│   │   │   ├── council.py      # LLM Council implementation
│   │   │   └── llm_clients.py  # Unified LLM client wrappers
│   │   ├── apis/               # API layer
│   │   │   ├── graphql_schema.py
│   │   │   └── rest_routes.py
│   │   ├── python/             # Core utilities
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── logging_config.py
│   │   └── main.py             # Application entry point
│   └── portal-ui/              # React frontend
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   └── lib/
│       └── vite.config.js
├── data/                       # Job search data
│   └── opportunities/
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── pnpm-workspace.yaml
└── turbo.json
```

**Note**: All external code has been consolidated into the main repository:
- `apps/portal-python/jobbernaut/` - Resume tailoring pipeline (formerly external)
- `apps/portal-python/resume_matcher/` - ATS analysis (formerly external)
- `apps/portal-python/ai/council.py` - Multi-model deliberation (integrated)

## API Documentation

### GraphQL API

The main API uses GraphQL for flexible data fetching. Access the interactive playground at `/graphql`.

**Example Query:**
```graphql
query {
  modules {
    id
    name
    description
    status
  }
}
```

**Example Mutation:**
```graphql
mutation {
  askCouncil(input: {
    query: "What are the best practices for writing a technical resume?"
  }) {
    query
    finalAnswer
    rankings
    individualResponses {
      model
      content
      tokensUsed
    }
  }
}
```

### REST API

Traditional REST endpoints for specific operations:

- `POST /api/upload/resume` - Upload resume file
- `POST /api/upload/job-description` - Upload job description
- `GET /api/health` - Health check
- `GET /api/events` - Server-sent events stream

## Environment Variables

Create a `.env` file in `apps/portal-python/`:

```env
# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# API Keys
OPENROUTER_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Database
DATABASE_URL=sqlite+aiosqlite:///./portal.db

# Storage
UPLOAD_DIR=/tmp/uploads
OUTPUT_DIR=/tmp/outputs
MAX_UPLOAD_SIZE=10485760
```

## LLM Council Configuration

The LLM Council uses multiple AI models for deliberation:

- **Council Models**: GPT-4o, Claude 3.5 Sonnet, Claude 3.5 Haiku, Gemini 2.0 Flash, Llama 3.3 70B
- **Chairman Model**: Gemini 2.0 Flash Thinking

Configure via `apps/portal-python/ai/council.py`.

## Development

### Running Tests

```bash
# Python tests
cd apps/portal-python
pytest

# Frontend tests
cd apps/portal-ui
pnpm test
```

### Code Quality

```bash
# Python formatting
cd apps/portal-python
black .
ruff check .

# Frontend linting
cd apps/portal-ui
pnpm lint
```

### Building

```bash
# Build all apps
pnpm build

# Build specific app
cd apps/portal-ui
pnpm build
```

## Deployment

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

1. Build the frontend:
   ```bash
   cd apps/portal-ui
   pnpm build
   ```

2. Run the backend:
   ```bash
   cd apps/portal-python
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. Serve frontend with nginx or similar

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions, please open a GitHub issue.
