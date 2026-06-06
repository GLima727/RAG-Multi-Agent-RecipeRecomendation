"""
agent.py — Public orchestration entry point.

Thin layer that resolves the provider and delegates to its `run` method.
All provider-specific logic lives in recipe_agent/providers/.
"""

from .providers import available_providers, get_provider


def run_agent(preferences: str, ingredients: str, provider: str = "anthropic") -> str:
    """
    Run the recipe recommendation agent and return Markdown recommendations.

    Parameters
    ----------
    preferences:
        Free-text dietary preferences, e.g. "vegetarian, gluten-free".
    ingredients:
        Comma-separated available ingredients, e.g. "eggs, spinach, garlic".
    provider:
        LLM backend to use. One of: {available_providers()}.

    Returns
    -------
    str
        Markdown-formatted recipe recommendations from the agent.
    """
    return get_provider(provider).run(preferences, ingredients)
