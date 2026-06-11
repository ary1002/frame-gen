# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Python Backend
```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run API server
uvicorn app.main:app --reload

# Run Celery worker
celery -A app.celery_app worker --loglevel=info

# Run all tests
pytest tests/ -v

# Run a single test file
pytest tests/test_timeline.py -v

# Database migrations
alembic upgrade head
```

### Node/Remotion
```bash
cd remotion && npm install && cd ..

# Remotion studio (dev preview UI)
npm run studio

# Render video from schema
node render.mjs <schema_json_path> <output_mp4_path> [upload_url]

# TypeScript check
npm run typecheck
```

### Frontend
```bash
cd frontend && npm install
npm run dev      # Vite dev server
npm run build    # Production build to frontend/dist/
```

### Infrastructure
```bash
# Start Postgres, Redis, MinIO
docker compose up -d
```

## Architecture

**Prompt-to-Video pipeline** — converts a text prompt into a narrated MP4 via a 6-stage async pipeline. FastAPI accepts jobs; Celery workers execute stages; results are stored in PostgreSQL and MinIO (S3-compatible).

### Pipeline Stages

| Stage | Module | Description |
|-------|--------|-------------|
| 1 | `app/llm/script_gen.py` | Claude generates narration text per slide |
| 2A | `app/llm/layout_gen.py` | Claude generates visual layout (template + props + effects) |
| 2B | `app/tts/elevenlabs.py` | ElevenLabs synthesizes audio; ffprobe measures actual duration |
| 3 | `app/pipeline/barrier.py` | Waits until all slides have both audio and layout |
| 4 | `app/pipeline/timeline.py` | Deterministic frame math → builds `RemotionSchema` JSON |
| 5 | `app/pipeline/render.py` | Spawns `node render.mjs` subprocess; uploads MP4 to MinIO |
| 6 | `app/llm/article_gen.py` | Claude generates article (async, parallel to render) |

Stages 2A and 2B run in parallel per slide. Stage 3 is a barrier that blocks Stage 4 until every slide completes both 2A and 2B.

### Key Files

- `app/contracts.py` — Pydantic models for all data passed between stages (`SlideScript`, `SlideLayout`, `RemotionSchema`, etc.)
- `app/states.py` — Slide and job state enums + valid transitions
- `app/pipeline/tasks.py` — All Celery task definitions (one per stage)
- `app/pipeline/quality_gate.py` — Validates scripts (word count, duration); triggers re-generation on failure (up to 3 attempts)
- `remotion/src/types.ts` — TypeScript interfaces mirroring `RemotionSchema`; must stay in sync with `contracts.py`
- `remotion/render.mjs` — Node CLI entry point; bundles composition, selects composition, renders H.264 MP4

### Cross-Runtime Boundary

Python passes a `RemotionSchema` JSON file to Node via subprocess. Node writes progress JSON lines to stdout which Python reads. The schema shape defined in `app/contracts.py` must match `remotion/src/types.ts`.

### Frame Math

All timing is at 30 fps. `duration_frames = round(actual_duration_s × 30)` — actual audio duration from ffprobe drives frame count, not the LLM estimate.

### Storage

`app/storage.py` wraps boto3 for both local MinIO and production S3. JSON blobs (scripts, layouts, schemas) go to MinIO; presigned URLs are returned to clients.

### Frontend

React + Vite SPA in `frontend/`. Talks to the FastAPI backend via `frontend/src/api.js`. `useJobPoller.js` polls job status; components live in `frontend/src/components/`.

### Configuration

All secrets and service URLs are in `.env` (see `.env.example`). Pydantic `Settings` in `app/config.py` validates them at startup.
