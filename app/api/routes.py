import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Job, Slide

router = APIRouter()


class CreateJobRequest(BaseModel):
    prompt: str


@router.post("/jobs", status_code=201)
async def create_job(body: CreateJobRequest, db: AsyncSession = Depends(get_db)) -> dict:
    from app.pipeline.tasks import run_script_gen

    job = Job(prompt=body.prompt)
    db.add(job)
    await db.flush()
    job_id = str(job.id)
    await db.commit()

    run_script_gen.delay(job_id)

    return {"job_id": job_id}


@router.get("/jobs/{job_id}")
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id")

    job = await db.get(Job, job_uuid)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    result = await db.execute(
        select(Slide).where(Slide.job_id == job_uuid).order_by(Slide.slide_index)
    )
    slides = result.scalars().all()

    return {
        "id": str(job.id),
        "prompt": job.prompt,
        "status": job.status,
        "prompt_version": job.prompt_version,
        "total_frames": job.total_frames,
        "video_url": job.video_url,
        "article_url": job.article_url,
        "render_progress": job.render_progress,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        "slides": [
            {
                "id": str(s.id),
                "slide_index": s.slide_index,
                "state": s.state,
                "status": s.status,
                "error_message": s.error_message,
                "audio_url": s.audio_url,
                "actual_duration_s": s.actual_duration_s,
            }
            for s in slides
        ],
    }


@router.post("/jobs/{job_id}/slides/{slide_index}/retry-tts", status_code=202)
async def retry_tts(
    job_id: str, slide_index: int, db: AsyncSession = Depends(get_db)
) -> dict:
    from app.pipeline.tasks import run_tts

    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id")

    result = await db.execute(
        select(Slide).where(
            Slide.job_id == job_uuid, Slide.slide_index == slide_index
        )
    )
    slide = result.scalar_one_or_none()
    if slide is None:
        raise HTTPException(status_code=404, detail="Slide not found")

    if slide.state != "ERROR":
        raise HTTPException(
            status_code=400,
            detail=f"Slide state is '{slide.state}', retry-tts only allowed when state is ERROR",
        )

    run_tts.delay(job_id, slide_index)
    return {"queued": True}


@router.post("/jobs/{job_id}/slides/{slide_index}/retry-layout", status_code=202)
async def retry_layout(
    job_id: str, slide_index: int, db: AsyncSession = Depends(get_db)
) -> dict:
    from app.pipeline.tasks import run_layout_gen

    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id")

    result = await db.execute(
        select(Slide).where(
            Slide.job_id == job_uuid, Slide.slide_index == slide_index
        )
    )
    slide = result.scalar_one_or_none()
    if slide is None:
        raise HTTPException(status_code=404, detail="Slide not found")

    run_layout_gen.delay(job_id, slide_index)
    return {"queued": True}
