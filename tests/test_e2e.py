"""
Layer 4 — End-to-end agent tests.

Calls the real Groq API and costs money. Skipped by default.
Run explicitly with: E2E=1 pytest tests/test_e2e.py
"""

import os

import pytest

from recipe_agent import run_agent

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module", autouse=True)
def require_e2e_flag():
    if os.environ.get("E2E", "").strip() != "1":
        pytest.skip("Set E2E=1 to run end-to-end tests")
    if not os.environ.get("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY not set")


class TestGroqE2E:
    def test_returns_non_empty_string(self):
        result = run_agent("any", "chicken, garlic, onion", provider="groq")
        assert isinstance(result, str) and len(result) > 50

    def test_response_has_urls(self):
        result = run_agent("any", "pasta, tomato", provider="groq")
        assert "allrecipes.com" in result

    def test_vegetarian_restriction(self):
        result = run_agent(
            preferences="simple recipes",
            ingredients="tofu, soy sauce, rice",
            provider="groq",
            dietary_restrictions=["vegetarian"],
        )
        assert len(result) > 50
