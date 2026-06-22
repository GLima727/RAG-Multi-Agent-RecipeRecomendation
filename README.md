# RAG Multi-Agent Recipe Recommendation

A recipe recommendation system combining **Retrieval-Augmented Generation (RAG)** with a **LangChain agent loop**. Tell it your dietary restrictions and available ingredients, and it searches a ~32 000-recipe ChromaDB index to recommend the best matches — powered by Groq's Llama 4 Scout.

---

## Architecture

```
Browser (React / Vite)
         │  HTTP  (port 3000 → nginx)
         ▼
  FastAPI API  (port 8000)
         │  JWT auth  ·  /recommend endpoint
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
3. **FastAPI service** (`services/api/`) — exposes `/auth/register`, `/auth/login`, and `/recommend` over HTTP. Passwords are hashed with bcrypt; sessions use signed 24-hour JWTs.
4. **React frontend** (`frontend/`) — a Vite-built SPA served by nginx, with a login/register page and a protected recipe recommendation page.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) (v2+)
- A [Groq API key](https://console.groq.com/keys)

Python 3.10+ and Node.js are **not** required on the host when using Docker.

---

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
# Required — get a key at https://console.groq.com/keys
GROQ_API_KEY=your_groq_api_key_here

# JWT signing secret — change to a long random string in production
SECRET_KEY=change-this-to-a-long-random-secret
```

Optional environment variables:

| Variable | Default | Description |
|---|---|---|
| `CHROMA_DB_PATH` | `./chroma_db` | Path to the ChromaDB storage directory |

---

## Quickstart (Docker)

### Step 1 — Build the recipe index (one-time setup)

```bash
docker compose run --rm ingest
```

This downloads the recipe dataset (~32 000 recipes) and indexes them into a named Docker volume (`chroma_data`). It takes a few minutes the first time.

Optional flags passed to `ingest.py`:

| Flag | Default | Description |
|---|---|---|
| `--subset N` | 32722 | Number of recipes to index |
| `--batch-size N` | 256 | Embedding batch size |

Example with a smaller subset for testing:

```bash
docker compose run --rm ingest python ingest.py --subset 1000
```

### Step 2 — Start the stack

```bash
docker compose up
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

Register an account in the browser, then enter your ingredients and dietary restrictions to get recipe recommendations.

---

## Running locally without Docker

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

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your GROQ_API_KEY and SECRET_KEY

# 5. Build the recipe index (one-time)
python ingest.py

# 6a. Start the API server
uvicorn services.api.main:app --reload

# 6b. Or use the CLI directly (no auth required)
python main.py
```

The CLI (`main.py`) skips authentication and talks to the agent directly, prompting for dietary preferences and ingredients in the terminal.

---

## Project structure

```
.
├── Dockerfile                     # Shared image for API and ingest services
├── docker-compose.yml             # API + frontend + ingest services
├── ingest.py                      # Dataset ingestion script
├── main.py                        # CLI entrypoint (no auth)
├── requirements.txt               # All dependencies (dev + test)
├── requirements-api.txt           # API service (CPU-only PyTorch)
├── requirements-ingest.txt        # Ingest service (CPU-only PyTorch)
├── .env.example                   # Template for environment variables
├── recipe_agent/
│   ├── __init__.py                # Public run_agent() entry point
│   ├── agent.py                   # Core agent runner
│   ├── config.py                  # Tuneable constants
│   ├── logger.py                  # Shared logger setup
│   ├── agents/
│   │   └── recipe_agent.py        # LangChain RecipeAgent class
│   ├── rag/
│   │   ├── ingestion.py           # Embedding + ChromaDB pipeline
│   │   └── retriever.py           # Similarity search helper
│   └── tools/
│       └── recipe_search.py       # search_recipes tool definition
├── services/
│   ├── api/
│   │   ├── main.py                # FastAPI app (CORS, routers)
│   │   ├── models.py              # Pydantic request/response models
│   │   ├── security.py            # JWT creation/validation, bcrypt helpers
│   │   ├── store.py               # In-memory user store
│   │   └── routers/
│   │       ├── auth.py            # /auth/register, /auth/login
│   │       └── recipes.py         # /recommend (JWT-protected)
│   └── tests/
│       ├── test_ingestion.py
│       ├── test_retriever.py
│       ├── test_tool.py
│       ├── test_pipeline.py
│       └── test_e2e.py
└── frontend/
    ├── Dockerfile                 # Vite build → nginx
    ├── nginx.conf
    └── src/
        ├── App.jsx
        ├── api/client.js          # Axios wrapper
        ├── context/AuthContext.jsx
        ├── components/
        └── pages/
            ├── Login.jsx
            └── Home.jsx
```

---

## API reference

All endpoints are documented interactively at `http://localhost:8000/docs`.

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | — | Create a new account, returns JWT |
| `POST` | `/auth/login` | — | Verify credentials, returns JWT |
| `POST` | `/recommend` | Bearer JWT | Get recipe recommendations |
| `GET` | `/health` | — | Health check |

---

## Running tests

```bash
pytest -m "not e2e"        # unit tests only (no API key or ChromaDB needed)
pytest                     # all tests (requires GROQ_API_KEY and a populated index)
```

End-to-end tests (`-m e2e`) require a live Groq API key and a populated ChromaDB index, so they are skipped in CI.

---

## CI/CD

GitHub Actions runs on every push and pull request to `main` / `dev`:

| Job | What it does |
|---|---|
| **Lint** | `ruff check` + `ruff format --check` |
| **Test** | `pytest -m "not e2e"` with a placeholder API key |
| **Docker Build** | Builds both the API and frontend images (no push) |

---

## Troubleshooting

**"ChromaDB index not found"** — Run `docker compose run --rm ingest` (or `python ingest.py` locally) first to build the recipe index.

**"Environment variable 'GROQ_API_KEY' is not set"** — Add `GROQ_API_KEY=...` to your `.env` file.

**"SECRET_KEY" warning** — The API falls back to a hardcoded development secret if `SECRET_KEY` is missing. Always set a strong random value in production.

**Slow ingestion** — The default ~32 000-recipe index takes a few minutes. Use `--subset 1000` for a quick test run.

**`DatasetNotFoundError`** — The project requires `datasets==3.6.0` (pinned in `requirements.txt`). Run `pip install "datasets==3.6.0"` to realign.
