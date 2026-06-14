# RAG Multi-Agent Recipe Recommendation

A recipe recommendation system combining **Retrieval-Augmented Generation (RAG)** with a **LangChain agent loop**. Tell it your dietary restrictions and available ingredients, and it searches a ~32 000-recipe ChromaDB index to recommend the best matches — powered by Groq's Llama 4 Scout.

---

## How it works

```
User input (Streamlit UI or CLI)
         │
         ▼
  LangChain Agent (Groq / Llama 4 Scout)
         │
         │── search_recipes tool ──► ChromaDB (E5-small-v2 embeddings)
         │◄────────────────────────────────────────────────────────────
         │   (repeated up to 5 times with different queries)
         ▼
  Markdown recipe recommendations
```

1. **Ingestion** (`ingest.py`) — downloads the [Shengtao/recipe](https://huggingface.co/datasets/Shengtao/recipe) dataset (~32 000 recipes) from Hugging Face, embeds every recipe with `intfloat/e5-small-v2`, and stores the vectors in a local ChromaDB collection.
2. **Agent loop** (`recipe_agent/agents/recipe_agent.py`) — a LangChain agent backed by Groq receives a `search_recipes` tool. It calls the tool one or more times with targeted queries, retrieves the top-k semantically similar recipes, checks dietary compliance, and writes a structured Markdown response.
3. **Streamlit UI** (`app.py`) — a web frontend for selecting dietary restrictions and entering ingredients without touching the CLI.

---

## Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com/keys) (`GROQ_API_KEY`)

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/GLima727/RAG-Multi-Agent-RecipeRecomendation.git
cd RAG-Multi-Agent-RecipeRecomendation

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

`python-dotenv` is installed as a dependency, so **the `.env` file is loaded automatically** — no manual `export` needed.

Optional environment variables:

| Variable | Default | Description |
|---|---|---|
| `CHROMA_DB_PATH` | `./chroma_db` | Path to the ChromaDB storage directory |

---

## Quickstart

### Step 1 — Build the recipe index (one-time setup)

```bash
python ingest.py
```

This downloads the recipe dataset (~32 000 recipes) and indexes them. It takes a few minutes the first time and is cached locally in `./chroma_db/`.

Optional flags:

| Flag | Default | Description |
|---|---|---|
| `--subset N` | 32722 | Number of recipes to index |
| `--batch-size N` | 256 | Embedding batch size |
| `--db-path PATH` | `./chroma_db` | ChromaDB storage directory |

### Step 2 — Run the app

**Streamlit UI (recommended):**

```bash
streamlit run app.py
```

Open the URL shown in the terminal. Use the sidebar to enter your API key if not already set via `.env`, select dietary restrictions from the pills menu, enter your available ingredients, and click **Find Recipes**.

**CLI:**

```bash
python main.py
```

You will be prompted for dietary preferences and available ingredients. The agent will search the index and return 3–5 Markdown-formatted recipe recommendations.

---

## Project structure

```
.
├── app.py                         # Streamlit frontend
├── main.py                        # CLI entrypoint
├── ingest.py                      # Dataset ingestion script
├── requirements.txt
├── pytest.ini
├── .env                           # API keys (never committed)
├── recipe_agent/
│   ├── __init__.py                # Public run_agent() entry point
│   ├── agent.py                   # Core agent runner
│   ├── config.py                  # All tuneable constants
│   ├── logger.py                  # Shared logger setup
│   ├── agents/
│   │   └── recipe_agent.py        # LangChain RecipeAgent class
│   ├── rag/
│   │   ├── ingestion.py           # Embedding + ChromaDB pipeline
│   │   └── retriever.py           # Similarity search helper
│   └── tools/
│       └── recipe_search.py       # search_recipes tool definition
└── tests/
    ├── test_ingestion.py
    ├── test_retriever.py
    ├── test_tool.py
    ├── test_pipeline.py
    └── test_e2e.py
```

---

## Running tests

```bash
pytest
```

---

## Troubleshooting

**"ChromaDB index not found"** — Run `python ingest.py` first to build the recipe index.

**"Environment variable 'GROQ_API_KEY' is not set"** — Add `GROQ_API_KEY=...` to your `.env` file or enter it directly in the Streamlit sidebar.

**Slow ingestion** — The default ~32 000-recipe index takes a few minutes. Use `--subset 1000` for a quick test run.

**`DatasetNotFoundError`** — The project requires `datasets==3.6.0` (pinned in `requirements.txt`). If you see version-related errors, run `pip install "datasets==3.6.0"` to realign.
