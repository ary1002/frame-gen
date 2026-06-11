import asyncio

import sqlalchemy
from celery import group

from app.celery_app import celery_app


@celery_app.task(bind=True, name="run_script_gen")
def run_script_gen(self, job_id: str):
    """Stage 1: generate script, persist slides, fan out TTS + layout."""
    asyncio.run(_run_script_gen_async(job_id))


async def _run_script_gen_async(job_id: str):
    import uuid

    from app.db import AsyncSessionLocal
    from app.llm.script_gen import generate_script
    from app.models import Job, Slide

    async with AsyncSessionLocal() as db:
        job = await db.get(Job, uuid.UUID(job_id))
        job.status = "RUNNING"
        await db.commit()

        scripts = await generate_script(job_id, job.prompt, db)

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

        tts_tasks = [run_tts.s(job_id, s.slide_index) for s in scripts]
        layout_tasks = [run_layout_gen.s(job_id, s.slide_index) for s in scripts]
        group(tts_tasks + layout_tasks).delay()


@celery_app.task(bind=True, name="run_tts")
def run_tts(self, job_id: str, slide_index: int):
    """Stage 2B: synthesize audio for one slide."""
    asyncio.run(_run_tts_async(job_id, slide_index))


async def _run_tts_async(job_id: str, slide_index: int):
    import uuid

    from app.config import get_settings
    from app.db import AsyncSessionLocal
    from app.models import Slide
    from app.pipeline.barrier import check_barrier
    from app.tts.elevenlabs import TTSError, synthesize_slide

    s = get_settings()
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            sqlalchemy.select(Slide).where(
                Slide.job_id == uuid.UUID(job_id),
                Slide.slide_index == slide_index,
            )
        )
        slide = result.scalar_one_or_none()
        if slide is None:
            raise ValueError(f"Slide {slide_index} not found for job {job_id}")

        if slide.state == "AUDIO_READY":
            return

        slide.state = "AUDIO_STALE"
        await db.commit()

        try:
            blob, word_timestamps = await synthesize_slide(
                slide_index=slide_index,
                text=slide.text,
                script_hash=slide.script_hash,
                voice_id=s.ELEVENLABS_VOICE_ID,
                job_id=job_id,
            )
        except TTSError as e:
            slide.state = "ERROR"
            slide.error_message = str(e)
            await db.commit()
            raise

        slide.audio_url = blob.url
        slide.actual_duration_s = blob.actual_duration_s
        slide.voice_id = blob.voice_id
        slide.word_timestamps = [wt.model_dump() for wt in word_timestamps]
        slide.state = "AUDIO_READY"
        await db.commit()

        await check_barrier(job_id, db)


@celery_app.task(bind=True, name="run_layout_gen")
def run_layout_gen(self, job_id: str, slide_index: int):
    pass  # Stage 2A — implemented later


@celery_app.task(bind=True, name="run_timeline")
def run_timeline(self, job_id: str):
    pass  # Stage 4 — implemented later


@celery_app.task(bind=True, name="run_render")
def run_render(self, job_id: str):
    pass  # Stage 6 — implemented later


@celery_app.task(bind=True, name="run_article_gen")
def run_article_gen(self, job_id: str):
    pass  # Stage 6 parallel — implemented later
