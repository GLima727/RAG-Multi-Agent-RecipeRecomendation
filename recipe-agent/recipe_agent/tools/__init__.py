"""
tools/ — Agent tool definitions and execution.

Each file in this package defines one tool (schema + execute function).
Providers import from here without knowing which file a symbol lives in.
"""

from .recipe_search import (
    ANTHROPIC_TOOLS,
    OPENAI_TOOLS,
    TOOL_DESC,
    TOOL_NAME,
    build_user_message,
    execute_tool,
    get_gemini_tools,
)

__all__ = [
    "TOOL_NAME",
    "TOOL_DESC",
    "ANTHROPIC_TOOLS",
    "OPENAI_TOOLS",
    "get_gemini_tools",
    "execute_tool",
    "build_user_message",
]
