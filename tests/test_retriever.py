"""
Layer 2 — Retriever integration tests.

Hits real ChromaDB and the real embedding model. Requires that ingestion
has been run (python ingest.py) before these tests will pass.

These are the most valuable tests in the suite: they validate embedding
quality and retrieval relevance without spending money on LLM API calls.
"""

import pytest

from recipe_agent.rag.retriever import search_recipes


# ── Result shape ──────────────────────────────────────────────────────────────

class TestResultShape:
    def test_returns_list(self):
        results = search_recipes("pasta with tomatoes")
        assert isinstance(results, list)

    def test_default_returns_five_results(self):
        results = search_recipes("chicken soup")
        assert len(results) == 5

    def test_k_parameter_respected(self):
        assert len(search_recipes("tacos", k=3)) == 3
        assert len(search_recipes("tacos", k=8)) == 8

    def test_result_has_required_keys(self):
        result = search_recipes("chocolate cake", k=1)[0]
        expected_keys = {"title", "ingredients", "directions", "category", "rating", "rating_count", "url", "document", "score"}
        assert expected_keys.issubset(result.keys())

    def test_ingredients_is_list(self):
        result = search_recipes("salad", k=1)[0]
        assert isinstance(result["ingredients"], list)

    def test_directions_is_list(self):
        result = search_recipes("salad", k=1)[0]
        assert isinstance(result["directions"], list)

    def test_score_is_float_in_range(self):
        for r in search_recipes("grilled salmon", k=5):
            assert isinstance(r["score"], float)
            assert 0.0 <= r["score"] <= 1.0


# ── Result ordering ───────────────────────────────────────────────────────────

class TestResultOrdering:
    def test_results_ordered_by_descending_score(self):
        results = search_recipes("vegetarian curry", k=5)
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_top_result_has_higher_score_than_last(self):
        results = search_recipes("beef stew", k=5)
        assert results[0]["score"] >= results[-1]["score"]


# ── Relevance smoke tests ─────────────────────────────────────────────────────
# These are intentionally lenient — we check that results are plausibly
# relevant, not that a specific recipe appears. Exact results change if the
# index is rebuilt or the model is swapped.

class TestRelevance:
    def test_chocolate_query_returns_chocolate_recipes(self):
        results = search_recipes("chocolate cake", k=5)
        titles_and_ingredients = " ".join(
            r["title"].lower() + " ".join(r["ingredients"]).lower()
            for r in results
        )
        assert "chocolate" in titles_and_ingredients

    def test_pasta_query_returns_pasta_recipes(self):
        results = search_recipes("pasta with garlic and olive oil", k=5)
        combined = " ".join(r["title"].lower() for r in results)
        assert any(word in combined for word in ["pasta", "spaghetti", "linguine", "noodle"])

    def test_different_queries_return_different_results(self):
        titles_a = {r["title"] for r in search_recipes("chocolate dessert", k=5)}
        titles_b = {r["title"] for r in search_recipes("spicy chicken wings", k=5)}
        # Result sets should not be identical
        assert titles_a != titles_b
