"""Stage 2A: generate a SlideLayout for one slide via Claude structured output."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts import SlideLayout
from app.llm.client import call_with_tool
from app.models import PromptTemplate

_LAYOUT_SCHEMA = {
    "type": "object",
    "required": ["slide_index", "template", "props", "effect", "transition_out"],
    "properties": {
        "slide_index": {"type": "integer"},
        "template": {
            "type": "string",
            "enum": ["title_card", "bullet_list", "comparison_two_col", "split_layout"],
        },
        "props": {"type": "object"},
        "effect": {
            "type": "object",
            "required": ["type", "from", "to", "easing"],
            "properties": {
                "type": {"type": "string", "enum": ["zoom", "blur", "spotlight"]},
                "from": {"type": "number"},
                "to": {"type": "number"},
                "easing": {"type": "string"},
            },
        },
        "transition_out": {
            "type": "object",
            "required": ["type", "duration_frames"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["wipe", "fade", "dissolve", "circle_wipe", "stack"],
                },
                "direction": {"type": "string"},
                "duration_frames": {"type": "integer"},
            },
        },
    },
}


async def generate_layout(
    job_id: str, slide_index: int, text: str, db: AsyncSession
) -> SlideLayout:
    """
    Call Claude to generate a SlideLayout for the given narration text.
    Retries up to 2 times on Pydantic validation failure (3 total attempts).
    Sets duration_frames=None — filled by timeline assembler.
    """
    template_row = await db.get(PromptTemplate, "layout_gen.v1")
    system = template_row.system_prompt

    last_err: Exception | None = None
    for attempt in range(3):
        raw = await call_with_tool(
            system=system,
            user=f"Slide {slide_index}:\n\n{text}",
            tool_name="generate_layout",
            tool_description="Generate the visual layout for this slide",
            input_schema=_LAYOUT_SCHEMA,
        )
        try:
            layout = SlideLayout.model_validate(raw)
            layout.slide_index = slide_index
            layout.duration_frames = None
            return layout
        except Exception as e:
            last_err = e

    raise ValueError(f"Layout gen failed after 3 attempts: {last_err}") from last_err
