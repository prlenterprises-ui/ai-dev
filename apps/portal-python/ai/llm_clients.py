"""
LLM Client Wrappers - Unified interface for multiple LLM providers.

Supports:
- OpenAI (GPT-4, GPT-4o)
- Anthropic (Claude 3, Claude 3.5)
- Google (Gemini Pro)
- OpenRouter (access to many models via single API)
- Ollama (local models)
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import httpx
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMResponse:
    """Standardized response from any LLM."""

    content: str
    model: str
    tokens_used: int
    latency_ms: float
    raw_response: Optional[dict] = None


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def query(self, prompt: str, **kwargs) -> LLMResponse:
        """Send a query to the LLM and get a response."""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the display name of the model."""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI API client (GPT-4, GPT-4o, etc.)."""

    def __init__(self, model: str = "gpt-4o", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"

    async def query(self, prompt: str, **kwargs) -> LLMResponse:
        import time

        start = time.time()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    **kwargs,
                },
                timeout=60.0,
            )

        latency = (time.time() - start) * 1000
        data = response.json()

        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            model=self.model,
            tokens_used=data.get("usage", {}).get("total_tokens", 0),
            latency_ms=latency,
            raw_response=data,
        )

    def get_model_name(self) -> str:
        return f"OpenAI {self.model}"


class AnthropicClient(BaseLLMClient):
    """Anthropic API client (Claude 3, Claude 3.5)."""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1"

    async def query(self, prompt: str, **kwargs) -> LLMResponse:
        import time

        start = time.time()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": kwargs.get("max_tokens", 4096),
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=60.0,
            )

        latency = (time.time() - start) * 1000
        data = response.json()

        return LLMResponse(
            content=data["content"][0]["text"],
            model=self.model,
            tokens_used=data.get("usage", {}).get("input_tokens", 0)
            + data.get("usage", {}).get("output_tokens", 0),
            latency_ms=latency,
            raw_response=data,
        )

    def get_model_name(self) -> str:
        return f"Anthropic {self.model}"


class OpenRouterClient(BaseLLMClient):
    """
    OpenRouter client - access many models via single API.

    This is great for LLM Council as it provides:
    - GPT-4, Claude, Gemini, Llama, Mistral, etc.
    - Single API key for all models
    - Pay-as-you-go pricing
    """

    def __init__(self, model: str = "openai/gpt-4o", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"

    async def query(self, prompt: str, **kwargs) -> LLMResponse:
        import time

        start = time.time()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:5173",  # Required by OpenRouter
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    **kwargs,
                },
                timeout=120.0,
            )

        latency = (time.time() - start) * 1000
        data = response.json()

        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            model=self.model,
            tokens_used=data.get("usage", {}).get("total_tokens", 0),
            latency_ms=latency,
            raw_response=data,
        )

    def get_model_name(self) -> str:
        # Extract readable name from model identifier
        return self.model.split("/")[-1].replace("-", " ").title()


class OllamaClient(BaseLLMClient):
    """
    Ollama client for local models.

    Great for:
    - Privacy-preserving resume analysis
    - Offline usage
    - Cost-free inference
    """

    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    async def query(self, prompt: str, **kwargs) -> LLMResponse:
        import time

        start = time.time()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=300.0,  # Local models can be slow
            )

        latency = (time.time() - start) * 1000
        data = response.json()

        return LLMResponse(
            content=data.get("response", ""),
            model=self.model,
            tokens_used=data.get("eval_count", 0),
            latency_ms=latency,
            raw_response=data,
        )

    def get_model_name(self) -> str:
        return f"Ollama {self.model}"


# =============================================================================
# FACTORY
# =============================================================================


def create_client(provider: str, model: Optional[str] = None, **kwargs) -> BaseLLMClient:
    """
    Factory function to create LLM clients.

    Usage:
        client = create_client("openai", "gpt-4o")
        client = create_client("anthropic", "claude-3-5-sonnet-20241022")
        client = create_client("openrouter", "google/gemini-pro")
        client = create_client("ollama", "llama3.2")
    """
    providers = {
        "openai": (OpenAIClient, "gpt-4o"),
        "anthropic": (AnthropicClient, "claude-3-5-sonnet-20241022"),
        "openrouter": (OpenRouterClient, "openai/gpt-4o"),
        "ollama": (OllamaClient, "llama3.2"),
    }

    if provider not in providers:
        raise ValueError(f"Unknown provider: {provider}. Choose from: {list(providers.keys())}")

    client_class, default_model = providers[provider]
    return client_class(model=model or default_model, **kwargs)

