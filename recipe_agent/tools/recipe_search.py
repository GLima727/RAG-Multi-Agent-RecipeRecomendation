import json

from langchain_core.tools import tool

from ..config import MAX_TOOL_K
from ..logger import get_logger
from ..rag.retriever import search_recipes as _search_recipes

log = get_logger("tools.recipe_search")


@tool
def search_recipes(query: str, k: int = 5) -> str:
    """Search the recipe database for recipes matching a natural-language query.
    Returns the most relevant recipes with their title, ingredients, directions,
    category, rating, and URL. Call multiple times with different queries to broaden the search.

    Args:
        query: Descriptive search query, e.g. 'pasta with tomatoes and basil'.
        k: Number of recipes to retrieve (default 5, max 10).
    """
    k = min(k, MAX_TOOL_K)
    log.debug("search_recipes query=%r k=%d", query, k)
    results = _search_recipes(query=query, k=k)
    log.debug("search_recipes returned %d results", len(results))
    return json.dumps(results, ensure_ascii=False)
