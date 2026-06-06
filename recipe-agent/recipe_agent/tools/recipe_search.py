"""
tools/recipe_search.py — search_recipes tool: schemas (all provider formats) + execution.

Adding a new tool means adding a new file here; providers import what they need
from the tools package without caring about which file it comes from.
"""

import json
from typing import Any

from ..config import MAX_TOOL_K
from ..rag.retriever import search_recipes

# ── Shared metadata ───────────────────────────────────────────────────────────

TOOL_NAME = "search_recipes"
TOOL_DESC = (
    "Search the recipe database for recipes matching a natural-language query. "
    "Returns the most relevant recipes with their title, ingredients, and directions. "
    "Call multiple times with different queries to broaden the search."
)

_QUERY_PARAM: dict[str, Any] = {
    "type": "string",
    "description": (
        "Descriptive search query, e.g. "
        "'vegetarian pasta with tomatoes and basil' or 'gluten-free chocolate dessert'."
    ),
}
_K_PARAM: dict[str, Any] = {
    "type": "integer",
    "description": f"Number of recipes to retrieve (default 5, max {MAX_TOOL_K}).",
}
_REQUIRED = ["query"]

# ── Anthropic tool schema ─────────────────────────────────────────────────────

ANTHROPIC_TOOLS: list[dict[str, Any]] = [
    {
        "name": TOOL_NAME,
        "description": TOOL_DESC,
        "input_schema": {
            "type": "object",
            "properties": {"query": _QUERY_PARAM, "k": _K_PARAM},
            "required": _REQUIRED,
        },
    }
]

# ── OpenAI / Groq tool schema ─────────────────────────────────────────────────

OPENAI_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": TOOL_NAME,
            "description": TOOL_DESC,
            "parameters": {
                "type": "object",
                "properties": {"query": _QUERY_PARAM, "k": _K_PARAM},
                "required": _REQUIRED,
            },
        },
    }
]

# ── Gemini tool schema (lazy import to avoid hard dependency) ─────────────────

def get_gemini_tools() -> list:
    """Build the Gemini FunctionDeclaration list (imports google.generativeai lazily)."""
    import google.generativeai as genai

    return [
        genai.protos.Tool(
            function_declarations=[
                genai.protos.FunctionDeclaration(
                    name=TOOL_NAME,
                    description=TOOL_DESC,
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            "query": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description=_QUERY_PARAM["description"],
                            ),
                            "k": genai.protos.Schema(
                                type=genai.protos.Type.INTEGER,
                                description=_K_PARAM["description"],
                            ),
                        },
                        required=_REQUIRED,
                    ),
                )
            ]
        )
    ]


# ── Tool execution ─────────────────────────────────────────────────────────────

def execute_tool(name: str, tool_input: dict[str, Any]) -> str:
    """Dispatch a tool call by name and return the result as a JSON string."""
    if name == TOOL_NAME:
        query = tool_input["query"]
        k = min(int(tool_input.get("k", 5)), MAX_TOOL_K)
        return json.dumps(search_recipes(query=query, k=k), ensure_ascii=False)

    return json.dumps({"error": f"Unknown tool: '{name}'"})


# ── Shared helpers ────────────────────────────────────────────────────────────

def build_user_message(preferences: str, ingredients: str) -> str:
    return (
        f"Dietary preferences: {preferences}\n"
        f"Available ingredients: {ingredients}\n\n"
        "Please recommend the best recipes for me."
    )
