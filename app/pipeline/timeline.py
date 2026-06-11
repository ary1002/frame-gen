"""Stage 4: deterministic timeline assembly. No LLM. Pure arithmetic."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts import (
    CaptionConfig,
    RemotionSchema,
    SlideEntry,
    SlideLayout,
    WordTimestamp,
)
from app.models import Job, Slide

FPS = 30
TRANSITION_OVERLAP_FRAMES = 20
# Silent padding added before each slide's audio. Must match BREATH_FRAMES in
# remotion/src/PipelineAComposition.tsx.
BREATH_FRAMES = 9


def assemble_timeline(slides_data: list[dict]) -> RemotionSchema:
    """
    Pure function: given a list of slide dicts produce a RemotionSchema.

    Frame math (spec §4):
      duration_frames = round(actual_duration_s × 30)
      start_frame     = Σ(previous duration_frames) - (20 × slide_index)
    """
    slides_data = sorted(slides_data, key=lambda s: s["slide_index"])

    slide_entries: list[SlideEntry] = []
    cumulative_frames = 0
    all_word_timestamps: list[WordTimestamp] = []

    for i, s in enumerate(slides_data):
        duration_frames = round(s["actual_duration_s"] * FPS) + BREATH_FRAMES
        start_frame = cumulative_frames - (TRANSITION_OVERLAP_FRAMES * i)

        layout_dict = dict(s["layout_json"])
        layout_dict["duration_frames"] = duration_frames
        layout = SlideLayout.model_validate(layout_dict)

        entry = SlideEntry(
            slide_index=s["slide_index"],
            start_frame=start_frame,
            duration_frames=duration_frames,
            audio_url=s["audio_url"],
            layout=layout,
        )
        slide_entries.append(entry)
        cumulative_frames += duration_frames

        slide_start_s = start_frame / FPS
        breath_s = BREATH_FRAMES / FPS
        for wt in s.get("word_timestamps") or []:
            all_word_timestamps.append(
                WordTimestamp(
                    word=wt["word"],
                    start_s=wt["start_s"] + slide_start_s + breath_s,
                    end_s=wt["end_s"] + slide_start_s + breath_s,
                )
            )

    n = len(slides_data)
    total_frames = cumulative_frames - (TRANSITION_OVERLAP_FRAMES * (n - 1)) if n > 1 else cumulative_frames

    captions = CaptionConfig(
        style="default",
        color_active="#FFFF00",
        word_timestamps=all_word_timestamps,
    )

    return RemotionSchema(
        slides=slide_entries,
        captions=captions,
        total_frames=total_frames,
        fps=FPS,
        serve_url="local",
    )


async def build_and_store_schema(job_id: str, db: AsyncSession) -> str:
    """
    Load all slides for job_id, assemble RemotionSchema, persist to MinIO and Job.
    Returns the MinIO key for the schema JSON.
    """
    result = await db.execute(select(Slide).where(Slide.job_id == uuid.UUID(job_id)))
    slides = result.scalars().all()

    slides_data = [
        {
            "slide_index": s.slide_index,
            "actual_duration_s": s.actual_duration_s,
            "layout_json": s.layout_json,
            "audio_url": s.audio_url,
            "word_timestamps": s.word_timestamps or [],
        }
        for s in slides
    ]

    schema = assemble_timeline(slides_data)

    from app import storage  # deferred to keep assemble_timeline importable without boto3
    key = f"{job_id}/remotion_schema.json"
    storage.put_json(key, schema.model_dump(by_alias=True))

    job = await db.get(Job, uuid.UUID(job_id))
    job.total_frames = schema.total_frames
    await db.commit()

    return key
