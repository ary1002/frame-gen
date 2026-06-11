from app.contracts import SlideScript
import math


def check_slide(slide: SlideScript) -> list[str]:
    violations = []
    target_words = slide.est_duration_s * (130 / 60)
    lower = target_words * 0.8
    upper = target_words * 1.2
    if not (lower <= slide.word_count <= upper):
        violations.append(
            f"word_count {slide.word_count} outside [{lower:.0f},{upper:.0f}]"
        )
    text = slide.text.strip()
    if text and text[-1] not in ".!?":
        violations.append("text does not end with sentence terminator")
    return violations


def quality_gate_pass(slides: list[SlideScript]) -> bool:
    if len(slides) < 2:
        return False
    return all(len(check_slide(s)) == 0 for s in slides)
