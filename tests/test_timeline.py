"""Unit tests for timeline assembly arithmetic. No DB or API calls."""
from app.pipeline.timeline import assemble_timeline


def _make_slide(idx, duration_s, template="title_card"):
    return {
        "slide_index": idx,
        "actual_duration_s": duration_s,
        "layout_json": {
            "slide_index": idx,
            "template": template,
            "props": {"title": f"Slide {idx}"},
            "effect": {"type": "zoom", "from": 1.0, "to": 1.05, "easing": "linear"},
            "transition_out": {"type": "fade", "duration_frames": 20},
            "duration_frames": None,
        },
        "audio_url": f"http://minio/audio/{idx}.mp3",
        "word_timestamps": [
            {"word": "hello", "start_s": 0.0, "end_s": 0.4},
            {"word": "world", "start_s": 0.5, "end_s": 0.9},
        ],
    }


def test_single_slide_frame_math():
    schema = assemble_timeline([_make_slide(0, 5.0)])
    assert schema.slides[0].duration_frames == 150  # round(5.0 * 30)
    assert schema.slides[0].start_frame == 0
    assert schema.total_frames == 150


def test_two_slides_overlap():
    schema = assemble_timeline([_make_slide(0, 5.0), _make_slide(1, 3.0)])
    assert schema.slides[0].start_frame == 0
    assert schema.slides[0].duration_frames == 150
    # start_frame[1] = 150 - (20 * 1) = 130
    assert schema.slides[1].start_frame == 130
    assert schema.slides[1].duration_frames == 90


def test_three_slides_overlap():
    schema = assemble_timeline([_make_slide(0, 2.0), _make_slide(1, 2.0), _make_slide(2, 2.0)])
    assert schema.slides[0].start_frame == 0   # 0 - 20*0 = 0
    assert schema.slides[1].start_frame == 40  # 60 - 20*1 = 40
    assert schema.slides[2].start_frame == 80  # 120 - 20*2 = 80


def test_total_frames_two_slides():
    schema = assemble_timeline([_make_slide(0, 5.0), _make_slide(1, 3.0)])
    # total = 150 + 90 - 20*(2-1) = 220
    assert schema.total_frames == 220


def test_total_frames_three_slides():
    schema = assemble_timeline([_make_slide(0, 2.0), _make_slide(1, 2.0), _make_slide(2, 2.0)])
    # total = 60+60+60 - 20*2 = 140
    assert schema.total_frames == 140


def test_duration_frames_filled_in_layout():
    schema = assemble_timeline([_make_slide(0, 4.0)])
    assert schema.slides[0].layout.duration_frames == 120


def test_word_timestamps_offset():
    schema = assemble_timeline([_make_slide(0, 5.0), _make_slide(1, 3.0)])
    # Slide 1 starts at frame 130 → start_time = 130/30
    slide1_hellos = [wt for wt in schema.captions.word_timestamps
                     if wt.word == "hello" and wt.start_s > 1.0]
    assert len(slide1_hellos) == 1
    expected_offset = 130 / 30
    assert abs(slide1_hellos[0].start_s - (0.0 + expected_offset)) < 0.01


def test_fps_constant():
    schema = assemble_timeline([_make_slide(0, 1.0)])
    assert schema.fps == 30


def test_slides_sorted_by_index():
    schema = assemble_timeline([_make_slide(1, 2.0), _make_slide(0, 3.0)])
    assert schema.slides[0].slide_index == 0
    assert schema.slides[1].slide_index == 1


def test_serve_url_local():
    schema = assemble_timeline([_make_slide(0, 1.0)])
    assert schema.serve_url == "local"
