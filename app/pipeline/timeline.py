"""Stage 4: deterministic timeline assembly. No LLM. Pure arithmetic."""
import re
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

_STOP_WORDS = frozenset(
    "a an the and or but in on at to for of with is are was were be been"
    " have has had it its this that these those i we you he she they".split()
)


def _first_content_word(text: str) -> str:
    """Return the first non-stop lowercase word from a text string."""
    for token in re.split(r"\W+", text.lower()):
        if token and token not in _STOP_WORDS:
            return token
    return re.split(r"\W+", text.lower())[0] if text else ""


def compute_reveal_cues(
    element_texts: list[str],
    word_timestamps: list[dict],
    total_duration_s: float,
) -> list[float]:
    """
    For each element text, find the start_s of the first spoken word that
    matches its first content word, searching forward past the previous cue.
    Falls back to even distribution across the spoken duration.
    """
    if not element_texts:
        return []

    wts = word_timestamps  # list of {"word": str, "start_s": float, "end_s": float}
    n = len(element_texts)
    cues: list[float] = []
    search_from = 0  # index into wts to start next search from

    for i, text in enumerate(element_texts):
        keyword = _first_content_word(text)
        found_s: float | None = None
        if keyword:
            for j in range(search_from, len(wts)):
                w = re.sub(r"\W+", "", wts[j]["word"].lower())
                if w == keyword:
                    found_s = wts[j]["start_s"]
                    search_from = j + 1
                    break
        if found_s is None:
            # Even distribution fallback
            stagger = total_duration_s / max(n, 1)
            found_s = i * stagger
        cues.append(round(found_s, 3))

    return cues


def _element_texts_for_template(template: str, props: dict) -> list[str]:
    """Extract ordered animatable element texts from a slide's props."""
    if template == "title_card":
        return [props.get("title", "")]
    if template == "bullet_list":
        return list(props.get("points", []))
    if template == "comparison_two_col":
        texts = []
        for col in props.get("columns", []):
            texts.append(col.get("heading", ""))
            texts.extend(col.get("points", []))
        return texts
    if template == "split_layout":
        return [props.get("title", ""), props.get("body", "")]
    return []


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

        raw_wts = s.get("word_timestamps") or []
        local_wts = [
            WordTimestamp(word=wt["word"], start_s=wt["start_s"], end_s=wt["end_s"])
            for wt in raw_wts
        ]
        element_texts = _element_texts_for_template(
            layout.template, layout.props
        )
        cues = compute_reveal_cues(
            element_texts,
            [{"word": wt.word, "start_s": wt.start_s, "end_s": wt.end_s} for wt in local_wts],
            s["actual_duration_s"],
        )

        entry = SlideEntry(
            slide_index=s["slide_index"],
            start_frame=start_frame,
            duration_frames=duration_frames,
            audio_url=s["audio_url"],
            layout=layout,
            word_timestamps=local_wts,
            cues=cues,
        )
        slide_entries.append(entry)
        cumulative_frames += duration_frames

        slide_start_s = start_frame / FPS
        breath_s = BREATH_FRAMES / FPS
        for wt in raw_wts:
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
