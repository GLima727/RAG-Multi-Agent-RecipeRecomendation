"""
rag/ — Retrieval-Augmented Generation pipeline.

    ingestion  — dataset loading, embedding, ChromaDB indexing
    retriever  — ChromaDB similarity search
"""

from .ingestion import ingest
from .retriever import search_recipes

__all__ = ["ingest", "search_recipes"]
