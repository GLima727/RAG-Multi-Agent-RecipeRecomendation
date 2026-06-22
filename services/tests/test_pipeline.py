"""
Pipeline diagnostic tests.

These tests verify each stage of the pipeline independently so you can
pinpoint exactly where a failure occurs without running the full agent.

No LLM API key required — all tests stop at the ChromaDB/tool layer.
Requires ingestion to have been run first (python ingest.py).
"""

import json
import pytest

from recipe_agent.rag.retriever import search_recipes
from recipe_agent.tools.recipe_search import execute_tool

# Ingredients clearly associated with meat
_MEAT_KEYWORDS = {
    "chicken", "beef", "pork", "lamb", "turkey", "bacon", "ham",
    "sausage", "salami", "pepperoni", "veal", "duck", "venison",
    "anchovies", "tuna", "salmon", "shrimp", "crab", "lobster",
    "fish sauce", "oyster sauce", "lard", "gelatin",
}

# Ingredients clearly associated with dairy
_DAIRY_KEYWORDS = {
    "milk", "butter", "cream", "cheese", "yogurt", "ghee",
    "whey", "casein", "lactose", "cheddar", "parmesan", "mozzarella",
    "brie", "ricotta", "sour cream", "cream cheese", "half-and-half",
}


def _ingredient_set(recipe: dict) -> set[str]:
    """Return a lowercase flat set of ingredient words for a recipe."""
    return {word for ing in recipe["ingredients"] for word in ing.lower().split()}


def _contains_any(recipe: dict, keywords: set[str]) -> list[str]:
    """Return which keywords appear as whole words in the recipe's ingredient list.

    Uses word-boundary matching so 'milk' does not match 'soy milk'
    (it would, since 'milk' is at a word boundary there — but 'oat milk'
    and 'almond milk' are dairy substitutes, not dairy). We exclude known
    plant-based qualifiers to avoid false positives.
    """
    import re
    hits = []
    raw = " ".join(recipe["ingredients"]).lower()
    for kw in keywords:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, raw):
            # Skip if a plant-based qualifier precedes the keyword
            plant_pattern = r"(soy|oat|almond|coconut|rice|cashew|hemp|flax)\s+" + re.escape(kw)
            if not re.search(plant_pattern, raw):
                hits.append(kw)
    return hits


# ── Stage 1: ChromaDB is alive and populated ──────────────────────────────────

class TestChromaDBHealth:
    def test_search_returns_results(self):
        """ChromaDB is reachable and has indexed recipes."""
        results = search_recipes("pasta", k=1)
        assert len(results) == 1, "ChromaDB returned no results — has ingestion been run?"

    def test_results_have_non_empty_titles(self):
        for r in search_recipes("soup", k=5):
            assert r["title"].strip(), f"Empty title in result: {r}"

    def test_results_have_ingredients(self):
        for r in search_recipes("cake", k=5):
            assert len(r["ingredients"]) > 0, f"Recipe '{r['title']}' has no ingredients"


# ── Stage 2: Retrieval relevance per dietary need ─────────────────────────────

class TestVegetarianRetrieval:
    """
    Verify that searching with vegetarian-specific queries returns recipes
    that plausibly avoid meat. This tests the retrieval layer only —
    dietary enforcement is the agent's job, but retrieval should help it.
    """

    def test_vegetarian_pasta_query(self):
        results = search_recipes("vegetarian pasta no meat", k=10)
        meat_hits = [(r["title"], _contains_any(r, _MEAT_KEYWORDS)) for r in results]
        safe_count = sum(1 for _, hits in meat_hits if not hits)
        # Retrieval doesn't enforce dietary constraints — the agent filters later.
        # We just need enough clean candidates (>=3) for the agent to recommend from.
        assert safe_count >= 3, (
            f"Fewer than 3 meat-free candidates in top-10 results — "
            f"agent won't have enough options.\n"
            f"All results: " + "\n".join(f"  {t}: {'MEAT' if h else 'ok'}" for t, h in meat_hits)
        )

    def test_vegan_dessert_query(self):
        results = search_recipes("vegan dessert no dairy no eggs", k=10)
        dairy_hits = [(r["title"], _contains_any(r, _DAIRY_KEYWORDS)) for r in results]
        dairy_count = sum(1 for _, hits in dairy_hits if hits)
        assert dairy_count <= len(results) // 2, (
            f"More than half of results contain dairy:\n"
            + "\n".join(f"  {t}: {h}" for t, h in dairy_hits if h)
        )


class TestSpecificDietaryQueries:
    def test_chicken_query_returns_chicken(self):
        results = search_recipes("chicken dinner", k=5)
        hits = [r for r in results if "chicken" in " ".join(r["ingredients"]).lower()
                or "chicken" in r["title"].lower()]
        assert len(hits) >= 3, (
            f"Expected mostly chicken recipes, got: {[r['title'] for r in results]}"
        )

    def test_chocolate_query_returns_chocolate(self):
        results = search_recipes("chocolate cake brownie", k=5)
        hits = [r for r in results if "chocolate" in " ".join(r["ingredients"]).lower()
                or "chocolate" in r["title"].lower()]
        assert len(hits) >= 3, (
            f"Expected mostly chocolate recipes, got: {[r['title'] for r in results]}"
        )

    def test_scores_are_reasonable(self):
        """Top results should have meaningfully high similarity scores."""
        results = search_recipes("spaghetti bolognese", k=5)
        assert results[0]["score"] >= 0.7, (
            f"Top result score too low ({results[0]['score']:.3f}) — "
            "embedding model may be mismatched with the index (re-run ingest.py)"
        )


# ── Stage 3: Tool layer passes results through correctly ──────────────────────

class TestToolPipeline:
    def test_tool_returns_parseable_recipes(self):
        raw = execute_tool("search_recipes", {"query": "vegetarian curry", "k": 3})
        recipes = json.loads(raw)
        assert len(recipes) == 3
        for r in recipes:
            assert "title" in r
            assert "ingredients" in r
            assert isinstance(r["ingredients"], list)

    def test_tool_result_ingredients_are_strings(self):
        raw = execute_tool("search_recipes", {"query": "salad", "k": 3})
        recipes = json.loads(raw)
        for r in recipes:
            for ing in r["ingredients"]:
                assert isinstance(ing, str), f"Non-string ingredient: {ing!r}"

    def test_tool_score_present_and_valid(self):
        raw = execute_tool("search_recipes", {"query": "soup", "k": 3})
        recipes = json.loads(raw)
        for r in recipes:
            assert "score" in r
            assert 0.0 <= r["score"] <= 1.0


# ── Stage 4: Dietary compliance spot-check (no LLM needed) ───────────────────

class TestDietaryCompliance:
    """
    Simulate what the agent does: retrieve candidates, then check compliance.
    These tests expose whether the retrieval layer is giving the agent
    reasonable candidates to filter from.
    """

    def test_vegetarian_candidates_mostly_safe(self):
        """
        For a vegetarian query, at least 50% of candidates should be safe
        so the agent has enough compliant options to recommend.
        """
        results = search_recipes("vegetarian dinner easy", k=10)
        safe = [r for r in results if not _contains_any(r, _MEAT_KEYWORDS)]
        assert len(safe) >= 5, (
            f"Only {len(safe)}/10 vegetarian candidates are meat-free.\n"
            "Unsafe recipes: "
            + str([(r["title"], _contains_any(r, _MEAT_KEYWORDS))
                   for r in results if _contains_any(r, _MEAT_KEYWORDS)])
        )

    def test_gluten_free_query_returns_candidates(self):
        results = search_recipes("gluten free dinner rice potato", k=5)
        assert len(results) == 5

    def test_retrieval_gives_agent_enough_options(self):
        """
        For a specific preference, at least one of the top-5 results
        should be plausibly usable — i.e. have a non-trivial score.
        """
        results = search_recipes("quick 30 minute weeknight dinner", k=5)
        assert any(r["score"] >= 0.6 for r in results), (
            f"No result scored above 0.6: {[(r['title'], r['score']) for r in results]}"
        )
