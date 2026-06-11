import hashlib
import pytest

from app.contracts import SlideScript
from app.pipeline.quality_gate import check_slide, quality_gate_pass


def make_slide(text: str, est_duration_s: float, slide_index: int = 0) -> SlideScript:
    word_count = len(text.split())
    return SlideScript(
        slide_index=slide_index,
        text=text,
        word_count=word_count,
        est_duration_s=est_duration_s,
        gen_attempts=1,
        status="READY",
        prompt_version="script_gen.v1",
        script_hash=hashlib.sha256(text.encode()).hexdigest(),
    )


def test_slide_within_bounds_passes():
    # 30s * 130/60 = 65 target words; ±20% = [52, 78]
    text = " ".join(["word"] * 65) + "."
    slide = make_slide(text, est_duration_s=30.0)
    violations = check_slide(slide)
    assert violations == []


def test_slide_too_few_words_fails():
    # 30s target = 65 words; 40 words is below 80% lower bound (52)
    text = " ".join(["word"] * 40) + "."
    slide = make_slide(text, est_duration_s=30.0)
    violations = check_slide(slide)
    assert any("word_count" in v for v in violations)


def test_slide_too_many_words_fails():
    # 30s target = 65 words; 90 words is above 120% upper bound (78)
    text = " ".join(["word"] * 90) + "."
    slide = make_slide(text, est_duration_s=30.0)
    violations = check_slide(slide)
    assert any("word_count" in v for v in violations)


def test_slide_ending_mid_sentence_fails():
    # Within word bounds but ends without sentence terminator
    text = " ".join(["word"] * 65) + " incomplete"
    slide = make_slide(text, est_duration_s=30.0)
    violations = check_slide(slide)
    assert any("sentence terminator" in v for v in violations)


def test_slide_ending_with_exclamation_passes():
    text = " ".join(["word"] * 65) + "!"
    slide = make_slide(text, est_duration_s=30.0)
    violations = check_slide(slide)
    # Should not have sentence terminator violation
    assert not any("sentence terminator" in v for v in violations)


def test_quality_gate_fewer_than_two_slides_fails():
    text = " ".join(["word"] * 65) + "."
    slide = make_slide(text, est_duration_s=30.0)
    assert quality_gate_pass([slide]) is False


def test_quality_gate_zero_slides_fails():
    assert quality_gate_pass([]) is False


def test_quality_gate_two_good_slides_passes():
    text = " ".join(["word"] * 65) + "."
    s1 = make_slide(text, est_duration_s=30.0, slide_index=0)
    s2 = make_slide(text, est_duration_s=30.0, slide_index=1)
    assert quality_gate_pass([s1, s2]) is True


def test_quality_gate_one_bad_slide_fails():
    good_text = " ".join(["word"] * 65) + "."
    bad_text = " ".join(["word"] * 10) + " no terminator"
    s1 = make_slide(good_text, est_duration_s=30.0, slide_index=0)
    s2 = make_slide(bad_text, est_duration_s=30.0, slide_index=1)
    assert quality_gate_pass([s1, s2]) is False
