"""
GraphQL Schema using Strawberry.

This is the unified GraphQL schema that combines all modules:
- Resume generation (jobbernaut-tailor)
- LLM Council deliberation
- Resume matching and scoring
- Job application tracking

Strawberry uses Python type hints for schema definition,
making it very Pythonic and easy to maintain.
"""

from datetime import datetime
from typing import Optional

import strawberry

# =============================================================================
# TYPES - Data structures returned by the API
# =============================================================================


@strawberry.type
class Module:
    """Represents one of the integrated submodules."""

    id: str
    name: str
    description: str
    status: str  # "active", "coming_soon", "maintenance"
    icon: str
    route: str


@strawberry.type
class HealthStatus:
    """API health check response."""

    status: str
    timestamp: datetime
    version: str
    modules_loaded: int


@strawberry.type
class LLMResponse:
    """Response from an LLM query."""

    model: str
    content: str
    tokens_used: int
    latency_ms: int


@strawberry.type
class CouncilDeliberation:
    """Result of LLM Council deliberation."""

    query: str
    individual_responses: list[LLMResponse]
    rankings: list[str]
    final_answer: str
    chairman_model: str


@strawberry.type
class ResumeScore:
    """Resume matching score against a job description."""

    overall_score: float
    keyword_match: float
    ats_compatibility: float
    suggestions: list[str]


@strawberry.type
class JobApplication:
    """A job application record."""

    id: str
    job_title: str
    company: str
    status: str  # "pending", "processing", "completed", "failed"
    created_at: datetime
    resume_url: Optional[str] = None
    cover_letter_url: Optional[str] = None


# =============================================================================
# INPUTS - Data structures for mutations
# =============================================================================


@strawberry.input
class CouncilQueryInput:
    """Input for LLM Council query."""

    query: str
    models: Optional[list[str]] = None  # If None, use defaults
    chairman_model: Optional[str] = None


@strawberry.input
class ResumeMatchInput:
    """Input for resume matching."""

    resume_text: str
    job_description: str


@strawberry.input
class JobApplicationInput:
    """Input for creating a job application."""

    job_title: str
    company: str
    job_description: str
    job_url: Optional[str] = None


# =============================================================================
# QUERIES - Read operations
# =============================================================================


@strawberry.type
class Query:
    """Root Query type - all read operations."""

    @strawberry.field
    def health(self) -> HealthStatus:
        """Check API health status."""
        return HealthStatus(
            status="healthy",
            timestamp=datetime.now(),
            version="0.1.0",
            modules_loaded=5,
        )

    @strawberry.field
    def modules(self) -> list[Module]:
        """Get list of all available modules."""
        return [
            Module(
                id="jobbernaut",
                name="Jobbernaut Tailor",
                description="Industrial-scale resume tailoring with AI validation",
                status="active",
                icon="📄",
                route="/jobbernaut",
            ),
            Module(
                id="llm-council",
                name="LLM Council",
                description="Multi-LLM deliberation with peer review",
                status="active",
                icon="🏛️",
                route="/council",
            ),
            Module(
                id="resume-matcher",
                name="Resume Matcher",
                description="Local AI resume analysis with Ollama",
                status="active",
                icon="🎯",
                route="/matcher",
            ),
            Module(
                id="resume-lm",
                name="ResumeLM",
                description="Full-featured AI resume builder",
                status="coming_soon",
                icon="✨",
                route="/resume-lm",
            ),
            Module(
                id="aihawk",
                name="AIHawk",
                description="Automated job application agent",
                status="coming_soon",
                icon="🦅",
                route="/aihawk",
            ),
        ]

    @strawberry.field
    def module(self, id: str) -> Optional[Module]:
        """Get a specific module by ID."""
        modules = self.modules()
        return next((m for m in modules if m.id == id), None)

    @strawberry.field
    def applications(self, status: Optional[str] = None) -> list[JobApplication]:
        """Get job applications, optionally filtered by status."""
        # TODO: Implement database query
        # For now, return mock data
        mock_apps = [
            JobApplication(
                id="app-001",
                job_title="Senior Software Engineer",
                company="TechCorp",
                status="completed",
                created_at=datetime.now(),
                resume_url="/outputs/resume.pdf",
                cover_letter_url="/outputs/cover_letter.pdf",
            ),
            JobApplication(
                id="app-002",
                job_title="Staff Engineer",
                company="StartupXYZ",
                status="pending",
                created_at=datetime.now(),
            ),
        ]
        if status:
            return [a for a in mock_apps if a.status == status]
        return mock_apps


# =============================================================================
# MUTATIONS - Write operations
# =============================================================================


@strawberry.type
class Mutation:
    """Root Mutation type - all write operations."""

    @strawberry.mutation
    async def ask_council(self, input: CouncilQueryInput) -> CouncilDeliberation:
        """
        Query the LLM Council for a deliberated answer.

        This triggers:
        1. Parallel queries to all council models
        2. Anonymous peer review and ranking
        3. Chairman synthesis of final answer
        """
        # TODO: Integrate with ai/llm_council.py
        # For now, return mock data
        return CouncilDeliberation(
            query=input.query,
            individual_responses=[
                LLMResponse(
                    model="gpt-4",
                    content="GPT-4's response...",
                    tokens_used=150,
                    latency_ms=1200,
                ),
                LLMResponse(
                    model="claude-3",
                    content="Claude's response...",
                    tokens_used=180,
                    latency_ms=1100,
                ),
            ],
            rankings=["claude-3", "gpt-4"],
            final_answer="Synthesized answer from the council...",
            chairman_model="gemini-pro",
        )

    @strawberry.mutation
    async def match_resume(self, input: ResumeMatchInput) -> ResumeScore:
        """
        Analyze how well a resume matches a job description.

        Uses local Ollama model for privacy-preserving analysis.
        """
        # TODO: Integrate with ai/resume_matcher.py
        return ResumeScore(
            overall_score=78.5,
            keyword_match=82.0,
            ats_compatibility=75.0,
            suggestions=[
                "Add more quantifiable achievements",
                "Include keywords: 'distributed systems', 'microservices'",
                "Shorten bullet points to under 118 characters for ATS",
            ],
        )

    @strawberry.mutation
    async def create_application(self, input: JobApplicationInput) -> JobApplication:
        """
        Create a new job application and start the tailoring pipeline.

        This triggers the Jobbernaut pipeline:
        1. Job resonance analysis
        2. Company research
        3. Storytelling arc generation
        4. Resume and cover letter generation
        5. PDF compilation
        """
        # TODO: Integrate with python/jobbernaut_service.py
        return JobApplication(
            id="app-new",
            job_title=input.job_title,
            company=input.company,
            status="pending",
            created_at=datetime.now(),
        )


# =============================================================================
# SCHEMA - Combine Query and Mutation
# =============================================================================

schema = strawberry.Schema(query=Query, mutation=Mutation)

