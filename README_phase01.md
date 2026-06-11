# Pipeline A — Phases 0 & 1

Prompt-to-video pipeline: infrastructure scaffold (Phase 0) and script generation (Phase 1).

## Prerequisites

- Docker & Docker Compose
- Python 3.11+
- `pip` or a virtual-env manager

## Quick Start

### 1. Copy and fill in secrets

```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY (required for Phase 1)
# Set ELEVENLABS_API_KEY / ELEVENLABS_VOICE_ID when you reach Phase 2b
```

### 2. Start infrastructure

```bash
docker compose up -d
```

This starts:
- **PostgreSQL 16** on `localhost:5432`
- **Redis 7** on `localhost:6379`
- **MinIO** on `localhost:9000` (console on `localhost:9001`)
- A one-shot `createbuckets` container that creates the `pipeline-a` bucket

Wait ~10 seconds for health checks to pass, then verify:

```bash
docker compose ps
```

### 3. Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 4. Run database migrations

```bash
# Apply alembic migrations (if any versions exist)
alembic upgrade head

# Or let the FastAPI lifespan create tables automatically on first start (dev mode)
```

### 5. Start the API server

```bash
uvicorn app.main:app --reload --port 8000
```

On first start the lifespan creates all DB tables and seeds `PromptTemplate` rows.

### 6. Start the Celery worker

In a separate terminal:

```bash
celery -A app.celery_app worker --loglevel=info
```

### 7. Submit a job

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain how black holes form in 5 slides."}'
```

The response returns a `job_id`. Poll status:

```bash
curl http://localhost:8000/jobs/<job_id>
```

### 8. Run tests

```bash
pytest tests/ -v
```

Tests in Phase 0+1 are pure unit tests (no external calls or DB needed).

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| POST | `/jobs` | Create a job and enqueue script generation |
| GET | `/jobs/{job_id}` | Get job status + slide list |
| POST | `/jobs/{job_id}/slides/{idx}/retry-tts` | Retry TTS for an ERROR slide |
| POST | `/jobs/{job_id}/slides/{idx}/retry-layout` | Retry layout gen for a slide |

## Project Structure

```
.
├── docker-compose.yml        # Postgres, Redis, MinIO, bucket init
├── .env.example              # Required environment variables
├── pyproject.toml            # Python project & dependencies
├── alembic.ini               # Alembic config
├── alembic/
│   ├── env.py                # Async alembic env (asyncpg)
│   ├── script.py.mako        # Migration template
│   └── versions/             # Migration files (empty at init)
├── app/
│   ├── config.py             # Pydantic-settings Settings + get_settings()
│   ├── db.py                 # Async SQLAlchemy engine + get_db() dep
│   ├── models.py             # ORM: Job, Slide, PromptTemplate
│   ├── contracts.py          # Pydantic v2 data contracts
│   ├── states.py             # SlideState enum + transition_slide()
│   ├── storage.py            # MinIO/S3 helpers
│   ├── celery_app.py         # Celery app configured with Redis
│   ├── main.py               # FastAPI app with lifespan + seeding
│   ├── api/
│   │   └── routes.py         # REST endpoints
│   ├── llm/
│   │   ├── client.py         # Anthropic async client + call_with_tool()
│   │   ├── prompts.py        # PROMPT_SEEDS list
│   │   └── script_gen.py     # generate_script() with retry + quality gate
│   └── pipeline/
│       ├── quality_gate.py   # check_slide() + quality_gate_pass()
│       └── tasks.py          # Celery tasks (run_script_gen, run_tts, etc.)
└── tests/
    ├── test_quality_gate.py  # Quality gate unit tests
    └── test_script_hash.py   # SHA-256 determinism tests
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Required for Claude script generation |
| `ELEVENLABS_API_KEY` | Required for TTS (Phase 2b) |
| `ELEVENLABS_VOICE_ID` | ElevenLabs voice to use |
| `CLAUDE_MODEL` | Claude model ID (default: `claude-sonnet-4-6`) |
| `DATABASE_URL` | Async PostgreSQL URL |
| `REDIS_URL` | Redis URL for Celery broker/backend |
| `MINIO_ENDPOINT` | MinIO server URL |
| `MINIO_ACCESS_KEY` | MinIO access key |
| `MINIO_SECRET_KEY` | MinIO secret key |
| `MINIO_BUCKET` | Storage bucket name |
