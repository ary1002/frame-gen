"""Stage 6 (parallel): generate a markdown article from all slide scripts."""
from app.llm.client import call_with_tool

_ARTICLE_SCHEMA = {
    "type": "object",
    "required": ["title", "body"],
    "properties": {
        "title": {"type": "string"},
        "body": {
            "type": "string",
            "description": "Full markdown article body",
        },
    },
}

_SYSTEM = """You are a content writer. Given the narration scripts for a series of video slides, write a comprehensive, well-structured markdown article that covers all the same information in a readable long-form format. Use headers, bullet points, and emphasis where appropriate. The article should stand alone — a reader who hasn't seen the video should find it complete and valuable."""


async def generate_article(job_id: str, slide_texts: list[str]) -> str:
    """
    Single Claude call over all slide texts → markdown article.
    Stores article.md in MinIO under {job_id}/article.md.
    Returns the MinIO key.
    """
    numbered = "\n\n".join(
        f"[Slide {i + 1}]\n{t}" for i, t in enumerate(slide_texts)
    )
    user = (
        f"Here are the narration scripts for a video:\n\n{numbered}\n\n"
        "Write a complete markdown article covering all this content."
    )

    result = await call_with_tool(
        system=_SYSTEM,
        user=user,
        tool_name="write_article",
        tool_description="Write a markdown article from the video narration scripts",
        input_schema=_ARTICLE_SCHEMA,
    )

    title = result.get("title", "Article")
    body = result.get("body", "")
    markdown = f"# {title}\n\n{body}"

    from app import storage  # deferred to avoid boto3 at import time
    key = f"{job_id}/article.md"
    storage.put_bytes(key, markdown.encode("utf-8"), "text/markdown")
    return key
