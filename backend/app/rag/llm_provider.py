"""
LLM provider abstraction used by translation, reconstruction and RAG
context-generation. Reads credentials only from environment variables
(app.core.config.Settings) — never hardcoded.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.config import get_settings


class LLMClient(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> str:
        raise NotImplementedError


class ClaudeLLMClient(LLMClient):
    def __init__(self, api_key: str, model: str):
        import anthropic  # requires `anthropic` package + LLM_API_KEY set

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def complete(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text")


class OpenAICompatibleLLMClient(LLMClient):
    def __init__(self, api_key: str, base_url: str, model: str):
        import openai

        self.client = openai.OpenAI(api_key=api_key, base_url=base_url or None)
        self.model = model

    def complete(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


class DemoLLMClient(LLMClient):
    """DEMO/FALLBACK MODE. Never fabricates historical content — returns an
    explicit placeholder so callers can detect and surface demo mode."""

    def complete(self, prompt: str) -> str:
        return "[DEMO MODE — no LLM_PROVIDER configured. Set LLM_PROVIDER and LLM_API_KEY in .env]"


def get_llm_client() -> LLMClient:
    settings = get_settings()
    try:
        if settings.LLM_PROVIDER == "claude" and settings.LLM_API_KEY:
            return ClaudeLLMClient(settings.LLM_API_KEY, settings.LLM_MODEL)
        if settings.LLM_PROVIDER == "openai_compatible" and settings.LLM_API_KEY:
            return OpenAICompatibleLLMClient(settings.LLM_API_KEY, settings.LLM_BASE_URL, settings.LLM_MODEL)
    except ImportError:
        pass  # required package not installed — fall back to demo
    return DemoLLMClient()
