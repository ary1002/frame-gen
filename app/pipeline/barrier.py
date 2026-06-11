from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Slide, Job
import uuid

async def check_barrier(job_id: str, db: AsyncSession) -> None:
    """After every TTS or layout completion, check if we can proceed to timeline."""
    slides = (await db.execute(select(Slide).where(Slide.job_id == uuid.UUID(job_id)))).scalars().all()

    if not slides:
        return

    # Any ERROR -> hold
    if any(s.state == "ERROR" for s in slides):
        return

    # All AUDIO_READY?
    all_audio_ready = all(s.state == "AUDIO_READY" for s in slides)
    # All layouts written?
    all_layouts_done = all(s.layout_json is not None for s in slides)

    if all_audio_ready and all_layouts_done:
        from app.pipeline.tasks import run_timeline
        run_timeline.delay(job_id)
        job = await db.get(Job, uuid.UUID(job_id))
        if job:
            job.status = "RENDERING"
            await db.commit()
