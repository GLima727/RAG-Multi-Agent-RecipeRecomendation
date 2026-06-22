"""
Layer 1 — Pure function unit tests.

No model, no DB, no API key required. Tests build_document and build_metadata
in isolation to catch regressions in how recipes are formatted before embedding.
"""

import json

import pytest

from recipe_agent.rag.ingestion import build_document, build_metadata


# ── build_document ────────────────────────────────────────────────────────────

class TestBuildDocument:
    def test_includes_title(self):
        recipe = {"title": "Spaghetti", "ingredients": "pasta", "directions": "boil"}
        assert "Title: Spaghetti" in build_document(recipe)

    def test_includes_ingredients(self):
        recipe = {"title": "X", "ingredients": "garlic; olive oil", "directions": "cook"}
        assert "Ingredients: garlic; olive oil" in build_document(recipe)

    def test_includes_directions(self):
        recipe = {"title": "X", "ingredients": "eggs", "directions": "fry until golden"}
        assert "Directions: fry until golden" in build_document(recipe)

    def test_includes_description_when_present(self):
        recipe = {"title": "X", "description": "A classic dish", "ingredients": "a", "directions": "b"}
        assert "Description: A classic dish" in build_document(recipe)

    def test_omits_description_when_empty(self):
        recipe = {"title": "X", "description": "", "ingredients": "a", "directions": "b"}
        assert "Description" not in build_document(recipe)

    def test_omits_description_when_none(self):
        recipe = {"title": "X", "description": None, "ingredients": "a", "directions": "b"}
        assert "Description" not in build_document(recipe)

    def test_handles_missing_keys_gracefully(self):
        # Should not raise — missing fields fall back to empty strings
        doc = build_document({"title": "Minimal"})
        assert "Title: Minimal" in doc

    def test_returns_string(self):
        assert isinstance(build_document({"title": "X", "ingredients": "y", "directions": "z"}), str)


# ── build_metadata ────────────────────────────────────────────────────────────

class TestBuildMetadata:
    def test_parses_semicolon_separated_ingredients(self):
        recipe = {"ingredients": "pasta; tomato; garlic"}
        meta = build_metadata(recipe)
        assert json.loads(meta["ingredients"]) == ["pasta", "tomato", "garlic"]

    def test_strips_whitespace_from_ingredients(self):
        recipe = {"ingredients": " chicken ;  rice ; salt "}
        ingredients = json.loads(build_metadata(recipe)["ingredients"])
        assert ingredients == ["chicken", "rice", "salt"]

    def test_rating_defaults_to_zero(self):
        assert build_metadata({})["rating"] == 0.0

    def test_rating_count_defaults_to_zero(self):
        assert build_metadata({})["rating_count"] == 0

    def test_rating_is_float(self):
        meta = build_metadata({"rating": "4.5"})
        assert isinstance(meta["rating"], float)

    def test_rating_count_is_int(self):
        meta = build_metadata({"rating_count": "120"})
        assert isinstance(meta["rating_count"], int)

    def test_ingredients_is_json_string(self):
        meta = build_metadata({"ingredients": "egg; flour"})
        # Must be a string (ChromaDB constraint — no list values)
        assert isinstance(meta["ingredients"], str)
        json.loads(meta["ingredients"])  # must be valid JSON

    def test_directions_is_json_string(self):
        meta = build_metadata({"instructions_list": ["Step 1", "Step 2"]})
        assert isinstance(meta["directions"], str)
        assert json.loads(meta["directions"]) == ["Step 1", "Step 2"]

    def test_directions_falls_back_to_directions_field(self):
        meta = build_metadata({"directions": "Mix and bake."})
        directions = json.loads(meta["directions"])
        assert directions == ["Mix and bake."]

    def test_all_values_are_chroma_compatible_types(self):
        meta = build_metadata({
            "title": "Cake",
            "ingredients": "flour; sugar",
            "directions": "mix",
            "category": "dessert",
            "rating": 4.2,
            "rating_count": 50,
            "url": "http://example.com",
        })
        allowed = (str, int, float, bool)
        for key, val in meta.items():
            assert isinstance(val, allowed), f"{key} has unsupported type {type(val)}"
