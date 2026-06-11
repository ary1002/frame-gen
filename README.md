# Pipeline A — Prompt to Video

Text prompt → narrated MP4 video via Claude (script + layout + article), ElevenLabs (TTS), and Remotion (render).

## Prerequisites

- Python 3.11+, Node 18+, ffmpeg (`apt install ffmpeg`)
- Docker + Docker Compose

## Setup

```bash
# 1. Copy and fill in API keys
cp .env.example .env

# 2. Python deps
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 3. Node deps
cd remotion && npm install && cd ..

# 4. Start services (Postgres, Redis, MinIO)
docker compose up -d

# 5. Run DB migrations
alembic upgrade head
```

## Run

```bash
# Terminal 1 — API
uvicorn app.main:app --reload

# Terminal 2 — Worker
celery -A app.celery_app worker --loglevel=info
```

## Submit a job

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain how neural networks work"}'
# → {"job_id": "<uuid>"}

# Poll status
curl http://localhost:8000/jobs/<uuid>
```

Job progresses: `PENDING → RUNNING → RENDERING → COMPLETE`.  
`video_url` and `article_url` are populated on completion.

## Tests

```bash
pytest tests/ -v
```

## Architecture

```
Prompt → [1] Script gen (Claude)
             ├── [2A] Layout gen (Claude)   ─┐
             └── [2B] TTS (ElevenLabs)      ─┤─ [3] Barrier
                                              ↓
                                    [4] Timeline assembly
                                              ↓
                              [5] Remotion render (Node)
                              [6] Article gen (Claude, parallel)
```

Storage: MinIO (local S3). Swap `MINIO_*` vars for real S3 to go to production.
