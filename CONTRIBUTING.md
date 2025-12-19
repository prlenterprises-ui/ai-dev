# Contributing to AI Dev Portal

Thank you for your interest in contributing! This guide will help you get started with development.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Common Tasks](#common-tasks)

## Development Setup

### Prerequisites

- **Python 3.11+** - Backend runtime
- **Node.js 20+** - Frontend runtime
- **pnpm 8+** - Package manager
- **Docker Desktop** - Container runtime
- **Git** - Version control

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai-dev
   ```

2. **Set up Python environment**:
   ```bash
   cd apps/portal-python
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Install Node dependencies**:
   ```bash
   cd ../..
   pnpm install
   ```

4. **Set up environment variables**:
   ```bash
   # Backend
   cp apps/portal-python/.env.example apps/portal-python/.env
   
   # Frontend
   cp apps/portal-ui/.env.example apps/portal-ui/.env
   
   # Edit files to add your API keys
   ```

5. **Start development servers**:
   ```bash
   # Option 1: Use Docker Compose
   docker-compose -f docker-compose.dev.yml up
   
   # Option 2: Run services separately
   # Terminal 1 - Backend
   cd apps/portal-python
   uvicorn main:app --reload --port 8000
   
   # Terminal 2 - Frontend
   cd apps/portal-ui
   pnpm dev
   ```

6. **Verify setup**:
   - Backend: http://localhost:8000/docs
   - Frontend: http://localhost:3000
   - GraphQL Playground: http://localhost:8000/graphql

## Project Structure

```
ai-dev/
├── apps/
│   ├── portal-python/          # FastAPI + GraphQL backend
│   │   ├── ai/                 # LLM council and AI logic
│   │   ├── apis/               # GraphQL schema + REST routes
│   │   ├── python/             # Core utilities (config, database, logging)
│   │   ├── test_*.py           # Test files
│   │   └── main.py             # Application entry point
│   │
│   └── portal-ui/              # React + Vite frontend
│       ├── src/
│       │   ├── components/     # Reusable React components
│       │   ├── pages/          # Page components
│       │   └── lib/            # GraphQL queries, utilities
│       └── public/             # Static assets
│
├── data/                       # Job application data (tracked separately)
├── external/                   # Git submodules for external tools
├── .github/                    # CI/CD workflows
└── docker-compose.*.yml        # Docker configurations
```

### Key Modules

- **`ai/council.py`**: Multi-model LLM deliberation system
- **`ai/llm_clients.py`**: OpenRouter API client for LLM calls
- **`apis/graphql_schema.py`**: GraphQL schema with queries and mutations
- **`apis/rest_routes.py`**: REST endpoints for file uploads
- **`python/database.py`**: SQLModel database models
- **`python/config.py`**: Environment configuration
- **`python/rate_limiter.py`**: API rate limiting middleware

## Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** with frequent commits:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

3. **Keep your branch updated**:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

4. **Run tests before pushing**:
   ```bash
   # Backend tests
   cd apps/portal-python
   pytest
   
   # Frontend tests
   cd apps/portal-ui
   pnpm test
   ```

5. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   # Then create PR on GitHub
   ```

## Coding Standards

### Python (Backend)

- **Style**: Follow [PEP 8](https://pep8.org/)
- **Formatter**: Use `black` for code formatting
- **Linter**: Use `ruff` for linting
- **Type hints**: Use type annotations for all functions

```python
# Good
async def create_application(
    job_title: str,
    company: str,
    status: str = "interested",
) -> JobApplication:
    """Create a new job application with validation."""
    pass

# Bad
def create_application(job_title, company, status="interested"):
    pass
```

- **Docstrings**: Use Google style docstrings
- **Logging**: Use structured logging with context

```python
logger.info("Creating application", extra={
    "job_title": job_title,
    "company": company,
})
```

### JavaScript/React (Frontend)

- **Style**: Use ESLint configuration
- **Formatter**: Use Prettier
- **Components**: Functional components with hooks
- **Naming**: PascalCase for components, camelCase for functions/variables

```javascript
// Good
export function JobCard({ job, onApply }) {
  const [isLoading, setIsLoading] = useState(false)
  
  const handleApply = async () => {
    setIsLoading(true)
    await onApply(job.id)
    setIsLoading(false)
  }
  
  return <div>...</div>
}

// Bad
export default ({ job }) => <div>...</div>
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Formatting changes
- `refactor:` - Code restructuring
- `test:` - Adding/updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add resume parsing endpoint
fix: correct CORS configuration for production
docs: update API documentation with examples
refactor: extract rate limiting to middleware
test: add integration tests for council API
```

## Testing Guidelines

### Backend Testing

**Unit Tests** - Test individual functions:
```python
# test_council.py
import pytest
from ai.council import LLMCouncil

def test_council_initialization():
    """Test council initializes with default models."""
    council = LLMCouncil()
    assert len(council.models) == 5
    assert council.chairman_model == "anthropic/claude-3.5-sonnet"
```

**Integration Tests** - Test API endpoints:
```python
# test_integration.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
```

**Run tests**:
```bash
cd apps/portal-python
pytest                    # All tests
pytest -v                 # Verbose
pytest -k "test_council"  # Specific test
pytest --cov              # Coverage report
```

### Frontend Testing

**Component Tests** - Test UI components:
```javascript
// JobCard.test.jsx
import { render, screen } from '@testing-library/react'
import { JobCard } from './JobCard'

test('displays job title and company', () => {
  const job = { title: 'Engineer', company: 'Acme' }
  render(<JobCard job={job} />)
  
  expect(screen.getByText('Engineer')).toBeInTheDocument()
  expect(screen.getByText('Acme')).toBeInTheDocument()
})
```

**Run tests**:
```bash
cd apps/portal-ui
pnpm test              # All tests
pnpm test:watch        # Watch mode
pnpm test:coverage     # Coverage report
```

### Test Coverage Goals

- **Backend**: Aim for 80%+ coverage
- **Frontend**: Aim for 70%+ coverage
- All new features should include tests
- Bug fixes should include regression tests

## Pull Request Process

### Before Submitting

1. ✅ All tests pass locally
2. ✅ Code follows style guidelines
3. ✅ Documentation updated (if needed)
4. ✅ Commit messages follow convention
5. ✅ Branch is up to date with main

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Review Process

1. **Automated checks** run on PR creation:
   - Linting (ruff, eslint)
   - Type checking (mypy, TypeScript)
   - Tests (pytest, vitest)
   - Security scanning (bandit)

2. **Code review** by maintainer:
   - Code quality and style
   - Test coverage
   - Documentation completeness
   - Security considerations

3. **Approval and merge**:
   - Requires 1 approval
   - All checks must pass
   - No merge conflicts
   - Squash and merge preferred

## Common Tasks

### Adding a New GraphQL Query

1. **Define the query in schema**:
   ```python
   # apis/graphql_schema.py
   @strawberry.type
   class Query:
       @strawberry.field
       async def get_job(self, id: str) -> JobApplication:
           """Get a specific job application by ID."""
           # Implementation
   ```

2. **Add GraphQL query to frontend**:
   ```javascript
   // src/lib/graphql.js
   export const GET_JOB = gql`
     query GetJob($id: String!) {
       getJob(id: $id) {
         id
         jobTitle
         company
       }
     }
   `
   ```

3. **Use in React component**:
   ```javascript
   // src/components/JobDetail.jsx
   import { useQuery } from '@apollo/client'
   import { GET_JOB } from '../lib/graphql'
   
   export function JobDetail({ jobId }) {
     const { data, loading } = useQuery(GET_JOB, {
       variables: { id: jobId }
     })
     // Render component
   }
   ```

### Adding a New Database Model

1. **Define the model**:
   ```python
   # python/database.py
   from sqlmodel import SQLModel, Field
   
   class NewModel(SQLModel, table=True):
       """Description of the model."""
       __tablename__ = "new_models"
       
       id: int = Field(primary_key=True)
       name: str = Field(max_length=200)
       created_at: datetime = Field(default_factory=datetime.now)
   ```

2. **Add to init_db**:
   ```python
   async def init_db():
       async with engine.begin() as conn:
           await conn.run_sync(SQLModel.metadata.create_all)
   ```

3. **Use in queries**:
   ```python
   from python.database import get_session, NewModel
   
   async with get_session() as session:
       model = NewModel(name="example")
       session.add(model)
       await session.commit()
   ```

### Adding Environment Variables

1. **Add to Settings class**:
   ```python
   # python/config.py
   class Settings(BaseSettings):
       new_variable: str = Field(default="default_value")
   ```

2. **Add to .env files**:
   ```bash
   # .env.example
   NEW_VARIABLE=your_value
   
   # .env
   NEW_VARIABLE=actual_value
   ```

3. **Use in code**:
   ```python
   from python.config import settings
   value = settings.new_variable
   ```

### Running Docker Builds Locally

```bash
# Build specific service
docker-compose -f docker-compose.dev.yml build portal-python

# Rebuild without cache
docker-compose -f docker-compose.dev.yml build --no-cache

# Run with build
docker-compose -f docker-compose.dev.yml up --build

# View logs
docker-compose -f docker-compose.dev.yml logs -f portal-python
```

## Getting Help

- **Documentation**: Check [README.md](README.md) and [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues**: Search [existing issues](https://github.com/your-repo/issues)
- **Discussions**: Use [GitHub Discussions](https://github.com/your-repo/discussions)
- **Code Review**: Tag maintainers in your PR

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
