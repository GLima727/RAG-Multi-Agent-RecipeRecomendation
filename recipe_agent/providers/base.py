"""
providers/base.py — Abstract base class every LLM provider must implement.
"""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
    Encapsulates one LLM backend.

    Subclasses declare three class-level attributes and implement `run`.
    The agent loop, tool schema, and tool execution are handled by each
    provider independently so that provider-specific quirks stay contained.

    Class attributes
    ----------------
    name        Unique key used in the provider registry (e.g. "anthropic").
    model       Model ID string sent to the API.
    api_key_env Name of the environment variable that holds the API key.
    """

    name: str
    model: str
    api_key_env: str

    @abstractmethod
    def run(self, preferences: str, ingredients: str) -> str:
        """
        Run the full agentic loop and return Markdown-formatted recommendations.

        Parameters
        ----------
        preferences:
            Free-text dietary preferences, e.g. "vegetarian, gluten-free".
        ingredients:
            Comma-separated list of available ingredients.
        """
        ...
