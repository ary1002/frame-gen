from app.celery_app import celery_app
from celery import group
import asyncio


@celery_app.task(bind=True, name="run_script_gen")
def run_script_gen(self, job_id: str):
    """Stage 1: generate script, persist slides, fan out TTS + layout."""
    asyncio.run(_run_script_gen_async(job_id))


async def _run_script_gen_async(job_id: str):
    from app.db import AsyncSessionLocal
    from app.models import Job, Slide
    from app.llm.script_gen import generate_script
    import uuid

    async with AsyncSessionLocal() as db:
        job = await db.get(Job, uuid.UUID(job_id))
        job.status = "RUNNING"
        await db.commit()

        scripts = await generate_script(job_id, job.prompt, db)

        # Persist slides
        for s in scripts:
            slide = Slide(
                job_id=uuid.UUID(job_id),
                slide_index=s.slide_index,
                state="SCRIPT_READY",
                text=s.text,
                word_count=s.word_count,
                est_duration_s=s.est_duration_s,
                gen_attempts=s.gen_attempts,
                status=s.status,
                prompt_version=s.prompt_version,
                script_hash=s.script_hash,
            )
            db.add(slide)
        await db.commit()

        # Fan out TTS + layout gen per slide
        tts_tasks = [run_tts.s(job_id, s.slide_index) for s in scripts]
        layout_tasks = [run_layout_gen.s(job_id, s.slide_index) for s in scripts]
        group(tts_tasks + layout_tasks).delay()


@celery_app.task(bind=True, name="run_tts")
def run_tts(self, job_id: str, slide_index: int):
    pass  # implemented in phases-2b-3


@celery_app.task(bind=True, name="run_layout_gen")
def run_layout_gen(self, job_id: str, slide_index: int):
    pass  # implemented later


@celery_app.task(bind=True, name="run_timeline")
def run_timeline(self, job_id: str):
    pass  # implemented later


@celery_app.task(bind=True, name="run_render")
def run_render(self, job_id: str):
    pass  # implemented later


@celery_app.task(bind=True, name="run_article_gen")
def run_article_gen(self, job_id: str):
    pass  # implemented later
