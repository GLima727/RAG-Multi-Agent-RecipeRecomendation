"""
providers/__init__.py — Provider registry.

To add a new provider:
  1. Create providers/<name>_provider.py with a class that subclasses BaseProvider.
  2. Import it here and add it to REGISTRY.
"""

from .anthropic_provider import AnthropicProvider
from .base import BaseProvider
from .gemini_provider import GeminiProvider
from .openai_provider import GroqProvider, OpenAIProvider

REGISTRY: dict[str, type[BaseProvider]] = {
    AnthropicProvider.name: AnthropicProvider,
    OpenAIProvider.name:    OpenAIProvider,
    GroqProvider.name:      GroqProvider,
    GeminiProvider.name:    GeminiProvider,
}


def get_provider(name: str) -> BaseProvider:
    """Instantiate and return the provider registered under *name*."""
    if name not in REGISTRY:
        raise ValueError(f"Unknown provider '{name}'. Available: {list(REGISTRY)}")
    return REGISTRY[name]()


def available_providers() -> list[str]:
    return list(REGISTRY)


__all__ = ["BaseProvider", "REGISTRY", "get_provider", "available_providers"]
