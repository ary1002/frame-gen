from app.celery_app import celery_app
import asyncio

@celery_app.task(bind=True, name="run_script_gen")
def run_script_gen(self, job_id: str):
    pass  # implemented in phases-0-1

@celery_app.task(bind=True, name="run_tts")
def run_tts(self, job_id: str, slide_index: int):
    asyncio.run(_run_tts_async(job_id, slide_index))

async def _run_tts_async(job_id: str, slide_index: int):
    from app.db import AsyncSessionLocal
    from app.models import Slide
    from app.tts.elevenlabs import synthesize_slide, TTSError
    from app.config import get_settings
    import uuid, json
    import sqlalchemy

    s = get_settings()
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            sqlalchemy.select(Slide).where(
                Slide.job_id == uuid.UUID(job_id),
                Slide.slide_index == slide_index
            )
        )
        slide = result.scalar_one_or_none()
        if slide is None:
            raise ValueError(f"Slide {slide_index} not found for job {job_id}")

        if slide.state == "AUDIO_READY":
            return  # already done

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

        from app.pipeline.barrier import check_barrier
        await check_barrier(job_id, db)

@celery_app.task(bind=True, name="run_layout_gen")
def run_layout_gen(self, job_id: str, slide_index: int):
    pass

@celery_app.task(bind=True, name="run_timeline")
def run_timeline(self, job_id: str):
    pass

@celery_app.task(bind=True, name="run_render")
def run_render(self, job_id: str):
    pass

@celery_app.task(bind=True, name="run_article_gen")
def run_article_gen(self, job_id: str):
    pass
