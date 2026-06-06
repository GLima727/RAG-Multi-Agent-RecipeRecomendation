"""
recipe_agent — RAG-powered recipe recommendation agent.

Quick start
-----------
    from recipe_agent import run_agent
    result = run_agent("vegetarian", "eggs, spinach, garlic", provider="anthropic")
"""

from .agent import run_agent

__all__ = ["run_agent"]
