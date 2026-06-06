"""
config.py — Single source of truth for all tuneable constants.

Override path/model via environment variables; everything else lives here.
"""

import os

# ── ChromaDB ──────────────────────────────────────────────────────────────────
CHROMA_DB_PATH: str = os.environ.get("CHROMA_DB_PATH", "./chroma_db")
CHROMA_COLLECTION_NAME: str = "recipes"

# ── Embedding model ───────────────────────────────────────────────────────────
EMBED_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

# ── Dataset ingestion ─────────────────────────────────────────────────────────
HUGGINGFACE_DATASET: str = "mbien/recipenlg"
DEFAULT_INGEST_SUBSET: int = 50_000
DEFAULT_INGEST_BATCH_SIZE: int = 256

# ── Retrieval ─────────────────────────────────────────────────────────────────
DEFAULT_TOP_K: int = 5
MAX_TOOL_K: int = 10   # hard ceiling the agent may request

# ── Agent loop ────────────────────────────────────────────────────────────────
MAX_TOOL_ROUNDS: int = 5

SYSTEM_PROMPT: str = """\
You are a knowledgeable and friendly recipe recommendation assistant.

Your job:
1. Understand the user's dietary preferences and available ingredients.
2. Use the search_recipes tool to find relevant recipes — call it multiple times
   with different, targeted queries if the first search isn't enough (e.g. once
   for the main dish type, again for a dietary constraint).
3. Select the best 3–5 recipes from all retrieved results.
4. Present each recommendation with:
   - The recipe title
   - Which of the user's available ingredients it uses
   - A clear, concise explanation of why it fits their preferences
   - Any simple substitutions if an ingredient is missing

Be practical, enthusiastic, and concise. Do not invent recipes that were not
returned by the tool.
"""
