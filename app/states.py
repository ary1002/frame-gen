from enum import Enum
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Slide


class SlideState(str, Enum):
    PENDING = "PENDING"
    SCRIPT_READY = "SCRIPT_READY"
    AUDIO_STALE = "AUDIO_STALE"
    AUDIO_READY = "AUDIO_READY"
    RENDER_READY = "RENDER_READY"
    ERROR = "ERROR"


ALLOWED_TRANSITIONS: dict[SlideState, set[SlideState]] = {
    SlideState.PENDING: {SlideState.SCRIPT_READY, SlideState.ERROR},
    SlideState.SCRIPT_READY: {SlideState.AUDIO_STALE, SlideState.AUDIO_READY, SlideState.ERROR},
    SlideState.AUDIO_STALE: {SlideState.AUDIO_READY, SlideState.ERROR},
    SlideState.AUDIO_READY: {SlideState.RENDER_READY, SlideState.AUDIO_STALE, SlideState.ERROR},
    SlideState.RENDER_READY: {SlideState.AUDIO_STALE, SlideState.ERROR},
    SlideState.ERROR: {SlideState.PENDING, SlideState.SCRIPT_READY},
}


async def transition_slide(
    slide_id: uuid.UUID,
    new_state: SlideState,
    db: AsyncSession,
) -> Slide:
    """Load slide, validate transition, persist new state, return updated slide."""
    slide = await db.get(Slide, slide_id)
    if slide is None:
        raise ValueError(f"Slide {slide_id} not found")

    current = SlideState(slide.state)
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if new_state not in allowed:
        raise ValueError(
            f"Transition {current} -> {new_state} is not allowed. "
            f"Allowed: {allowed}"
        )

    slide.state = new_state.value
    await db.commit()
    await db.refresh(slide)
    return slide
