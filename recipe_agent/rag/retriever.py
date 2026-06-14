"""
rag/retriever.py — ChromaDB query interface.

Module-level lazy singletons keep the embedding model and DB client
initialised once per process and reused across all tool calls.
"""

import json
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer

from ..config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DB_PATH,
    DEFAULT_TOP_K,
    EMBED_MODEL,
)
from ..logger import get_logger

log = get_logger("retriever")

_model: SentenceTransformer | None = None
_collection: chromadb.Collection | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def _get_collection() -> chromadb.Collection:
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        _collection = client.get_collection(CHROMA_COLLECTION_NAME)
    return _collection


def search_recipes(
    query: str,
    k: int = DEFAULT_TOP_K,
) -> list[dict[str, Any]]:
    """
    Embed *query* and return the top-k most similar recipes from ChromaDB.

    Dietary compliance is assessed by the agent from the returned ingredients
    list rather than by keyword post-filtering here.

    Each result dict contains:
        title        — recipe title
        ingredients  — list[str]
        directions   — list[str]
        category     — AllRecipes category (e.g. "world-cuisine", "main-dish")
        rating       — average user rating (0.0 if unavailable)
        rating_count — number of ratings (0 if unavailable)
        url          — full AllRecipes URL for the recipe
        document     — full embedded text
        score        — cosine similarity in [0, 1] (higher = more relevant)
    """
    log.debug("search_recipes query=%r k=%d", query, k)
    embedding = _get_model().encode(["query: " + query], convert_to_numpy=True)[0].tolist()

    results = _get_collection().query(
        query_embeddings=[embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    recipes: list[dict[str, Any]] = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        # ChromaDB cosine space: distance 0 = identical, 2 = opposite.
        score = round(1.0 - dist / 2.0, 4)
        recipes.append({
            "title": meta.get("title", "Unknown"),
            "ingredients": json.loads(meta.get("ingredients", "[]")),
            "directions": json.loads(meta.get("directions", "[]")),
            "category": meta.get("category", ""),
            "rating": meta.get("rating", 0.0),
            "rating_count": meta.get("rating_count", 0),
            "url": meta.get("url", ""),
            "document": doc,
            "score": score,
        })

    log.debug(
        "search_recipes returned %d results: %s",
        len(recipes),
        [(r["title"], r["score"]) for r in recipes],
    )
    return recipes
