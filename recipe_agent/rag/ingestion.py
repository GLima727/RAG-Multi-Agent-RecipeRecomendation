"""
rag/ingestion.py — Dataset loading, embedding, and ChromaDB indexing logic.

Kept separate from the CLI (ingest.py at project root) so it can be imported,
tested, or called programmatically without going through argparse.
"""

import json

import chromadb
from datasets import load_dataset
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn
from sentence_transformers import SentenceTransformer

from ..config import (
    CHROMA_COLLECTION_NAME,
    DEFAULT_INGEST_BATCH_SIZE,
    DEFAULT_INGEST_SUBSET,
    EMBED_MODEL,
    HUGGINGFACE_DATASET,
)

console = Console()


# ── Document builders ─────────────────────────────────────────────────────────

def build_document(recipe: dict) -> str:
    """
    Flatten a recipe into a single searchable text block.

    Example output:
        "Title: Garlic Butter Pasta
         Ingredients: 200g spaghetti, 3 cloves garlic, 2 tbsp butter
         Directions: Boil pasta. Melt butter, sauté garlic. Toss and serve."
    """
    title = recipe.get("title", "").strip()

    raw_ing = recipe.get("ingredients", [])
    ingredients = ", ".join(str(i).strip() for i in raw_ing if i) if isinstance(raw_ing, list) else str(raw_ing)

    raw_dir = recipe.get("directions", [])
    directions = " ".join(str(d).strip() for d in raw_dir if d) if isinstance(raw_dir, list) else str(raw_dir)

    return f"Title: {title}\nIngredients: {ingredients}\nDirections: {directions}"


def build_metadata(recipe: dict) -> dict:
    """
    Return a ChromaDB-compatible metadata dict (str/int/float/bool values only).

    Lists are JSON-serialised because ChromaDB doesn't support list values.

    Example output:
        {
            "title": "Garlic Butter Pasta",
            "ingredients": '["200g spaghetti", "3 cloves garlic", "2 tbsp butter"]',
            "directions": '["Boil pasta.", "Melt butter, sauté garlic.", "Toss and serve."]'
        }
    """
    raw_ing = recipe.get("ingredients", [])
    ingredients = [str(i).strip() for i in raw_ing if i] if isinstance(raw_ing, list) else [str(raw_ing)]

    raw_dir = recipe.get("directions", [])
    directions = [str(d).strip() for d in raw_dir if d] if isinstance(raw_dir, list) else [str(raw_dir)]

    return {
        "title": str(recipe.get("title", "")).strip(),
        "ingredients": json.dumps(ingredients),
        "directions": json.dumps(directions),
    }


# ── Main ingestion pipeline ───────────────────────────────────────────────────

def ingest(
    db_path: str,
    subset: int = DEFAULT_INGEST_SUBSET,
    batch_size: int = DEFAULT_INGEST_BATCH_SIZE,
) -> None:
    """
    Load RecipeNLG, embed every recipe, and persist in ChromaDB.

    Parameters
    ----------
    db_path:    Directory for ChromaDB persistence.
    subset:     Number of recipes to index (default 50 000).
    batch_size: Recipes embedded per batch (default 256).
    """
    console.rule("[bold cyan]Recipe Ingestion Pipeline")

    # 1. Dataset
    console.print(f"[bold]Loading dataset[/bold] '{HUGGINGFACE_DATASET}' (first {subset:,} recipes)…")
    dataset = load_dataset(HUGGINGFACE_DATASET, split="train", streaming=False, trust_remote_code=True)
    recipes = dataset.select(range(min(subset, len(dataset))))
    console.print(f"  Loaded [green]{len(recipes):,}[/green] recipes.")

    # 2. Embedding model
    console.print(f"\n[bold]Loading embedding model[/bold] ({EMBED_MODEL})…")
    model = SentenceTransformer(EMBED_MODEL)
    console.print("  Model ready.")

    # 3. ChromaDB — delete existing collection so re-runs produce a clean index
    console.print(f"\n[bold]Connecting to ChromaDB[/bold] at '{db_path}'…")
    client = chromadb.PersistentClient(path=db_path)

    existing = [c.name for c in client.list_collections()]
    if CHROMA_COLLECTION_NAME in existing:
        console.print(f"  [yellow]Collection '{CHROMA_COLLECTION_NAME}' exists — rebuilding.[/yellow]")
        client.delete_collection(CHROMA_COLLECTION_NAME)

    collection = client.create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    console.print(f"  Collection '{CHROMA_COLLECTION_NAME}' created.")

    # 4. Embed + store in batches
    console.print(f"\n[bold]Embedding & storing[/bold] in batches of {batch_size}…\n")
    total = len(recipes)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Ingesting recipes", total=total)

        for start in range(0, total, batch_size):
            batch = recipes.select(range(start, min(start + batch_size, total)))
            documents = [build_document(r) for r in batch]
            metadatas = [build_metadata(r) for r in batch]
            ids = [str(start + i) for i in range(len(batch))]
            embeddings = model.encode(documents, show_progress_bar=False, convert_to_numpy=True)

            collection.add(
                embeddings=embeddings.tolist(),
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            progress.advance(task, len(batch))

    console.print(
        f"\n[bold green]Done![/bold green] "
        f"Indexed [green]{total:,}[/green] recipes into ChromaDB at '{db_path}'."
    )
