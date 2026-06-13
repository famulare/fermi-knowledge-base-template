# Optional: Semantic Search (F2)

This branch adds **semantic search** — local embeddings that boost retrieval recall beyond
keyword + entity matching. It is **optional**: without it, `kb_search` runs keyword + entity +
knowledge-graph fine and **degrades gracefully** (nothing breaks if the embedding server is absent).

This is the only part of the system that needs a heavier tool than `uv` + Python. The rest of the
template — hybrid keyword/entity search, the knowledge graph, modeling-judgment, audit — works on
`main` with no extra setup.

## What it needs

A local **[llama.cpp](https://github.com/ggml-org/llama.cpp)** embedding server. No cloud, no API
key, no GPU required.

1. Install llama.cpp (provides `llama-server`):
   - macOS: `brew install llama.cpp` (or build from source).
2. `numpy` is declared in `pyproject.toml` on this branch — `uv` installs it automatically.
3. Serve the embedding model (downloaded + cached on first run):
   ```bash
   llama-server -hf Qwen/Qwen3-Embedding-0.6B-GGUF --embedding --pooling last \
       -b 8192 -ub 8192 -c 8192 --host 127.0.0.1 --port 8077
   ```
   `uv run scripts/kb_search.py rebuild` also auto-launches a transient server if one isn't running.

## Use

With the server up, `kb_search` automatically fuses semantic similarity into results
(`--mode hybrid`, the default; `--mode semantic` for vectors only). Tune via env vars:
`KB_EMBED_ENABLED=0` (disable), `KB_EMBED_ENDPOINT`, `KB_EMBED_HF`, `KB_EMBED_DIM`.

If the server is unavailable, search silently falls back to keyword + entity — by design.

## Why this is a separate branch

Semantic search is a clear recall win but carries a real setup cost (the llama.cpp server +
a model download) that not every user wants. It lives on this branch so `main` stays
zero-heavy-dependency; merge or cherry-pick it when you want semantic retrieval.
