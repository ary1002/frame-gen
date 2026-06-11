import hashlib
import math
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts import SlideScript
from app.llm.client import call_with_tool
from app.models import PromptTemplate
from app.pipeline.quality_gate import check_slide, quality_gate_pass

TOOL_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "slides": {
            "type": "array",
            "description": "Ordered list of slides for the video",
            "items": {
                "type": "object",
                "properties": {
                    "slide_index": {
                        "type": "integer",
                        "description": "Zero-based index of the slide",
                    },
                    "text": {
                        "type": "string",
                        "description": "Narration text for the slide",
                    },
                    "word_count": {
                        "type": "integer",
                        "description": "Number of words in the narration text",
                    },
                    "est_duration_s": {
                        "type": "number",
                        "description": "Estimated duration in seconds at 130 WPM",
                    },
                },
                "required": ["slide_index", "text", "word_count", "est_duration_s"],
            },
        }
    },
    "required": ["slides"],
}


async def generate_script(
    job_id: str, prompt: str, db: AsyncSession
) -> list[SlideScript]:
    """Generate a slide script using Claude with quality gate retry logic."""
    # Load prompt template from DB
    template: PromptTemplate | None = await db.get(PromptTemplate, "script_gen.v1")
    system_base = template.system_prompt if template else ""

    last_violations: list[str] = []
    MAX_ATTEMPTS = 3

    for attempt in range(1, MAX_ATTEMPTS + 1):
        # Build system prompt (append violation context on retries)
        if attempt > 1 and last_violations:
            violations_str = "; ".join(last_violations)
            system = (
                system_base
                + f"\n\nPrevious attempt FAILED quality gate. Tighten word counts to be closer to est_duration_s × 130/60 words. Issues: {violations_str}"
            )
        else:
            system = system_base

        raw = await call_with_tool(
            system=system,
            user=prompt,
            tool_name="generate_slides",
            tool_description="Generate a structured list of narrated slides for a short educational video.",
            input_schema=TOOL_INPUT_SCHEMA,
        )

        raw_slides: list[dict[str, Any]] = raw.get("slides", [])

        slides: list[SlideScript] = []
        for i, raw_slide in enumerate(raw_slides):
            text: str = raw_slide.get("text", "")
            word_count = len(text.split())
            est_duration_s: float = float(raw_slide.get("est_duration_s", 0.0))
            script_hash = hashlib.sha256(text.encode()).hexdigest()

            slide = SlideScript(
                slide_index=raw_slide.get("slide_index", i),
                text=text,
                word_count=word_count,
                est_duration_s=est_duration_s,
                gen_attempts=attempt,
                status="READY",
                prompt_version="script_gen.v1",
                script_hash=script_hash,
            )
            slides.append(slide)

        # Collect violations for feedback
        all_violations: list[str] = []
        for s in slides:
            all_violations.extend(check_slide(s))
        last_violations = all_violations

        if quality_gate_pass(slides):
            return slides

        # On final attempt: hard-truncate failing slides
        if attempt == MAX_ATTEMPTS:
            for s in slides:
                violations = check_slide(s)
                if violations:
                    target = math.ceil(s.est_duration_s * 130 / 60)
                    words = s.text.split()
                    truncated = " ".join(words[:target])
                    s.text = truncated
                    s.word_count = len(truncated.split())
                    s.script_hash = hashlib.sha256(truncated.encode()).hexdigest()
                    s.status = "TRUNCATED"
            return slides

    return slides
