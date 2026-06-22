"""
ingest.py — CLI wrapper for the ingestion pipeline.

Run once (or re-run to rebuild the index):
    python ingest.py [--subset 50000] [--batch-size 256] [--db-path ./chroma_db]
"""

import argparse

from recipe_agent.config import CHROMA_DB_PATH, DEFAULT_INGEST_BATCH_SIZE, DEFAULT_INGEST_SUBSET
from recipe_agent.rag.ingestion import ingest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the ChromaDB recipe index from RecipeNLG.")
    parser.add_argument("--subset",     type=int, default=DEFAULT_INGEST_SUBSET,     help="Number of recipes to index")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_INGEST_BATCH_SIZE, help="Embedding batch size")
    parser.add_argument("--db-path",    type=str, default=CHROMA_DB_PATH,            help="ChromaDB persistence directory")
    args = parser.parse_args()

    ingest(db_path=args.db_path, subset=args.subset, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
