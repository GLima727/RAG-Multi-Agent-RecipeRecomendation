"""
Layer 3 — Tool dispatch tests.

Tests execute_tool and build_user_message without touching the LLM.
Validates the glue layer between the agent loop and the retriever.
"""

import json

import pytest

from recipe_agent.config import MAX_TOOL_K
from recipe_agent.tools.recipe_search import build_user_message, execute_tool


# ── execute_tool ──────────────────────────────────────────────────────────────

class TestExecuteTool:
    def test_returns_json_string(self):
        result = execute_tool("search_recipes", {"query": "pasta"})
        assert isinstance(result, str)
        json.loads(result)  # must be valid JSON

    def test_returns_list_of_recipes(self):
        result = json.loads(execute_tool("search_recipes", {"query": "soup"}))
        assert isinstance(result, list)

    def test_default_k_is_five(self):
        result = json.loads(execute_tool("search_recipes", {"query": "salad"}))
        assert len(result) == 5

    def test_k_is_respected(self):
        result = json.loads(execute_tool("search_recipes", {"query": "cake", "k": 3}))
        assert len(result) == 3

    def test_k_is_capped_at_max_tool_k(self):
        result = json.loads(execute_tool("search_recipes", {"query": "steak", "k": 999}))
        assert len(result) <= MAX_TOOL_K

    def test_unknown_tool_returns_error(self):
        result = json.loads(execute_tool("nonexistent_tool", {}))
        assert "error" in result

    def test_unknown_tool_error_mentions_name(self):
        result = json.loads(execute_tool("make_reservation", {}))
        assert "make_reservation" in result["error"]


# ── build_user_message ────────────────────────────────────────────────────────

class TestBuildUserMessage:
    def test_includes_preferences(self):
        msg = build_user_message("low-carb", "chicken, broccoli")
        assert "low-carb" in msg

    def test_includes_ingredients(self):
        msg = build_user_message("any", "eggs, spinach, garlic")
        assert "eggs, spinach, garlic" in msg

    def test_includes_dietary_restrictions(self):
        msg = build_user_message("any", "tofu", dietary_restrictions=["vegan", "gluten-free"])
        assert "vegan" in msg
        assert "gluten-free" in msg

    def test_no_restrictions_says_none(self):
        msg = build_user_message("any", "chicken", dietary_restrictions=None)
        assert "none" in msg.lower()

    def test_returns_string(self):
        assert isinstance(build_user_message("any", "rice"), str)
