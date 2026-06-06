# Scoutr — project commands. `just` is our AI-readable interface (Integral SDLC2).
# Day-1 subset; ingest/eval/trace/capture-failure land on later days.

# List available recipes.
default:
    @just --list

# Install/refresh the environment.
sync:
    uv sync

# Run the MCP server over stdio (what Claude Desktop launches).
serve:
    uv run python -m scoutr.main

# Interactive testing in the MCP Inspector (browser UI).
dev:
    uv run mcp dev src/scoutr/mcp_server/server.py

# Lint, types, tests — the same gates CI runs.
lint:
    uv run ruff check .
    uv run ruff format --check .

typecheck:
    uv run mypy

test:
    uv run pytest

# Full local gate; run before every PR.
check: lint typecheck test

# Ingest API data into DB
ingest:
    uv run python -c "import asyncio; from scoutr.catalog.ingest import ingest; print(asyncio.run(ingest()))"

# Bring up the DB
db-up:
    docker compose up -d db

# Migrations
migrate:
    uv run alembic upgrade head
