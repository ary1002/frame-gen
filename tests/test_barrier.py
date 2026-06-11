import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch


def make_slide(state: str, layout_json=None):
    slide = MagicMock()
    slide.state = state
    slide.layout_json = layout_json
    return slide


@pytest.mark.asyncio
async def test_all_audio_ready_and_layouts_enqueues_timeline():
    """All AUDIO_READY + all layouts present -> enqueue timeline."""
    job_id = str(uuid.uuid4())
    slides = [
        make_slide("AUDIO_READY", layout_json={"template": "title_card"}),
        make_slide("AUDIO_READY", layout_json={"template": "bullet_list"}),
    ]

    mock_db = AsyncMock()
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = slides
    mock_db.execute = AsyncMock(return_value=mock_execute_result)

    mock_job = MagicMock()
    mock_db.get = AsyncMock(return_value=mock_job)

    with patch("app.pipeline.tasks.run_timeline") as mock_run_timeline:
        mock_run_timeline.delay = MagicMock()
        from app.pipeline.barrier import check_barrier
        await check_barrier(job_id, mock_db)

    mock_run_timeline.delay.assert_called_once_with(job_id)
    assert mock_job.status == "RENDERING"
    mock_db.commit.assert_called()


@pytest.mark.asyncio
async def test_error_slide_does_not_enqueue():
    """One ERROR slide -> do not enqueue timeline."""
    job_id = str(uuid.uuid4())
    slides = [
        make_slide("AUDIO_READY", layout_json={"template": "title_card"}),
        make_slide("ERROR", layout_json={"template": "bullet_list"}),
    ]

    mock_db = AsyncMock()
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = slides
    mock_db.execute = AsyncMock(return_value=mock_execute_result)

    with patch("app.pipeline.tasks.run_timeline") as mock_run_timeline:
        mock_run_timeline.delay = MagicMock()
        from app.pipeline.barrier import check_barrier
        await check_barrier(job_id, mock_db)

    mock_run_timeline.delay.assert_not_called()


@pytest.mark.asyncio
async def test_audio_ready_but_missing_layout_does_not_enqueue():
    """All AUDIO_READY but one layout_json=None -> do not enqueue timeline."""
    job_id = str(uuid.uuid4())
    slides = [
        make_slide("AUDIO_READY", layout_json={"template": "title_card"}),
        make_slide("AUDIO_READY", layout_json=None),
    ]

    mock_db = AsyncMock()
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = slides
    mock_db.execute = AsyncMock(return_value=mock_execute_result)

    with patch("app.pipeline.tasks.run_timeline") as mock_run_timeline:
        mock_run_timeline.delay = MagicMock()
        from app.pipeline.barrier import check_barrier
        await check_barrier(job_id, mock_db)

    mock_run_timeline.delay.assert_not_called()
