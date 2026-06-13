#!/usr/bin/env python3
"""Local embedding client for the KB, backed by a llama.cpp embedding server.

Uses the installed `llama-server` (~/.local/bin/llama-server) with
Qwen3-Embedding-0.6B-GGUF over its OpenAI-compatible `/v1/embeddings` endpoint.
Pure stdlib HTTP + numpy — no torch, no extra ML deps.

Embeddings are an *optional acceleration*. If the server can't be reached or
launched, callers fall back to keyword-only retrieval (see kb_search.py).

Config via env (personal instance defaults):
    KB_EMBED_ENABLED   "0" to disable entirely (default on)
    KB_EMBED_HOST      default 127.0.0.1
    KB_EMBED_PORT      default 8077
    KB_EMBED_ENDPOINT  default http://HOST:PORT/v1/embeddings
    KB_EMBED_HF        default Qwen/Qwen3-Embedding-0.6B-GGUF
    KB_EMBED_DIM       default 1024
    KB_EMBED_POOLING   default last
    KB_LLAMA_SERVER    default ~/.local/bin/llama-server
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import numpy as np

ENABLED = os.environ.get("KB_EMBED_ENABLED", "1") != "0"
HOST = os.environ.get("KB_EMBED_HOST", "127.0.0.1")
PORT = int(os.environ.get("KB_EMBED_PORT", "8077"))
ENDPOINT = os.environ.get("KB_EMBED_ENDPOINT", f"http://{HOST}:{PORT}/v1/embeddings")
HEALTH = f"http://{HOST}:{PORT}/health"
MODEL_HF = os.environ.get("KB_EMBED_HF", "Qwen/Qwen3-Embedding-0.6B-GGUF")
DIM = int(os.environ.get("KB_EMBED_DIM", "1024"))
POOLING = os.environ.get("KB_EMBED_POOLING", "last")
LLAMA_SERVER = Path(
    os.environ.get("KB_LLAMA_SERVER", str(Path.home() / ".local" / "bin" / "llama-server"))
)
BATCH = int(os.environ.get("KB_EMBED_BATCH", "16"))
MAX_CHARS = int(os.environ.get("KB_EMBED_MAX_CHARS", "2000"))  # truncate per chunk for embedding

# Session-daemon bookkeeping (in temp dir, keyed by port)
_RUNTIME = Path(tempfile.gettempdir())
PID_PATH = _RUNTIME / f"kb_embed_{PORT}.pid"
LOG_PATH = _RUNTIME / f"kb_embed_{PORT}.log"


def _health_ok(timeout: float = 1.0) -> bool:
    try:
        with urllib.request.urlopen(HEALTH, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


def available() -> bool:
    """True if embeddings can plausibly be produced (endpoint up, or launchable)."""
    return ENABLED and (_health_ok() or LLAMA_SERVER.exists())


def ensure_server(startup_timeout: float = 600.0):
    """Launch a transient embedding server if one isn't already up.

    Returns the Popen handle if we launched one (caller must stop_server it),
    or None if the endpoint was already up / disabled / couldn't launch.
    """
    if not ENABLED or _health_ok() or not LLAMA_SERVER.exists():
        return None
    proc = subprocess.Popen(
        [
            str(LLAMA_SERVER), "-hf", MODEL_HF, "--embedding",
            "--pooling", POOLING, "--host", HOST, "--port", str(PORT),
            "-b", "8192", "-ub", "8192", "-c", "8192",
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + startup_timeout
    while time.time() < deadline:
        if _health_ok():
            return proc
        if proc.poll() is not None:  # server died during startup
            return None
        time.sleep(2)
    proc.terminate()
    return None


def stop_server(proc) -> None:
    if proc is None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except Exception:
        proc.kill()


def _post(texts: list[str], timeout: float = 180.0) -> list[np.ndarray]:
    payload = json.dumps({"input": texts, "model": MODEL_HF}).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read())
    # OpenAI format: {"data": [{"embedding": [...], "index": i}, ...]}; sort by index to be safe.
    items = sorted(data["data"], key=lambda d: d.get("index", 0))
    return [np.asarray(it["embedding"], dtype=np.float32) for it in items]


def embed_texts(texts: list[str]) -> list[np.ndarray] | None:
    """Embed texts → list of L2-normalized float32 vectors, or None if unavailable."""
    if not ENABLED or not texts or not _health_ok():
        return None
    out: list[np.ndarray] = []
    for i in range(0, len(texts), BATCH):
        batch = [t[:MAX_CHARS] if t else " " for t in texts[i:i + BATCH]]
        try:
            out.extend(_post(batch))
        except Exception:
            return None
    # L2-normalize so dot product == cosine
    normed = []
    for v in out:
        n = float(np.linalg.norm(v))
        normed.append(v / n if n > 0 else v)
    return normed


def embed_query(text: str) -> np.ndarray | None:
    vecs = embed_texts([text])
    return vecs[0] if vecs else None


# --- Session daemon control (CLI) -------------------------------------------
# Pattern: bring up at session start, tear down on goodbye. Deliberate sessions.


def _launch_cmd() -> list[str]:
    return [
        str(LLAMA_SERVER), "-hf", MODEL_HF, "--embedding",
        "--pooling", POOLING, "--host", HOST, "--port", str(PORT),
        "-b", "8192", "-ub", "8192", "-c", "8192",
    ]


def start(wait: float = 600.0) -> int:
    """Launch a detached, session-scoped embedding server (idempotent)."""
    if not ENABLED:
        print("embeddings disabled (KB_EMBED_ENABLED=0)")
        return 0
    if _health_ok():
        print(f"embedding server already up at {ENDPOINT}")
        return 0
    if not LLAMA_SERVER.exists():
        print(f"llama-server not found at {LLAMA_SERVER}", file=sys.stderr)
        return 1
    logf = open(LOG_PATH, "ab")
    proc = subprocess.Popen(_launch_cmd(), stdout=logf, stderr=logf, start_new_session=True)
    PID_PATH.write_text(str(proc.pid))
    deadline = time.time() + wait
    while time.time() < deadline:
        if _health_ok():
            print(f"embedding server up (pid {proc.pid}, {MODEL_HF}, dim {DIM})")
            return 0
        if proc.poll() is not None:
            print(f"server exited during startup; see {LOG_PATH}", file=sys.stderr)
            return 1
        time.sleep(2)
    print(f"timeout waiting for embedding server; see {LOG_PATH}", file=sys.stderr)
    return 1


def stop() -> int:
    """Stop the session embedding server, if one is on record."""
    pid = None
    if PID_PATH.exists():
        try:
            pid = int(PID_PATH.read_text().strip())
        except ValueError:
            pid = None
    if pid is not None:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"embedding server stopped (pid {pid})")
        except ProcessLookupError:
            print("embedding server already gone")
        PID_PATH.unlink(missing_ok=True)
        return 0
    print("no embedding server on record")
    return 0


def status() -> int:
    up = _health_ok()
    pid = PID_PATH.read_text().strip() if PID_PATH.exists() else "—"
    print(f"endpoint: {ENDPOINT}")
    print(f"status:   {'UP' if up else 'down'}  (pid {pid})")
    print(f"model:    {MODEL_HF}  dim {DIM}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="KB embedding server control (llama.cpp)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("start", help="Launch a detached session embedding server (idempotent)")
    sub.add_parser("stop", help="Stop the session embedding server")
    sub.add_parser("status", help="Show embedding server status")
    args = ap.parse_args()
    return {"start": start, "stop": stop, "status": status}[args.cmd]()


if __name__ == "__main__":
    sys.exit(main())
