"""
rag/ — Retrieval-Augmented Generation pipeline.

    ingestion  — dataset loading, embedding, ChromaDB indexing
    retriever  — ChromaDB similarity search
"""

from .retriever import search_recipes

__all__ = ["search_recipes"]
