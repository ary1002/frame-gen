"""Verify the render.mjs path resolves correctly."""
from pathlib import Path


def test_render_mjs_path_points_to_correct_file():
    from app.pipeline.render import _RENDER_MJS
    assert _RENDER_MJS.name == "render.mjs"
    assert _RENDER_MJS.exists(), f"render.mjs not found at {_RENDER_MJS}"
