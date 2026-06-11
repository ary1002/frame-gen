"""Unit tests for article generation — mocks Claude and storage."""
import sys
from unittest.mock import MagicMock

import pytest

# Stub out boto3 before any app imports so storage.py doesn't fail
sys.modules.setdefault("boto3", MagicMock())
sys.modules.setdefault("botocore", MagicMock())
sys.modules.setdefault("botocore.client", MagicMock())


@pytest.mark.asyncio
async def test_article_gen_formats_markdown(monkeypatch):
    import app.llm.article_gen as article_gen
    import app.storage as storage_mod

    async def fake_call_with_tool(*args, **kwargs):
        return {"title": "Test Title", "body": "Some body text."}

    monkeypatch.setattr(article_gen, "call_with_tool", fake_call_with_tool)

    stored = {}
    monkeypatch.setattr(storage_mod, "put_bytes", lambda key, data, ct: stored.__setitem__(key, data))

    key = await article_gen.generate_article("job-123", ["Slide one.", "Slide two."])

    assert key == "job-123/article.md"
    content = stored[key].decode("utf-8")
    assert content.startswith("# Test Title")
    assert "Some body text." in content


@pytest.mark.asyncio
async def test_article_gen_key_uses_job_id(monkeypatch):
    import app.llm.article_gen as article_gen
    import app.storage as storage_mod

    async def fake_call(*args, **kwargs):
        return {"title": "T", "body": "B"}

    monkeypatch.setattr(article_gen, "call_with_tool", fake_call)
    monkeypatch.setattr(storage_mod, "put_bytes", lambda *a: None)

    key = await article_gen.generate_article("abc-999", ["text"])
    assert key == "abc-999/article.md"
