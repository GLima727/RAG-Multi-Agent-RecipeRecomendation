# RAG Multi-Agent Recipe Recommendation

A CLI-based recipe recommendation agent that combines **Retrieval-Augmented Generation (RAG)** with a **multi-provider LLM agent loop**. Tell it your dietary preferences and available ingredients, and it searches a 7 000-recipe ChromaDB index to recommend the best matches — powered by your choice of Claude, GPT-4o, Groq (Llama 3), or Gemini.

---

## How it works

```
User input
    │
    ▼
LLM Agent  ──── search_recipes tool ────►  ChromaDB (RecipeNLG embeddings)
    │                                            │
    │◄───────────────────────────────────────────┘
    │
    ▼
Markdown recipe recommendations
```

1. **Ingestion** (`ingest.py`) — downloads the [recipe_nlg_lite dataset](https://huggingface.co/datasets/m3hrdadfi/recipe_nlg_lite) from Hugging Face, embeds every recipe with `sentence-transformers/all-MiniLM-L6-v2`, and stores the vectors in a local ChromaDB collection.
2. **Agent loop** (`main.py`) — the chosen LLM receives a `search_recipes` tool. It calls the tool one or more times with targeted queries, retrieves the top-k semantically similar recipes, and writes a structured Markdown response.

---

## Prerequisites

- Python 3.10+
- One or more API keys (see [Configuration](#configuration))

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

Copy `.env` (already provided) and fill in the key(s) for the provider(s) you want to use:

```bash
cp .env .env          # it's already there — just open and edit it
```

| Provider | Environment variable | Where to get the key |
|---|---|---|
| Anthropic (Claude) | `ANTHROPIC_API_KEY` | https://console.anthropic.com/ |
| OpenAI (GPT-4o mini) | `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| Groq (Llama 3) | `GROQ_API_KEY` | https://console.groq.com/keys |
| Google Gemini | `GEMINI_API_KEY` | https://aistudio.google.com/app/apikey |

`python-dotenv` is installed as a dependency, so **the `.env` file is loaded automatically** when you run `main.py` — no manual `export` needed.

> Only the key for the provider you choose needs to be set.

---

## Quickstart

### Step 1 — Build the recipe index (one-time setup)

```bash
python ingest.py
```

This downloads the recipe_nlg_lite dataset (~7 000 recipes) and indexes them. It takes a minute or two the first time and is cached locally in `./chroma_db/`.

Optional flags:

| Flag | Default | Description |
|---|---|---|
| `--subset N` | 7000 | Number of recipes to index |
| `--batch-size N` | 256 | Embedding batch size |
| `--db-path PATH` | `./chroma_db` | ChromaDB storage directory |

### Step 2 — Run the agent

```bash
# Default provider: Anthropic (Claude)
python main.py

# Choose a different provider
python main.py --provider openai
python main.py --provider groq
python main.py --provider gemini
```

You will be prompted for:
- **Dietary preferences** — e.g. `vegetarian`, `gluten-free`, `low-carb`
- **Available ingredients** — e.g. `chicken, garlic, lemon, olive oil`

The agent will then search the index and return 3–5 Markdown-formatted recipe recommendations.

---

## Project structure

```
.
├── main.py                        # CLI entrypoint
├── ingest.py                      # Dataset ingestion script
├── requirements.txt
├── .env                           # API keys (never committed)
└── recipe_agent/
    ├── agent.py                   # Public run_agent() function
    ├── config.py                  # All tuneable constants
    ├── providers/
    │   ├── anthropic_provider.py  # Claude
    │   ├── openai_provider.py     # GPT-4o mini + Groq
    │   └── gemini_provider.py     # Gemini 1.5 Flash
    ├── rag/
    │   ├── ingestion.py           # Embedding + ChromaDB pipeline
    │   └── retriever.py           # Similarity search helper
    └── tools/
        └── recipe_search.py       # search_recipes tool definition
```

---

## Adding a new LLM provider

1. Create `recipe_agent/providers/<name>_provider.py` subclassing `BaseProvider`.
2. Implement `run(self, preferences, ingredients) -> str` following the existing examples.
3. Register it in `recipe_agent/providers/__init__.py` under `REGISTRY`.

---

## Troubleshooting

**"ChromaDB index not found"** — Run `python ingest.py` first.

**"Missing API key"** — Make sure the relevant environment variable is exported in your shell session (see [Configuration](#configuration)).

**Slow ingestion** — The default 7 000-recipe index typically completes in 1–2 minutes. Use `--subset 1000` for an even faster test run.

**`DatasetNotFoundError` or script errors** — The project requires `datasets==3.6.0` (pinned in `requirements.txt`). If you see version-related errors, run `pip install "datasets==3.6.0"` to realign.
